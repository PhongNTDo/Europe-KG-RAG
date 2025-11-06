from __future__ import annotations

from neo4j import GraphDatabase


class KnowledgeGraphQuerier:
    """Thin Neo4j wrapper for running arbitrary Cypher queries."""

    def __init__(self, uri: str, user: str, password: str) -> None:
        self.driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)

    def close(self) -> None:
        self.driver.close()

    def query(self, cypher_query: str, parameters: dict | None = None) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(cypher_query, parameters or {})
            return [record.data() for record in result]
