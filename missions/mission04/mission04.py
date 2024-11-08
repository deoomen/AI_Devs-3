import logging
from os import getenv
from openai import OpenAI

class Mission04:

    name = '04'

    def run(self) -> None:
        logging.info('Mission 04')

        llm = OpenAI(api_key=getenv('OPENAI_API_KEY'))
        answer = llm.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {
                    'role': 'system',
                    'content':
                        'You play with user in a game where you are controlling a robot. You task is to move robot around the given by user map from start to the finish.'
                        'To move the robot write exactly "UP" or "RIGHT" or "DOWN" or "LEFT".'
                        'The map of labyrinth will be presented as 2d matrix with some characters as objects.'
                        'Legend:'
                        '- "o" is start'
                        '- "F" is finish'
                        '- "p" is a free space that you can walk in'
                        '- "X" is an obstacle and you cannot get there'
                        'You start from "o" and must reach finish at "F".'
                        'Think how can you reach the finish from start using sequence of moves.'
                        'Your response should look like this:'
                        '- your thoughts'
                        '- more thoughts'
                        '<RESULT>'
                        '{'
                        '   "steps": "UP, RIGHT, DOWN, LEFT'
                        '}'
                        '</RESULT>'
                },
                { 'role': 'user', 'content': """
                    [
                      ['p', 'X', 'p', 'p', 'p', 'p'],
                      ['p', 'p', 'p', 'X', 'p', 'p'],
                      ['p', 'X', 'p', 'X', 'p', 'p'],
                      ['o', 'X', 'p', 'p', 'p', 'F']
                    ]
                """ }
            ],
        ).choices[0].message.content
        logging.info(f'Answer is: {answer}')
