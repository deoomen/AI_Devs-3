import logging
import re
import json
from services.AIDevs3 import AIDevs3
from os import getenv
from requests import post
from services.OpenAI import OpenAI

class Mission13:
    __name = "database"
    __banan_api = getenv("HEADQUARTERS_SYSTEM_URL") + "/apidb"

    async def run(self) -> None:
        report = {}

        system_message = (
            "<role>Jesteś ekspertem SQL.</role>"
            "<objective>"
            "Twoim zadaniem jest przygotowanie zapytania SQL które pozowli zwrócić odpowiedź na pytanie:"
            "Które aktywne datacenter (DC_ID) są zarządzane przez pracowników, którzy są na urlopie (is_active=0)?"
            "Musisz przygotować zapytania w języku SQL, które będą następnie wykonane na serwerze."
            "Dostaniesz odpowiedź w formacie JSON z rezultatem zapytania."
            "Jeśli wykonasz niepoprawną operację zostanie zwrócony błąd. Zapoznaj się z nim i pomyśl co musisz zmienić w zapytaniu."
            "W każdej wiadomości możesz przygotować tylko jedną operację SQL."
            "Nie znamy dokładnej struktury bazy danych. Rozpocznij analizę od zapoznania się jakie tabele istnieją w systemie."
            "Przemyśl dokładnie krok po kroku zadanie oraz orpowiedź jaką uzyskasz, następnie wypisz zapytanie SQL dokładnie pomiędzy tagami <SQL></SQL>."
            "Oto lista operacji jakie są dostępne i z jakich możesz korzystać: SELECT, SHOW TABLES, DESC TABLE, SHOW CREATE TABLE."
            "Jeśli znajdziesz rozwiązanie zadania zwróć w formacie JSON tylko ID czynnych datacenter."
            "</objective>"
            "<rules>"
            "- Możesz korzystać tylko z operacji: SELECT, SHOW TABLES, DESC TABLE, SHOW CREATE TABLE"
            "- Tylko jedno polecenie SQL w odpowiedzi"
            "- Twoje polecenie SQL MUSI być wypisane pomiędzy tagami <SQL></SQL>"
            "</rules>"
            "<examples>"
            "<work_example>"
            "Przykład Twojej odpowiedzi w czasie pracy:"
            "Muszę poznać jakie są tabele w systemie."
            "<SQL>"
            "SHOW TABLES"
            "</SQL>"
            "</work_example>"
            "<done_example>"
            "Przykład Twojej odpowiedzi jeśli znajdziesz rozwiązanie zadania:"
            "[1,2,3,4]"
            "</done_example>"
            "</examples>"
        )
        openai = OpenAI()
        openai.reset_chat().set_chat_model("gpt-4o").set_chat_system_message(system_message)
        max_iterations = 10

        result = "Przygotuj pierwsze zapytanie SQL. Zacznij od rozpoznania jakie tabele istnieją w systemie."
        # banan call
        # sql result as user msg to llm
        # llm answer with sql
        for iteration in range(max_iterations):
            logging.info(f"Iteration: {iteration}")
            logging.info(f"User message: {result}")
            answer = openai.chat(result)
            logging.info(f"Answer: {answer}")
            matches = re.findall(r"<SQL>(.*?)</SQL>", answer, re.DOTALL)
            if 0 == len(matches):
                report = json.loads(answer)
                break
            sql = matches[0].strip()
            logging.info(f"SQL: {sql}")
            result = self.__call_banan(sql)

        aidevs = AIDevs3()
        aidevs.send_report_to_headquarter(self.__name, report)

    def __call_banan(self, query: str) -> str:
        return str(post(
            self.__banan_api,
            json={
                "task": self.__name,
                "apikey": getenv("API_KEY"),
                "query": query
            }
        ).content)
