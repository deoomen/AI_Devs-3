import logging
from os import getenv, listdir, path
from openai import OpenAI
from services.AIDevs3 import AIDevs3
from groq import Groq

class Mission06:

    name = "mp3"
    openai = OpenAI(api_key=getenv("OPENAI_API_KEY"))
    groq = Groq(api_key=getenv("GROQ_API_KEY"))

    def run(self) -> None:
        logging.info("Mission 06 - mp3")

        # self.process_recordings("missions/mission06/przesluchania")
        context = self.prepare_context("missions/mission06/przesluchania")
        deduction = self.deduce_the_answer(context)
        answer = self.get_street_from_deduction(deduction)
        self.send_answer(answer)

    def prepare_context(self, context_directory: str) -> str:
        context = "<recordings>"

        for filename in listdir(context_directory):
            if filename.endswith(".txt"):
                file_path = path.join(context_directory, filename)
                with open(file_path, "r") as transcription:
                    context += f"<recording>{path.splitext(filename)[0]}: {transcription.read().strip()}</recording>"

        context += "</recordings>"

        return context

    def transcribe(self, file_path: str) -> str|None:
        transcription = None

        with open(file_path, "rb") as file:
            transcription = self.groq.audio.transcriptions.create(
                file=(file_path, file.read()),
                model="whisper-large-v3",
                prompt="Specify context, be patient and make precise transcription",
                response_format="json",
                language="pl",
                temperature=0.0
            ).text

        return transcription

    def process_recordings(self, directory: str) -> None:
        for filename in listdir(directory):
            self.process_recording(directory, filename)

    def process_recording(self, directory: str, filename: str) -> None:
        if filename.endswith(".m4a"):
            file_path = path.join(directory, filename)
            logging.info(f"Processing file: {file_path}")
            transcription = self.transcribe(file_path)

            if transcription:
                txt_filename = f"missions/mission06/przesluchania/{path.splitext(filename)[0]}.txt"
                with open(txt_filename, "w", encoding="utf-8") as txt_file:
                    txt_file.write(transcription)
                logging.info(f"Transcription saved to: {txt_filename}")

    def deduce_the_answer(self, context: str) -> str:
        answer = self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content":
                        "Jesteś zawodowym detektywem z wieloletnim stażem. Twoja praca polega głównie na przesłuchwaniu świadków i wyciąganiu wniosków z przesłuchań."
                        "Musisz myśleć nieszablonowo i widzieć powiązania między zeznaniami różnych ludzi. Wyciągać wnioski z niewielkich poszlak."
                        "Zeznania przesłuchiwanych osób mogą być niespójne. Przesłuchiwani mogą też próbować kłamać lub zeznawać nie na temat."
                        "Musisz przemyśleć każde zeznanie osobno, a następnie podsumować całość krok po kroku tak aby wyciągnąć odpowiednie wniosku i móc odpowiedzieć na pytanie zadane przez użytkoniwka."
                        "Może, że będziesz też musiał sięgnąć do swojej własnej wiedzy i na podstawie poszlak z zeznań oraz swojej wiedzy skojarzyć fakty i dać odpowiedź na pytanie."
                        "Nie śpiesz się, przemyśl każdy swój krok dwa razy."
                        "Oto zeznania świadków: " + context
                },
                { "role": "user", "content": "Podaj proszę nazwę ulicy, na której znajduje się uczelnia (konkretny instytut!), gdzie wykłada profesor Andrzej Maj" }
            ],
        ).choices[0].message.content
        logging.info(f"Deduction is: {answer}")

        return answer

    def get_street_from_deduction(self, deduction: str) -> str:
        answer = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                { "role": "system", "content": "Z podawanej przez użytkownika wypowiedzi wyciągnij nazwę ulicy i zwróć tylko ją w odpowiedzi. Nie zwracaj niczego więcej." },
                { "role": "user", "content": deduction }
            ],
        ).choices[0].message.content
        logging.info(f"Answer is: {answer}")

        return answer

    def send_answer(self, answer: str) -> None:
        aidevs = AIDevs3()
        result = aidevs.answer(
            getenv("HEADQUARTERS_SYSTEM_URL") + "/report",
            self.name,
            answer,
        )
        logging.info(result)
