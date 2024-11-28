import logging
import json
import random
from os import path, getenv
from services.AIDevs3 import AIDevs3
from services.OpenAI import OpenAI

class Mission17:
    __name = "research"
    __system_message = "Classify the numbers"
    __user_message = "Numbers: "
    __validation_percent: float = 0.15

    async def run(self) -> None:
        if not path.exists("missions/mission17/training.jsonl"):
            self.__prepare_training_data()

        report = []
        verify_data = []

        with open("missions/mission17/verify.txt", "r") as file:
            for line in file:
                record = line.strip().split("=")
                verify_data.append({"id": record[0], "data": record[1]})

        openai = OpenAI()
        for verify_record in verify_data:
            answer = openai.complete(
                "custom",
                self.__system_message,
                f"{self.__user_message}{verify_record['data']}",
                0.000001,
                getenv("OPENAI_CUSTOM_MODEL"),
            )

            if "INCORRECT" == answer:
                continue
            elif "CORRECT" == answer:
                report.append(verify_record["id"])
            else:
                logging.error(f"Incorrect model answer: {answer}")

        if 0 == len(report):
            raise ValueError("Empty report")

        aidevs = AIDevs3()
        aidevs.send_report_to_headquarter(self.__name, report)

    def __prepare_training_data(self):
        incorrect = []
        correct = []

        with open("missions/mission17/incorrect.txt", "r") as file:
            for line in file:
                incorrect.append(
                    {
                        "messages": [
                            {
                                "role": "system",
                                "content": self.__system_message
                            },
                            {
                                "role": "user",
                                "content": f"{self.__user_message}{line}".strip()
                            },
                            {
                                "role": "assistant",
                                "content": "INCORRECT"
                            }
                        ]
                    }
                )

        with open("missions/mission17/correct.txt", "r") as file:
            for line in file:
                correct.append(
                    {
                        "messages": [
                            {
                                "role": "system",
                                "content": self.__system_message
                            },
                            {
                                "role": "user",
                                "content": f"{self.__user_message}{line}".strip()
                            },
                            {
                                "role": "assistant",
                                "content": "CORRECT"
                            }
                        ]
                    }
                )

        validation_data = []

        incorrect_total = len(incorrect)
        incorrect_data_count = int(round(incorrect_total * self.__validation_percent, 0))
        for _ in range(incorrect_data_count):
            index = random.randrange(incorrect_total)
            validation_data.append(incorrect.pop(index))
            incorrect_total -= 1

        correct_total = len(correct)
        correct_data_count = int(round(correct_total * self.__validation_percent, 0))
        for _ in range(correct_data_count):
            index = random.randrange(correct_total)
            validation_data.append(correct.pop(index))
            correct_total -= 1

        training_data = incorrect + correct
        with open("missions/mission17/training.jsonl", "w") as file:
            for training_record in training_data:
                file.write(json.dumps(training_record) + "\n")

        with open("missions/mission17/validating.jsonl", "w") as file:
            for validation_record in validation_data:
                file.write(json.dumps(validation_record) + "\n")
