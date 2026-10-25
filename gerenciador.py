# Integração das árvores que armazenam a mesma coleção de veículos.

from copy import copy

from avl import ArvoreAVL
from rubro_negra import ArvoreRubroNegra
from veiculos import Veiculo

#Essa classe é quem realmente gerencia as duas árvores, e envia as saídas para a interface em interfaec.py
class GerenciadorVeiculos:

    def __init__(self) -> None:
        # Cria as duas árvores, seleciona a AVL e desativa o modo detalhado (padrão)

        self.avl = ArvoreAVL() #objeto AVL
        self.rubro_negra = ArvoreRubroNegra() #objeto rubro-negra

        self.estrutura_selecionada = "AVL"
        self.detalhado = False

    @property
    def arvore_atual(self) -> ArvoreAVL | ArvoreRubroNegra:
        # Retorna a árvore que está selecionada para consultas e exibição

        if self.estrutura_selecionada == "AVL":
            return self.avl
        return self.rubro_negra

    def selecionar_estrutura(self, estrutura: str) -> None:
        # Seleciona uma das árvores e aplica a ela o estado do modo detalhado

        if estrutura not in ("AVL", "Rubro-Negra"):
            raise ValueError("Selecione AVL ou Rubro-Negra.")

        self.estrutura_selecionada = estrutura
        self._atualizar_modo_detalhado()

    def cadastrar_veiculo(self, veiculo: Veiculo) -> bool:
        # Insere cópias do veículo nas duas árvores e retorna se o cadastro relamente ocorreu
        # Cópias impedem que alterações no objeto recebido mudem as chaves armazenadas.

        inserido_avl = self.avl.inserir(copy(veiculo))
        inserido_rubro_negra = self.rubro_negra.inserir(copy(veiculo))

        if inserido_avl != inserido_rubro_negra:
            raise RuntimeError("As árvores divergiram durante o cadastro do veículo.")

        return inserido_avl

    def buscar_veiculo(self, renavam: str) -> Veiculo | None:
        # Busca na árvore selecionada e devolve uma cópia do veículo ou None.

        veiculo = self.arvore_atual.buscar(renavam)

        return copy(veiculo) if veiculo is not None else None

    def remover_veiculo(self, renavam: str) -> bool:
        # Remove o RENAVAM das duas árvores e retorna se a remoção ocorreu.

        removido_avl = self.avl.remover(renavam)
        removido_rubro_negra = self.rubro_negra.remover(renavam)

        if removido_avl != removido_rubro_negra:
            raise RuntimeError("As árvores divergiram durante a remoção do veículo.")

        return removido_avl

    def listar_veiculos(self, ordem: str = "em_ordem") -> list[Veiculo]:
        # Retorna cópias dos veículos no caminhamento escolhido da árvore selecionada

        arvore = self.arvore_atual

        if ordem == "em_ordem":
            veiculos = arvore.em_ordem()

        elif ordem == "pre_ordem":
            veiculos = arvore.pre_ordem()

        elif ordem == "pos_ordem":
            veiculos = arvore.pos_ordem()

        else:
            raise ValueError("Caminhamento inválido.")

        return [copy(veiculo) for veiculo in veiculos]

    def obter_extremos(self) -> tuple[Veiculo | None, Veiculo | None]:
        # Retorna cópias dos veículos de menor e maior chave, ou None para árvore vazia.

        arvore = self.arvore_atual
        menor = arvore.minimo()
        maior = arvore.maximo()

        return (
            copy(menor) if menor is not None else None,
            copy(maior) if maior is not None else None,
        )

    def obter_estatisticas(self) -> dict[str, str | int]:
        # Reúne altura, quantidade de nós e contadores da árvore selecionada.

        arvore = self.arvore_atual

        estatisticas = {
            "estrutura": self.estrutura_selecionada,
            "altura": arvore.obter_altura(),
            "quantidade_nos": arvore.obter_quantidade_nos(),
            "rotacoes_insercao": arvore.rotacoes_insercao,
            "rotacoes_remocao": arvore.rotacoes_remocao,
            "comparacoes": arvore.comparacoes,
        }

        #se for rubro negra, adiciona a quantidade de recoloracoes, não pode na lista por que é único dela
        if isinstance(arvore, ArvoreRubroNegra):
            estatisticas["recoloracoes_insercao"] = arvore.recoloracoes_insercao
            estatisticas["recoloracoes_remocao"] = arvore.recoloracoes_remocao

        return estatisticas

    def validar_arvores(self) -> dict[str, bool]:
        # Verifica as propriedades de cada árvore e retorna os dois resultados.
        return {"AVL": self.avl.validar(), "Rubro-Negra": self.rubro_negra.validar()}

    def exibir_arvore(self) -> None:
        # Solicita à árvore selecionada que mostre sua estrutura no terminal.
        self.arvore_atual.exibir()

    def alternar_modo_detalhado(self) -> bool:
        # Inverte o modo detalhado, aplica à árvore selecionada e retorna o novo estado

        self.detalhado = not self.detalhado
        self._atualizar_modo_detalhado()
        return self.detalhado

    def _atualizar_modo_detalhado(self) -> None:
        # Habilita a exibição das correções somente na árvore selecionada.
        self.avl.detalhado = self.detalhado and self.estrutura_selecionada == "AVL"
        
        self.rubro_negra.detalhado = (
            self.detalhado and self.estrutura_selecionada == "Rubro-Negra"
        )
