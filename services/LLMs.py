import logging
from typing import Literal
from services.Groq import Groq
from services.OpenAI import OpenAI

class ImageDescription:
    paths: list[str]
    caption: str|None
    context: str
    description: str|None = None

    def __init__(self, paths: list[str], caption: str|None, context: str):
        self.paths = paths
        self.caption = caption
        self.context = context

class LLMs:

    __llm = {
        "groq": Groq(),
        "openai": OpenAI(),
    }

    def completeOpenAI(
        self,
        model: Literal["gpt-4o", "gpt-4o-mini"],
        system_message: str,
        user_message: str,
        temperature: float = 1.0,
    ) -> str:
        logging.info("Calling OpenAI chat completions")
        logging.debug("Arguments", model, system_message, user_message, temperature)
        content = self.__llm["openai"].complete(
            model,
            system_message,
            user_message,
            temperature,
        )
        logging.info(f"OpenAI chat completions response: {content}")

        return content

    def describe_image(
        self,
        file_paths: list[str],
        system_message: str,
        user_message: str,
        model: Literal["gpt-4o", "gpt-4o-mini"] = "gpt-4o-mini",
        temperature: float = 1.0,
    ) -> str:
        logging.info("Processing image file")

        description = self.__llm["openai"].describe_image(
            model,
            system_message,
            user_message,
            file_paths,
            temperature,
        )

        logging.info(f"Image description is: {description}")

        return description

    def transcribeByGroq(
        self,
        file_path: str,
        prompt: str,
        language: str,
        model: Literal["whisper-large-v3"] = "whisper-large-v3",
        temperature: float = 1.0,
    ) -> str|None:
        logging.info("Processing audio file")
        # logging.debug("Arguments", model, prompt, language, file_path, temperature)

        transcription = self.__llm["groq"].transcribe(
            model,
            prompt,
            language,
            file_path,
            temperature,
        )

        logging.info(f"Groq audio transcriptions response: {transcription}")

        return transcription

    def transcribeByOpenAI(
        self,
        file_path: str,
        prompt: str,
        language: str,
        model: Literal["whisper-1"] = "whisper-1",
        temperature: float = 1.0,
    ) -> str:
        logging.info("Processing audio file")
        # logging.debug("Arguments", model, prompt, language, file_path, temperature)

        transcription = self.__llm["openai"].transcribe(
            file_path,
            prompt,
            language,
            model,
            temperature,
        )

        logging.info(f"Audio transcriptions response: {transcription}")

        return transcription

    def createEmbedding(
        self,
        model: Literal["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"],
        input: str,
        dimensions: int,
    ) -> list[float]:
        return self.__llm["openai"].createEmbedding(model, input, dimensions)
