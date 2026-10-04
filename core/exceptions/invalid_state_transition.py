"""
Invalid lifecycle transition.
"""


from __future__ import annotations

from typing import TYPE_CHECKING

from .lifecycle_error import LifecycleError

if TYPE_CHECKING:
    # Import apenas para type checking: em runtime, core.lifecycle
    # importa core.exceptions (para InvalidStateTransition), entao
    # um import de nivel de modulo aqui criaria um ciclo
    # (core.exceptions -> core.lifecycle -> core.exceptions) que
    # quebra dependendo da ordem em que os pacotes sao importados
    # primeiro. `from __future__ import annotations` ja torna as
    # anotacoes abaixo strings em runtime, entao este import nunca
    # precisa rodar fora de checagem de tipos.
    from core.lifecycle.component_state import ComponentState



class InvalidStateTransition(LifecycleError):
    """
    Raised when a lifecycle transition is invalid.
    """


    def __init__(
        self,
        current: ComponentState,
        target: ComponentState,
    ) -> None:

        # Import tardio (runtime) para quebrar o ciclo com
        # core.lifecycle - ver nota acima no bloco TYPE_CHECKING.
        from core.lifecycle.component_state import ComponentState

        if not isinstance(
            current,
            ComponentState,
        ):
            raise TypeError(
                "current must be ComponentState."
            )


        if not isinstance(
            target,
            ComponentState,
        ):
            raise TypeError(
                "target must be ComponentState."
            )


        super().__init__(
            f"Invalid lifecycle transition: "
            f"{current.name} -> {target.name}"
        )


        self.current = current

        self.target = target