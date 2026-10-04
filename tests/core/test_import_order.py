"""
KALATRACE Core - Testes de ordem de import

Fase 0 (achado durante T0.2): core.exceptions e core.lifecycle
tinham uma dependencia circular (core.exceptions.invalid_state_transition
importava core.lifecycle.component_state no nivel de modulo, e
core.lifecycle.lifecycle_state_machine importava core.exceptions no
nivel de modulo) que so quebrava se core.exceptions fosse importado
ANTES de core.lifecycle em um processo Python novo.

Como isso depende da ordem de import - e o cache de modulos do
Python (sys.modules) esconde o problema assim que qualquer teste
anterior no mesmo processo ja importou core.lifecycle primeiro -
este teste roda cada cenario em um SUBPROCESSO limpo, para garantir
que a regressao seja detectada de forma confiavel.
"""

import subprocess
import sys


def _run_import_in_fresh_process(import_statement: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-c", import_statement],
        capture_output=True,
        text=True,
    )


def test_importing_core_exceptions_before_core_lifecycle_does_not_fail():
    """
    Regressao: `from core.exceptions import InvalidStateTransition`
    como PRIMEIRO import do processo costumava lancar ImportError
    por dependencia circular com core.lifecycle.
    """

    result = _run_import_in_fresh_process(
        "from core.exceptions import InvalidStateTransition"
    )

    assert result.returncode == 0, result.stderr


def test_importing_core_lifecycle_before_core_exceptions_still_works():
    """
    Garante que a ordem inversa (que ja funcionava antes) continua
    funcionando apos a correcao.
    """

    result = _run_import_in_fresh_process(
        "import core.lifecycle; from core.exceptions import InvalidStateTransition"
    )

    assert result.returncode == 0, result.stderr


def test_importing_core_package_directly_works():
    result = _run_import_in_fresh_process("import core")

    assert result.returncode == 0, result.stderr
