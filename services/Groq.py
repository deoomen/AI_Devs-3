import logging
from os import getenv
from typing import Literal
from groq import Groq as LLM_Groq
from requests import get
import io

class Groq:

    __groq = LLM_Groq(api_key=getenv("GROQ_API_KEY"))

    def transcribe(
        self,
        model: Literal["whisper-large-v3"],
        prompt: str,
        language: str,
        file_path: str,
        temperature: float = 1.0,
   ) -> str|None:
        logging.info("Calling Groq audio transcriptions")
        logging.debug("Arguments", model, prompt, language, file_path, temperature)
        transcription = None

        if file_path.startswith("http"):
            file_buffer = io.BytesIO(get(file_path).content)
            file_buffer.name = file_path.split("/")[-1]
            transcription = self.__groq.audio.transcriptions.create(
                file=file_buffer,
                model=model,
                prompt=prompt,
                response_format="json",
                language=language,
                temperature=temperature,
            ).text
        else:
            with open(file_path, "rb") as file:
                transcription = self.__groq.audio.transcriptions.create(
                    file=(file_path, file.read()),
                    model=model,
                    prompt=prompt,
                    response_format="json",
                    language=language,
                    temperature=temperature,
                ).text

        logging.info(f"Groq audio transcriptions response: {transcription}")

        return transcription
