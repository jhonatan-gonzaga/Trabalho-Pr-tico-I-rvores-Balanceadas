import experimentos
from gerenciador import GerenciadorVeiculos
from veiculos import Veiculo

#literalmente a interface do terminal
# Essa classe fica responsável somente por interagir com o usuário lendo suas entradas, e enviando para a classe GerenciadorVeiculos, que é responsável por toda a lógica em si.
#Depois, a classe InterfaceTerminal recebe os resultados do GerenciadorVeiculos e mostra para o usuário. Esse é o pipeline.
class InterfaceTerminal:
    def __init__(self, gerenciador: GerenciadorVeiculos | None = None) -> None:
        # Usa o gerenciador informado ou cria um novo para o menu.
        self.gerenciador = gerenciador if gerenciador is not None else GerenciadorVeiculos()

    def executar(self) -> None:
        #Executa a opção escolhida e repete o menu até o usuário digitar 0
        acoes = {
            "1": self._alternar_estrutura,
            "2": self._cadastrar_veiculo,
            "3": self._buscar_veiculo,
            "4": self._remover_veiculo,
            "5": self._listar_veiculos,
            "6": self._exibir_altura_e_quantidade,
            "7": self._exibir_estatisticas,
            "8": self._validar_arvores,
            "9": self._executar_experimentos,
            "10": self._exibir_arvore,
            "11": self._exibir_extremos,
            "12": self._escolher_caminhamento,
            "13": self._alternar_modo_detalhado,
        }

        print("Cadastro de veículos: AVL e Rubro-Negra")
        print("Cadastros e remoções atualizam as duas árvores.")
        print("A seleção define qual árvore será consultada ou exibida quando a opção relacionada for escolhida")

        #fica em loop até o usuário digitar 0 para sair
        while True:
            self._exibir_menu()

            opcao = input("Escolha uma opção: ")

            if opcao == "0":
                print("Aplicação encerrada.")
                return

            acao = acoes.get(opcao)

            if acao is None:
                print("Opção inválida. Escolha uma das opções do menu.")
                continue

            acao()

    def _exibir_menu(self) -> None:
        # Mostra as opções, a árvore selecionada e o estado do modo detalhado

        gerenciador = self.gerenciador
        modo = "ativado" if gerenciador.detalhado else "desativado"
        print(f"\nEstrutura selecionada: {gerenciador.estrutura_selecionada}")
        print(f"Modo detalhado: {modo}")

        print("1. Alternar entre AVL e Rubro-Negra")
        print("2. Cadastrar veículo")
        print("3. Buscar por RENAVAM")
        print("4. Remover por RENAVAM")
        print("5. Listar veículos em ordem")
        print("6. Exibir altura e quantidade de nós")
        print("7. Exibir estatísticas de rebalanceamento")
        print("8. Validar as propriedades das árvores")
        print("9. Executar experimentos automáticos")
        print("10. Exibir estrutura da árvore")
        print("11. Consultar menor e maior RENAVAM")
        print("12. Listar em pré-ordem ou pós-ordem")
        print("13. Ativar/desativar modo detalhado")

        print("0. Sair")

    def _alternar_estrutura(self) -> None:
        # Troca diretamente a árvore selecionada entre AVL e Rubro-Negra (já que é binário)
        if self.gerenciador.estrutura_selecionada == "AVL":
            estrutura = "Rubro-Negra"

        else:
            estrutura = "AVL"

        self.gerenciador.selecionar_estrutura(estrutura)

        print(f"Estrutura selecionada: {self.gerenciador.estrutura_selecionada}.")

    @staticmethod
    def _ler_texto(campo: str) -> str:
        #essa classe é para não ter que repetir o código em várias entradas de texto
        while True:
            valor = input(f"{campo}: ").strip()
            if valor:
                return valor
            print(f"O campo {campo.lower()} é obrigatório.")

    @staticmethod
    def _ler_renavam() -> str:
        # Lê e normaliza o RENAVAM, repetindo entradas sem dígitos.

        while True:
            valor = input("RENAVAM: ")
            try:
                return Veiculo.normalizar_renavam(valor) #função do veiculo.py de normalizacao do RENAVAM

            except ValueError as erro:
                print(f"RENAVAM inválido: {erro}")

    @staticmethod
    def _ler_ano() -> int:
        # Lê um ano inteiro entre 1 e 9999, repetindo entradas inválidas.
        while True:
            try:
                ano = int(input("Ano: "))

            except ValueError:
                print("Ano inválido. Informe um número inteiro entre 1 e 9999.")
                continue

            if 1 <= ano <= 9999:
                return ano

            print("Ano inválido. Informe um número inteiro entre 1 e 9999.")

    def _cadastrar_veiculo(self) -> None:
        # Lê os dados do veículo e solicita seu cadastro nas duas árvores.

        print("\nCadastro de veículo")

        #os dados do veículo
        renavam = self._ler_renavam()
        placa = self._ler_texto("Placa").upper()
        modelo = self._ler_texto("Modelo")
        ano = self._ler_ano()
        proprietario = self._ler_texto("Proprietário")

        #cria o objeto em si com os dados pegados
        veiculo = Veiculo(renavam, placa, modelo, ano, proprietario)

        if self.gerenciador.cadastrar_veiculo(veiculo):
            print(f"Veículo {renavam} cadastrado nas duas árvores.")

        else:
            print(f"Já existe um veículo com o RENAVAM {renavam}. Cadastro preservado.")

    @staticmethod
    def _exibir_veiculo(veiculo: Veiculo) -> None:
        # Mostra os cinco atributos de um veículo
        print(f"RENAVAM: {veiculo.renavam}")
        print(f"Placa: {veiculo.placa}")
        print(f"Modelo: {veiculo.modelo}")
        print(f"Ano: {veiculo.ano}")
        print(f"Proprietário: {veiculo.proprietario}")

    def _buscar_veiculo(self) -> None:
        # Busca o RENAVAM na árvore selecionada e mostra o veículo encontrado

        print("\nBusca de veículo")

        veiculo = self.gerenciador.buscar_veiculo(self._ler_renavam())

        if veiculo is None:
            print("Nenhum veículo encontrado com esse RENAVAM.")
            return

        print("Veículo encontrado:")

        self._exibir_veiculo(veiculo)

    def _remover_veiculo(self) -> None:
        # Lê o RENAVAM e solicita a remoção do veículo das duas árvores.
        print("\nRemoção de veículo")

        renavam = self._ler_renavam()

        if self.gerenciador.remover_veiculo(renavam):
            print(f"Veículo {renavam} removido das duas árvores.")
        else:
            print("Nenhum veículo encontrado com esse RENAVAM.")

    def _listar_veiculos(self, ordem: str = "em_ordem") -> None:
        # Lista os veículos da árvore selecionada no caminhamento informado. Em ordem por padrão
        veiculos = self.gerenciador.listar_veiculos(ordem)

        #se não tiver veículos
        if not veiculos:
            print("Nenhum veículo cadastrado.")
            return

        nomes = {"em_ordem": "em ordem", "pre_ordem": "em pré-ordem", "pos_ordem": "em pós-ordem"}

        print(f"\nVeículos {nomes[ordem]} - {self.gerenciador.estrutura_selecionada}")

        for veiculo in veiculos:
            print()
            self._exibir_veiculo(veiculo)

        print(f"\nTotal: {len(veiculos)} veículo(s).")

    def _exibir_altura_e_quantidade(self) -> None:
        # Mostra a altura e a quantidade de nós da árvore selecionada

        estatisticas = self.gerenciador.obter_estatisticas()
        print(f"\nEstrutura: {estatisticas['estrutura']}")
        print(f"Altura: {estatisticas['altura']}")
        print(f"Quantidade de nós: {estatisticas['quantidade_nos']}")

    def _exibir_estatisticas(self) -> None:
        # Mostra os contadores acumulados de operações da árvore selecionada.
        estatisticas = self.gerenciador.obter_estatisticas()
        print(f"\nEstatísticas — {estatisticas['estrutura']}")
        print(f"Rotações na inserção: {estatisticas['rotacoes_insercao']}")
        print(f"Rotações na remoção: {estatisticas['rotacoes_remocao']}")
        if "recoloracoes_insercao" in estatisticas:
            print(f"Recolorações na inserção: {estatisticas['recoloracoes_insercao']}")
            print(f"Recolorações na remoção: {estatisticas['recoloracoes_remocao']}")
        print(
            "Comparações acumuladas (inserção, busca e remoção): "
            f"{estatisticas['comparacoes']}"
        )

    def _validar_arvores(self) -> None:
        # Verifica as propriedades das duas árvores e mostra os resultados.
        for estrutura, valida in self.gerenciador.validar_arvores().items():
            resultado = "válida" if valida else "INVÁLIDA"
            print(f"{estrutura}: {resultado}.")

    @staticmethod
    def _executar_experimentos() -> None:
        # Abre o submenu dos experimentos sem alterar os cadastros do menu principal.
        InterfaceExperimentos().executar()

    def _exibir_arvore(self) -> None:
        # Exibe a estrutura dos nós da árvore selecionada.
        print(f"\nEstrutura da árvore — {self.gerenciador.estrutura_selecionada}")
        self.gerenciador.exibir_arvore()

    def _exibir_extremos(self) -> None:
        # Mostra os veículos de menor e maior RENAVAM da árvore selecionada.
        menor, maior = self.gerenciador.obter_extremos()
        if menor is None or maior is None:
            print("Nenhum veículo cadastrado.")
            return
        print("\nVeículo de menor RENAVAM:")
        self._exibir_veiculo(menor)
        print("\nVeículo de maior RENAVAM:")
        self._exibir_veiculo(maior)

    def _escolher_caminhamento(self) -> None:
        # Solicita pré-ordem ou pós-ordem e lista os veículos nesse percurso.
        print("\n1. Pré-ordem\n2. Pós-ordem")
        opcao = input("Selecione o caminhamento: ")
        ordens = {"1": "pre_ordem", "2": "pos_ordem"}
        if opcao not in ordens:
            print("Escolha 1 para pré-ordem ou 2 para pós-ordem.")
            return
        self._listar_veiculos(ordens[opcao])

    def _alternar_modo_detalhado(self) -> None:
        # Ativa ou desativa a exibição das correções da árvore selecionada.
        ativo = self.gerenciador.alternar_modo_detalhado()
        estado = "ativado" if ativo else "desativado"
        print(f"Modo detalhado {estado} para {self.gerenciador.estrutura_selecionada}.")


class InterfaceExperimentos:
    # Mostra as opções de experimentação e apresenta as métricas retornadas pelo executor.

    def __init__(self, executor: experimentos.ExperimentosArvores | None = None) -> None:
        # Usa o executor informado ou cria um com os parâmetros do enunciado.
        if executor is None:
            executor = experimentos.ExperimentosArvores()
        self.executor = executor

    def executar(self) -> None:
        # Executa o experimento escolhido, salva seus resultados e permite outra escolha.
        acoes = {
            "A": self.executor.insercao_crescente,
            "B": self.executor.insercao_aleatoria,
            "C": self.executor.buscas,
            "D": self.executor.remocoes,
            "T": self.executor.todos,
        }
        while True:
            self._exibir_menu()
            opcao = input("Escolha o experimento: ").upper()
            if opcao == "0":
                return
            if opcao == "G":
                self._gerar_graficos()
                continue
            acao = acoes.get(opcao)
            if acao is None:
                print("Opção inválida. Escolha A, B, C, D, T, G ou 0.")
                continue
            print("Executando os experimentos...")
            resultados = acao()
            self.executor.salvar_csv()
            self._exibir_resultados(resultados)
            print(f"Resultados salvos em: {self.executor.diretorio_resultados / 'resultados.csv'}")
            if opcao in ("C", "T"):
                print(f"Visitas por busca salvas em: {self.executor.diretorio_resultados / 'buscas.csv'}")

    def _exibir_menu(self) -> None:
        # Apresenta os quatro cenários e os parâmetros usados nas medições.
        print("\nExperimentos comparativos — AVL e Rubro-Negra")
        print(f"Tamanhos: {self.executor.tamanhos}")
        print(f"Semente inicial: {self.executor.semente}; repetições: {self.executor.repeticoes}")
        print("Cada repetição usa a semente inicial mais seu índice, começando em zero.")
        print(f"Buscas por grupo: até {self.executor.limite_buscas} por tamanho.")
        print(f"Percentuais de remoção: {self.executor.percentuais_remocao}")
        print("A. Inserção em ordem crescente")
        print("B. Inserção em ordem aleatória")
        print("C. Busca por chaves existentes e inexistentes")
        print("D. Remoção de subconjuntos")
        print("T. Executar todos os experimentos")
        print("G. Gerar gráficos do CSV")
        print("0. Voltar ao menu principal")

    def _gerar_graficos(self) -> None:
        # Carrega o gerador ao escolher G e usa o CSV da pasta dos experimentos.
        from graficos import gerar_graficos

        imagens = gerar_graficos(self.executor.diretorio_resultados / "resultados.csv")
        if imagens:
            print(f"Gráficos salvos em: {imagens[0].parent}")

    def _exibir_resultados(self, resultados: list[dict]) -> None:
        # Mostra uma linha por medição; os CSVs preservam todas as métricas e configurações.
        print("\nExp | Árvore | n | rep | ordem | grupo | altura | tempo(s) | rotações | recolorações | média visitas")
        for resultado in resultados:
            experimento = resultado["experimento"]
            grupo = "-"
            media = "-"
            recoloracoes = resultado["recoloracoes"]
            if experimento in ("A", "B"):
                tempo = resultado["tempo_insercao"]
                rotacoes = resultado["rotacoes_insercao"]
            elif experimento == "C":
                grupo = resultado["tipo_busca"]
                tempo = resultado["tempo_busca"]
                media = f"{resultado['media_nos_visitados']:.2f}"
                rotacoes = 0
            else:
                grupo = f"{resultado['percentual_remocao']}%"
                tempo = resultado["tempo_remocao"]
                rotacoes = resultado["rotacoes_remocao"]
            print(
                f"{experimento} | {resultado['estrutura']} | {resultado['n']} | "
                f"{resultado['repeticao']} | {resultado['ordem_insercao']} | {grupo} | "
                f"{resultado['altura_antes']}->{resultado['altura_final']} | "
                f"{tempo:.6f} | {rotacoes} | {recoloracoes} | {media}"
            )
        print("Rotações e recolorações da tabela referem-se à operação medida.")
        print("Os tempos podem variar entre execuções; compare também alturas e contadores.")
