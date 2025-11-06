from __future__ import annotations

from neo4j import GraphDatabase

from europe_kg_rag.data.loader import DatabaseLoader
from europe_kg_rag.data.models import Country, GraphDataset, River


class KnowledgeGraphBuilder:
    """Create the Europe knowledge graph inside Neo4j."""

    def __init__(self, uri: str, user: str, password: str) -> None:
        self.driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)

    def close(self) -> None:
        self.driver.close()

    def clear_database(self) -> None:
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def build_from_loader(self, loader: DatabaseLoader) -> None:
        dataset = loader.load()
        self.build(dataset)

    def build(self, dataset: GraphDataset) -> None:
        with self.driver.session() as session:
            for country in dataset.countries:
                session.execute_write(self._upsert_country, country)

            for country in dataset.countries:
                self._create_country_relationships(session, country)

            for river in dataset.rivers:
                session.execute_write(self._upsert_river, river)

            for river in dataset.rivers:
                self._create_river_relationships(session, river)

    @staticmethod
    def _upsert_country(tx, country: Country) -> None:
        tx.run(
            """
            MERGE (c:Country {name: $name})
            SET c.capital = $capital,
                c.eu_member = $eu_member
            """,
            name=country.name,
            capital=country.capital,
            eu_member=country.eu_member,
        )

        if country.capital:
            tx.run(
                """
                MATCH (c:Country {name: $name})
                MERGE (city:City {name: $capital})
                MERGE (c)-[:HAS_CAPITAL]->(city)
                """,
                name=country.name,
                capital=country.capital,
            )

    def _create_country_relationships(self, session, country: Country) -> None:
        for neighbor in country.borders_with:
            session.execute_write(self._link_neighbors, country.name, neighbor)

    @staticmethod
    def _link_neighbors(tx, country_name: str, neighbor_name: str) -> None:
        if not neighbor_name:
            return
        tx.run(
            """
            MERGE (c:Country {name: $country_name})
            MERGE (n:Country {name: $neighbor_name})
            MERGE (c)-[:BORDERS_WITH]->(n)
            """,
            country_name=country_name,
            neighbor_name=neighbor_name,
        )

    @staticmethod
    def _upsert_river(tx, river: River) -> None:
        tx.run(
            """
            MERGE (r:River {name: $name})
            SET r.length = $length,
                r.basin = $basin,
                r.flow = $flow,
                r.mouth = $mouth,
                r.rank_of_length = $rank_of_length,
                r.rank_of_area = $rank_of_area,
                r.rank_of_flow = $rank_of_flow
            """,
            name=river.name,
            length=river.length,
            basin=river.basin,
            flow=river.flow,
            mouth=river.mouth,
            rank_of_length=river.rank_of_length,
            rank_of_area=river.rank_of_area,
            rank_of_flow=river.rank_of_flow,
        )

    def _create_river_relationships(self, session, river: River) -> None:
        for country_name in river.countries:
            session.execute_write(self._link_river_country, river.name, country_name)

        if river.parent:
            session.execute_write(self._link_river_parent, river.name, river.parent)

    @staticmethod
    def _link_river_country(tx, river_name: str, country_name: str) -> None:
        if not country_name:
            return
        tx.run(
            """
            MERGE (r:River {name: $river_name})
            MERGE (c:Country {name: $country_name})
            MERGE (r)-[:FLOWS_THROUGH]->(c)
            """,
            river_name=river_name,
            country_name=country_name,
        )

    @staticmethod
    def _link_river_parent(tx, river_name: str, parent_name: str) -> None:
        tx.run(
            """
            MATCH (child:River {name: $river_name})
            OPTIONAL MATCH (parentRiver:River {name: $parent_name})
            FOREACH (_ IN CASE WHEN parentRiver IS NOT NULL THEN [1] ELSE [] END |
                MERGE (child)-[:TRIBUTES_TO]->(parentRiver)
            )
            FOREACH (_ IN CASE WHEN parentRiver IS NULL THEN [1] ELSE [] END |
                MERGE (water:WaterBody {name: $parent_name})
                MERGE (child)-[:FLOWS_INTO]->(water)
            )
            """,
            river_name=river_name,
            parent_name=parent_name,
        )
