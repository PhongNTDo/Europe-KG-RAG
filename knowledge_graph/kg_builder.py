import json
from neo4j import GraphDatabase

class KnowledgeGraphBuilder:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)

    def close(self):
        self.driver.close()

    def _execute_write_query(self, tx, query, **kwargs):
        tx.run(query, **kwargs)

    def clear_database(self):
        with self.driver.session() as session:
            session.execute_write(self._execute_write_query, "MATCH (n) DETACH DELETE n")
        print("Database cleared!")

    def build_graph(self, data):
        with self.driver.session() as session:
            # create nodes
            for country in data['countries']:
                session.execute_write(self._execute_write_query, "CREATE (:Country {name: $name})", name=country['name'])
                session.execute_write(self._execute_write_query, "CREATE (:City {name:$name})", name=country['capital'])
            for river in data['rivers']:
                session.execute_write(self._execute_write_query, "CREATE (:River {name: $name})", name=river['name'])
            for landmark in data['landmarks']:
                session.execute_write(self._execute_write_query, "CREATE (:Landmark {name: $name})", name=landmark['name'])
            print("Nodes created!")

            # create relationships
            for country in data['countries']:
                session.execute_write(self._execute_write_query,
                                      "MATCH (c:Country {name: $country_name}), (cap:City {name: $city_name})"
                                      "CREATE (c)-[:HAS_CAPITAL]->(cap)",
                                      country_name=country['name'], city_name=country['capital'])
                for border in country['borders_with']:
                    session.execute_write(self._execute_write_query,
                                          "MATCH (c:Country {name: $country_name}), (border_country:Country {name: $border})"
                                          "CREATE (c)-[:BORDERS_WITH]->(border_country)",
                                          country_name=country['name'], border=border)
            for river in data['rivers']:
                for country in river['flows_through']:
                    session.execute_write(self._execute_write_query,
                                          "MATCH (r:River {name: $river_name}), (c:Country {name:$country_name})"
                                          "CREATE (r)-[:FLOWS_THROUGH]->(c)",
                                          river_name=river['name'], country_name=country)
            for landmark in data['landmarks']:
                session.execute_write(self._execute_write_query,
                                      "MATCH (l:Landmark {name: $landmark_name}), (c:Country {name: $country_name})"
                                      "CREATE (l)-[:LOCATED_IN]->(c)",
                                      landmark_name=landmark['name'], country_name=landmark['location'])
            print("Relationships created!")
            print("Knowledge Graph built successfully!")

if __name__ == "__main__":
    from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

    with open("data/europe_data.json", "r") as file:
        europe_data = json.load(file)

    kg_builder = KnowledgeGraphBuilder(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
    kg_builder.clear_database()
    kg_builder.build_graph(europe_data)
    kg_builder.close()
