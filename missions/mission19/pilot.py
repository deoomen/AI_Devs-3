import json
from openai import OpenAI

class Pilot:
    __openai = OpenAI()
    __map = [
        ['<START>', '<grass>', '<tree>', '<house>'],
        ['<grass>', '<windmill>', '<grass>', '<grass>'],
        ['<grass>', '<grass>', '<rocks>', '<trees>'],
        ['<rocks>', '<rocks>', '<car>', '<cave>'],
    ]

    async def description(self, instruction: str) -> dict:
        print(f"Instruction: {instruction}")
        system_message = (
            "You play with user in a game where user will tell you how he move on the map. Your task is to find place where user stops."
            "User will give you a description of his moves on 2d matrix map. The size of map is 4x4."
            "Description will be in natural language, in polish language."
            "User always starts from <START>, it is in top left corner of the map."
            "Watch out what user will say you. It can be tricky and can have some redundant or incorrect information."
            "Think step by step what user said you and iterate each user step to find where he stops."
            "You MUST answer in JSON format like below and nothing else:"
            'ANSWER: {"_thinking":"<Your thoughts>","description":"<Place where user stops in ONE or max TWO WORDS>"}'
            "The map of labyrinth will be presented as 2d matrix with some characters as objects."
            "Legend:"
            '- "<START> is the place from where you start' 
            '- "<grass> is a grass field' 
            '- "<tree> is a single tree' 
            '- "<house> is a house' 
            '- "<windmill> is a windmill' 
            '- "<rocks> is a group of rocks and stones' 
            '- "<trees> is a multiple trees' 
            '- "<car> is a car' 
            '- "<cave> is an entrance to the cave' 
            "<map>"
            f"{json.dumps(self.__map)}"
            "</map>"
            "<examples>"
            "<example>"
            "USER: Idziemy sobie dwa razy w prawo, potem w dół do końca i raz w lewo. Gdzie jesteśmy?"
            'ASSISTANT: {"_thinking":"Gracz wykonał najpierw dwa kroki w prawo, następnie poszedł do końca w dół czyli wykonał 3 kroki w dół i na koniec jeden krok w lewo.","description":"Skały"}'
            "</example>"
            "<example>"
            "USER: Ruszamy! Lecimy do końca w prawo. Albo nie, nie! Idziemy najpierw na dół dwa razy, a potem raz w prawo."
            'ASSISTANT: {"_thinking":"Gracz najpierw poszedł w prawo albo zrezygnował z tej akcji więc ja również powinienem ją zignorować. Tak więc zaczynamy od nowa. Gracz ruszył dwa razy w dół, a następnie raz w prawo.","description":"Trawa"}'
            "</example>"
            "</examples>"
        )

        answer = self.__openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                { "role": "system", "content": system_message },
                { "role": "user", "content": instruction }
            ],
            temperature=0.7,
        ).choices[0].message.content
        print(f"Answer: {answer}")
        description = json.loads(answer)

        return description
