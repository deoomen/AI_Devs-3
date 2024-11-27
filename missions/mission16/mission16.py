import logging
import re
import json
from services.AIDevs3 import AIDevs3
from services.OpenAI import OpenAI

class Mission16:
    __name = "photos"
    __aidevs = AIDevs3()
    __openai = OpenAI()

    async def run(self) -> None:
        welcome_message = self.__aidevs.send_report_to_headquarter(self.__name, "START")
        image_base_url = re.findall(r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)|www\.[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)", welcome_message)[0].strip(".")
        images_filename = self.__find_images(welcome_message)
        max_iterations = 10
        descriptions = []

        for image_filename in images_filename:
            for iteration in range(max_iterations):
                logging.info(f"Interation [{iteration}] with [{image_filename}]")

                # decide what to do first
                decision = json.loads(
                    self.__openai.describe_image(
                        "gpt-4o-mini",
                        (
                            "You are an image verification system. Your task is to decide if the image looks good, is clear and can be described what contains or not."
                            "Use your perfect eyes and loook closly to the image."
                            'If image looks good yous should return "action" as "DESCRIBE". You must be sure that the image does not have any glitches.'
                            'When image is not ok you must clarify what wrong with image.'
                            '- If image is too dark - the "action" should be "BRIGHTEN".'
                            '- If image is too bright - the "action" should be "DARKEN".'
                            '- If on image are some glitches and is totally unreadable, "action" should be "REPAIR".'
                            "Answer in JSON format like this:"
                            '{"_thinking": "<your thoughts about image>", "action": "DESCRIBE or BRIGHTEN or DARKEN or REPAIR"}'
                        ),
                        "What to do with this image?",
                        [image_base_url + image_filename],
                    )
                )

                if "REPAIR" == decision["action"]:
                    answer = self.__repair(image_filename)
                elif "DARKEN" == decision["action"]:
                    answer = self.__darken(image_filename)
                elif "BRIGHTEN" == decision["action"]:
                    answer = self.__brighten(image_filename)
                elif "DESCRIBE" == decision["action"]:
                    descriptions.append(self.__describe(image_base_url + image_filename))
                    break
                else:
                    logging.error(f"Incorrect action: {decision['action']}")
                    break

                new_images = self.__find_images(answer)
                if 0 == len(new_images):
                    logging.error("No images found")
                    break

                image_filename = new_images[0]

        description = self.__summarize(descriptions)
        self.__report(description)

    def __find_images(self, message: str) -> list[str]:
        return re.findall(r"(\w+\.PNG)", message)

    def __repair(self, image: str) -> str:
        return self.__aidevs.send_report_to_headquarter(self.__name, f"REPAIR {image}")

    def __darken(self, image: str) -> str:
        return self.__aidevs.send_report_to_headquarter(self.__name, f"DARKEN {image}")

    def __brighten(self, image: str) -> str:
        return self.__aidevs.send_report_to_headquarter(self.__name, f"BRIGHTEN {image}")

    def __describe(self, image_url: str) -> str:
        return self.__openai.describe_image(
            "gpt-4o-mini",
            (
                "You are a professional system for preparing a description of person on the image."
                "Pay attention to details. Focus your description on the person and ignore background."
                "Be precise."
                "Prepare ana accurate description in few sentences."
            ),
            "Prepare a professional description of person you see on image.",
            [image_url],
        )

    def __summarize(self, descriptions: list[str]) -> str:
        return self.__openai.complete(
            "gpt-4o-mini",
            (
                "Your task is to summarize all given descriptions of the person and prepare single, unified description of the same person."
                "Include all elements of the description that are repeated."
                "The unified description must reflect the other descriptions."
                "Pay attention on any details of the person in descriptions."
                "Include also all elements that can help to recognize person in the future like any special signs, details, accessories."
                "You MUST answer in POLISH language."
            ),
            "Prepare an unified description of the person from this: \n" + "\n\n".join(descriptions),
        )

    def __report(self, report: str) -> None:
        self.__aidevs.send_report_to_headquarter(self.__name, report)
