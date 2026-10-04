"""
KALATRACE Core Services Smoke Tests

T1.1c - rede de seguranca minima para core/services/,
migrado de kernel/services/ (sem nenhum ponto do projeto
referenciando-o antes desta migracao).

Nao pretende ser cobertura completa - o objetivo e detectar
regressao obvia se algo for quebrado ao mexer no modulo.
"""

import pytest

from core.services import KernelService, KernelLogger


class DummyService(KernelService):
    def initialize(self):
        self.initialized = True

    def shutdown(self):
        self.initialized = False


class TestKernelService:
    def test_starts_uninitialized(self):
        service = DummyService(name="db")
        assert service.name == "db"
        assert service.is_initialized is False

    def test_initialize_and_shutdown(self):
        service = DummyService(name="db")
        service.initialize()
        assert service.is_initialized is True
        service.shutdown()
        assert service.is_initialized is False

    def test_cannot_instantiate_abstract_class_directly(self):
        with pytest.raises(TypeError):
            KernelService(name="db")


class TestKernelLogger:
    def test_starts_with_no_logs(self):
        logger = KernelLogger()
        assert logger.get_logs() == []

    def test_log_with_invalid_level_raises(self):
        logger = KernelLogger()
        with pytest.raises(ValueError):
            logger.log("NOT_A_LEVEL", "msg")

    def test_info_appends_log_with_expected_fields(self):
        logger = KernelLogger()
        entry = logger.info("hello", source="TEST")
        assert entry["level"] == "INFO"
        assert entry["message"] == "hello"
        assert entry["source"] == "TEST"
        assert len(logger.get_logs()) == 1

    @pytest.mark.parametrize("level_method", ["debug", "info", "warning", "error", "critical"])
    def test_each_level_shortcut_logs_correct_level(self, level_method):
        logger = KernelLogger()
        entry = getattr(logger, level_method)("msg")
        assert entry["level"] == level_method.upper()

    def test_clear_removes_all_logs(self):
        logger = KernelLogger()
        logger.info("a")
        logger.info("b")
        logger.clear()
        assert logger.get_logs() == []
