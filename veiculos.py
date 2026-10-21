"""Entidade compartilhada pelas árvores do cadastro de veículos."""


class Veiculo:
    """Veículo identificado pelo RENAVAM, preservando zeros à esquerda."""

    def __init__(
        self,
        renavam: str,
        placa: str,
        modelo: str,
        ano: int,
        proprietario: str,
    ) -> None:
        self.renavam = self.normalizar_renavam(renavam)
        self.placa = placa
        self.modelo = modelo
        self.ano = ano
        self.proprietario = proprietario

    @staticmethod
    def normalizar_renavam(renavam: str) -> str:
        """Remove a pontuação e exige ao menos um algarismo ASCII."""
        if not isinstance(renavam, str):
            raise TypeError("O RENAVAM deve ser uma string.")

        normalizado = "".join(caractere for caractere in renavam if "0" <= caractere <= "9")
        if not normalizado:
            raise ValueError("O RENAVAM deve conter ao menos um dígito.")
        return normalizado
