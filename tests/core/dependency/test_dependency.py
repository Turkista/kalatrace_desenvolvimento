"""
KALATRACE Core Dependency Smoke Tests

T1.1b - rede de seguranca minima para core/dependency/,
migrado de kernel/dependency/ (usado por kernel/kernel.py
e kernel/__init__.py, sem outros pontos do projeto
referenciando-o antes desta migracao).

Nao pretende ser cobertura completa - o objetivo e detectar
regressao obvia se algo for quebrado ao mexer no modulo.
"""

import pytest

from core.dependency import (
    DependencyContainer,
    ServiceRegistry,
    ServiceLocator,
    Injector,
)


class TestDependencyContainer:
    def test_register_requires_initialize_first(self):
        container = DependencyContainer()
        with pytest.raises(RuntimeError):
            container.register("db", object())

    def test_register_and_resolve(self):
        container = DependencyContainer()
        container.initialize()
        sentinel = object()
        container.register("db", sentinel)
        assert container.resolve("db") is sentinel

    def test_register_duplicate_raises(self):
        container = DependencyContainer()
        container.initialize()
        container.register("db", object())
        with pytest.raises(ValueError):
            container.register("db", object())

    def test_replace_overwrites(self):
        container = DependencyContainer()
        container.initialize()
        container.register("db", "v1")
        container.replace("db", "v2")
        assert container.resolve("db") == "v2"

    def test_resolve_missing_raises_keyerror(self):
        container = DependencyContainer()
        container.initialize()
        with pytest.raises(KeyError):
            container.resolve("nao-existe")

    def test_exists_and_remove(self):
        container = DependencyContainer()
        container.initialize()
        container.register("db", object())
        assert container.exists("db") is True
        container.remove("db")
        assert container.exists("db") is False

    def test_shutdown_clears_and_deinitializes(self):
        container = DependencyContainer()
        container.initialize()
        container.register("db", object())
        container.shutdown()
        assert container.count() == 0
        assert container.initialized is False


class TestServiceRegistry:
    def test_register_requires_initialize_first(self):
        registry = ServiceRegistry()
        with pytest.raises(RuntimeError):
            registry.register("svc", object())

    def test_register_and_get(self):
        registry = ServiceRegistry()
        registry.initialize()
        sentinel = object()
        registry.register("svc", sentinel)
        assert registry.get("svc") is sentinel

    def test_register_empty_name_raises(self):
        registry = ServiceRegistry()
        registry.initialize()
        with pytest.raises(ValueError):
            registry.register("", object())

    def test_register_none_service_raises(self):
        registry = ServiceRegistry()
        registry.initialize()
        with pytest.raises(ValueError):
            registry.register("svc", None)

    def test_get_missing_raises_keyerror(self):
        registry = ServiceRegistry()
        registry.initialize()
        with pytest.raises(KeyError):
            registry.get("nao-existe")

    def test_list_services_and_shutdown(self):
        registry = ServiceRegistry()
        registry.initialize()
        registry.register("svc", object())
        assert registry.list_services() == ["svc"]
        registry.shutdown()
        assert registry.list_services() == []
        assert registry.initialized is False


class TestServiceLocator:
    def setup_method(self):
        ServiceLocator.clear()

    def teardown_method(self):
        ServiceLocator.clear()

    def test_get_without_configure_raises(self):
        with pytest.raises(RuntimeError):
            ServiceLocator.get("svc")

    def test_exists_without_configure_returns_false(self):
        assert ServiceLocator.exists("svc") is False

    def test_configure_then_get(self):
        registry = ServiceRegistry()
        registry.initialize()
        sentinel = object()
        registry.register("svc", sentinel)
        ServiceLocator.configure(registry)
        assert ServiceLocator.get("svc") is sentinel
        assert ServiceLocator.exists("svc") is True


class TestInjector:
    def test_resolve_injects_matching_registry_names(self):
        registry = ServiceRegistry()
        registry.initialize()
        registry.register("logger", "the-logger")

        class Component:
            def __init__(self, logger=None):
                self.logger = logger

        injector = Injector(registry)
        instance = injector.resolve(Component)
        assert instance.logger == "the-logger"

    def test_inject_sets_declared_dependency_attributes(self):
        registry = ServiceRegistry()
        registry.initialize()
        registry.register("logger", "the-logger")

        class Component:
            __dependencies__ = ["logger"]

        injector = Injector(registry)
        instance = injector.inject(Component())
        assert instance.logger == "the-logger"
