# Testes de geração de dados, medições e exportação dos experimentos.

import csv
import unittest
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from avl import ArvoreAVL
from experimentos import CAMPOS_BUSCAS, CAMPOS_RESULTADOS, ExperimentosArvores
from rubro_negra import ArvoreRubroNegra


class TesteExperimentos(unittest.TestCase):
    # Usa árvores pequenas e arquivos temporários para verificar o protocolo de comparação.

    def setUp(self) -> None:
        # Cria um diretório exclusivo que é removido ao terminar cada teste.
        temporario = TemporaryDirectory()
        self.addCleanup(temporario.cleanup)
        self.diretorio = Path(temporario.name)

    def criar(
        self, tamanhos=(10,), repeticoes=1, percentuais_remocao=(10, 30, 50), limite_buscas=5,
    ) -> ExperimentosArvores:
        # Cria experimentos pequenos com arquivos temporários.
        return ExperimentosArvores(
            tamanhos=tamanhos, repeticoes=repeticoes, percentuais_remocao=percentuais_remocao,
            limite_buscas=limite_buscas, diretorio_resultados=self.diretorio,
        )

    def ler_csv(self, nome: str) -> list[dict]:
        # Lê um CSV produzido no diretório temporário.
        with (self.diretorio / nome).open(encoding="utf-8", newline="") as arquivo:
            return list(csv.DictReader(arquivo))

    def test_dados(self) -> None:
        # Confere as mesmas chaves nos dois cenários e a reprodução da ordem aleatória.
        executor = self.criar()

        crescente = executor.gerar_dados(20)
        primeira = executor.gerar_dados(20, "aleatoria", 42)
        segunda = executor.gerar_dados(20, "aleatoria", 42)
        outra = executor.gerar_dados(20, "aleatoria", 43)

        chaves = [v.renavam for v in crescente]
        ordem = [v.renavam for v in primeira]
        self.assertEqual(chaves, sorted(chaves))
        self.assertEqual(len(set(chaves)), 20)
        self.assertTrue(all(len(chave) == 11 and chave.isdigit() for chave in chaves))
        self.assertTrue(all(int(chave) % 2 == 0 for chave in chaves))
        self.assertEqual(ordem, [v.renavam for v in segunda])
        self.assertEqual(sorted(ordem), chaves)
        self.assertNotEqual(ordem, [v.renavam for v in outra])

    def test_parametros(self) -> None:
        # Impede divisões por zero e percentuais fora do intervalo permitido.
        for alteracao in (
            {"tamanhos": ()}, {"tamanhos": (0,)}, {"repeticoes": 0},
            {"limite_buscas": 0}, {"percentuais_remocao": (0,)},
            {"percentuais_remocao": (101,)},
        ):

            with self.subTest(alteracao=alteracao), self.assertRaises(ValueError):
                self.criar(**alteracao)
        executor = self.criar()

        with self.assertRaises(ValueError):
            executor.gerar_dados(0)
        with self.assertRaises(ValueError):
            executor.gerar_dados(3, "inexistente")

    def test_insercao(self) -> None:
        # Três chaves crescentes exigem uma rotação em cada árvore e três recolorações na RN.
        resultados = self.criar(tamanhos=(3,)).insercao_crescente()
        self.assertEqual(len(resultados), 2)
        for resultado in resultados:
            self.assertEqual(resultado["experimento"], "A")
            self.assertEqual(resultado["altura_final"], 2)
            self.assertEqual(resultado["rotacoes_insercao"], 1)
            self.assertEqual(resultado["rotacoes_remocao"], 0)
            self.assertGreaterEqual(resultado["tempo_insercao"], 0)
            self.assertEqual(resultado["tempo_busca"], "")
            esperado = 3 if resultado["estrutura"] == "Rubro-Negra" else 0
            self.assertEqual(resultado["recoloracoes"], esperado)

    def test_mesmos_dados(self) -> None:
        # Observa as entradas reais das construções, incluindo a repetição com ordem invertida.
        executor = self.criar(repeticoes=2)
        with patch.object(executor, "_montar", wraps=executor._montar) as construir:
            resultados = executor.insercao_aleatoria()
        chamadas = construir.call_args_list
        for indice in range(0, len(chamadas), 2):
            primeira = [v.renavam for v in chamadas[indice].args[1]]
            segunda = [v.renavam for v in chamadas[indice + 1].args[1]]
            self.assertEqual(primeira, segunda)
        self.assertEqual([r["semente"] for r in resultados], [42, 42, 43, 43])
        self.assertEqual(
            [r["estrutura"] for r in resultados], ["AVL", "Rubro-Negra", "Rubro-Negra", "AVL"]
        )

    def test_buscas(self) -> None:
        # Na árvore de três nós, buscar todos visita cinco nós; cada busca ausente visita dois.
        executor = self.criar(tamanhos=(3,), limite_buscas=3)
        resultados = executor.buscas()
        self.assertEqual(len(resultados), 8)
        self.assertEqual(len(executor.buscas_detalhadas), 24)
        for resultado in resultados:
            total = 5 if resultado["tipo_busca"] == "existente" else 6
            self.assertEqual(resultado["comparacoes_busca"], total)
            self.assertEqual(resultado["media_nos_visitados"], total / 3)
            self.assertEqual(resultado["quantidade_buscas"], 3)
            self.assertEqual(resultado["altura_antes"], resultado["altura_final"])

    def test_mesmas_buscas(self) -> None:
        # Confere a sequência de chaves efetivamente pesquisada em cada cenário.
        executor = self.criar()
        executor.buscas()
        grupos = {}
        for busca in executor.buscas_detalhadas:
            chave = (busca["ordem_insercao"], busca["tipo_busca"], busca["estrutura"])
            grupos.setdefault(chave, []).append(busca["renavam"])
        for tipo in ("existente", "inexistente"):
            referencia = grupos[("crescente", tipo, "AVL")]
            if tipo == "inexistente":
                self.assertTrue(all(int(chave) % 2 == 1 for chave in referencia))
                self.assertLess(min(referencia), f"{10 * 2:011d}")
            for ordem in ("crescente", "aleatoria"):
                for estrutura in ("AVL", "Rubro-Negra"):
                    self.assertEqual(grupos[(ordem, tipo, estrutura)], referencia)

    def test_tempo(self) -> None:
        # Um relógio controlado permite conferir os tempos sem depender da velocidade da máquina.
        executor = self.criar(tamanhos=(3,), limite_buscas=3)
        with patch("experimentos.perf_counter", side_effect=range(1000)):
            resultados = executor.buscas()
        for resultado in resultados:
            self.assertEqual(resultado["tempo_insercao"], 1)
            self.assertEqual(resultado["tempo_busca"], 1)
            self.assertIn(resultado["comparacoes_busca"], (5, 6))

    def test_remocoes(self) -> None:
        # Confere 10%, 30% e 50% do conjunto original, sem acumular as remoções.
        executor = self.criar()
        with patch.object(executor, "_validar", wraps=executor._validar) as validar:
            resultados = executor.remocoes()
        self.assertEqual(len(resultados), 12)
        # Cada árvore é validada depois da construção e depois da remoção.
        finais = validar.call_args_list[1::2]
        self.assertEqual(len(finais), 12)
        for resultado, chamada in zip(resultados, finais):
            arvore = chamada.args[0]
            restantes = 10 - resultado["percentual_remocao"] // 10
            self.assertEqual(arvore.obter_quantidade_nos(), restantes)
            self.assertGreaterEqual(resultado["altura_antes"], resultado["altura_final"])
            self.assertGreaterEqual(resultado["tempo_remocao"], 0)
            esperado = arvore.recoloracoes_remocao if isinstance(arvore, ArvoreRubroNegra) else 0
            self.assertEqual(resultado["recoloracoes"], esperado)

    def test_mesmas_remocoes(self) -> None:
        # Intercepta as remoções reais e compara seus RENAVAMs para cada árvore construída.
        executor = self.criar()
        with (
            patch.object(ArvoreAVL, "remover", autospec=True, side_effect=ArvoreAVL.remover) as avl,
            patch.object(
                ArvoreRubroNegra, "remover", autospec=True, side_effect=ArvoreRubroNegra.remover
            ) as rn,
        ):
            executor.remocoes()
        sequencias = []
        for chamadas in (avl.call_args_list, rn.call_args_list):
            por_arvore = {}
            for chamada in chamadas:
                por_arvore.setdefault(id(chamada.args[0]), []).append(chamada.args[1])
            sequencias.append(list(por_arvore.values()))
        self.assertEqual(sequencias[0], sequencias[1])
        self.assertEqual([len(chaves) for chaves in sequencias[0]], [1, 3, 5, 1, 3, 5])

    def test_remocao_total(self) -> None:
        # Trata a remoção de todos os nós e percentuais que resultam em zero remoções.
        executor = self.criar(tamanhos=(1,), percentuais_remocao=(10, 100))
        resultados = executor.remocoes()
        for resultado in resultados:
            esperado = 0 if resultado["percentual_remocao"] == 100 else 1
            self.assertEqual(resultado["altura_final"], esperado)

    def test_arvore_invalida(self) -> None:
        # Um defeito estrutural deve interromper a medição antes de registrar resultados válidos.
        executor = self.criar()
        with patch.object(ArvoreAVL, "validar", return_value=False):
            with self.assertRaises(RuntimeError):
                executor.insercao_crescente()
        self.assertEqual(executor.resultados, [])

    def test_busca_incorreta(self) -> None:
        # Detecta uma árvore que deixa de encontrar chaves presentes, mesmo mantendo sua estrutura.
        executor = self.criar()
        with patch.object(ArvoreAVL, "buscar", return_value=None):
            with self.assertRaises(RuntimeError):
                executor.buscas()

    def test_csv(self) -> None:
        # Salvar duas vezes não duplica linhas; outra instância acrescenta novas execuções.
        executor = self.criar()
        executor.insercao_crescente()
        executor.salvar_csv()
        executor.salvar_csv()
        self.assertEqual(len(self.ler_csv("resultados.csv")), 2)
        executor.insercao_aleatoria()
        executor.salvar_csv()
        outro = self.criar()
        outro.insercao_crescente()
        outro.salvar_csv()
        linhas = self.ler_csv("resultados.csv")
        self.assertEqual(len(linhas), 6)
        self.assertEqual(tuple(linhas[0]), CAMPOS_RESULTADOS)
        outro.buscas()
        outro.salvar_csv()
        outro.salvar_csv()
        buscas = self.ler_csv("buscas.csv")
        self.assertEqual(len(self.ler_csv("resultados.csv")), 14)
        self.assertEqual(len(buscas), 40)
        self.assertEqual(tuple(buscas[0]), CAMPOS_BUSCAS)

    def test_cabecalho(self) -> None:
        # Evita misturar silenciosamente arquivos de resultados com formatos diferentes.
        arquivo = self.diretorio / "resultados.csv"
        arquivo.write_text("coluna_antiga\nvalor\n", encoding="utf-8")
        executor = self.criar()
        executor.insercao_crescente()
        with self.assertRaises(ValueError):
            executor.salvar_csv()
        self.assertEqual(arquivo.read_text(encoding="utf-8"), "coluna_antiga\nvalor\n")

    def test_todos(self) -> None:
        # Confere a cobertura dos quatro cenários e a presença das métricas do enunciado.
        executor = self.criar()
        resultados = executor.todos()
        self.assertEqual(Counter(r["experimento"] for r in resultados), {"A": 2, "B": 2, "C": 8, "D": 12})
        obrigatorias = {
            "altura_final", "rotacoes_insercao", "rotacoes_remocao", "recoloracoes",
            "media_nos_visitados", "tempo_insercao", "tempo_busca", "tempo_remocao",
        }
        for resultado in resultados:
            self.assertTrue(obrigatorias.issubset(resultado))
            self.assertNotIn("python", resultado)
            self.assertNotIn("plataforma", resultado)
            self.assertNotIn("execucao", resultado)


if __name__ == "__main__":
    unittest.main()
