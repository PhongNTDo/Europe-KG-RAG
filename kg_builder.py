# Author: Felix Do
# Date: 2025-09-15

from neo4j import GraphDatabase

class EuropeKnowledgeGraph:
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
            for country in data['countries']:
                session.execute_write(self._execute_write_query,
                                      "CREATE (:Country {name: $name, eu_member: $eu_member})",
                                      name=country['name'], eu_member=country['eu_member'])
                
            for capital in data['capitals']:
                session.execute_write(self._execute_write_query,
                                      "CREATE (:City {name: $name})",
                                      name=capital)
            
            for river in data['rivers']:
                session.execute_write(self._execute_write_query,
                                      "CREATE (:River {name: $name})",
                                      name=river['name'])
                
            for mountain in data['mountains']:
                session.execute_write(self._execute_write_query,
                                      "CREATE (:Mountain {name: $name})",
                                      name=mountain['name'])
                
            for landmark in data['landmarks']:
                session.execute_write(self._execute_write_query,
                                      "CREATE (:Landmark {name: $name})",
                                      name=landmark['name'])
            
            print("Nodes created!")

            # Create relationships
            for country, capital in data['relations']['has_capital'].items():
                session.execute_write(self._execute_write_query,
                                      "MATCH (c:Country {name: $country}), (cap:City {name: $capital_name})"
                                      "CREATE (c)-[:HAS_CAPITAL]->(cap)",
                                      country=country, capital_name=capital)
                
            for country, borders in data['relations']['borders_with'].items():
                for border in borders:
                    session.execute_write(self._execute_write_query,
                                          "MATCH (c1:Country {name: $country1}), (c2:Country {name: $country2})"
                                          "CREATE (c1)-[:BORDERS_WITH]->(c2)",
                                          country1=country, country2=border)
                    
            for river in data['rivers']:
                for country in river['flows_through']:
                    session.execute_write(self._execute_write_query,
                                          "MATCH (r:River {name: $river_name}), (c:Country {name: $country_name})"
                                          "CREATE (r)-[:FLOWS_THROUGH]->(c)",
                                          river_name=river['name'], country_name=country)

            for mountain in data['mountains']:
                for country in mountain['location']:
                    session.execute_write(self._execute_write_query,
                                          "MATCH (m:Mountain {name: $mountain_name}), (c:Country {name: $country_name})"
                                          "CREATE (m)-[:HIGHEST_POINT]->(c)",
                                          mountain_name=mountain['name'], country_name=country)
                    
            for landmark in data['landmarks']:
                session.execute_write(self._execute_write_query,
                                      "MATCH (l:Landmark {name: $landmark_name}), (c:Country {name: $country_name})"
                                      "CREATE (l)-[:LOCATED_IN]->(c)",
                                      landmark_name=landmark['name'], country_name=landmark['location'])
                
            print("Relationships created!")
            print("Knowledge Graph built successfully!")

    def run_queries(self):
        # Example Cypher queries
        queries = {
            "a) Which countries border Germany?":
            "MATCH (c:Country {name: 'Germany'})-[:BORDERS_WITH]->(neighbor) "
            "RETURN neighbor.name AS neighboring_country",
            "b) Which rivers flow through more than 3 countries? ":
            "MATCH (r:River)-[:FLOWS_THROUGH]->(c:Country) "
            "WITH r, COUNT(DISTINCT c) AS country_count "
            "WHERE country_count > 3 "
            "RETURN r.name AS river_name, country_count AS countries",
            "c) Which landmarks are located in France?":
            "MATCH (l:Landmark)-[:LOCATED_IN]->(c:Country {name: 'France'}) "
            "RETURN l.name AS landmark_name"
        }

        with self.driver.session() as session:
            for query_name, query in queries.items():
                print(f"\n--- Query: {query_name} ---\n")
                result = session.run(query)
                for record in result:
                    print(record.data)

def get_europe_data():
    return {
    "countries": [
        {"name": "Germany", "eu_member": True},
        {"name": "France", "eu_member": True},
        {"name": "Switzerland", "eu_member": False},
        {"name": "Austria", "eu_member": True},
        {"name": "Poland", "eu_member": True},
        {"name": "Czech Republic", "eu_member": True},
        {"name": "Belgium", "eu_member": True},
        {"name": "Netherlands", "eu_member": True},
        {"name": "Luxembourg", "eu_member": True},
        {"name": "Denmark", "eu_member": True},
        {"name": "Italy", "eu_member": True},
        {"name": "Spain", "eu_member": True}
    ],
    "capitals": [
        "Berlin", "Paris", "Bern", "Vienna", "Warsaw", "Prague", "Brussels",
        "Amsterdam", "Luxembourg", "Copenhagen", "Rome", "Madrid"
    ],
    "rivers": [
        {"name": "Danube", "flows_through": ["Germany", "Austria"]},
        {"name": "Rhine", "flows_through": ["Switzerland", "Austria", "Germany", "France", "Netherlands"]},
        {"name": "Elbe", "flows_through": ["Czech Republic", "Germany"]},
        {"name": "Seine", "flows_through": ["France"]},
        {"name": "Po", "flows_through": ["Italy"]}
    ],
    "mountains": [
        {"name": "Mont Blanc", "location": ["France", "Italy"]},
        {"name": "Zugspitze", "location": ["Germany"]},
        {"name": "Monte Rosa", "location": ["Switzerland", "Italy"]}
    ],
    "landmarks": [
        {"name": "Eiffel Tower", "location": "France"},
        {"name": "Brandenburg Gate", "location": "Germany"},
        {"name": "Colosseum", "location": "Italy"},
        {"name": "Louvre Museum", "location": "France"},
        {"name": "Neuschwanstein Castle", "location": "Germany"}
    ],
    "relations": {
        "has_capital": {
            "Germany": "Berlin", "France": "Paris", "Switzerland": "Bern", "Austria": "Vienna",
            "Poland": "Warsaw", "Czech Republic": "Prague", "Belgium": "Brussels",
            "Netherlands": "Amsterdam", "Luxembourg": "Luxembourg", "Denmark": "Copenhagen",
            "Italy": "Rome", "Spain": "Madrid"
        },
        "borders_with": {
            "Germany": ["France", "Switzerland", "Austria", "Poland", "Czech Republic", "Belgium", "Netherlands", "Luxembourg", "Denmark"]
        }
    }
}


if __name__ == "__main__":
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "12345678"

    europe_kg = EuropeKnowledgeGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    europe_kg.clear_database()
    
    europe_data = get_europe_data()
    europe_kg.build_graph(europe_data)
    europe_kg.run_queries()

    europe_kg.close()