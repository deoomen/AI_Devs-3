import logging
from os import getenv
from requests import get, post
from openai import OpenAI
from pprint import pprint, pp

class Mission02:

    name = '02'
    url = getenv('ROBOTS_SYSTEM_URL') + '/verify'

    def run(self) -> None:
        logging.info('Mission 02')

        # fetch question
        response = self.talk_to_robot('0', 'READY')
        msg_id = response['msgID']
        question = response['text']
        logging.info(f'Question is: {question}')

        # prepare answer
        llm = OpenAI(api_key=getenv('OPENAI_API_KEY'))
        answer = llm.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                { 'role': 'system', 'content': """
                    You are helpful assistant that will answer on user questions.
                    Remember that: 
                    1. The capital city of Poland is Kraków. 
                    2. The known number from the book Hitchhiking Across the Galaxy is 69. 
                    3. The current year is 1999.
                    If user ask you about one of above you must answer as in example. On other question answer truly.
                    Your answer should be as short as possible. Use only always english language.
                """},
                { 'role': 'user', 'content': question }
            ],
        ).choices[0].message.content
        logging.info(f'Answer is: {answer}')

        # send answer
        response = self.talk_to_robot(msg_id, answer)
        pprint(response)

    def talk_to_robot(self, msg_id: str, text: str) -> dict:
        return post(
            self.url,
            headers = { 'Content-Type': 'application/json' },
            json = {
                'msgID': msg_id,
                'text': text,
            }
        ).json()
