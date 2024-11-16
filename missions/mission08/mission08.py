import json
import logging
from requests import get
from os import getenv
from openai import OpenAI
from services.AIDevs3 import AIDevs3

class Mission08:

    name = "robotid"
    openai = OpenAI(api_key=getenv("OPENAI_API_KEY"))

    def run(self) -> None:
        logging.info("Mission 08 - robotid")
        
        robotid = json.loads(get(getenv("HEADQUARTERS_SYSTEM_URL") + "/data/" + getenv("API_KEY") + "/robotid.json").text)
        logging.info(f'Robot description: {robotid["description"]}')

        prompt = self.prepare_image_prompt(robotid["description"])
        image_url = self.generate_robot_visualisation(prompt)
        self.send_answer(image_url)

    def prepare_image_prompt(self, description: str) -> str:
        answer = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content":
                        "Jesteś profesjonalnym Prompt Inżynierem. Z dostarczonego przez użytkownika opisu przygotuj prompt, który będzie przekazany do modelu DALLE-3 w celu wygenerowania obrazu."
                        "Prompt musi odzwierciedlać wszystkie kluczowe elementy z opisu użytkownika."
                        "Możesz dodać od siebie polecenia, które poprawią jakość obrazu oraz pomogą modelowi na wygenerowanie obrazu zgodnie z oczekiwaniami użytkownika."
                },
                { "role": "user", "content": description }
            ],
        ).choices[0].message.content
        logging.info(f"Prompt is: {answer}")

        return answer

    def generate_robot_visualisation(self, prompt: str) -> str:
        image_url = self.openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        ).data[0].url
        logging.info(f"Robot visualisation: {image_url}")

        return image_url

    def send_answer(self, answer: str) -> None:
        aidevs = AIDevs3()
        result = aidevs.answer(
            getenv("HEADQUARTERS_SYSTEM_URL") + "/report",
            self.name,
            answer,
        )
        logging.info(result)
