"""Security regressions for Neo4j operational status responses."""
from integrations.neo4j import Neo4jClient, Neo4jSettings


class FakeResult:
    def single(self):
        return {"ok": 1}


class FakeSession:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def run(self, query):
        assert query == "RETURN 1 AS ok"
        return FakeResult()


class FakeDriver:
    def verify_connectivity(self):
        return None

    def session(self, *, database):
        assert database == "neo4j-test"
        return FakeSession()


def test_health_response_does_not_disclose_connection_identity(monkeypatch):
    client = Neo4jClient(
        Neo4jSettings(
            uri="neo4j+s://internal-host.example:7687",
            username="private-service-user",
            password="private-password",
            database="neo4j-test",
        )
    )
    monkeypatch.setattr(client, "_get_driver", lambda: FakeDriver())

    result = client.verify_connectivity()

    assert result == {
        "enabled": True,
        "connected": True,
        "database": "neo4j-test",
    }
    assert "uri" not in result
    assert "username" not in result
    assert "password" not in result
