import experimentos
from gerenciador import GerenciadorVeiculos
from veiculos import Veiculo

#literalmente a interface do terminal
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
        # Mostra as opções, a árvore selecionada e o estado do modo detalhado.

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
        print("9. Executar experimentos automáticos (em desenvolvimento)")
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
        # Lê um campo não vazio, removendo espaços nas extremidades.
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
                return Veiculo.normalizar_renavam(valor)
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
        renavam = self._ler_renavam()
        placa = self._ler_texto("Placa").upper()
        modelo = self._ler_texto("Modelo")
        ano = self._ler_ano()
        proprietario = self._ler_texto("Proprietário")
        veiculo = Veiculo(renavam, placa, modelo, ano, proprietario)
        if self.gerenciador.cadastrar_veiculo(veiculo):
            print(f"Veículo {renavam} cadastrado nas duas árvores.")
        else:
            print(f"Já existe um veículo com o RENAVAM {renavam}. Cadastro preservado.")

    @staticmethod
    def _exibir_veiculo(veiculo: Veiculo) -> None:
        # Mostra os cinco atributos de um veículo.
        print(f"RENAVAM: {veiculo.renavam}")
        print(f"Placa: {veiculo.placa}")
        print(f"Modelo: {veiculo.modelo}")
        print(f"Ano: {veiculo.ano}")
        print(f"Proprietário: {veiculo.proprietario}")

    def _buscar_veiculo(self) -> None:
        # Busca o RENAVAM na árvore selecionada e mostra o veículo encontrado.
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
        # Lista os veículos da árvore selecionada no caminhamento informado.
        veiculos = self.gerenciador.listar_veiculos(ordem)
        if not veiculos:
            print("Nenhum veículo cadastrado.")
            return
        nomes = {"em_ordem": "em ordem", "pre_ordem": "em pré-ordem", "pos_ordem": "em pós-ordem"}
        print(f"\nVeículos {nomes[ordem]} — {self.gerenciador.estrutura_selecionada}")
        print("RENAVAM | Placa | Modelo | Ano | Proprietário")
        print("-" * 72)
        for veiculo in veiculos:
            print(
                f"{veiculo.renavam} | {veiculo.placa} | {veiculo.modelo} | "
                f"{veiculo.ano} | {veiculo.proprietario}"
            )
        print(f"Total: {len(veiculos)} veículo(s).")

    def _exibir_altura_e_quantidade(self) -> None:
        # Mostra a altura e a quantidade de nós da árvore selecionada.
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
        # Chama os experimentos e informa quando ainda não estão implementados.
        try:
            experimentos.executar_experimentos()
        except NotImplementedError as erro:
            print(erro)

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
