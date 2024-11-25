import logging
import re
import json
from pprint import pprint

from services.AIDevs3 import AIDevs3
from os import getenv, path
from requests import post
from services.OpenAI import OpenAI

class Mission14:
    __name = "loop"
    __people_api = getenv("HEADQUARTERS_SYSTEM_URL") + "/people"
    __places_api = getenv("HEADQUARTERS_SYSTEM_URL") + "/places"
    __aidevs = AIDevs3()

    async def run(self) -> None:
        report = {}
        openai = OpenAI()

        if not path.exists("missions/mission14/knowledge.json"):
            with open("missions/mission14/barbara.txt") as file:
                barbara_note = file.read().strip()

            with open("missions/mission14/knowledge.json", "w") as file:
                result = openai.complete(
                    "gpt-4o-mini",
                    (
                        "You task is to extract information about people, cities and relations about which person was in which city from given context from user."
                        "Response only with first names of people and cities as noun in JSON format as in examples below and nothing else."
                        "First name of person MUST contain only english letters. Do not use any special characters or local language letters."
                        "Be patient and rewrite name exactly like in context from user."
                        "<examples>"
                        "USER: U Adama Nowaka w jego kawalerce w Warszawie była impreza i przyjechała Zofia Kowalska z Rafałem Fajnym z Łodzi."
                        'ASSISTANT: {"peoples": ["ADAM", "RAFAL", "ZOFIA], "cities": ["WARSZAWA", "LODZ"], "relations": {"ADAM": ["WARSZAWA"]}, {"RAFAL": ["LODZ", "WARSZAWA"]}, {"ZOFIA": ["LODZ", "WARSZAWA"]}}'
                        "</examples>"
                    ),
                    barbara_note,
                    0.6,
                )
                knowledge = json.loads(result)
                knowledge["checked_cities"] = []
                knowledge["checked_peoples"] = []
                with open("missions/mission14/knowledge.json", "w") as file:
                    json.dump(knowledge, file)

        with open("missions/mission14/knowledge.json", "r") as file:
            knowledge = json.load(file)

        max_iterations = 20
        user_message = "Zdecyduj co robić"
        error_message = ""

        # add response as context knowledge
        # decide what to do
        # - call people
        # - call places
        # - return result
        # if call, do call
        for iteration in range(max_iterations):
            logging.info(f"Iteration: {iteration}")
            answer = openai.complete(
                "gpt-4o-mini",
                (
                    "<role>"
                    "Jesteś detektywem z ogromnym zmysłem kojarzenia faktów i dedukcji."
                    "</role>"
                    "<objective>"
                    "Twoim zadaniem jest odnaleźć informację, w którym mieście znajduje się osoba o imieniu Barbara."
                    "Wszystkie informacje, które posiadasz znajdują się z sekcji <context> i będą one aktualizowane z każdym kolejnym zapytaniem."
                    "Wykorzystaj swój zmysł dedukcji i pomysł krok po kroku co należy wykonać aby osiągnąć cel."
                    "Swoje przemyślenia możesz opisać w odpowiedzi w polu \"_thinking\"."
                    "Akcję jaką chcesz wykonać zapisz w polu \"a\"."
                    "Zapytanie jakie ma zostać wysłane do wybranego systemu zapisz w polu \"q\"."
                    "W polu \"checked_cities\" zapisane są miasta dużymi literami bez polskich znaków, które zostały już sprawdzone i nie ma potrzeby ich ponownego sprawdzania."
                    "W polu \"checked_peoples\" zapisane są osoby dużymi literami bez polskich znaków, które zostały już sprawdzone i nie ma potrzeby ich ponownego sprawdzania."
                    "Nazwy miast i imiona ludzi pisz ZAWSZE DUŻYMI LITERAMI I BEZ POLSKICH ZNAKÓW SPECJALNYCH."
                    "</objective>"
                    "<actions>"
                    "Do dyspozycji masz 3 akcje:"
                    "- akcja \"people\" - zwróci informację o miastach jakie odwiedziła osoba, o którą zapytasz"
                    "- akcja \"places\" - zwróci informację o osobach, które odwiedziły miasto, o które zapytasz"
                    "- akcja \"report\" - wyśle odpowiedź do systemu weryfikującego"
                    "</actions>"
                    "<response>"
                    "<examples>"
                    "<example_objective>"
                    "Znajdź miasto, w którym przebywa MATEUSZ"
                    "</example_objective>"
                    "<example>"
                    'CONTEXT: {"peoples": ["ADAM", "RAFAL", "ZOFIA", "MATEUSZ"], "cities": ["WARSZAWA", "LODZ"], "relations": {"ADAM": ["WARSZAWA"]}, {"RAFAL": ["LODZ", "WARSZAWA"]}, {"ZOFIA": ["LODZ", "WARSZAWA"]}, {"MATEUSZ": []}}, "checked_cities": [], "checked_peoples": []}'
                    "USER: Zdecyduj co robić"
                    'ASSISTANT: {"_thinking": "Wiem, że RAFAL i ZOFIA byli w mieście LODZ. Muszę sprawdzić kto jeszcze był w tym mieście", "a": "places", "q": "LODZ"}'
                    "</example>"
                    "<example>"
                    'CONTEXT: {"peoples": ["ADAM", "RAFAL", "ZOFIA], "cities": ["WARSZAWA", "LODZ"], "relations": {"ADAM": ["WARSZAWA"]}, {"RAFAL": ["LODZ", "WARSZAWA"]}, {"ZOFIA": ["LODZ", "WARSZAWA"]}, {"MATEUSZ": []}, {"ARTUR": ["LODZ"]}}, "checked_cities": ["LODZ"], "checked_peoples": []}'
                    "USER: Zdecyduj co robić"
                    'ASSISTANT: {"_thinking": "W mieście LODZ był ARTUR. Sprawdzę, gdzie jeszcze była ta osoba", "a": "people", "q": "ARTUR"}'
                    "</example>"
                    "<example>"
                    'CONTEXT: {"peoples": ["ADAM", "RAFAL", "ZOFIA], "cities": ["WARSZAWA", "LODZ", "GDANSK"], "relations": {"ADAM": ["WARSZAWA"]}, {"RAFAL": ["LODZ", "WARSZAWA"]}, {"ZOFIA": ["LODZ", "WARSZAWA"]}, {"MATEUSZ": []}, {"ARTUR": ["LODZ", "GDANSK"]}}, "checked_cities": ["LODZ"], "checked_peoples": ["ARTUR"]}'
                    "USER: Zdecyduj co robić"
                    'ASSISTANT: {"_thinking": "Pojawiło sie nowe miasto. Sprawdzę kto jeszcze znajduje się w mieście GDANSK", "a": "places", "q": "GDANSK"}'
                    "</example>"
                    "<example>"
                    'CONTEXT: {"peoples": ["ADAM", "RAFAL", "ZOFIA], "cities": ["WARSZAWA", "LODZ", "GDANSK"], "relations": {"ADAM": ["WARSZAWA"]}, {"RAFAL": ["LODZ", "WARSZAWA"]}, {"ZOFIA": ["LODZ", "WARSZAWA"]}, {"MATEUSZ": ["GDANSK"]}, {"ARTUR": ["LODZ", "GDANSK"]}}, "checked_cities": ["LODZ", "GDANSK"], "checked_peoples": ["ARTUR"]}'
                    "USER: Zdecyduj co robić"
                    'ASSISTANT: {"_thinking": "W mieście GDANSK był MATEUSZ. A więc to tego miasta szukamy!", "a": "report", "q": "GDANSK"}'
                    "</example>"
                    "</examples>"
                    "</response>"
                    "<context>"
                    f"{json.dumps(knowledge)}"
                    "</context>"
                ),
                error_message + user_message,
                0.7,
            )
            logging.info(f"Answer: {answer}")
            data = json.loads(answer)
            error_message = ""

            if "people" == data["a"]:
                # check person
                person = data["q"]
                logging.info(f"Checking person: {person}")
                person_cities = self.__call_people(data["q"])
                logging.info(f"Cities for {person}: {person_cities}")

                if -1 < person_cities.find("RESTRICTED DATA"):
                    person_cities = person_cities.strip("*").replace(" ", "_")

                # add new cities to checked person
                # add relation between checked person and all cities
                knowledge_cities = set(knowledge["cities"])
                knowledge_person_cities = set(knowledge["relations"][person])
                person_cities = '"' + person_cities.replace(" ", '","') + '"'
                person_cities = json.loads(f'[{person_cities}]')
                for new_city in person_cities:
                    knowledge_cities.add(new_city)
                    knowledge_person_cities.add(new_city)
                knowledge["cities"] = list(knowledge_cities)
                knowledge["relations"][person] = list(knowledge_person_cities)

                # add person to checked list
                checked_peoples = set(knowledge["checked_peoples"])
                checked_peoples.add(person)
                knowledge["checked_peoples"] = list(checked_peoples)
            elif "places" == data["a"]:
                # check city
                city = data["q"]
                logging.info(f"Checking city: {city}")
                city_peoples = self.__call_places(city)
                logging.info(f"Peoples in {city}: {city_peoples}")

                if -1 < city_peoples.find("RESTRICTED DATA"):
                    city_peoples = city_peoples.strip("*").replace(" ", "_")

                # add new peoples to checked city
                knowledge_peoples = set(knowledge["peoples"])
                knowledge_relations = knowledge["relations"]
                city_peoples = '"' + city_peoples.replace(" ", '","') + '"'
                city_peoples = json.loads(f'[{city_peoples}]')
                for new_person in city_peoples:
                    knowledge_peoples.add(new_person)

                    # add relation between checked city and all peoples in city
                    if new_person not in knowledge_relations:
                        knowledge["relations"][new_person] = [city]
                    else:
                        knowledge_relations_person = set(knowledge["relations"][new_person])
                        knowledge_relations_person.add(city)
                        knowledge["relations"][new_person] = list(knowledge_relations_person)

                # add city to checked list
                checked_cities = set(knowledge["checked_cities"])
                checked_cities.add(city)
                knowledge["checked_cities"] = list(checked_cities)
                knowledge["peoples"] = list(knowledge_peoples)
            elif "report" == data["a"]:
                result = self.__report(data["q"])
                if result.startswith("{"):
                    logging.info(f"Flag found: {result}")
                    exit(0)
                else:
                    error_message = f"Error: {result} "
            else:
                error_message = "W poprzedniej akcji wybrałeś niepoprawną akcję. Dostępne akcje to: people, places, report. "

            with open("missions/mission14/knowledge.json", "w") as file:
                json.dump(knowledge, file)

    def __call_people(self, query: str) -> str:
        return post(
            self.__people_api,
            json={
                "apikey": getenv("API_KEY"),
                "query": query,
            }
        ).json()["message"]

    def __call_places(self, query: str) -> str:
        return post(
            self.__places_api,
            json={
                "apikey": getenv("API_KEY"),
                "query": query,
            }
        ).json()["message"]

    def __report(self, report: str) -> str:
        return self.__aidevs.send_report_to_headquarter(self.__name, report)
