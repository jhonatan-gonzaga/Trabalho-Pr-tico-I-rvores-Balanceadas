# Trabalho Prático I — Árvores Balanceadas

Implementação e comparação de árvores AVL e Rubro-Negra para o minimundo
**Cadastro de Veículos**, usando o RENAVAM normalizado como chave única.

## Estrutura do projeto

```text
projeto/
├── main.py
├── interface.py
├── gerenciador.py
├── veiculos.py
├── avl.py
├── rubro_negra.py
├── experimentos.py
├── testes/
│   ├── __init__.py
│   ├── test_avl.py
│   ├── test_rubro_negra.py
│   ├── test_integracao.py
│   └── test_experimentos.py
├── resultados/
│   └── graficos/
│       └── .gitkeep
├── docs/
│   ├── TrabalhoPráticoAEDII.pdf
│   └── divisao_tarefas_cadastro_veiculos.md
├── README.md
└── .gitignore
```

| Arquivo ou diretório | Responsabilidade |
|---|---|
| `main.py` | Iniciar a aplicação. |
| `interface.py` | Menu, leitura de entradas e apresentação das respostas. |
| `gerenciador.py` | Coordenar as operações nas duas árvores e selecionar a estrutura consultada. |
| `veiculos.py` | Entidade `Veiculo` e normalização do RENAVAM. |
| `avl.py` e `rubro_negra.py` | Implementações das árvores e seus contadores. |
| `experimentos.py` | Gerar sequências reproduzíveis, executar cenários, medir e salvar resultados. |
| `testes/` | Testes das árvores, da integração e dos experimentos. |
| `resultados/` | Resultados brutos e gráficos produzidos pelos experimentos. |
| `docs/` | Enunciado, divisão de tarefas e relatório da entrega. |

Os arquivos `main.py`, `interface.py`, `gerenciador.py` e `experimentos.py`
estão reservados para implementação. O menu e os experimentos ainda não estão
disponíveis. Em `testes/`, apenas `test_avl.py` possui testes implementados;
os demais arquivos de teste estão reservados para as próximas etapas.

`resultados/resultados.csv`, os gráficos e `docs/relatorio.pdf` serão criados
quando os experimentos e o relatório forem desenvolvidos. O arquivo `.gitkeep`
permite versionar o diretório de gráficos enquanto ele estiver vazio.

## Requisitos e execução dos testes

Use Python 3.10 ou superior. O código atual utiliza apenas a biblioteca padrão,
sem dependências externas para instalar.

Execute os comandos na raiz do projeto. Para descobrir e executar os testes:

```bash
python3 -m unittest discover -s testes -v
```

Para executar somente os testes da AVL:

```bash
python3 -m unittest testes.test_avl -v
```

## Política de chaves

O RENAVAM é armazenado como string, preservando zeros à esquerda e removendo
caracteres que não sejam dígitos ASCII. Uma inserção duplicada retorna `False`
e preserva o registro existente. Busca inexistente retorna `None`, e remoção
inexistente retorna `False`.

## Documentação

- [Enunciado do trabalho](docs/TrabalhoPráticoAEDII.pdf)
- [Divisão de tarefas e contrato das árvores](docs/divisao_tarefas_cadastro_veiculos.md)
