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

O menu textual e a integração estão implementados em `main.py`, `interface.py`
e `gerenciador.py`. Há testes da AVL em `testes/test_avl.py` e testes do
gerenciador e da interface em `testes/test_integracao.py`. Os arquivos de testes
específicos da Rubro-Negra e dos experimentos continuam reservados.

A opção de experimentos automáticos já aparece no menu, mas informa que a
implementação ainda está pendente. `experimentos.executar_experimentos()` é o
ponto reservado para conectar essa etapa à interface.

`resultados/resultados.csv`, os gráficos e `docs/relatorio.pdf` serão criados
quando os experimentos e o relatório forem desenvolvidos. O arquivo `.gitkeep`
permite versionar o diretório de gráficos enquanto ele estiver vazio.

## Requisitos e execução

Use Python 3.10 ou superior. O código atual utiliza apenas a biblioteca padrão,
sem dependências externas para instalar.

Execute os comandos na raiz do projeto. Para iniciar o menu:

```bash
python3 main.py
```

A seleção inicial é AVL. A opção `1` alterna diretamente entre AVL e Rubro-Negra.
Cadastros e remoções atualizam as duas árvores com os
mesmos registros; a seleção determina qual árvore será consultada ou exibida.
A validação verifica as duas estruturas. Os dados são mantidos em memória
somente durante a execução; não há salvamento dos cadastros entre sessões.

O menu permite cadastrar, buscar e remover por RENAVAM, listar em ordem,
consultar altura e quantidade de nós, exibir rotações e recolorações, e validar
as árvores. Também oferece visualização da estrutura, mínimo e máximo,
pré-ordem, pós-ordem e modo detalhado da árvore selecionada. A árvore vazia tem
altura zero; uma folha tem altura um.

As estatísticas de comparações são acumuladas desde a criação da árvore e
incluem inserções, buscas e remoções; não representam uma média de busca.

Use a opção `0` para sair.

Para descobrir e executar os testes:

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
