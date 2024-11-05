from os import getenv
from bs4 import BeautifulSoup
from requests import get, post
from openai import OpenAI
from pprint import pprint, pp

class Mission01:

    name = '01'
    url = 'https://xyz.ag3nts.org'

    def run(self) -> None:
        print('Mission 01')

        # fetch question
        bs = BeautifulSoup(get(self.url).content, 'html.parser')
        question = bs.find(id='human-question').get_text(' ').strip('Question: ')
        print(f'Question is: {question}')

        # get answer
        llm = OpenAI(api_key=getenv('OPENAI_API_KEY'))
        answer = llm.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                { 'role': 'system', 'content': 'You are helpful assistant that will answer on user questions. The answer is always a number. You will return only number and nothing else.' },
                { 'role': 'user', 'content': question }
            ],
        ).choices[0].message.content
        print(f'Answer is: {answer}')

        if None is answer:
            raise ValueError('Answer not found')

        # send answer
        response = post(
            self.url,
            {
                'username': 'tester',
                'password': '574e112a',
                'answer': answer,
            }
        )
        print(f'Status code: {response.status_code}')
        print('Headers: ')
        pprint(response.headers)
        print('Content: ')
        pprint(response.content)
        with open('missions/mission01/system.html', 'wb') as file:
            file.write(response.content)
