"""Árvore binária de busca AVL indexada pelo RENAVAM do veículo."""

from __future__ import annotations

if __package__:
    from .modelos import Veiculo
else:
    from modelos import Veiculo


class NoAVL:
    """Nó com a altura da subárvore enraizada nele."""

    def __init__(self, veiculo: Veiculo) -> None:
        self.veiculo = veiculo
        self.esquerda: NoAVL | None = None
        self.direita: NoAVL | None = None
        self.altura = 1


class ArvoreAVL:
    """Índice AVL sem substituição de RENAVAMs duplicados.

    Cada rotação simples conta como uma rotação; uma rotação dupla conta como duas.
    `comparacoes` conta uma comparação de chave por nó visitado em inserir,
    buscar e remover.
    """

    def __init__(self, detalhado: bool = False) -> None:
        self.raiz: NoAVL | None = None
        self.quantidade_nos = 0
        self.rotacoes_insercao = 0
        self.rotacoes_remocao = 0
        self.comparacoes = 0
        self.detalhado = detalhado

    def _log(self, mensagem: str) -> None:
        if self.detalhado:
            print(mensagem)

    @staticmethod
    def _obter_altura(no: NoAVL | None) -> int:
        return no.altura if no is not None else 0

    def _obter_fator_balanceamento(self, no: NoAVL) -> int:
        return self._obter_altura(no.esquerda) - self._obter_altura(no.direita)

    def _atualizar_altura(self, no: NoAVL) -> None:
        no.altura = 1 + max(self._obter_altura(no.esquerda), self._obter_altura(no.direita))

    def _contar_rotacao(self, operacao: str) -> None:
        if operacao == "insercao":
            self.rotacoes_insercao += 1
        else:
            self.rotacoes_remocao += 1

    def _rotacao_esquerda(self, no: NoAVL, operacao: str) -> NoAVL:
        nova_raiz = no.direita
        assert nova_raiz is not None
        no.direita = nova_raiz.esquerda
        nova_raiz.esquerda = no
        self._atualizar_altura(no)
        self._atualizar_altura(nova_raiz)
        self._contar_rotacao(operacao)
        self._log(f"Rotação à esquerda em {no.veiculo.renavam}.")
        return nova_raiz

    def _rotacao_direita(self, no: NoAVL, operacao: str) -> NoAVL:
        nova_raiz = no.esquerda
        assert nova_raiz is not None
        no.esquerda = nova_raiz.direita
        nova_raiz.direita = no
        self._atualizar_altura(no)
        self._atualizar_altura(nova_raiz)
        self._contar_rotacao(operacao)
        self._log(f"Rotação à direita em {no.veiculo.renavam}.")
        return nova_raiz

    def _rebalancear(self, no: NoAVL, operacao: str) -> NoAVL:
        self._atualizar_altura(no)
        fator = self._obter_fator_balanceamento(no)

        if fator > 1:
            assert no.esquerda is not None
            if self._obter_fator_balanceamento(no.esquerda) < 0:
                self._log(f"Desequilíbrio LR em {no.veiculo.renavam} (FB={fator}).")
                no.esquerda = self._rotacao_esquerda(no.esquerda, operacao)
            else:
                self._log(f"Desequilíbrio LL em {no.veiculo.renavam} (FB={fator}).")
            return self._rotacao_direita(no, operacao)

        if fator < -1:
            assert no.direita is not None
            if self._obter_fator_balanceamento(no.direita) > 0:
                self._log(f"Desequilíbrio RL em {no.veiculo.renavam} (FB={fator}).")
                no.direita = self._rotacao_direita(no.direita, operacao)
            else:
                self._log(f"Desequilíbrio RR em {no.veiculo.renavam} (FB={fator}).")
            return self._rotacao_esquerda(no, operacao)

        return no

    def inserir(self, veiculo: Veiculo) -> bool:
        """Insere um veículo e retorna False se a chave já existir."""
        veiculo.renavam = Veiculo.normalizar_renavam(veiculo.renavam)
        self.raiz, inserido = self._inserir(self.raiz, veiculo)
        if inserido:
            self.quantidade_nos += 1
            self._log(f"Inserido RENAVAM {veiculo.renavam}.")
        else:
            self._log(f"RENAVAM duplicado: {veiculo.renavam}.")
        return inserido

    def _inserir(self, no: NoAVL | None, veiculo: Veiculo) -> tuple[NoAVL, bool]:
        if no is None:
            return NoAVL(veiculo), True

        self.comparacoes += 1
        chave = veiculo.renavam
        if chave < no.veiculo.renavam:
            no.esquerda, inserido = self._inserir(no.esquerda, veiculo)
        elif chave > no.veiculo.renavam:
            no.direita, inserido = self._inserir(no.direita, veiculo)
        else:
            return no, False

        return (self._rebalancear(no, "insercao") if inserido else no), inserido

    def buscar(self, renavam: str) -> Veiculo | None:
        """Busca pelo RENAVAM, aceitando a chave com pontuação."""
        chave = Veiculo.normalizar_renavam(renavam)
        no = self._buscar(self.raiz, chave)
        return no.veiculo if no is not None else None

    def _buscar(self, no: NoAVL | None, renavam: str) -> NoAVL | None:
        while no is not None:
            self.comparacoes += 1
            if renavam == no.veiculo.renavam:
                return no
            no = no.esquerda if renavam < no.veiculo.renavam else no.direita
        return None

    def remover(self, renavam: str) -> bool:
        """Remove a chave e retorna False quando ela não existe."""
        chave = Veiculo.normalizar_renavam(renavam)
        self.raiz, removido = self._remover(self.raiz, chave)
        if removido:
            self.quantidade_nos -= 1
            self._log(f"Removido RENAVAM {chave}.")
        else:
            self._log(f"RENAVAM não encontrado: {chave}.")
        return removido

    def _remover(self, no: NoAVL | None, renavam: str) -> tuple[NoAVL | None, bool]:
        if no is None:
            return None, False

        self.comparacoes += 1
        if renavam < no.veiculo.renavam:
            no.esquerda, removido = self._remover(no.esquerda, renavam)
        elif renavam > no.veiculo.renavam:
            no.direita, removido = self._remover(no.direita, renavam)
        else:
            if no.esquerda is None:
                return no.direita, True
            if no.direita is None:
                return no.esquerda, True

            sucessor = self._minimo(no.direita)
            no.veiculo = sucessor.veiculo
            no.direita = self._remover_minimo(no.direita)
            removido = True

        return (self._rebalancear(no, "remocao") if removido else no), removido

    def _remover_minimo(self, no: NoAVL) -> NoAVL | None:
        if no.esquerda is None:
            return no.direita
        no.esquerda = self._remover_minimo(no.esquerda)
        return self._rebalancear(no, "remocao")

    @staticmethod
    def _minimo(no: NoAVL) -> NoAVL:
        while no.esquerda is not None:
            no = no.esquerda
        return no
