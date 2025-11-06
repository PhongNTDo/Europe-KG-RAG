"""
Utility entry point for (re)building the Europe knowledge graph in Neo4j.
"""

from config import NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME
from europe_kg_rag.data import DatabaseLoader
from europe_kg_rag.graph import KnowledgeGraphBuilder


def rebuild_europe_graph(clear_existing: bool = True) -> None:
    loader = DatabaseLoader()
    builder = KnowledgeGraphBuilder(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
    try:
        if clear_existing:
            builder.clear_database()
        builder.build_from_loader(loader)
    finally:
        builder.close()


if __name__ == "__main__":
    rebuild_europe_graph()
