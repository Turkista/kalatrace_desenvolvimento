"""
KALATRACE Core Logger

Migrated from kernel/services/logger.py as
part of ADR-001 (T1.1c) — no prior equivalent
in core/.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any


class KernelLogger:
    """
    Kernel Logger

    Serviço centralizado de logging
    e diagnóstico do KALATRACE.
    """

    LEVELS = {
        "DEBUG": 1,
        "INFO": 2,
        "WARNING": 3,
        "ERROR": 4,
        "CRITICAL": 5
    }

    def __init__(self):
        self.logs: List[Dict[str, Any]] = []
        self.minimum_level = "DEBUG"

    def _create_log(
        self,
        level: str,
        message: str,
        source: str
    ):
        """
        Cria registro interno de log.
        """

        log = {
            "timestamp": datetime.now(
                timezone.utc
            ),
            "level": level,
            "source": source,
            "message": message
        }

        self.logs.append(log)

        return log

    def log(
        self,
        level: str,
        message: str,
        source: str = "KERNEL"
    ):
        """
        Registra uma mensagem.
        """

        if level not in self.LEVELS:
            raise ValueError(
                f"Nível inválido: {level}"
            )

        log = self._create_log(
            level,
            message,
            source
        )

        print(
            f"[{level}] "
            f"{source}: "
            f"{message}"
        )

        return log

    def debug(
        self,
        message: str,
        source: str = "KERNEL"
    ):
        return self.log(
            "DEBUG",
            message,
            source
        )

    def info(
        self,
        message: str,
        source: str = "KERNEL"
    ):
        return self.log(
            "INFO",
            message,
            source
        )

    def warning(
        self,
        message: str,
        source: str = "KERNEL"
    ):
        return self.log(
            "WARNING",
            message,
            source
        )

    def error(
        self,
        message: str,
        source: str = "KERNEL"
    ):
        return self.log(
            "ERROR",
            message,
            source
        )

    def critical(
        self,
        message: str,
        source: str = "KERNEL"
    ):
        return self.log(
            "CRITICAL",
            message,
            source
        )

    def get_logs(self):
        """
        Retorna histórico de logs.
        """

        return self.logs

    def clear(self):
        """
        Limpa registros.
        """

        self.logs.clear()