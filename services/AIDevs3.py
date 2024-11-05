import logging
import os
import requests

class WrongAnswerError(Exception):
    def __init__(self, code: int, msg: str) -> None:
        self.code = code
        self.msg = msg
        super().__init__(self.msg)

class AIDevs3:

    headers = {
        'Content-Type': 'application/json',
    }
    api_key = os.getenv('API_KEY')
    api_url = os.getenv('API_URL')

    def parse_response(self, response: requests.Response) -> dict:
        if response.status_code == 406:
            json = response.json()
            raise WrongAnswerError(json['code'], json['message'])
        elif response.status_code != 200:
            raise RuntimeError('Unexpected HTTP status code: {}; Content: {}'.format(response.status_code, response.text))

        json = response.json()

        if json['code'] != 0:
            raise RuntimeError('Something went wrong :( Content: %s', json)

        return json

    def answer(self, mission_name: str, answer) -> str:
        response = requests.post(
            self.api_url + '/verify',
            headers = self.headers,
            json = {
                'task': mission_name,
                'apikey': self.api_key,
                'answer': answer,
            }
        )
        logging.info('Answer sent: {}'.format(answer))
        json = self.parse_response(response)

        logging.info(json['message'])

        return json['message']
