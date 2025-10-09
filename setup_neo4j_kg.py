from neo4j import GraphDatabase

class EuropeKnowledgeGraph:
    def __init__(self, uri, user, password):
        self.__uri = uri
        self.__user = user
        self.__password = password
        self.__driver = None
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def clear_database(self):
        with self.__driver.session() as session:
            session.execute_write(self._execute_write_query, "MATCH (n) DETACH DELETE n")
        print("Database cleared!")

    def query(self, query, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response

    def build_graph(self, data):
        pass


def get_europe_data():
    return {
        "countries": [
            {"name": "Germany", "population": 83000000, "capital": "Berlin"},
            {"name": "France", "population": 67000000, "capital": "Paris"},
            {"name": "Switzerland", "population": 8600000, "capital": "Bern"},
            {"name": "Austria", "population": 9000000, "capital": "Vienna"}
        ],
        "rivers": [
            {"name": "Danube", "length": 2850, "flows_through": ["Germany", "Austria"]},
            {"name": "Seine", "length": 777, "flows_through": ["France"]},
            {"name": "Rhine", "length": 1233, "flows_through": ["Switzerland", "Germany", "France"]}
        ]
    }