from services.AIDevs3 import AIDevs3
from requests import get
from os import getenv

class Mission00:

    name = "POLIGON"

    def run(self) -> None:
        print("Mission 00 - POLIGON")

        aidevs = AIDevs3()
        api_url = getenv("POLIGON_API_URL")

        with get(api_url + "/dane.txt") as response:
            result = aidevs.answer(api_url + '/verify', self.name, response.text.strip().split("\n"))
            print(result)
