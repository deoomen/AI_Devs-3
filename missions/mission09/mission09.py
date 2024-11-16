import logging
from os import getenv, listdir, path
from services.AIDevs3 import AIDevs3
from services.Groq import Groq
from services.OpenAI import OpenAI

class Mission09:

    __name = "kategorie"
    __llm = {
        "groq": Groq(),
        "openai": OpenAI(),
    }
    __report_analysis_prompt = (
        "Twoim zadaniem jest analiza raportów, które przekaże Ci użytkownik."
        "Musisz ocenić jego zawartość pod kątem występowania informacji na temat ludzi, którzy zostali schwytani i są gdzieś przetrzymywani"
        "lub o wszelkich naprawionych usterkach technicznych i hardwarowych."
        "Informacja o błędzie lub usterce musi zawierać konkretną informację o problemie."
        "Nie interesują nas informacje o aktualizacjach systemu."
        "Przeanalizuj dokładnie całą treść, pomyśl spokojnie jaki jest kontekst raportu i czy zawiera on kluczowe informacje."
        "ZASADY:"
        "- Jeśli raport zawiera informacje na temat schwytanych ludzi - odpowiedz słowem \"people\" i nic więcej."
        "- Jeśli raport zawiera informacje o usterkach, błędach technicznych, hardwarowych - odpowiedz słowem \"hardware\" i nic więcej."
        "- Jeśli raport nie zawiera żadnych kluczowych informacji - odpowiedz słowym \"unknown\" i nic więcej."
    )

    def run(self) -> None:
        logging.info("Mission 09 - kategorie")
        report = self.process_files("missions/pliki_z_fabryki")
        logging.info(f"Report is: {report}")
        self.send_answer(report)

    def process_files(self, directory: str) -> dir:
        hardware = []
        people = []

        for filename in listdir(directory):
            type = self.process_file(directory, filename)

            if "hardware" == type:
                hardware.append(filename)
            elif "people" == type:
                people.append(filename)

        return {
            "hardware": hardware,
            "people": people,
        }

    def process_file(self, directory: str, filename: str) -> str:
        logging.info(f"Processing {filename}")
        file_path = path.join(directory, filename)
        type = "unknown"

        if filename.endswith(".txt"):
            type = self.process_text_file(file_path)
        elif filename.endswith(".png"):
            type = self.process_image_file(file_path)
        elif filename.endswith(".mp3"):
            type = self.process_audio_file(file_path)

        return type

    def process_text_file(self, file_path: str) -> str:
        logging.info(f"Processing text file: {file_path}")
        type = "unknown"

        with open(file_path, "r") as file:
            type = self.__llm["openai"].complete(
                "gpt-4o-mini",
                self.__report_analysis_prompt,
                file.read(),
                0.7,
            )

        logging.info(f"Text report type is: {type}")

        return type

    def process_image_file(self, file_path: str) -> str:
        logging.info(f"Processing image file: {file_path}")

        type = self.__llm["openai"].describe_image(
            "gpt-4o-mini",
            self.__report_analysis_prompt,
            [file_path],
            0.7,
        )

        logging.info(f"Image report type is: {type}")

        return type

    def process_audio_file(self, file_path: str) -> str:
        logging.info(f"Processing audio file: {file_path}")
        type = "unknown"

        transcription = self.__llm["groq"].transcribe(
            "whisper-large-v3",
            "Specify context, be patient and make precise transcription",
            "en",
            file_path,
        )
        type = self.__llm["openai"].complete(
            "gpt-4o-mini",
            self.__report_analysis_prompt,
            transcription,
            0.7,
        )

        logging.info(f"Audio report type is: {type}")

        return type

    def send_answer(self, answer: dict) -> None:
        aidevs = AIDevs3()
        result = aidevs.answer(
            getenv("HEADQUARTERS_SYSTEM_URL") + "/report",
            self.__name,
            answer,
        )
        logging.info(result)
