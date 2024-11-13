import logging
import base64
from os import getenv
from openai import OpenAI

class Mission07:

    name = '07'
    openai = OpenAI(api_key=getenv("OPENAI_API_KEY"))

    def run(self) -> None:
        logging.info('Mission 07')
        maps_directory = "missions/mission07"
        city = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text":
                                "The picture shows a fragment of a map of some city in Poland. Try to figure out which city it is."
                                "Three of them feature the same city. One section of the map contains a different city."
                                "Take a closer look on streets and other points of interests. Think step by step, each map fragment what the city can be."
                                "You propably need to use your knowledge to search the name of streets and others points from maps to search the city name."
                                "This is what we know:"
                                "- One of streets have a typo."
                                "- In the city there are granaries and forts."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url":  f"data:image/jpeg;base64,{self.encode_image(maps_directory + "/map1.png")}"
                            },
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url":  f"data:image/jpeg;base64,{self.encode_image(maps_directory + "/map2.png")}"
                            },
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url":  f"data:image/jpeg;base64,{self.encode_image(maps_directory + "/map3.png")}"
                            },
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url":  f"data:image/jpeg;base64,{self.encode_image(maps_directory + "/map4.png")}"
                            },
                        },
                    ],
                }
            ],
        ).choices[0].message.content

        logging.info(f"The city is: {city}")

    def encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
