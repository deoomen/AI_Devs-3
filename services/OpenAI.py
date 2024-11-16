import logging
import base64
from os import getenv
from typing import Literal
from openai import OpenAI as LLM_OpenAI

class OpenAI:

    __openai = LLM_OpenAI(api_key=getenv("OPENAI_API_KEY"))

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

    def __encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def __transform_list_to_dict(self, images_path: list) -> list:
        return [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{self.__encode_image(image_path)}"
                },
            }
            for image_path in images_path
        ]

    def describe_image(
        self,
        model: Literal["gpt-4o", "gpt-4o-mini"],
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
                    "role": "user",
                    "content": [{ "type": "text", "text": user_message }] + self.__transform_list_to_dict(images_path),
                }
            ],
            temperature=temperature,
        ).choices[0].message.content
        logging.info(f"OpenAI image describe response: {content}")

        return content
