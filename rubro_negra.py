from veiculo import Veiculo


# Cores permitidas para os nós da árvore rubro-negra.
VERMELHO = "VERMELHO"
PRETO = "PRETO"


class NoRubroNegro:
    def __init__(self, veiculo=None, cor=VERMELHO):
        # Cada nó armazena um veículo, sua cor e as ligações da árvore.
        self.veiculo = veiculo
        self.cor = cor
        self.esquerda = None
        self.direita = None
        self.pai = None

class ArvoreRubroNegra:
    def __init__(self, detalhado=False):
        # NIL é um único nó sentinela preto que representa todas as folhas vazias.
        # Apontar seus filhos para ele mesmo permite consultar suas cores com segurança.
        self.NIL = NoRubroNegro(veiculo=None, cor=PRETO)
        self.NIL.esquerda = self.NIL
        self.NIL.direita = self.NIL
        self.root = self.NIL

        # O modo detalhado mostra inserções, remoções, rotações e recolorações.
        self.detalhado = detalhado

        # Estatísticas acumuladas durante a utilização da árvore.
        self.quantidade_nos = 0
        self.rotacoes_insercao = 0
        self.rotacoes_remocao = 0
        self.recoloracoes_insercao = 0
        self.recoloracoes_remocao = 0
        self.comparacoes = 0

        # Identifica a operação responsável por cada rotação ou recoloração.
        self._operacao_atual = None

    def _log(self, mensagem):
        # Evita espalhar testes de "detalhado" por todas as mensagens do algoritmo.
        if self.detalhado:
            print(mensagem)

    def _definir_cor(self, no, cor):
        # O sentinela NIL deve permanecer preto em todas as circunstâncias.
        if no == self.NIL:
            no.cor = PRETO
            return

        # Uma atribuição para a mesma cor não conta como recoloração.
        if no.cor == cor:
            return

        no.cor = cor
        if self._operacao_atual == "insercao":
            self.recoloracoes_insercao += 1
        elif self._operacao_atual == "remocao":
            self.recoloracoes_remocao += 1
        self._log(f"Recoloração do RENAVAM {no.veiculo.renavam} para {cor}")

    def _registrar_rotacao(self, tipo, no):
        # Separa as rotações provocadas por inserções e por remoções.
        if self._operacao_atual == "insercao":
            self.rotacoes_insercao += 1
        elif self._operacao_atual == "remocao":
            self.rotacoes_remocao += 1
        self._log(f"Rotação {tipo} no RENAVAM {no.veiculo.renavam}")

    def _rotacao_esquerda(self, no):
        # O filho direito sobe e o nó recebido desce para a esquerda.
        self._registrar_rotacao("à esquerda", no)
        y = no.direita
        no.direita = y.esquerda

        if y.esquerda != self.NIL:
            y.esquerda.pai = no

        y.pai = no.pai

        # Reconecta a nova raiz da subárvore ao antigo pai.
        if no.pai is None:
            self.root = y
        elif no == no.pai.esquerda:
            no.pai.esquerda = y
        else:
            no.pai.direita = y

        y.esquerda = no
        no.pai = y

    def _rotacao_direita(self, no):
        # O filho esquerdo sobe e o nó recebido desce para a direita.
        self._registrar_rotacao("à direita", no)
        x = no.esquerda
        no.esquerda = x.direita

        if x.direita != self.NIL:
            x.direita.pai = no

        x.pai = no.pai

        # Reconecta a nova raiz da subárvore ao antigo pai.
        if no.pai is None:
            self.root = x
        elif no == no.pai.direita:
            no.pai.direita = x
        else:
            no.pai.esquerda = x

        x.direita = no
        no.pai = x

    def inserir(self, veiculo: Veiculo) -> bool:
        # A entidade Veiculo centraliza a normalização e a validação do RENAVAM.
        renavam = Veiculo.normalizar_renavam(veiculo.renavam)

        # Mantém normalizado mesmo um RENAVAM alterado depois da criação do veículo.
        veiculo.renavam = renavam
        pai = None
        atual = self.root

        # Localiza iterativamente a posição do novo nó como em uma ABB comum.
        while atual != self.NIL:
            pai = atual
            self.comparacoes += 1

            # RENAVAM é uma chave única; registros duplicados não são substituídos.
            if renavam == atual.veiculo.renavam:
                self._log(f"RENAVAM duplicado: {renavam}")
                return False
            if renavam < atual.veiculo.renavam:
                atual = atual.esquerda
            else:
                atual = atual.direita

        novo_no = NoRubroNegro(veiculo=veiculo, cor=VERMELHO)
        novo_no.esquerda = self.NIL
        novo_no.direita = self.NIL
        novo_no.pai = pai

        if pai is None:
            self.root = novo_no
        elif renavam < pai.veiculo.renavam:
            pai.esquerda = novo_no
        else:
            pai.direita = novo_no

        self.quantidade_nos += 1
        self._log(f"Inserido RENAVAM {renavam}")

        # Corrige possíveis conflitos entre o novo nó vermelho e seu pai.
        self._operacao_atual = "insercao"
        try:
            self._corrigir_insercao(novo_no)
        finally:
            self._operacao_atual = None

        if self.detalhado:
            self.exibir()
        return True

    def _corrigir_insercao(self, no):
        # Caso 1: o pai do nó inserido é vermelho.
        while no.pai is not None and no.pai.cor == VERMELHO:
            if no.pai == no.pai.pai.esquerda:
                tio = no.pai.pai.direita

                # Caso 2: pai e tio são vermelhos.
                if tio.cor == VERMELHO:
                    self._definir_cor(no.pai, PRETO)
                    self._definir_cor(tio, PRETO)
                    self._definir_cor(no.pai.pai, VERMELHO)
                    no = no.pai.pai
                else:
                    # Pai vermelho, tio preto e o nó é filho direito.
                    if no == no.pai.direita:
                        no = no.pai
                        self._rotacao_esquerda(no)

                    # Caso 3: recoloração e rotação à direita.
                    self._definir_cor(no.pai, PRETO)
                    self._definir_cor(no.pai.pai, VERMELHO)
                    self._rotacao_direita(no.pai.pai)
            else:
                tio = no.pai.pai.esquerda

                # Caso 2: pai e tio são vermelhos.
                if tio.cor == VERMELHO:
                    self._definir_cor(no.pai, PRETO)
                    self._definir_cor(tio, PRETO)
                    self._definir_cor(no.pai.pai, VERMELHO)
                    no = no.pai.pai
                else:
                    # Pai vermelho, tio preto e o nó é filho esquerdo.
                    if no == no.pai.esquerda:
                        no = no.pai
                        self._rotacao_direita(no)

                    # Caso 3: recoloração e rotação à esquerda.
                    self._definir_cor(no.pai, PRETO)
                    self._definir_cor(no.pai.pai, VERMELHO)
                    self._rotacao_esquerda(no.pai.pai)

        # A raiz é sempre preta depois da correção da inserção.
        self._definir_cor(self.root, PRETO)

    def buscar(self, renavam: str) -> Veiculo | None:
        # A interface pública devolve o veículo, sem expor o nó interno.
        renavam = Veiculo.normalizar_renavam(renavam)
        no = self._buscar(self.root, renavam)
        return None if no == self.NIL else no.veiculo

    def _buscar(self, no, renavam):
        # A busca interna devolve o nó encontrado ou o sentinela NIL.
        atual = no
        while atual != self.NIL:
            # Uma comparação representa um nó visitado durante a busca.
            self.comparacoes += 1
            if renavam == atual.veiculo.renavam:
                return atual
            if renavam < atual.veiculo.renavam:
                atual = atual.esquerda
            else:
                atual = atual.direita
        return self.NIL

    def remover(self, renavam: str) -> bool:
        # Primeiro encontra o nó correspondente à chave normalizada.
        renavam = Veiculo.normalizar_renavam(renavam)

        z = self._buscar(self.root, renavam)
        if z == self.NIL:
            return False

        self._operacao_atual = "remocao"
        try:
            y = z
            cor_original_y = y.cor

            # Sem filho esquerdo: o filho direito ocupa a posição do nó removido.
            if z.esquerda == self.NIL:
                x = z.direita
                self._transplantar(z, z.direita)

            # Sem filho direito: o filho esquerdo ocupa a posição do nó removido.
            elif z.direita == self.NIL:
                x = z.esquerda
                self._transplantar(z, z.esquerda)
            else:
                # Com dois filhos, utiliza o sucessor: o menor nó da subárvore direita.
                y = self._minimo(z.direita)
                cor_original_y = y.cor
                x = y.direita
                if y.pai == z:
                    x.pai = y
                else:
                    self._transplantar(y, y.direita)
                    y.direita = z.direita
                    y.direita.pai = y

                self._transplantar(z, y)
                y.esquerda = z.esquerda
                y.esquerda.pai = y
                self._definir_cor(y, z.cor)

            self.quantidade_nos -= 1

            # Remover um nó preto pode reduzir a altura negra de um caminho.
            if cor_original_y == PRETO:
                self._corrigir_remocao(x)
        finally:
            # O pai de NIL só é temporariamente necessário durante a correção.
            self._operacao_atual = None
            self.NIL.pai = None
            self.NIL.cor = PRETO

        self._log(f"Removido RENAVAM {renavam}")
        if self.detalhado:
            self.exibir()
        return True

    def _transplantar(self, u, v):
        # Substitui a subárvore enraizada em "u" pela subárvore enraizada em "v".
        if u.pai is None:
            self.root = v
        elif u == u.pai.esquerda:
            u.pai.esquerda = v
        else:
            u.pai.direita = v
        v.pai = u.pai

    def _corrigir_remocao(self, x):
        # Propaga ou elimina o "preto extra" criado pela remoção de um nó preto.
        while x != self.root and x.cor == PRETO:
            if x == x.pai.esquerda:
                irmao = x.pai.direita

                # Caso 1: o irmão é vermelho.
                if irmao.cor == VERMELHO:
                    self._definir_cor(irmao, PRETO)
                    self._definir_cor(x.pai, VERMELHO)
                    self._rotacao_esquerda(x.pai)
                    irmao = x.pai.direita

                # Caso 2: o irmão e seus dois filhos são pretos.
                if irmao.esquerda.cor == PRETO and irmao.direita.cor == PRETO:
                    self._definir_cor(irmao, VERMELHO)
                    x = x.pai
                else:
                    # Caso 3: o irmão é preto, seu filho esquerdo é vermelho
                    # e seu filho direito é preto.
                    if irmao.direita.cor == PRETO:
                        self._definir_cor(irmao.esquerda, PRETO)
                        self._definir_cor(irmao, VERMELHO)
                        self._rotacao_direita(irmao)
                        irmao = x.pai.direita

                    # Caso 4: o filho direito do irmão é vermelho.
                    self._definir_cor(irmao, x.pai.cor)
                    self._definir_cor(x.pai, PRETO)
                    self._definir_cor(irmao.direita, PRETO)
                    self._rotacao_esquerda(x.pai)
                    x = self.root
            else:
                irmao = x.pai.esquerda

                # Caso 1: o irmão é vermelho.
                if irmao.cor == VERMELHO:
                    self._definir_cor(irmao, PRETO)
                    self._definir_cor(x.pai, VERMELHO)
                    self._rotacao_direita(x.pai)
                    irmao = x.pai.esquerda

                # Caso 2: o irmão e seus dois filhos são pretos.
                if irmao.direita.cor == PRETO and irmao.esquerda.cor == PRETO:
                    self._definir_cor(irmao, VERMELHO)
                    x = x.pai
                else:
                    # Caso 3: o irmão é preto, seu filho direito é vermelho
                    # e seu filho esquerdo é preto.
                    if irmao.esquerda.cor == PRETO:
                        self._definir_cor(irmao.direita, PRETO)
                        self._definir_cor(irmao, VERMELHO)
                        self._rotacao_esquerda(irmao)
                        irmao = x.pai.esquerda

                    # Caso 4: o filho esquerdo do irmão é vermelho.
                    self._definir_cor(irmao, x.pai.cor)
                    self._definir_cor(x.pai, PRETO)
                    self._definir_cor(irmao.esquerda, PRETO)
                    self._rotacao_direita(x.pai)
                    x = self.root

        self._definir_cor(x, PRETO)

    def minimo(self) -> Veiculo | None:
        # Em uma ABB, a menor chave é o nó mais à esquerda.
        if self.root == self.NIL:
            return None
        return self._minimo(self.root).veiculo

    def _minimo(self, no):
        while no.esquerda != self.NIL:
            no = no.esquerda
        return no

    def maximo(self) -> Veiculo | None:
        # Em uma ABB, a maior chave é o nó mais à direita.
        if self.root == self.NIL:
            return None
        return self._maximo(self.root).veiculo

    def _maximo(self, no):
        while no.direita != self.NIL:
            no = no.direita
        return no

    def pre_ordem(self) -> list[Veiculo]:
        # Percurso: raiz, subárvore esquerda e subárvore direita.
        lista = []
        self._pre_ordem(self.root, lista)
        return lista

    def _pre_ordem(self, no, lista):
        if no == self.NIL:
            return
        lista.append(no.veiculo)
        self._pre_ordem(no.esquerda, lista)
        self._pre_ordem(no.direita, lista)

    def em_ordem(self) -> list[Veiculo]:
        # Percurso: esquerda, raiz e direita; produz RENAVAMs ordenados.
        lista = []
        self._em_ordem(self.root, lista)
        return lista

    def _em_ordem(self, no, lista):
        if no == self.NIL:
            return
        self._em_ordem(no.esquerda, lista)
        lista.append(no.veiculo)
        self._em_ordem(no.direita, lista)

    def pos_ordem(self) -> list[Veiculo]:
        # Percurso: subárvores esquerda e direita, seguidas pela raiz.
        lista = []
        self._pos_ordem(self.root, lista)
        return lista

    def _pos_ordem(self, no, lista):
        if no == self.NIL:
            return
        self._pos_ordem(no.esquerda, lista)
        self._pos_ordem(no.direita, lista)
        lista.append(no.veiculo)

    def obter_altura(self) -> int:
        # A árvore vazia tem altura zero e uma folha tem altura um.
        return self._calcular_altura(self.root)

    def _calcular_altura(self, no):
        if no == self.NIL:
            return 0
        return 1 + max(
            self._calcular_altura(no.esquerda),
            self._calcular_altura(no.direita),
        )

    def obter_quantidade_nos(self) -> int:
        # O contador é atualizado apenas em inserções e remoções bem-sucedidas.
        return self.quantidade_nos

    def exibir(self) -> None:
        # Mostra uma representação textual com o RENAVAM e a cor de cada nó.
        if self.root == self.NIL:
            print("Árvore vazia")
            return
        self._exibir(self.root, prefixo="", ultimo=True)

    def _exibir(self, no, prefixo, ultimo):
        if no == self.NIL:
            return

        conector = "└── " if ultimo else "├── "
        print(f"{prefixo}{conector}{no.veiculo.renavam} ({no.cor})")
        novo_prefixo = prefixo + ("    " if ultimo else "│   ")

        filhos = [filho for filho in (no.esquerda, no.direita) if filho != self.NIL]
        for indice, filho in enumerate(filhos):
            self._exibir(filho, novo_prefixo, indice == len(filhos) - 1)

    def validar(self) -> bool:
        # Verifica primeiro as propriedades globais do sentinela e da raiz.
        if self.NIL.cor != PRETO:
            return False
        if self.root == self.NIL:
            return self.quantidade_nos == 0
        if self.root.cor != PRETO or self.root.pai is not None:
            return False

        # A validação recursiva também conta os nós realmente alcançáveis.
        valida, _, quantidade = self._validar_no(self.root, None, None)
        return valida and quantidade == self.quantidade_nos

    def _validar_no(self, no, limite_inferior, limite_superior):
        # Cada NIL encerra um caminho e contribui com uma unidade de altura negra.
        if no == self.NIL:
            return True, 1, 0
        if no is None or no.veiculo is None:
            return False, 0, 0

        chave = no.veiculo.renavam

        # Os limites garantem a propriedade de árvore binária de busca.
        if limite_inferior is not None and chave <= limite_inferior:
            return False, 0, 0
        if limite_superior is not None and chave >= limite_superior:
            return False, 0, 0
        if no.cor not in (VERMELHO, PRETO):
            return False, 0, 0
        if no.esquerda is None or no.direita is None:
            return False, 0, 0
        if no.esquerda != self.NIL and no.esquerda.pai != no:
            return False, 0, 0
        if no.direita != self.NIL and no.direita.pai != no:
            return False, 0, 0

        # Um nó vermelho não pode possuir filhos vermelhos.
        if no.cor == VERMELHO:
            if no.esquerda.cor == VERMELHO or no.direita.cor == VERMELHO:
                return False, 0, 0

        esquerda_valida, altura_esquerda, quantidade_esquerda = self._validar_no(
            no.esquerda, limite_inferior, chave
        )
        direita_valida, altura_direita, quantidade_direita = self._validar_no(
            no.direita, chave, limite_superior
        )

        if not esquerda_valida or not direita_valida:
            return False, 0, 0

        # Todos os caminhos descendentes devem possuir a mesma altura negra.
        if altura_esquerda != altura_direita:
            return False, 0, 0

        altura_negra = altura_esquerda + (1 if no.cor == PRETO else 0)
        quantidade = 1 + quantidade_esquerda + quantidade_direita
        return True, altura_negra, quantidade
