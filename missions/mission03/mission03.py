import logging
from os import getenv
from requests import get, post
from openai import OpenAI
from pprint import pprint
import json

from services.AIDevs3 import AIDevs3


class Mission03:

    name = 'JSON'
    llm = OpenAI(api_key=getenv('OPENAI_API_KEY'))

    def run(self) -> None:
        logging.info('Mission 03 - JSON')
        calibration_data = None

        with open('missions/mission03/calibration.json', 'r') as file:
            calibration_data = json.load(file)

        if None is calibration_data:
            raise ValueError('Data not found')

        calibration_data = self.fix_calibration_data(calibration_data)
        self.send_fixed_calibration_data(calibration_data)

    def fix_calibration_data(self, calibration_data: dict) -> dict:
        calibration_data['apikey'] = getenv('API_KEY')

        for index, test_data in enumerate(calibration_data['test-data']):
            operation = test_data['question'].split(' ')
            calibration_data['test-data'][index]['answer'] = self.calculate_operation(int(operation[0]), int(operation[2]), operation[1])

            if 'test' in test_data:
                calibration_data['test-data'][index]['test']['a'] = self.get_answer_to_question(test_data['test']['q'])

        return calibration_data

    def calculate_operation(self, left_number: int, right_number: int, operation: str) -> int:
        if '+' == operation:
            return left_number + right_number
        elif '-' == operation:
            return  left_number - right_number

    def get_answer_to_question(self, question: str) -> str:
        logging.info(f'Question is: {question}')
        answer = self.llm.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                { 'role': 'system', 'content': 'You are helpful assistant that will answer on user questions. Use very short answer. Use only english language.'},
                { 'role': 'user', 'content': question }
            ],
        ).choices[0].message.content
        logging.info(f'Answer is: {answer}')

        return answer

    def send_fixed_calibration_data(self, calibration_data: dict) -> None:
        aidevs = AIDevs3()
        result = aidevs.answer(
            getenv('HEADQUARTERS_SYSTEM_URL') + '/report',
            self.name,
            calibration_data,
        )
        logging.info(result)
