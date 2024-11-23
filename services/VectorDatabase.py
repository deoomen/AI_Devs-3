from os import getenv
from typing import Self
from qdrant_client import QdrantClient
from qdrant_client.http.models import ScoredPoint
from qdrant_client.models import VectorParams, Distance, PointStruct
from uuid import UUID, uuid4

class Point:
    id: UUID|None
    vector: list[float]
    metadata: dict

    def __init__(self, id: UUID|None, vector: list[float], metadata: dict) -> None:
        self.id = uuid4() if id is None else id
        self.vector = vector
        self.metadata = metadata

class VectorDatabase:
    __qdrant = None
    __collection_name = None
    __vector_size = 1024

    def __init__(self) -> None:
        self.__qdrant = QdrantClient(host=getenv("QDRANT_HOST"), port=getenv("QDRANT_PORT"))

    def set_collection_name(self, collection_name: str) -> Self:
        self.__collection_name = collection_name
        return self

    def set_vector_size(self, vector_size: int) -> Self:
        self.__vector_size = vector_size
        return self

    def create_collection_if_not_exist(self) -> Self:
        if not self.__qdrant.collection_exists(self.__collection_name):
            if not self.__qdrant.create_collection(
                collection_name=self.__collection_name,
                vectors_config=VectorParams(size=self.__vector_size, distance=Distance.COSINE),
            ):
                raise RuntimeError("Qdrant collection creating failed")

        return self

    def add_points(
        self,
        points: list[Point],
    ) -> None:
        self.__qdrant.upsert(
            self.__collection_name,
            [
                PointStruct(
                    id=str(point.id),
                    vector=point.vector,
                    payload=point.metadata
                )
                for point in points
            ]
        )

    def is_collection_empty(self) -> bool:
        return 0 == self.__qdrant.get_collection(self.__collection_name).points_count

    def search(
        self,
        query_vector: list[float],
        limit: int = 5,
    ) -> list[ScoredPoint]:
        return self.__qdrant.search(
            collection_name=self.__collection_name,
            query_vector=query_vector,
            limit=limit,
        )
