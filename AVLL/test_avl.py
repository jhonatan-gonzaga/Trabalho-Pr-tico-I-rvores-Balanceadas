"""Testes da interface e das invariantes da árvore AVL."""

import contextlib
import io
import random
import unittest

from AVLL import ArvoreAVL
from veiculos import Veiculo


def veiculo(chave: str) -> Veiculo:
    return Veiculo(chave, "ABC-1234", "Modelo", 2024, "Proprietário")


class TesteAVL(unittest.TestCase):
    def test_normalizacao_e_chaves_duplicadas(self) -> None:
        arvore = ArvoreAVL()
        primeiro = veiculo("001.234.567-89")
        self.assertEqual(primeiro.renavam, "00123456789")
        self.assertTrue(arvore.inserir(primeiro))
        self.assertFalse(arvore.inserir(veiculo("00123456789")))
        self.assertIs(arvore.buscar("001.234.567-89"), primeiro)
        self.assertIsNone(arvore.buscar("999"))
        self.assertEqual(arvore.obter_quantidade_nos(), 1)
        self.assertTrue(arvore.validar())

        with self.assertRaises(ValueError):
            veiculo("---")
        with self.assertRaises(TypeError):
            Veiculo(123, "", "", 2024, "")

    def test_quatro_casos_de_rotacao_na_insercao(self) -> None:
        for chaves in (("3", "2", "1"), ("1", "2", "3"), ("3", "1", "2"), ("1", "3", "2")):
            with self.subTest(chaves=chaves):
                arvore = ArvoreAVL()
                for chave in chaves:
                    self.assertTrue(arvore.inserir(veiculo(chave)))
                    self.assertTrue(arvore.validar())
                self.assertEqual(arvore.raiz.veiculo.renavam, "2")
                rotacoes_esperadas = 2 if chaves in (("3", "1", "2"), ("1", "3", "2")) else 1
                self.assertEqual(arvore.rotacoes_insercao, rotacoes_esperadas)
                self.assertEqual([item.renavam for item in arvore.em_ordem()], ["1", "2", "3"])
                self.assertEqual([item.renavam for item in arvore.pre_ordem()], ["2", "1", "3"])
                self.assertEqual([item.renavam for item in arvore.pos_ordem()], ["1", "3", "2"])
                self.assertEqual(arvore.obter_altura(), 2)

    def test_quatro_casos_de_rotacao_na_remocao(self) -> None:
        casos = (
            (("3", "2", "4", "1"), "4", "2", 1),  # LL
            (("2", "1", "3", "4"), "1", "3", 1),  # RR
            (("5", "2", "7", "3"), "7", "3", 2),  # LR
            (("2", "1", "5", "4"), "1", "4", 2),  # RL
        )
        for chaves, removida, nova_raiz, rotacoes in casos:
            with self.subTest(chaves=chaves):
                arvore = ArvoreAVL()
                for chave in chaves:
                    arvore.inserir(veiculo(chave))
                self.assertTrue(arvore.remover(removida))
                self.assertTrue(arvore.validar())
                self.assertEqual(arvore.raiz.veiculo.renavam, nova_raiz)
                self.assertEqual(arvore.rotacoes_remocao, rotacoes)

    def test_remocao_de_folha_um_filho_e_dois_filhos(self) -> None:
        arvore = ArvoreAVL()
        for chave in ("50", "30", "70", "20", "40", "60", "80", "35"):
            arvore.inserir(veiculo(chave))

        self.assertTrue(arvore.remover("20"))  # folha
        self.assertTrue(arvore.validar())
        self.assertTrue(arvore.remover("40"))  # um filho
        self.assertTrue(arvore.validar())
        self.assertTrue(arvore.remover("50"))  # dois filhos e raiz
        self.assertTrue(arvore.validar())
        self.assertFalse(arvore.remover("999"))
        self.assertEqual(arvore.obter_quantidade_nos(), 5)
        self.assertEqual(
            [item.renavam for item in arvore.em_ordem()], ["30", "35", "60", "70", "80"]
        )
        self.assertEqual(arvore.minimo().renavam, "30")
        self.assertEqual(arvore.maximo().renavam, "80")
        self.assertEqual(len(arvore.pre_ordem()), 5)
        self.assertEqual(len(arvore.pos_ordem()), 5)

    def test_remocoes_em_ordens_variadas_preservam_invariantes(self) -> None:
        for semente in range(5):
            with self.subTest(semente=semente):
                chaves = [f"{numero:04d}" for numero in range(100)]
                gerador = random.Random(semente)
                gerador.shuffle(chaves)
                arvore = ArvoreAVL()
                restantes: set[str] = set()
                for chave in chaves:
                    self.assertTrue(arvore.inserir(veiculo(chave)))
                    restantes.add(chave)
                    self.assertTrue(arvore.validar())

                gerador.shuffle(chaves)
                for chave in chaves:
                    self.assertTrue(arvore.remover(chave))
                    restantes.remove(chave)
                    self.assertTrue(arvore.validar())
                    self.assertEqual(arvore.obter_quantidade_nos(), len(restantes))
                    self.assertEqual(
                        [item.renavam for item in arvore.em_ordem()], sorted(restantes)
                    )
                self.assertEqual(arvore.obter_altura(), 0)
                self.assertIsNone(arvore.minimo())
                self.assertIsNone(arvore.maximo())
                self.assertGreater(arvore.comparacoes, 0)

    def test_validacao_detecta_altura_e_ordem_incorretas(self) -> None:
        arvore = ArvoreAVL()
        for chave in ("2", "1", "3"):
            arvore.inserir(veiculo(chave))
        arvore.raiz.altura = 9
        self.assertFalse(arvore.validar())
        arvore.raiz.altura = 2
        arvore.raiz.esquerda.veiculo.renavam = "4"
        self.assertFalse(arvore.validar())

    def test_modo_detalhado_exibe_correcao(self) -> None:
        arvore = ArvoreAVL(detalhado=True)
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            for chave in ("3", "1", "2"):
                arvore.inserir(veiculo(chave))
            arvore.remover("1")
        self.assertIn("Desequilíbrio LR", saida.getvalue())
        self.assertIn("Rotação à esquerda", saida.getvalue())
        self.assertIn("Árvore após a remoção", saida.getvalue())


if __name__ == "__main__":
    unittest.main()
