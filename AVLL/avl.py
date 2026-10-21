"""Árvore binária de busca AVL indexada pelo RENAVAM do veículo."""

from __future__ import annotations

from veiculos import Veiculo


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
            if self.detalhado:
                self._log("Árvore após a inserção e o rebalanceamento:")
                self.exibir()
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
            if self.detalhado:
                self._log("Árvore após a remoção e o rebalanceamento:")
                self.exibir()
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

    @staticmethod
    def _maximo(no: NoAVL) -> NoAVL:
        while no.direita is not None:
            no = no.direita
        return no

    def minimo(self) -> Veiculo | None:
        return self._minimo(self.raiz).veiculo if self.raiz is not None else None

    def maximo(self) -> Veiculo | None:
        return self._maximo(self.raiz).veiculo if self.raiz is not None else None

    def pre_ordem(self) -> list[Veiculo]:
        resultado: list[Veiculo] = []

        def percorrer(no: NoAVL | None) -> None:
            if no is not None:
                resultado.append(no.veiculo)
                percorrer(no.esquerda)
                percorrer(no.direita)

        percorrer(self.raiz)
        return resultado

    def em_ordem(self) -> list[Veiculo]:
        resultado: list[Veiculo] = []

        def percorrer(no: NoAVL | None) -> None:
            if no is not None:
                percorrer(no.esquerda)
                resultado.append(no.veiculo)
                percorrer(no.direita)

        percorrer(self.raiz)
        return resultado

    def pos_ordem(self) -> list[Veiculo]:
        resultado: list[Veiculo] = []

        def percorrer(no: NoAVL | None) -> None:
            if no is not None:
                percorrer(no.esquerda)
                percorrer(no.direita)
                resultado.append(no.veiculo)

        percorrer(self.raiz)
        return resultado

    def obter_altura(self) -> int:
        return self._obter_altura(self.raiz)

    def obter_quantidade_nos(self) -> int:
        return self.quantidade_nos

    def exibir(self) -> None:
        """Imprime a estrutura da árvore com alturas e fatores de balanceamento."""
        if self.raiz is None:
            print("Árvore vazia.")
            return

        def linha(no: NoAVL, rotulo: str) -> str:
            fator = self._obter_fator_balanceamento(no)
            return f"{rotulo}{no.veiculo.renavam} (altura={no.altura}, FB={fator})"

        print(linha(self.raiz, "Raiz: "))

        def percorrer(no: NoAVL, prefixo: str) -> None:
            filhos = [("E: ", no.esquerda), ("D: ", no.direita)]
            presentes = [(rotulo, filho) for rotulo, filho in filhos if filho is not None]
            for indice, (rotulo, filho) in enumerate(presentes):
                ultimo = indice == len(presentes) - 1
                print(prefixo + ("└── " if ultimo else "├── ") + linha(filho, rotulo))
                percorrer(filho, prefixo + ("    " if ultimo else "│   "))

        percorrer(self.raiz, "")

    def validar(self) -> bool:
        """Confere ordenação, alturas, balanceamento, unicidade e quantidade."""
        visitados: set[int] = set()

        def verificar(
            no: NoAVL | None, limite_inferior: str | None, limite_superior: str | None
        ) -> tuple[bool, int, int]:
            if no is None:
                return True, 0, 0
            if id(no) in visitados:
                return False, 0, 0
            visitados.add(id(no))

            chave = no.veiculo.renavam
            try:
                if chave != Veiculo.normalizar_renavam(chave):
                    return False, 0, 0
            except (TypeError, ValueError):
                return False, 0, 0
            if (limite_inferior is not None and chave <= limite_inferior) or (
                limite_superior is not None and chave >= limite_superior
            ):
                return False, 0, 0

            esquerda_valida, altura_esquerda, quantidade_esquerda = verificar(
                no.esquerda, limite_inferior, chave
            )
            direita_valida, altura_direita, quantidade_direita = verificar(
                no.direita, chave, limite_superior
            )
            altura = 1 + max(altura_esquerda, altura_direita)
            valido = (
                esquerda_valida
                and direita_valida
                and abs(altura_esquerda - altura_direita) <= 1
                and no.altura == altura
            )
            return valido, altura, 1 + quantidade_esquerda + quantidade_direita

        valida, _, quantidade = verificar(self.raiz, None, None)
        return valida and quantidade == self.quantidade_nos
