import json
from services.AIDevs3 import AIDevs3
from os import getenv, path
from requests import post
from neo4j import GraphDatabase

class Mission15:
    __name = "connections"
    __banan_api = getenv("HEADQUARTERS_SYSTEM_URL") + "/apidb"

    async def run(self) -> None:
        report = []

        if not path.exists("missions/mission15/connections.json"):
            connections = self.__call_banan("SELECT * FROM connections")
            with open("missions/mission15/connections.json", "w") as file:
                json.dump(connections, file)
        else:
            with open("missions/mission15/connections.json", "r") as file:
                connections = json.load(file)

        if not path.exists("missions/mission15/users.json"):
            users = self.__call_banan("SELECT * FROM users")
            with open("missions/mission15/users.json", "w") as file:
                json.dump(users, file)
        else:
            with open("missions/mission15/users.json", "r") as file:
                users = json.load(file)

        driver = GraphDatabase.driver(getenv("NEO4J_URL"), auth=(getenv("NEO4J_USER"), getenv("NEO4J_PASSWORD")))
        with driver.session() as session:
            for user in users:
                session.execute_write(self._create_user, user)

            for connection in connections:
                session.execute_write(self._create_relationship, connection["user1_id"], connection["user2_id"])

            result = session.execute_read(self._shortest_path)
            for record in result:
                if isinstance(record, dict):
                    report.append(record["name"])

        driver.close()

        aidevs = AIDevs3()
        aidevs.send_report_to_headquarter(self.__name, ", ".join(report))

    @staticmethod
    def _create_user(tx, user: dict):
        tx.run("MERGE (u:User {id: $id}) SET u.name = $name", id=user["id"], name=user["username"])

    @staticmethod
    def _create_relationship(tx, user1_id, user2_id):
        tx.run("""
            MATCH (a:User {id: $user1_id}), (b:User {id: $user2_id})
            CREATE (a)-[r:CONNECT]->(b)
            RETURN type(r)
        """, user1_id=user1_id, user2_id=user2_id)

    @staticmethod
    def _shortest_path(tx):
        result =  tx.run("""
            MATCH p = shortestPath((start:User {name: 'Rafał'})-[:CONNECT*]-(end:User {name: 'Barbara'}))
            RETURN p
        """)
        return [record.data() for record in result][0]["p"]

    def __call_banan(self, query: str) -> dict:
        return post(
            self.__banan_api,
            json={
                "task": self.__name,
                "apikey": getenv("API_KEY"),
                "query": query,
            }
        ).json()["reply"]
