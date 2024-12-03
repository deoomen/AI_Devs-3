import json
from typing import Self
from os import path

class FileMemory:
    __memory_path: str
    __memory_file_ext: str = ".json"

    def set_memory_path(self, memory_path: str) -> Self:
        self.__memory_path = memory_path

        return self

    def has_key_in_memory(self, key: str) -> bool:
        return path.exists(self.__memory_path + key + self.__memory_file_ext)

    def recall(self, key: str) -> str:
        fullpath = self.__memory_path + key + self.__memory_file_ext
        with open(fullpath, "r") as file:
            return json.load(file)["content"]

    def remember(self, key: str, value: str) -> None:
        fullpath = self.__memory_path + key + self.__memory_file_ext
        with open(fullpath, "w") as file:
            memory_json = {
                "key": key,
                "fullpath": fullpath,
                "content": value,
            }
            json.dump(memory_json, file)
