"""Integração das árvores que armazenam a mesma coleção de veículos."""

from copy import copy

from avl import ArvoreAVL
from rubro_negra import ArvoreRubroNegra
from veiculos import Veiculo


class GerenciadorVeiculos:
    """Atualiza as duas árvores e consulta a estrutura selecionada."""

    def __init__(self) -> None:
        self.avl = ArvoreAVL()
        self.rubro_negra = ArvoreRubroNegra()
        self.estrutura_selecionada = "AVL"
        self.detalhado = False

    @property
    def arvore_atual(self) -> ArvoreAVL | ArvoreRubroNegra:
        if self.estrutura_selecionada == "AVL":
            return self.avl
        return self.rubro_negra

    def selecionar_estrutura(self, estrutura: str) -> None:
        if estrutura not in ("AVL", "Rubro-Negra"):
            raise ValueError("Selecione AVL ou Rubro-Negra.")
        self.estrutura_selecionada = estrutura
        self._atualizar_modo_detalhado()

    def cadastrar_veiculo(self, veiculo: Veiculo) -> bool:
        # Cópias impedem que alterações no objeto recebido mudem as chaves armazenadas.
        inserido_avl = self.avl.inserir(copy(veiculo))
        inserido_rubro_negra = self.rubro_negra.inserir(copy(veiculo))
        if inserido_avl != inserido_rubro_negra:
            raise RuntimeError("As árvores divergiram durante o cadastro do veículo.")
        return inserido_avl

    def buscar_veiculo(self, renavam: str) -> Veiculo | None:
        veiculo = self.arvore_atual.buscar(renavam)
        return copy(veiculo) if veiculo is not None else None

    def remover_veiculo(self, renavam: str) -> bool:
        removido_avl = self.avl.remover(renavam)
        removido_rubro_negra = self.rubro_negra.remover(renavam)
        if removido_avl != removido_rubro_negra:
            raise RuntimeError("As árvores divergiram durante a remoção do veículo.")
        return removido_avl

    def listar_veiculos(self, ordem: str = "em_ordem") -> list[Veiculo]:
        arvore = self.arvore_atual
        caminhamentos = {
            "em_ordem": arvore.em_ordem,
            "pre_ordem": arvore.pre_ordem,
            "pos_ordem": arvore.pos_ordem,
        }
        if ordem not in caminhamentos:
            raise ValueError("Caminhamento inválido.")
        return [copy(veiculo) for veiculo in caminhamentos[ordem]()]

    def obter_extremos(self) -> tuple[Veiculo | None, Veiculo | None]:
        menor = self.arvore_atual.minimo()
        maior = self.arvore_atual.maximo()
        return (
            copy(menor) if menor is not None else None,
            copy(maior) if maior is not None else None,
        )

    def obter_estatisticas(self) -> dict[str, str | int]:
        arvore = self.arvore_atual
        estatisticas = {
            "estrutura": self.estrutura_selecionada,
            "altura": arvore.obter_altura(),
            "quantidade_nos": arvore.obter_quantidade_nos(),
            "rotacoes_insercao": arvore.rotacoes_insercao,
            "rotacoes_remocao": arvore.rotacoes_remocao,
            "comparacoes": arvore.comparacoes,
        }
        if isinstance(arvore, ArvoreRubroNegra):
            estatisticas["recoloracoes_insercao"] = arvore.recoloracoes_insercao
            estatisticas["recoloracoes_remocao"] = arvore.recoloracoes_remocao
        return estatisticas

    def validar_arvores(self) -> dict[str, bool]:
        return {"AVL": self.avl.validar(), "Rubro-Negra": self.rubro_negra.validar()}

    def exibir_arvore(self) -> None:
        self.arvore_atual.exibir()

    def alternar_modo_detalhado(self) -> bool:
        self.detalhado = not self.detalhado
        self._atualizar_modo_detalhado()
        return self.detalhado

    def _atualizar_modo_detalhado(self) -> None:
        # As duas árvores são atualizadas, mas só a selecionada exibe as correções.
        self.avl.detalhado = self.detalhado and self.estrutura_selecionada == "AVL"
        self.rubro_negra.detalhado = (
            self.detalhado and self.estrutura_selecionada == "Rubro-Negra"
        )
