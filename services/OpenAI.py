import logging
import base64
from os import getenv
from pprint import pprint
from typing import Literal
from openai import OpenAI as LLM_OpenAI
from requests import get
from typing import Self
import io

class OpenAI:
    __openai = LLM_OpenAI(api_key=getenv("OPENAI_API_KEY"))
    __chat = {
        "model": "",
        "temperature": 1.0,
        "messages": [],
    }

    def complete(
        self,
        model: Literal["gpt-4o", "gpt-4o-mini"],
        system_message: str,
        user_message: str,
        temperature: float = 1.0,
    ) -> str:
        logging.info("Calling OpenAI chat completions")
        logging.debug("Arguments", model, system_message, user_message, temperature)
        content = self.__openai.chat.completions.create(
            model=model,
            messages=[
                { "role": "system", "content": system_message },
                { "role": "user", "content": user_message }
            ],
            temperature=temperature,
        ).choices[0].message.content
        logging.info(f"OpenAI chat completions response: {content}")

        return content

    def reset_chat(self) -> Self:
        self.__chat = {
            "model": "",
            "temperature": 1.0,
            "messages": [],
        }
        return self

    def set_chat_model(self, model: Literal["gpt-4o", "gpt-4o-mini"]) -> Self:
        self.__chat["model"] = model
        return self

    def set_chat_system_message(self, system_message: str) -> Self:
        self.__chat["messages"].append({"role": "system", "content": system_message})
        return self

    def chat(self, user_message: str) -> str:
        self.__chat["messages"].append({"role": "user", "content": user_message})
        content = self.__openai.chat.completions.create(
            model=self.__chat["model"],
            messages=self.__chat["messages"],
            temperature=self.__chat["temperature"],
        ).choices[0].message.content
        self.__chat["messages"].append({"role": "assistant", "content": content})

        return content

    def __encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def __transform_list_to_dict(self, images_path: list[str]) -> list:
        return [
            {
                "type": "image_url",
                "image_url": {
                    "url": image_path if image_path.startswith("http") else f"data:image/jpeg;base64,{self.__encode_image(image_path)}"
                },
            }
            for image_path in images_path
        ]

    def describe_image(
        self,
        model: Literal["gpt-4o", "gpt-4o-mini"],
        system_message: str,
        user_message: str,
        images_path: list,
        temperature: float = 1.0,
    ) -> str:
        logging.info("Calling OpenAI image describe")
        logging.debug("Arguments", model, user_message, images_path, temperature)
        content = self.__openai.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_message,
                },
                {
                    "role": "user",
                    "content": [{ "type": "text", "text": user_message }] + self.__transform_list_to_dict(images_path),
                }
            ],
            temperature=temperature,
        ).choices[0].message.content
        logging.info(f"OpenAI image describe response: {content}")

        return content

    def transcribe(
        self,
        file_path: str,
        prompt: str,
        language: str,
        model: Literal["whisper-1"] = "whisper-1",
        temperature: float = 1.0,
    ) -> str:
        logging.info("Processing audio file")

        if file_path.startswith("http"):
            file_buffer = io.BytesIO(get(file_path).content)
            file_buffer.name = file_path.split("/")[-1]

            transcription = self.__openai.audio.transcriptions.create(
                file=file_buffer,
                model=model,
                prompt=prompt,
                response_format="json",
                language=language,
                temperature=temperature,
            ).text

        logging.info(f"Audio transcriptions response: {transcription}")

        return transcription

    def createEmbedding(
        self,
        model: Literal["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"],
        input: str,
        dimensions: int,
    ) -> list[float]:
        logging.info(f"Calling OpenAI embeddings. Model: {model} with {dimensions} dimensions.")

        response = self.__openai.embeddings.create(
            model=model,
            input=input,
            dimensions=dimensions,
        )

        return response.data[0].embedding
