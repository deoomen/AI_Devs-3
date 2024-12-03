from os import getenv

from services.AIDevs3 import AIDevs3

class Mission19:
    __name = 'webhook'

    async def run(self) -> None:
        aidevs = AIDevs3()
        aidevs.send_report_to_headquarter(self.__name, getenv("S04E04_API_URL") + "/webhook")
