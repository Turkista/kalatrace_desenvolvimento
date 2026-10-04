"""Smoke test for the configured Neo4j Aura connection."""
from integrations.neo4j import neo4j_client

if __name__ == "__main__":
    result = neo4j_client.verify_connectivity()
    print("Neo4j connection OK")
    print(result)
    neo4j_client.close()
