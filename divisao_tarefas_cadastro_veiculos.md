# Divisão de Tarefas — Trabalho Prático I de AED II

## Mini-mundo escolhido: Cadastro de Veículos

Este documento define a divisão de responsabilidades entre três integrantes da equipe, além de padronizar os nomes das classes, métodos, atributos e requisitos de implementação.

O trabalho consiste na implementação e comparação de duas árvores binárias de busca balanceadas:

- Árvore AVL;
- Árvore Rubro-Negra.

As duas estruturas devem armazenar a mesma coleção de veículos e utilizar o **RENAVAM normalizado** como chave única de ordenação.

---

# 1. Entidade principal

## Classe `Veiculo`

Todos os registros armazenados nas árvores serão objetos da classe `Veiculo`.

### Atributos obrigatórios

```python
class Veiculo:
    def __init__(
        self,
        renavam: str,
        placa: str,
        modelo: str,
        ano: int,
        proprietario: str
    ):
        self.renavam = renavam
        self.placa = placa
        self.modelo = modelo
        self.ano = ano
        self.proprietario = proprietario
```

### Regra da chave

O atributo:

```python
veiculo.renavam
```

será sempre utilizado como chave de ordenação nas duas árvores.

O RENAVAM deverá:

- ser armazenado como `str`;
- conter somente números;
- preservar zeros à esquerda;
- ser único;
- ser normalizado antes da inserção, busca ou remoção.

Exemplo:

```text
001.234.567-89
```

deve ser convertido para:

```text
00123456789
```

Método sugerido:

```python
@staticmethod
def normalizar_renavam(renavam: str) -> str:
    return ''.join(filter(str.isdigit, renavam))
```

---

# 2. Organização do projeto

Estrutura de arquivos padronizada:

```text
projeto/
│
├── veiculos.py
├── avl.py
├── rubro_negra.py
├── experimentos.py
├── main.py
├── README.md
│
└── resultados/
    └── resultados.csv
```

---

# 3. Divisão das tarefas

## Pessoa 1 — Modelo de dados e Árvore AVL

### Arquivos

```text
veiculos.py
avl.py
```

### Responsabilidades

A Pessoa 1 deverá implementar:

- classe `Veiculo`;
- normalização do RENAVAM;
- classe `NoAVL`;
- classe `ArvoreAVL`;
- inserção;
- busca;
- remoção;
- mínimo;
- máximo;
- caminhamentos;
- cálculo de altura;
- quantidade de nós;
- exibição da árvore;
- validação da AVL;
- rotações;
- contagem das rotações;
- modo detalhado das operações da AVL.

### Classes

```python
class Veiculo:
    ...
```

```python
class NoAVL:
    ...
```

```python
class ArvoreAVL:
    ...
```

### Estrutura sugerida do nó

```python
class NoAVL:
    def __init__(self, veiculo: Veiculo):
        self.veiculo = veiculo
        self.esquerda = None
        self.direita = None
        self.altura = 1
```

### Métodos públicos obrigatórios

```python
inserir(veiculo)
buscar(renavam)
remover(renavam)

minimo()
maximo()

pre_ordem()
em_ordem()
pos_ordem()

obter_altura()
obter_quantidade_nos()

exibir()
validar()
```

### Métodos privados sugeridos

```python
_obter_altura(no)
_obter_fator_balanceamento(no)

_rotacao_esquerda(no)
_rotacao_direita(no)

_rebalancear(no)

_inserir(no, veiculo)
_remover(no, renavam)
_buscar(no, renavam)

_minimo(no)
_maximo(no)
```

### Estatísticas

A classe deverá manter, no mínimo:

```python
self.quantidade_nos
self.rotacoes_insercao
self.rotacoes_remocao
self.comparacoes
```

### Requisitos específicos da AVL

A implementação deverá:

- manter altura ou fator de balanceamento;
- implementar rotação simples à esquerda;
- implementar rotação simples à direita;
- implementar rotação dupla LR;
- implementar rotação dupla RL;
- rebalancear após inserções;
- rebalancear após remoções;
- contabilizar rotações;
- validar a propriedade de árvore binária de busca;
- validar que todos os nós respeitam:

```text
|FB| <= 1
```

---

# 4. Pessoa 2 — Árvore Rubro-Negra

### Arquivo

```text
rubro_negra.py
```

### Responsabilidades

A Pessoa 2 deverá implementar:

- classe `NoRubroNegro`;
- classe `ArvoreRubroNegra`;
- tratamento de nós NIL;
- inserção;
- busca;
- remoção;
- mínimo;
- máximo;
- caminhamentos;
- cálculo de altura;
- quantidade de nós;
- exibição;
- rotações;
- recolorações;
- correções após inserção;
- correções após remoção;
- contagem de rotações;
- contagem de recolorações;
- validação da Rubro-Negra;
- modo detalhado das operações.

### Classes

```python
class NoRubroNegro:
    ...
```

```python
class ArvoreRubroNegra:
    ...
```

### Estrutura sugerida do nó

```python
class NoRubroNegro:
    def __init__(self, veiculo=None, cor="PRETO"):
        self.veiculo = veiculo
        self.cor = cor
        self.esquerda = None
        self.direita = None
        self.pai = None
```

### Métodos públicos obrigatórios

A Rubro-Negra deverá possuir exatamente a mesma interface pública da AVL:

```python
inserir(veiculo)
buscar(renavam)
remover(renavam)

minimo()
maximo()

pre_ordem()
em_ordem()
pos_ordem()

obter_altura()
obter_quantidade_nos()

exibir()
validar()
```

### Métodos privados sugeridos

```python
_rotacao_esquerda(no)
_rotacao_direita(no)

_corrigir_insercao(no)
_corrigir_remocao(no)

_transplantar(u, v)

_buscar(no, renavam)
_minimo(no)
_maximo(no)

_calcular_altura(no)
```

### Estatísticas

```python
self.quantidade_nos

self.rotacoes_insercao
self.rotacoes_remocao

self.recoloracoes_insercao
self.recoloracoes_remocao

self.comparacoes
```

### Requisitos específicos da Rubro-Negra

A implementação deverá garantir:

- raiz preta;
- nenhum nó vermelho possui filho vermelho;
- todos os caminhos até NIL possuem a mesma altura negra;
- propriedade de árvore binária de busca;
- recolorações após inserções quando necessário;
- rotações após inserções quando necessário;
- correções após remoções;
- contagem de rotações;
- contagem de recolorações.

---

# 5. Pessoa 3 — Aplicação, integração e experimentos

### Arquivos

```text
main.py
experimentos.py
README.md
resultados/resultados.csv
```

### Responsabilidades

A Pessoa 3 deverá implementar:

- menu principal;
- integração das duas árvores;
- cadastro de veículos;
- busca;
- remoção;
- listagem;
- seleção entre AVL e Rubro-Negra;
- execução dos experimentos;
- geração dos mesmos dados para as duas árvores;
- coleta das métricas;
- medição de tempo;
- contagem de comparações/nós visitados;
- salvamento dos resultados;
- README;
- testes de integração.

### Classe sugerida para integração

```python
class GerenciadorVeiculos:
    def __init__(self):
        self.avl = ArvoreAVL()
        self.rubro_negra = ArvoreRubroNegra()
```

### Métodos sugeridos

```python
cadastrar_veiculo(veiculo)

buscar_veiculo(renavam)

remover_veiculo(renavam)

listar_veiculos()

exibir_estatisticas()
```

### Classe dos experimentos

```python
class ExperimentosArvores:
    ...
```

### Métodos sugeridos

```python
executar_insercao_crescente()

executar_insercao_aleatoria()

executar_buscas()

executar_remocoes()

salvar_resultados_csv()
```

---

# 6. Experimentos obrigatórios

As duas árvores deverão receber exatamente os mesmos dados.

## Experimento A — Inserção crescente

Inserir RENAVAMs distintos em ordem crescente.

Registrar:

- altura final;
- tempo total de inserção;
- rotações;
- recolorações, quando aplicável.

---

## Experimento B — Inserção aleatória

Inserir os mesmos dados em ordem aleatória.

A semente aleatória deverá ser registrada para permitir reprodução do experimento.

Registrar:

- altura final;
- tempo total de inserção;
- rotações;
- recolorações.

---

## Experimento C — Busca

Realizar buscas por:

- chaves existentes;
- chaves inexistentes.

Registrar:

- tempo total;
- quantidade de comparações;
- quantidade média de nós visitados.

---

## Experimento D — Remoção

Remover subconjuntos dos elementos armazenados.

Sugestão:

```text
10%
30%
50%
```

Registrar:

- altura antes da remoção;
- altura depois da remoção;
- tempo total;
- rotações;
- recolorações da Rubro-Negra.

---

# 7. Métricas padronizadas

Os experimentos deverão produzir, no mínimo:

```text
altura_final
rotacoes_insercao
rotacoes_remocao
recoloracoes
media_nos_visitados
tempo_insercao
tempo_busca
tempo_remocao
```

Exemplo de CSV:

```csv
experimento,estrutura,n,altura_final,rotacoes_insercao,rotacoes_remocao,recoloracoes,media_nos_visitados,tempo_insercao,tempo_busca,tempo_remocao
```

---

# 8. Contrato obrigatório das árvores

As duas estruturas deverão ter a mesma interface pública.

## `ArvoreAVL`

```python
class ArvoreAVL:

    def inserir(self, veiculo: Veiculo) -> bool:
        ...

    def buscar(self, renavam: str) -> Veiculo | None:
        ...

    def remover(self, renavam: str) -> bool:
        ...

    def minimo(self) -> Veiculo | None:
        ...

    def maximo(self) -> Veiculo | None:
        ...

    def pre_ordem(self) -> list[Veiculo]:
        ...

    def em_ordem(self) -> list[Veiculo]:
        ...

    def pos_ordem(self) -> list[Veiculo]:
        ...

    def obter_altura(self) -> int:
        ...

    def obter_quantidade_nos(self) -> int:
        ...

    def exibir(self) -> None:
        ...

    def validar(self) -> bool:
        ...
```

## `ArvoreRubroNegra`

```python
class ArvoreRubroNegra:

    def inserir(self, veiculo: Veiculo) -> bool:
        ...

    def buscar(self, renavam: str) -> Veiculo | None:
        ...

    def remover(self, renavam: str) -> bool:
        ...

    def minimo(self) -> Veiculo | None:
        ...

    def maximo(self) -> Veiculo | None:
        ...

    def pre_ordem(self) -> list[Veiculo]:
        ...

    def em_ordem(self) -> list[Veiculo]:
        ...

    def pos_ordem(self) -> list[Veiculo]:
        ...

    def obter_altura(self) -> int:
        ...

    def obter_quantidade_nos(self) -> int:
        ...

    def exibir(self) -> None:
        ...

    def validar(self) -> bool:
        ...
```

---

# 9. Padronização de nomes

## Classes

Utilizar `PascalCase`.

Correto:

```python
Veiculo
NoAVL
ArvoreAVL
NoRubroNegro
ArvoreRubroNegra
GerenciadorVeiculos
ExperimentosArvores
```

Evitar misturar:

```text
AVLTree
RedBlackTree
RBTree
Carro
Automovel
Vehicle
NodeAVL
```

---

## Métodos e atributos

Utilizar `snake_case`.

Exemplos:

```python
obter_altura()
obter_quantidade_nos()
rotacoes_insercao
rotacoes_remocao
recoloracoes_insercao
```

---

## Métodos privados

Todo método auxiliar deverá iniciar com `_`.

Exemplo:

```python
_rotacao_esquerda()
_rotacao_direita()
_corrigir_insercao()
_corrigir_remocao()
```

---

## Constantes

Utilizar letras maiúsculas.

Exemplo:

```python
VERMELHO = "VERMELHO"
PRETO = "PRETO"
```

---

# 10. Política para RENAVAM duplicado

Não será permitido inserir dois veículos com o mesmo RENAVAM.

O método:

```python
inserir(veiculo)
```

deverá retornar:

```python
True
```

quando o veículo for inserido com sucesso.

E:

```python
False
```

quando já existir um veículo com o mesmo RENAVAM.

Não deverá ocorrer substituição silenciosa do registro existente.

---

# 11. Política para busca inexistente

```python
buscar(renavam)
```

deverá retornar:

```python
None
```

quando o RENAVAM não existir.

---

# 12. Política para remoção inexistente

```python
remover(renavam)
```

deverá retornar:

```python
False
```

quando a chave não existir.

Quando a remoção for realizada:

```python
True
```

---

# 13. Caminhamentos

Os três caminhamentos deverão retornar listas de objetos `Veiculo`.

```python
pre_ordem() -> list[Veiculo]

em_ordem() -> list[Veiculo]

pos_ordem() -> list[Veiculo]
```

A listagem em ordem deverá apresentar os veículos ordenados pelo RENAVAM.

---

# 14. Modo detalhado

As duas árvores deverão possuir uma forma de ativar/desativar informações detalhadas.

Sugestão:

```python
ArvoreAVL(detalhado=False)

ArvoreRubroNegra(detalhado=False)
```

Quando:

```python
detalhado=True
```

o programa deverá mostrar informações como:

- chave inserida;
- chave removida;
- nó onde ocorreu desequilíbrio;
- tipo de rotação;
- recolorações;
- árvore depois da correção.

---

# 15. Divisão resumida

| Pessoa | Responsabilidade | Arquivos |
|---|---|---|
| Pessoa 1 | Modelo `Veiculo` + AVL completa | `veiculos.py`, `avl.py` |
| Pessoa 2 | Rubro-Negra completa | `rubro_negra.py` |
| Pessoa 3 | Integração, menu, experimentos, métricas, CSV e README | `main.py`, `experimentos.py`, `README.md` |

---

# 16. Integração entre os integrantes

Antes de juntar os códigos, conferir:

- [ ] `Veiculo` possui exatamente os mesmos atributos usados por todos.
- [ ] RENAVAM é sempre `str`.
- [ ] RENAVAM é normalizado.
- [ ] `ArvoreAVL` e `ArvoreRubroNegra` possuem a mesma interface pública.
- [ ] `inserir()` recebe um objeto `Veiculo`.
- [ ] `buscar()` recebe RENAVAM.
- [ ] `remover()` recebe RENAVAM.
- [ ] `buscar()` retorna `Veiculo` ou `None`.
- [ ] `remover()` retorna `bool`.
- [ ] `inserir()` retorna `bool`.
- [ ] caminhamentos retornam listas.
- [ ] rotações são contabilizadas.
- [ ] recolorações da Rubro-Negra são contabilizadas.
- [ ] comparações/nós visitados são contabilizados.
- [ ] ambas as árvores possuem `validar()`.
- [ ] ambas as árvores possuem `exibir()`.
- [ ] os mesmos dados são utilizados nos experimentos.

---

# 17. Estrutura conceitual

```text
                     Cadastro de Veículos
                            │
                      ┌─────┴─────┐
                      │  Veiculo  │
                      └─────┬─────┘
                            │
                RENAVAM = chave de ordenação
                            │
              ┌─────────────┴─────────────┐
              │                           │
          ArvoreAVL               ArvoreRubroNegra
              │                           │
            NoAVL                    NoRubroNegro
              │                           │
              └─────────────┬─────────────┘
                            │
                   ExperimentosArvores
                            │
                            ▼
                      resultados.csv
```

---

# 18. Observação para a defesa

Embora o desenvolvimento esteja dividido entre três pessoas, todos os integrantes devem saber explicar:

- inserção na AVL;
- remoção na AVL;
- rotações LL, LR, RR e RL;
- inserção na Rubro-Negra;
- remoção na Rubro-Negra;
- recolorações;
- rotações da Rubro-Negra;
- busca;
- mínimo e máximo;
- caminhamentos;
- cálculo de altura;
- validação das árvores;
- coleta das métricas;
- resultados dos experimentos.

A divisão define quem implementa cada parte, mas o código final pertence a toda a equipe.
