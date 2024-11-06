from services.AIDevs3 import AIDevs3
from requests import get
from os import getenv

class Mission00:

    name = "POLIGON"

    def run(self) -> None:
        print("Mission 00 - POLIGON")

        aidevs = AIDevs3()

        with get(getenv("POLIGON_API_URL") + "/dane.txt") as response:
            result = aidevs.answer(self.name, response.text.strip().split('\n'))
            print(result)