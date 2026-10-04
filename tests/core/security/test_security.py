"""
KALATRACE Core Security Smoke Tests

T1.1c - rede de seguranca minima para core/security/,
migrado de kernel/security/ (sem nenhum ponto do projeto
referenciando-o antes desta migracao).

Nao pretende ser cobertura completa - o objetivo e detectar
regressao obvia se algo for quebrado ao mexer no modulo.
"""

from core.security import SecurityManager


class TestTrustedModules:
    def test_starts_with_no_trusted_modules(self):
        manager = SecurityManager()
        assert manager.is_trusted("core.events") is False

    def test_register_and_unregister_module(self):
        manager = SecurityManager()
        manager.register_module("core.events")
        assert manager.is_trusted("core.events") is True
        manager.unregister_module("core.events")
        assert manager.is_trusted("core.events") is False

    def test_unregister_unknown_module_is_noop(self):
        manager = SecurityManager()
        manager.unregister_module("nao-existe")  # nao deve levantar excecao


class TestPermissions:
    def test_grant_and_check_permission(self):
        manager = SecurityManager()
        manager.grant_permission("core.events", "publish")
        assert manager.has_permission("core.events", "publish") is True
        assert manager.has_permission("core.events", "subscribe") is False

    def test_revoke_permission(self):
        manager = SecurityManager()
        manager.grant_permission("core.events", "publish")
        manager.revoke_permission("core.events", "publish")
        assert manager.has_permission("core.events", "publish") is False

    def test_list_permissions_sorted(self):
        manager = SecurityManager()
        manager.grant_permission("core.events", "subscribe")
        manager.grant_permission("core.events", "publish")
        assert manager.list_permissions("core.events") == ["publish", "subscribe"]

    def test_list_permissions_unknown_module_returns_empty(self):
        manager = SecurityManager()
        assert manager.list_permissions("nao-existe") == []


class TestClear:
    def test_clear_removes_trust_and_permissions(self):
        manager = SecurityManager()
        manager.register_module("core.events")
        manager.grant_permission("core.events", "publish")
        manager.clear()
        assert manager.is_trusted("core.events") is False
        assert manager.list_permissions("core.events") == []
