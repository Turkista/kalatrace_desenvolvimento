from typing import Dict, Any


class ConfigurationManager:
    """
    Configuration Manager

    Responsável pelo gerenciamento
    centralizado das configurações
    do KALATRACE.
    """

    def __init__(self):
        self.configurations: Dict[str, Any] = {}
        self.loaded = False

    def load(
        self,
        configuration: Dict[str, Any]
    ):
        """
        Carrega configurações.
        """

        self.configurations = configuration
        self.loaded = True

        print(
            "Configurações carregadas."
        )

    def get(
        self,
        key: str,
        default=None
    ):
        """
        Recupera uma configuração.
        """

        if not self.loaded:
            raise RuntimeError(
                "Configurações ainda não carregadas."
            )

        return self.configurations.get(
            key,
            default
        )

    def set(
        self,
        key: str,
        value: Any
    ):
        """
        Atualiza uma configuração.
        """

        self.configurations[key] = value

    def exists(
        self,
        key: str
    ) -> bool:
        """
        Verifica existência.
        """

        return key in self.configurations

    def all(self):
        """
        Retorna todas as configurações.
        """

        return self.configurations

    def clear(self):
        """
        Limpa configurações.
        """

        self.configurations.clear()

        self.loaded = False

        print(
            "Configurações removidas."
        )