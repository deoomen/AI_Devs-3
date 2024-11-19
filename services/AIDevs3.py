import logging
import os
import requests

class WrongAnswerError(Exception):
    def __init__(self, code: int, msg: str) -> None:
        self.code = code
        self.msg = msg
        super().__init__(self.msg)

class AIDevs3:

    def parse_response(self, response: requests.Response) -> dict:
        if response.status_code == 406:
            json = response.json()
            raise WrongAnswerError(json['code'], json['message'])
        elif response.status_code != 200:
            raise RuntimeError('Unexpected HTTP status code: {}; Content: {}'.format(response.status_code, response.text))
        logging.debug(response.text)
        json = response.json()

        if json['code'] != 0:
            raise RuntimeError('Something went wrong :( Content: %s', json)

        return json

    def answer(self, api_url: str, mission_name: str, answer) -> str:
        response = requests.post(
            api_url,
            headers = {
                'Content-Type': 'application/json',
            },
            json = {
                'task': mission_name,
                'apikey': os.getenv('API_KEY'),
                'answer': answer,
            }
        )
        logging.info('Answer sent: {}'.format(answer))
        json = self.parse_response(response)

        logging.info(json['message'])

        return json['message']

    def send_report_to_headquarter(self, mission_name: str, report) -> None:
        self.answer(
            os.getenv("HEADQUARTERS_SYSTEM_URL") + "/report",
            mission_name,
            report,
        )
