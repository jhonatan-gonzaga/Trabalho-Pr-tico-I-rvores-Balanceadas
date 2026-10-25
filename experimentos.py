# Compara AVL e Rubro-Negra com os mesmos dados nos experimentos A, B, C e D.
# Os tempos são medidos em segundos, sem incluir geração, validação ou gravação.

import csv
from copy import copy
from pathlib import Path
from random import Random
from time import perf_counter

from avl import ArvoreAVL
from rubro_negra import ArvoreRubroNegra
from veiculos import Veiculo


CAMPOS_RESULTADOS = (
    "experimento", "estrutura", "n", "semente", "repeticao", "ordem_insercao",
    "tipo_busca", "percentual_remocao", "altura_antes", "altura_final",
    "rotacoes_insercao", "rotacoes_remocao", "recoloracoes", "quantidade_buscas",
    "comparacoes_busca", "media_nos_visitados", "tempo_insercao", "tempo_busca",
    "tempo_remocao",
)

CAMPOS_BUSCAS = (
    "estrutura", "n", "semente", "repeticao", "ordem_insercao",
    "tipo_busca", "renavam", "nos_visitados",
)


class ExperimentosArvores:
    # Executa os cenários e guarda as medições que ainda precisam ser salvas.

    def __init__(
        self, tamanhos: tuple[int, ...] = (100, 1000, 10000), semente: int = 42,
        repeticoes: int = 3, percentuais_remocao: tuple[int, ...] = (10, 30, 50),
        limite_buscas: int = 1000, diretorio_resultados: str | Path | None = None,
    ) -> None:
        # Define os tamanhos, sementes, repetições e a pasta dos arquivos CSV.
        if not tamanhos or any(n <= 0 for n in tamanhos):
            raise ValueError("Os tamanhos devem ser maiores que zero.")
        if repeticoes <= 0 or limite_buscas <= 0:
            raise ValueError("Repetições e limite de buscas devem ser maiores que zero.")
        if not percentuais_remocao or any(p <= 0 or p > 100 for p in percentuais_remocao):
            raise ValueError("Os percentuais de remoção devem estar entre 1 e 100.")
        self.tamanhos = tuple(tamanhos)
        self.semente = semente
        self.repeticoes = repeticoes
        self.percentuais_remocao = tuple(percentuais_remocao)
        self.limite_buscas = limite_buscas
        if diretorio_resultados is None:
            diretorio_resultados = Path(__file__).resolve().parent / "resultados"
        self.diretorio_resultados = Path(diretorio_resultados)
        self.resultados = []
        self.buscas_detalhadas = []

    def gerar_dados(self, n: int, ordem: str = "crescente", semente: int | None = None) -> list[Veiculo]:
        # Gera veículos com chaves únicas e embaralha quando a ordem é aleatória.
        if n <= 0:
            raise ValueError("A quantidade de veículos deve ser maior que zero.")
        dados = []
        for numero, chave in enumerate(self._chaves(n), 1):
            dados.append(Veiculo(chave, f"TST{numero % 10000:04d}", f"Modelo {numero}",
                                 2020 + numero % 6, f"Proprietário {numero}"))
        if ordem == "aleatoria":
            if semente is None:
                semente = self.semente
            Random(semente).shuffle(dados)
        elif ordem != "crescente":
            raise ValueError("A ordem deve ser crescente ou aleatoria.")
        return dados

    def _chaves(self, n: int) -> list[str]:
        # Usa chaves pares com 11 dígitos; as ímpares ficam para buscas ausentes.
        return [f"{numero * 2:011d}" for numero in range(1, n + 1)]

    def insercao_crescente(self) -> list[dict]:
        # Executa A com os veículos em ordem crescente.
        return self._insercoes("A", "crescente")

    def insercao_aleatoria(self) -> list[dict]:
        # Executa B com os veículos embaralhados por uma semente registrada.
        return self._insercoes("B", "aleatoria")

    def _insercoes(self, experimento: str, ordem: str) -> list[dict]:
        # Mede as inserções para cada tamanho e repetição nas duas árvores.
        resultados = []
        for n in self.tamanhos:
            for repeticao in range(1, self.repeticoes + 1):
                dados = self.gerar_dados(n, ordem, self.semente + repeticao - 1)
                for nome, classe in self._arvores(repeticao):
                    arvore, tempo = self._montar(classe, dados)
                    resultado = self._resultado(experimento, nome, n, repeticao, ordem, arvore)
                    resultado["altura_antes"] = 0
                    resultado["tempo_insercao"] = tempo
                    resultados.append(resultado)
        self.resultados.extend(resultados)
        return resultados

    def buscas(self) -> list[dict]:
        # Executa C com buscas presentes e ausentes nas duas ordens de construção.
        resultados = []
        for n in self.tamanhos:
            chaves = self._chaves(n)
            quantidade = min(n, self.limite_buscas)
            lacunas = [f"{numero * 2 - 1:011d}" for numero in range(1, n + 1)]
            for repeticao in range(1, self.repeticoes + 1):
                semente = self.semente + repeticao - 1
                gerador = Random(semente + 1)
                grupos = (
                    ("existente", gerador.sample(chaves, quantidade)),
                    ("inexistente", gerador.sample(lacunas, quantidade)),
                )
                for ordem in ("crescente", "aleatoria"):
                    dados = self.gerar_dados(n, ordem, semente)
                    for nome, classe in self._arvores(repeticao):
                        arvore, tempo_insercao = self._montar(classe, dados)
                        for tipo, consultas in grupos:
                            tempo, visitas = self._buscar(arvore, consultas, tipo == "existente")
                            self._validar(arvore, chaves)
                            total = sum(visitas)
                            resultado = self._resultado("C", nome, n, repeticao, ordem, arvore)
                            resultado.update({
                                "tipo_busca": tipo, "quantidade_buscas": quantidade,
                                "comparacoes_busca": total,
                                "media_nos_visitados": total / quantidade,
                                "tempo_insercao": tempo_insercao, "tempo_busca": tempo,
                            })
                            resultados.append(resultado)
                            for chave, visitados in zip(consultas, visitas):
                                self.buscas_detalhadas.append({
                                    "estrutura": nome, "n": n, "semente": semente,
                                    "repeticao": repeticao, "ordem_insercao": ordem,
                                    "tipo_busca": tipo, "renavam": chave, "nos_visitados": visitados,
                                })
        self.resultados.extend(resultados)
        return resultados

    def _buscar(self, arvore, consultas: list[str], esperado: bool) -> tuple:
        # Mede o tempo e depois conta as visitas, sem incluir registros de CSV na medição.
        inicio = perf_counter()
        for chave in consultas:
            arvore.buscar(chave)
        tempo = perf_counter() - inicio
        visitas = []
        for chave in consultas:
            antes = arvore.comparacoes
            encontrado = arvore.buscar(chave) is not None
            if encontrado != esperado:
                raise RuntimeError("Uma busca retornou um resultado incorreto.")
            visitas.append(arvore.comparacoes - antes)
        return tempo, visitas

    def remocoes(self) -> list[dict]:
        # Executa D a partir de uma árvore nova para cada percentual.
        resultados = []
        for n in self.tamanhos:
            chaves = self._chaves(n)
            for repeticao in range(1, self.repeticoes + 1):
                semente = self.semente + repeticao - 1
                ordem_remocao = Random(semente + 2).sample(chaves, n)
                for ordem in ("crescente", "aleatoria"):
                    dados = self.gerar_dados(n, ordem, semente)
                    for percentual in self.percentuais_remocao:
                        removidas = ordem_remocao[:n * percentual // 100]
                        conjunto = set(removidas)
                        restantes = [chave for chave in chaves if chave not in conjunto]
                        for nome, classe in self._arvores(repeticao):
                            arvore, tempo_insercao = self._montar(classe, dados)
                            altura = arvore.obter_altura()
                            inicio = perf_counter()
                            for chave in removidas:
                                arvore.remover(chave)
                            tempo = perf_counter() - inicio
                            self._validar(arvore, restantes)
                            resultado = self._resultado("D", nome, n, repeticao, ordem, arvore)
                            resultado.update({
                                "percentual_remocao": percentual, "altura_antes": altura,
                                "tempo_insercao": tempo_insercao, "tempo_remocao": tempo,
                            })
                            resultados.append(resultado)
        self.resultados.extend(resultados)
        return resultados

    def todos(self) -> list[dict]:
        # Executa os quatro cenários e reúne suas medições.
        resultados = self.insercao_crescente() + self.insercao_aleatoria()
        resultados += self.buscas() + self.remocoes()
        return resultados

    def _arvores(self, repeticao: int) -> list[tuple[str, type]]:
        # Alterna qual estrutura é medida primeiro a cada repetição.
        tipos = [("AVL", ArvoreAVL), ("Rubro-Negra", ArvoreRubroNegra)]
        if repeticao % 2 == 0:
            tipos.reverse()
        return tipos

    def _montar(self, classe: type, dados: list[Veiculo]) -> tuple:
        # Prepara cópias, mede as inserções e confere a árvore fora do cronômetro.
        registros = [copy(veiculo) for veiculo in dados]
        arvore = classe(detalhado=False)
        inicio = perf_counter()
        for veiculo in registros:
            arvore.inserir(veiculo)
        tempo = perf_counter() - inicio
        self._validar(arvore, sorted(v.renavam for v in dados))
        return arvore, tempo

    def _validar(self, arvore, esperadas: list[str]) -> None:
        # Confere propriedades, quantidade e chaves antes de aceitar os resultados.
        chaves = [veiculo.renavam for veiculo in arvore.em_ordem()]
        if not arvore.validar() or arvore.obter_quantidade_nos() != len(esperadas) or chaves != esperadas:
            raise RuntimeError("A árvore não preservou as propriedades ou os dados esperados.")

    def _resultado(self, experimento: str, nome: str, n: int, repeticao: int, ordem: str, arvore) -> dict:
        # Reúne as métricas; recolorações correspondem à operação medida em A/B ou D.
        recoloracoes = 0
        if isinstance(arvore, ArvoreRubroNegra):
            if experimento in ("A", "B"):
                recoloracoes = arvore.recoloracoes_insercao
            elif experimento == "D":
                recoloracoes = arvore.recoloracoes_remocao
        altura = arvore.obter_altura()
        return {
            "experimento": experimento, "estrutura": nome, "n": n,
            "semente": self.semente + repeticao - 1, "repeticao": repeticao,
            "ordem_insercao": ordem, "tipo_busca": "", "percentual_remocao": "",
            "altura_antes": altura, "altura_final": altura,
            "rotacoes_insercao": arvore.rotacoes_insercao, "rotacoes_remocao": arvore.rotacoes_remocao,
            "recoloracoes": recoloracoes, "quantidade_buscas": "", "comparacoes_busca": "",
            "media_nos_visitados": "", "tempo_insercao": "", "tempo_busca": "", "tempo_remocao": "",
        }

    def salvar_csv(self) -> None:
        # Salva somente os registros pendentes e limpa as listas para não duplicá-los.
        self.diretorio_resultados.mkdir(parents=True, exist_ok=True)
        self._gravar("resultados.csv", CAMPOS_RESULTADOS, self.resultados)
        self.resultados.clear()
        self._gravar("buscas.csv", CAMPOS_BUSCAS, self.buscas_detalhadas)
        self.buscas_detalhadas.clear()

    def _gravar(self, nome: str, campos: tuple[str, ...], registros: list[dict]) -> None:
        # Acrescenta linhas sem sobrescrever resultados anteriores ou repetir o cabeçalho.
        if not registros:
            return
        arquivo = self.diretorio_resultados / nome
        novo = not arquivo.exists() or arquivo.stat().st_size == 0
        if not novo:
            with arquivo.open(encoding="utf-8", newline="") as entrada:
                if next(csv.reader(entrada)) != list(campos):
                    raise ValueError(f"O cabeçalho de {arquivo} não corresponde às métricas atuais.")
        with arquivo.open("a", encoding="utf-8", newline="") as saida:
            escritor = csv.DictWriter(saida, fieldnames=campos)
            if novo:
                escritor.writeheader()
            escritor.writerows(registros)
