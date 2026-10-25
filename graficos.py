# Gera gráficos das métricas já salvas em resultados/resultados.csv.

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


INSERCAO = (
    ("altura_final", "Altura final", "Níveis", 1),
    ("rotacoes_insercao", "Rotações na inserção", "Rotações", 1),
    ("recoloracoes", "Recolorações na inserção", "Recolorações", 1),
    ("tempo_insercao", "Tempo total de inserção", "Tempo (ms)", 1000),
)

REMOCAO = (
    ("altura_final", "Altura antes e depois", "Níveis", 1),
    ("rotacoes_remocao", "Rotações na remoção", "Rotações", 1),
    ("recoloracoes", "Recolorações na remoção", "Recolorações", 1),
    ("tempo_remocao", "Tempo total de remoção", "Tempo (ms)", 1000),
)


def ler_csv(arquivo: Path) -> list[dict]:
    # Lê as linhas do CSV de resultados sem alterar os dados originais.
    with arquivo.open(encoding="utf-8", newline="") as entrada:
        return list(csv.DictReader(entrada))


def media(linhas: list[dict], campo: str) -> float:
    # Calcula a média de uma métrica nas linhas do mesmo cenário e tamanho.
    return sum(float(linha[campo]) for linha in linhas) / len(linhas)


def barras(eixo, dados: list[dict], campo: str, titulo: str, unidade: str, fator: float) -> None:
    # Compara as duas estruturas por tamanho, usando apenas as medições presentes no CSV.
    tamanhos = sorted({int(linha["n"]) for linha in dados})
    estruturas = (("AVL", -0.2, "#2563eb"), ("Rubro-Negra", 0.2, "#dc2626"))
    antes = campo == "altura_final" and dados[0]["experimento"] == "D"
    for estrutura, deslocamento, cor in estruturas:
        posicoes = []
        valores = []
        alturas = []
        for indice, n in enumerate(tamanhos):
            linhas = [linha for linha in dados if linha["estrutura"] == estrutura and int(linha["n"]) == n]
            if linhas:
                posicoes.append(indice + deslocamento)
                valores.append(media(linhas, campo) * fator)
                if antes:
                    alturas.append(media(linhas, "altura_antes"))
        if valores:
            legenda = f"{estrutura} depois" if antes else estrutura
            eixo.bar(posicoes, valores, width=0.36, color=cor, label=legenda)
            if antes:
                eixo.plot(posicoes, alturas, "--_", color=cor, label=f"{estrutura} antes")
    eixo.set_title(titulo)
    eixo.set_xlabel("Quantidade de registros (n)")
    eixo.set_ylabel(unidade)
    eixo.set_xticks(range(len(tamanhos)), [f"{n:,}".replace(",", ".") for n in tamanhos])
    eixo.set_ylim(bottom=0)
    eixo.grid(axis="y", alpha=0.25)
    eixo.set_axisbelow(True)
    eixo.legend(fontsize=8)


def figura(paineis: list[tuple], titulo: str, arquivo: Path) -> None:
    # Organiza quatro gráficos em uma imagem PNG com resolução para o relatório.
    imagem, eixos = plt.subplots(2, 2, figsize=(10, 7))
    for eixo, painel in zip(eixos.flat, paineis):
        dados, campo, nome, unidade, fator = painel
        barras(eixo, dados, campo, nome, unidade, fator)
    imagem.suptitle(titulo, fontsize=14)
    imagem.text(0.5, 0.015, "Médias das medições registradas no CSV.", ha="center", fontsize=9)
    imagem.tight_layout(rect=(0, 0.04, 1, 0.94))
    imagem.savefig(arquivo, dpi=300)
    plt.close(imagem)


def gerar_graficos(arquivo: str | Path | None = None, pasta: str | Path | None = None) -> list[Path]:
    # Gera as imagens dos cenários disponíveis no CSV e retorna os caminhos criados.
    if arquivo is None:
        arquivo = Path(__file__).resolve().parent / "resultados" / "resultados.csv"
    arquivo = Path(arquivo)
    if not arquivo.is_file():
        print("CSV não encontrado. Execute os experimentos primeiro.")
        return []
    dados = ler_csv(arquivo)
    if not dados:
        print("O CSV ainda não contém resultados.")
        return []
    if pasta is None:
        pasta = arquivo.parent / "graficos"
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    imagens = []

    for experimento, ordem in (("A", "crescente"), ("B", "aleatoria")):
        linhas = [linha for linha in dados if linha["experimento"] == experimento]
        if linhas:
            destino = pasta / f"{experimento.lower()}_insercao.png"
            paineis = [(linhas, campo, nome, unidade, fator) for campo, nome, unidade, fator in INSERCAO]
            figura(paineis, f"Experimento {experimento} — Inserção {ordem}", destino)
            imagens.append(destino)

    for ordem in ("crescente", "aleatoria"):
        linhas = [linha for linha in dados if linha["experimento"] == "C" and linha["ordem_insercao"] == ordem]
        if linhas:
            paineis = []
            for tipo in ("existente", "inexistente"):
                grupo = [linha for linha in linhas if linha["tipo_busca"] == tipo]
                if grupo:
                    paineis.append((grupo, "media_nos_visitados", f"Chave {tipo}: nós visitados", "Nós por busca", 1))
                    paineis.append((grupo, "tempo_busca", f"Chave {tipo}: tempo total", "Tempo (ms)", 1000))
            destino = pasta / f"c_busca_{ordem}.png"
            figura(paineis, f"Experimento C — Construção {ordem}", destino)
            imagens.append(destino)

        linhas = [linha for linha in dados if linha["experimento"] == "D" and linha["ordem_insercao"] == ordem]
        percentuais = sorted({int(linha["percentual_remocao"]) for linha in linhas})
        for percentual in percentuais:
            grupo = [linha for linha in linhas if int(linha["percentual_remocao"]) == percentual]
            destino = pasta / f"d_remocao_{ordem}_{percentual}.png"
            paineis = [(grupo, campo, nome, unidade, fator) for campo, nome, unidade, fator in REMOCAO]
            figura(paineis, f"Experimento D — Remoção de {percentual}% | Construção {ordem}", destino)
            imagens.append(destino)
    return imagens


def main() -> None:
    # Gera os gráficos do CSV padrão e informa onde foram salvos.
    imagens = gerar_graficos()
    if imagens:
        print(f"{len(imagens)} gráficos salvos em: {imagens[0].parent}")


if __name__ == "__main__":
    main()
