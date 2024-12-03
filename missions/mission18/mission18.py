import logging
import json
from os import path, getenv
from requests import get
from services.AIDevs3 import AIDevs3
from services.OpenAI import OpenAI
from tools.AnswerWebCrawler import AnswerWebCrawler
from tools.FileMemory import FileMemory

class Mission18:
    __name = "softo"
    __crawler = None
    __openai = OpenAI()

    async def run(self) -> None:
        if path.exists("missions/mission18/softo.json"):
            with open("missions/mission18/softo.json", "r") as file:
                questions = json.load(file)
        else:
            with open("missions/mission18/softo.json", "w") as file:
                questions = get(getenv("HEADQUARTERS_SYSTEM_URL") + "/data/" + getenv("API_KEY") + "/softo.json").json()
                json.dump(questions, file)

        memory = FileMemory().set_memory_path("missions/mission18/memory/")
        self.__crawler = AnswerWebCrawler(memory, self.__openai)
        self.__crawler.set_start_webpage(getenv("SOFTOAI_URL")).set_page_scrap_threshold(10)
        answers = {}
        for question_number in questions:
            question = questions[question_number]
            answer = await self.__crawler.seek_answer(question)
            logging.info(f"Answer: {answer}")
            answers[question_number] = answer

        aidevs = AIDevs3()
        aidevs.send_report_to_headquarter(self.__name, answers)
