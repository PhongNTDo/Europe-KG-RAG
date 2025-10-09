from neo4j import GraphDatabase

class KnowledgeGraphQuerier:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)

    def close(self):
        self.driver.close()

    def query(self, cypher_query):
        with self.driver.session() as session:
            result = session.run(cypher_query)
            return [record.data() for record in result]
        
    
if __name__ == '__main__':
    from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

    kg_builder = KnowledgeGraphQuerier(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)

    # example
    query = "MATCH (c:Country {name: 'Germany'})-[:BORDERS_WITH]->(neighbor) RETURN neighbor.name as neighbor_country"
    results = kg_builder.query(query)
    print(results)

    kg_builder.close()