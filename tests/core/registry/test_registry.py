"""
KALATRACE Core Registry Smoke Tests

Fase 0 (T0.3) - rede de seguranca minima para core/registry/
antes de qualquer fusao/refatoracao futura (ADR-001, Fase 1).

Cobre o comportamento critico de:
- Registry (armazenamento central)
- RegistryEntry (estado de runtime de um componente)
- RegistryManager (camada de coordenacao usada por Runtime)

Nao pretende ser cobertura completa - o objetivo e detectar
regressao obvia se algo for quebrado ao mexer no modulo.
"""

import pytest

from core.metadata import ComponentMetadata
from core.registry import (
    ComponentType,
    Registry,
    RegistryEntry,
    RegistryManager,
)


class DummyComponent:
    """Classe simples usada como component_class/instance nos testes."""


def make_entry(identifier="comp-1"):
    metadata = ComponentMetadata(
        identifier=identifier,
        name=f"Component {identifier}",
    )

    return RegistryEntry(
        identifier=identifier,
        metadata=metadata,
        component_type=ComponentType.SERVICE,
        component_class=DummyComponent,
    )


# ---------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------

def test_registry_starts_empty():
    registry = Registry()

    assert len(registry) == 0
    assert registry.all() == ()


def test_registry_register_and_get():
    registry = Registry()
    entry = make_entry()

    registry.register(entry)

    assert len(registry) == 1
    assert "comp-1" in registry
    assert registry.get("comp-1") is entry


def test_registry_register_duplicate_raises():
    registry = Registry()
    registry.register(make_entry("comp-1"))

    with pytest.raises(ValueError):
        registry.register(make_entry("comp-1"))


def test_registry_unregister():
    registry = Registry()
    registry.register(make_entry("comp-1"))

    registry.unregister("comp-1")

    assert "comp-1" not in registry
    assert registry.get("comp-1") is None


def test_registry_register_instance_and_clear():
    registry = Registry()
    registry.register(make_entry("comp-1"))
    instance = DummyComponent()

    registry.register_instance("comp-1", instance)
    entry = registry.get("comp-1")

    assert entry.instance is instance
    assert entry.is_loaded()

    registry.clear_instance("comp-1")

    assert entry.instance is None


def test_registry_register_instance_unknown_raises():
    registry = Registry()

    with pytest.raises(KeyError):
        registry.register_instance("missing", DummyComponent())


def test_registry_find_by_type_and_tag():
    registry = Registry()

    entry_a = make_entry("comp-a")
    entry_a.metadata.add_tag("vision")

    entry_b = make_entry("comp-b")

    registry.register(entry_a)
    registry.register(entry_b)

    by_type = registry.find_by_type(ComponentType.SERVICE)
    assert len(by_type) == 2

    by_tag = registry.find_by_tag("vision")
    assert by_tag == [entry_a]


# ---------------------------------------------------------------------
# RegistryEntry
# ---------------------------------------------------------------------

def test_registry_entry_requires_matching_identifier():
    metadata = ComponentMetadata(
        identifier="comp-x",
        name="Component X",
    )

    with pytest.raises(ValueError):
        RegistryEntry(
            identifier="different-id",
            metadata=metadata,
            component_type=ComponentType.SERVICE,
            component_class=DummyComponent,
        )


def test_registry_entry_mark_loaded_requires_instance():
    entry = make_entry()

    with pytest.raises(RuntimeError):
        entry.mark_loaded()

    entry.instance = DummyComponent()
    entry.mark_loaded()

    assert entry.is_loaded()
    assert entry.load_count == 1
    assert entry.active is True


def test_registry_entry_mark_unloaded_resets_instance():
    entry = make_entry()
    entry.instance = DummyComponent()
    entry.mark_loaded()

    entry.mark_unloaded()

    assert entry.instance is None
    assert entry.active is False
    assert entry.unloaded_at is not None


# ---------------------------------------------------------------------
# RegistryManager
# ---------------------------------------------------------------------

def test_registry_manager_register_component():
    manager = RegistryManager()

    metadata = ComponentMetadata(
        identifier="comp-1",
        name="Component 1",
    )

    entry = manager.register_component(
        metadata,
        ComponentType.SERVICE,
        DummyComponent,
    )

    assert manager.exists("comp-1")
    assert manager.get("comp-1") is entry
    assert manager.registry is not None


def test_registry_manager_load_and_unload_component():
    manager = RegistryManager()

    metadata = ComponentMetadata(
        identifier="comp-1",
        name="Component 1",
    )

    manager.register_component(
        metadata,
        ComponentType.SERVICE,
        DummyComponent,
    )

    instance = DummyComponent()
    manager.load_component("comp-1", instance)

    assert manager.get("comp-1").instance is instance

    manager.unload_component("comp-1")

    assert manager.get("comp-1").instance is None


def test_registry_manager_unload_unknown_component_raises():
    manager = RegistryManager()

    with pytest.raises(KeyError):
        manager.unload_component("missing")


def test_registry_manager_unregister_component():
    manager = RegistryManager()

    metadata = ComponentMetadata(
        identifier="comp-1",
        name="Component 1",
    )

    manager.register_component(
        metadata,
        ComponentType.SERVICE,
        DummyComponent,
    )

    manager.unregister_component("comp-1")

    assert not manager.exists("comp-1")
