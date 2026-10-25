# Testes básicos das operações e propriedades da árvore Rubro-Negra.

import contextlib
import io
import unittest

from rubro_negra import ArvoreRubroNegra, PRETO, VERMELHO
from veiculos import Veiculo


def veiculo(chave: str) -> Veiculo:
    # Cria um veículo simples para os testes.
    return Veiculo(chave, "ABC1234", "Modelo", 2024, "Proprietário")


class TesteRubroNegra(unittest.TestCase):
    def test_cadastro(self) -> None:
        # Confere normalização, duplicatas e busca pelo RENAVAM.
        arvore = ArvoreRubroNegra()
        primeiro = veiculo("001.234.567-89")
        self.assertTrue(arvore.inserir(primeiro))
        self.assertFalse(arvore.inserir(veiculo("00123456789")))
        self.assertIs(arvore.buscar("001.234.567-89"), primeiro)
        self.assertEqual(arvore.obter_quantidade_nos(), 1)
        self.assertEqual(arvore.root.cor, PRETO)
        self.assertTrue(arvore.validar())

    def test_rotacoes(self) -> None:
        # Confere rotações simples e duplas nas duas direções.
        casos = ((("3", "2", "1"), 1), (("1", "2", "3"), 1),
                 (("3", "1", "2"), 2), (("1", "3", "2"), 2))
        for chaves, rotacoes in casos:
            with self.subTest(chaves=chaves):
                arvore = ArvoreRubroNegra()
                for chave in chaves:
                    arvore.inserir(veiculo(chave))
                self.assertEqual(arvore.root.veiculo.renavam, "2")
                self.assertEqual(arvore.rotacoes_insercao, rotacoes)
                self.assertEqual(arvore.recoloracoes_insercao, 3)
                self.assertTrue(arvore.validar())

    def test_remocao(self) -> None:
        # Remove uma folha, um nó com um filho e a raiz com dois filhos.
        casos = ((("2", "1", "3"), "1"), (("2", "1", "3", "4"), "3"),
                 (("2", "1", "3"), "2"))
        for chaves, removida in casos:
            with self.subTest(chaves=chaves):
                arvore = ArvoreRubroNegra()
                for chave in chaves:
                    arvore.inserir(veiculo(chave))
                self.assertTrue(arvore.remover(removida))
                self.assertIsNone(arvore.buscar(removida))
                self.assertEqual(arvore.obter_quantidade_nos(), len(chaves) - 1)
                self.assertEqual([v.renavam for v in arvore.em_ordem()],
                                 sorted(chave for chave in chaves if chave != removida))
                self.assertTrue(arvore.validar())

    def test_correcao(self) -> None:
        # Confere rotações e recolorações depois de quatro casos de remoção.
        casos = ((("2", "1", "3", "4"), "1", 1, 1),
                 (("3", "4", "2", "1"), "4", 1, 1),
                 (("2", "1", "4", "3"), "1", 2, 3),
                 (("3", "4", "1", "2"), "4", 2, 3))
        for chaves, removida, rotacoes, cores in casos:
            with self.subTest(chaves=chaves):
                arvore = ArvoreRubroNegra()
                for chave in chaves:
                    arvore.inserir(veiculo(chave))
                self.assertTrue(arvore.remover(removida))
                self.assertEqual(arvore.rotacoes_remocao, rotacoes)
                self.assertEqual(arvore.recoloracoes_remocao, cores)
                self.assertTrue(arvore.validar())

    def test_percursos(self) -> None:
        # Confere caminhamentos, menor e maior chave e altura.
        arvore = ArvoreRubroNegra()
        for chave in ("2", "1", "3"):
            arvore.inserir(veiculo(chave))
        self.assertEqual([v.renavam for v in arvore.em_ordem()], ["1", "2", "3"])
        self.assertEqual([v.renavam for v in arvore.pre_ordem()], ["2", "1", "3"])
        self.assertEqual([v.renavam for v in arvore.pos_ordem()], ["1", "3", "2"])
        self.assertEqual(arvore.minimo().renavam, "1")
        self.assertEqual(arvore.maximo().renavam, "3")
        self.assertEqual(arvore.obter_altura(), 2)

    def test_vazia(self) -> None:
        # Confere operações sem registros e a remoção do último veículo.
        arvore = ArvoreRubroNegra()
        self.assertIsNone(arvore.buscar("999"))
        self.assertFalse(arvore.remover("999"))
        self.assertIsNone(arvore.minimo())
        self.assertIsNone(arvore.maximo())
        self.assertEqual(arvore.em_ordem(), [])
        self.assertEqual(arvore.obter_altura(), 0)
        arvore.inserir(veiculo("1"))
        self.assertTrue(arvore.remover("1"))
        self.assertIs(arvore.root, arvore.NIL)
        self.assertEqual(arvore.obter_quantidade_nos(), 0)
        self.assertTrue(arvore.validar())

    def test_validacao(self) -> None:
        # Confere a rejeição de raiz vermelha, altura negra desigual e ordem incorreta.
        arvore = ArvoreRubroNegra()
        for chave in ("2", "1", "3"):
            arvore.inserir(veiculo(chave))
        arvore.root.cor = VERMELHO
        self.assertFalse(arvore.validar())
        arvore.root.cor = PRETO
        arvore.root.esquerda.cor = PRETO
        self.assertFalse(arvore.validar())
        arvore.root.esquerda.cor = VERMELHO
        arvore.root.esquerda.veiculo.renavam = "9"
        self.assertFalse(arvore.validar())

    def test_detalhado(self) -> None:
        # Confere as mensagens e a exibição das chaves com suas cores.
        arvore = ArvoreRubroNegra(detalhado=True)
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            for chave in ("3", "1", "2"):
                arvore.inserir(veiculo(chave))
            arvore.remover("1")
        for trecho in ("Rotação à esquerda", "Rotação à direita", "Recoloração",
                       "Removido RENAVAM 1", "2 (PRETO)"):
            self.assertIn(trecho, saida.getvalue())
        self.assertTrue(arvore.validar())


if __name__ == "__main__":
    unittest.main()
