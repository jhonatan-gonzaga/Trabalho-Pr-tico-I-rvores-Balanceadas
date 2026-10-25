# Testes do gerenciador, do menu principal e do submenu de experimentos.

import contextlib
import csv
import io
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from experimentos import ExperimentosArvores
from gerenciador import GerenciadorVeiculos
from interface import InterfaceExperimentos, InterfaceTerminal
from veiculos import Veiculo


def veiculo(chave: str, proprietario: str = "Ana") -> Veiculo:
    # Cria um registro simples para os testes de cadastro e consulta.
    return Veiculo(chave, "ABC1234", "Modelo de teste", 2024, proprietario)


class TesteGerenciador(unittest.TestCase):
    def setUp(self) -> None:
        # Cria um gerenciador vazio e independente para cada teste.
        self.gerenciador = GerenciadorVeiculos()

    def test_cadastro(self) -> None:
        # Confere a normalização e a preservação do primeiro cadastro nas duas árvores.
        self.assertTrue(self.gerenciador.cadastrar_veiculo(veiculo("001.234.567-89")))
        self.assertFalse(
            self.gerenciador.cadastrar_veiculo(veiculo("00123456789", "Outra pessoa"))
        )
        for arvore in (self.gerenciador.avl, self.gerenciador.rubro_negra):
            self.assertEqual(arvore.obter_quantidade_nos(), 1)
            self.assertEqual(arvore.buscar("00123456789").proprietario, "Ana")
            self.assertTrue(arvore.validar())

    def test_selecao(self) -> None:
        # Trocar a seleção preserva os registros e direciona a busca para uma só árvore.
        self.gerenciador.cadastrar_veiculo(veiculo("00123456789"))
        antes_avl = self.gerenciador.avl.comparacoes
        antes_rn = self.gerenciador.rubro_negra.comparacoes
        self.gerenciador.selecionar_estrutura("Rubro-Negra")
        self.assertEqual(
            self.gerenciador.buscar_veiculo("001.234.567-89").renavam, "00123456789"
        )
        self.assertEqual(self.gerenciador.avl.comparacoes, antes_avl)
        self.assertEqual(self.gerenciador.rubro_negra.comparacoes, antes_rn + 1)
        self.gerenciador.selecionar_estrutura("AVL")
        self.assertEqual(self.gerenciador.listar_veiculos()[0].renavam, "00123456789")

    def test_remocao(self) -> None:
        # Confere que cada remoção deixa as mesmas chaves nas duas árvores.
        chaves = [f"{numero:011d}" for numero in (30, 10, 40, 20, 50)]
        for chave in chaves:
            self.gerenciador.cadastrar_veiculo(veiculo(chave))
        for chave in chaves:
            self.assertTrue(self.gerenciador.remover_veiculo(chave))
            self.assertEqual(
                [item.renavam for item in self.gerenciador.avl.em_ordem()],
                [item.renavam for item in self.gerenciador.rubro_negra.em_ordem()],
            )
            self.assertTrue(all(self.gerenciador.validar_arvores().values()))
        self.assertEqual(self.gerenciador.obter_estatisticas()["quantidade_nos"], 0)

    def test_arvore_vazia(self) -> None:
        # Confere os resultados das operações quando nenhum veículo foi cadastrado.
        self.assertIsNone(self.gerenciador.buscar_veiculo("999"))
        self.assertFalse(self.gerenciador.remover_veiculo("999"))
        self.assertEqual(self.gerenciador.listar_veiculos(), [])
        self.assertEqual(self.gerenciador.obter_extremos(), (None, None))
        self.assertEqual(self.gerenciador.obter_estatisticas()["altura"], 0)
        self.assertTrue(all(self.gerenciador.validar_arvores().values()))

    def test_copias(self) -> None:
        # Alterar os objetos recebidos ou devolvidos não deve mudar as chaves armazenadas.
        original = veiculo("00123456789")
        self.gerenciador.cadastrar_veiculo(original)
        original.renavam = "999"
        consultado = self.gerenciador.buscar_veiculo("00123456789")
        consultado.renavam = "888"
        self.gerenciador.listar_veiculos()[0].renavam = "777"
        menor, maior = self.gerenciador.obter_extremos()
        menor.renavam = "666"
        maior.renavam = "555"
        for arvore in (self.gerenciador.avl, self.gerenciador.rubro_negra):
            self.assertEqual(arvore.em_ordem()[0].renavam, "00123456789")
            self.assertTrue(arvore.validar())
        self.assertIsNot(
            self.gerenciador.avl.em_ordem()[0], self.gerenciador.rubro_negra.em_ordem()[0]
        )

    def test_percursos(self) -> None:
        # Confere a ordem dos percursos e os registros de menor e maior chave.
        for chave in ("3", "1", "2"):
            self.gerenciador.cadastrar_veiculo(veiculo(chave))
        for estrutura in ("AVL", "Rubro-Negra"):
            self.gerenciador.selecionar_estrutura(estrutura)
            for ordem, esperado in (
                ("em_ordem", ["1", "2", "3"]),
                ("pre_ordem", ["2", "1", "3"]),
                ("pos_ordem", ["1", "3", "2"]),
            ):
                self.assertEqual(
                    [item.renavam for item in self.gerenciador.listar_veiculos(ordem)],
                    esperado,
                )
            menor, maior = self.gerenciador.obter_extremos()
            self.assertEqual((menor.renavam, maior.renavam), ("1", "3"))

    def test_estatisticas(self) -> None:
        # Confere os contadores e as recolorações exclusivas da Rubro-Negra.
        for chave in ("3", "2", "1"):
            self.gerenciador.cadastrar_veiculo(veiculo(chave))
        for estrutura in ("AVL", "Rubro-Negra"):
            self.gerenciador.selecionar_estrutura(estrutura)
            estatisticas = self.gerenciador.obter_estatisticas()
            self.assertEqual(estatisticas["estrutura"], estrutura)
            self.assertEqual(estatisticas["altura"], 2)
            self.assertEqual(estatisticas["quantidade_nos"], 3)
            self.assertEqual(estatisticas["rotacoes_insercao"], 1)
            self.assertEqual(estatisticas["rotacoes_remocao"], 0)
            if estrutura == "Rubro-Negra":
                self.assertGreater(estatisticas["recoloracoes_insercao"], 0)
                self.assertEqual(estatisticas["recoloracoes_remocao"], 0)
            else:
                self.assertNotIn("recoloracoes_insercao", estatisticas)

    def test_modo_detalhado(self) -> None:
        # Somente a estrutura selecionada deve exibir as correções do modo detalhado.
        self.assertTrue(self.gerenciador.alternar_modo_detalhado())
        self.assertTrue(self.gerenciador.avl.detalhado)
        self.assertFalse(self.gerenciador.rubro_negra.detalhado)
        self.gerenciador.selecionar_estrutura("Rubro-Negra")
        self.assertFalse(self.gerenciador.avl.detalhado)
        self.assertTrue(self.gerenciador.rubro_negra.detalhado)
        self.assertFalse(self.gerenciador.alternar_modo_detalhado())
        self.assertFalse(self.gerenciador.avl.detalhado)
        self.assertFalse(self.gerenciador.rubro_negra.detalhado)

    def test_validacao(self) -> None:
        # Confere seleções inválidas e a detecção de um defeito em apenas uma árvore.
        with self.assertRaises(ValueError):
            self.gerenciador.selecionar_estrutura("Inexistente")
        with self.assertRaises(ValueError):
            self.gerenciador.listar_veiculos("Inexistente")
        self.assertEqual(self.gerenciador.estrutura_selecionada, "AVL")
        self.gerenciador.cadastrar_veiculo(veiculo("1"))
        self.gerenciador.avl.raiz.altura = 9
        self.assertEqual(
            self.gerenciador.validar_arvores(), {"AVL": False, "Rubro-Negra": True}
        )


class TesteMenu(unittest.TestCase):
    def setUp(self) -> None:
        # Prepara um gerenciador vazio para os fluxos do menu principal.
        self.gerenciador = GerenciadorVeiculos()

    def menu(self, entradas: list) -> str:
        # Simula as entradas do usuário e captura as mensagens exibidas pelo menu.
        saida = io.StringIO()
        with patch("builtins.input", side_effect=entradas), contextlib.redirect_stdout(saida):
            InterfaceTerminal(self.gerenciador).executar()
        return saida.getvalue()

    def test_fluxo(self) -> None:
        # Confere o fluxo de cadastro, consulta, alternância e remoção pelo menu.
        saida = self.menu(
            [
                "2", "001.234.567-89", "abc1234", "Modelo de teste", "2024", "Ana",
                "3", "00123456789", "1", "5", "6", "7", "8", "10", "11",
                "12", "1", "12", "2", "13", "13", "9", "0",
                "4", "001.234.567-89", "3", "00123456789", "5", "0",
            ]
        )
        for trecho in (
            "cadastrado nas duas árvores", "Placa: ABC1234", "Proprietário: Ana",
            "Estrutura selecionada: Rubro-Negra", "Quantidade de nós: 1",
            "Recolorações na inserção:", "AVL: válida.", "Rubro-Negra: válida.",
            "00123456789 (PRETO)", "Veículo de menor RENAVAM:",
            "em pré-ordem", "em pós-ordem", "Modo detalhado ativado",
            "Experimentos comparativos", "removido das duas árvores",
            "Nenhum veículo encontrado", "Nenhum veículo cadastrado",
            "Aplicação encerrada.",
        ):
            self.assertIn(trecho, saida)
        self.assertEqual(self.gerenciador.avl.obter_quantidade_nos(), 0)
        self.assertEqual(self.gerenciador.rubro_negra.obter_quantidade_nos(), 0)

    def test_entradas(self) -> None:
        # Confere a correção de campos vazios, RENAVAM inválido e ano inválido.
        saida = self.menu(
            [
                "2", "---", "00123456789", "", "abc1234", "", "Modelo",
                "texto", "0", "2024", "", "Ana", "0",
            ]
        )
        for trecho in ("RENAVAM inválido", "placa é obrigatório", "modelo é obrigatório",
                       "Ano inválido", "proprietário é obrigatório"):
            self.assertIn(trecho, saida)
        self.assertEqual(self.gerenciador.avl.obter_quantidade_nos(), 1)
        self.assertTrue(all(self.gerenciador.validar_arvores().values()))

    def test_opcao_invalida(self) -> None:
        # Confere que opções inexistentes não interrompem o menu.
        saida = self.menu(["inválida", "12", "3", "0"])
        self.assertIn("Opção inválida", saida)
        self.assertIn("Escolha 1 para pré-ordem", saida)
        self.assertIn("Aplicação encerrada.", saida)

    def test_alternancia(self) -> None:
        # Confere a troca nas duas direções sem solicitar uma segunda opção.
        saida = self.menu(["13", "1", "1", "0"])
        self.assertIn("Estrutura selecionada: Rubro-Negra.", saida)
        self.assertIn("Estrutura selecionada: AVL.", saida)
        self.assertEqual(self.gerenciador.estrutura_selecionada, "AVL")
        self.assertTrue(self.gerenciador.detalhado)
        self.assertTrue(self.gerenciador.avl.detalhado)
        self.assertFalse(self.gerenciador.rubro_negra.detalhado)

    def test_duplicata(self) -> None:
        # Confere que o menu informa a duplicata e mantém os dados do primeiro cadastro.
        saida = self.menu(
            [
                "2", "00123456789", "ABC1234", "Modelo", "2024", "Ana",
                "2", "001.234.567-89", "XYZ9876", "Outro", "2025", "Bia", "0",
            ]
        )
        self.assertIn("Cadastro preservado", saida)
        self.assertEqual(self.gerenciador.buscar_veiculo("00123456789").proprietario, "Ana")
        self.assertEqual(self.gerenciador.avl.obter_quantidade_nos(), 1)
        self.assertEqual(self.gerenciador.rubro_negra.obter_quantidade_nos(), 1)

    def test_arvore_vazia(self) -> None:
        # Confere busca, remoção, listagem e visualização sem registros cadastrados.
        saida = self.menu(
            ["3", "999", "4", "999", "5", "6", "7", "8", "10", "11", "12", "1", "0"]
        )
        self.assertIn("Nenhum veículo encontrado", saida)
        self.assertIn("Nenhum veículo cadastrado", saida)
        self.assertIn("Quantidade de nós: 0", saida)
        self.assertIn("Altura: 0", saida)
        self.assertIn("Árvore vazia", saida)
        self.assertIn("AVL: válida.", saida)

    def test_listagem(self) -> None:
        # Confere a ordem dos veículos apresentados em blocos com seus atributos.
        for chave in ("3", "1", "2"):
            self.gerenciador.cadastrar_veiculo(veiculo(chave))
        saida = self.menu(["5", "0"])
        self.assertLess(saida.index("RENAVAM: 1\n"), saida.index("RENAVAM: 2\n"))
        self.assertLess(saida.index("RENAVAM: 2\n"), saida.index("RENAVAM: 3\n"))

    def test_isolamento(self) -> None:
        # Executa A, B, C e D pelo menu e confere o isolamento dos dados da sessão.
        self.gerenciador.cadastrar_veiculo(veiculo("00123456789"))
        self.gerenciador.selecionar_estrutura("Rubro-Negra")
        self.gerenciador.alternar_modo_detalhado()
        antes = self.gerenciador.obter_estatisticas()
        with TemporaryDirectory() as diretorio:
            executor = ExperimentosArvores(
                tamanhos=(10,), repeticoes=1, limite_buscas=3,
                diretorio_resultados=diretorio,
            )
            with patch("interface.experimentos.ExperimentosArvores", return_value=executor):
                saida = self.menu(["9", "A", "B", "C", "D", "0", "0"])
            self.assertTrue((Path(diretorio) / "resultados.csv").is_file())
            self.assertTrue((Path(diretorio) / "buscas.csv").is_file())
        self.assertIn("Resultados salvos em:", saida)
        self.assertEqual(self.gerenciador.obter_estatisticas(), antes)
        self.assertTrue(self.gerenciador.rubro_negra.detalhado)
        for arvore in (self.gerenciador.avl, self.gerenciador.rubro_negra):
            self.assertEqual(arvore.obter_quantidade_nos(), 1)
            self.assertEqual(arvore.em_ordem()[0].renavam, "00123456789")
            self.assertTrue(arvore.validar())

    def test_fim_entrada(self) -> None:
        # Confere que o laço principal deixa EOFError se propagar.
        with self.assertRaises(EOFError):
            self.menu([EOFError()])

    def test_interrupcao(self) -> None:
        # Confere que uma interrupção se propaga sem cadastrar dados incompletos.
        with self.assertRaises(KeyboardInterrupt):
            self.menu(["2", "00123456789", KeyboardInterrupt()])
        self.assertEqual(self.gerenciador.avl.obter_quantidade_nos(), 0)
        self.assertEqual(self.gerenciador.rubro_negra.obter_quantidade_nos(), 0)


class TesteMenuExperimentos(unittest.TestCase):
    # Verifica a interação do submenu com os experimentos e com os arquivos de resultados.

    def setUp(self) -> None:
        # Prepara experimentos pequenos em um diretório temporário.
        temporario = TemporaryDirectory()
        self.addCleanup(temporario.cleanup)
        self.diretorio = Path(temporario.name)
        self.executor = ExperimentosArvores(
            tamanhos=(10,), repeticoes=1, limite_buscas=3,
            diretorio_resultados=self.diretorio,
        )

    def menu(self, entradas: list) -> str:
        # Simula as escolhas do submenu e captura a apresentação dos resultados.
        saida = io.StringIO()
        with patch("builtins.input", side_effect=entradas), contextlib.redirect_stdout(saida):
            InterfaceExperimentos(self.executor).executar()
        return saida.getvalue()

    def ler_csv(self) -> list[dict]:
        # Lê as medições que o submenu salvou no CSV temporário.
        with (self.diretorio / "resultados.csv").open(encoding="utf-8", newline="") as arquivo:
            return list(csv.DictReader(arquivo))

    def test_opcoes(self) -> None:
        # Confere A, B, C e D, incluindo escolhas em minúsculas e exportação das visitas.
        saida = self.menu(["a", "b", "c", "d", "0"])
        resultados = self.ler_csv()
        self.assertEqual({r["experimento"] for r in resultados}, {"A", "B", "C", "D"})
        self.assertEqual(len(resultados), 24)
        self.assertIn("Visitas por busca salvas em:", saida)
        self.assertIn("A. Inserção em ordem crescente", saida)
        self.assertIn("D. Remoção de subconjuntos", saida)
        self.assertTrue((self.diretorio / "buscas.csv").is_file())

    def test_todos(self) -> None:
        # Confere a execução conjunta dos experimentos por uma única escolha.
        self.menu(["T", "0"])
        self.assertEqual(len(self.ler_csv()), 24)

    def test_opcao_invalida(self) -> None:
        # Uma escolha inválida e o retorno não devem executar experimentos.
        saida = self.menu(["X", "0"])
        self.assertIn("Opção inválida", saida)
        self.assertEqual(self.executor.resultados, [])
        self.assertFalse((self.diretorio / "resultados.csv").exists())

    def test_repeticao(self) -> None:
        # Confere que executar A duas vezes preserva quatro medições, sem duplicar as primeiras.
        self.menu(["A", "A", "0"])
        resultados = self.ler_csv()
        self.assertEqual(len(resultados), 4)


if __name__ == "__main__":
    unittest.main()
