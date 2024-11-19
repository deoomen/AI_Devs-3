import logging
from os import getenv, path
from time import sleep
from requests import get
from services.AIDevs3 import AIDevs3
from services.LLMs import LLMs
from crawl4ai import AsyncWebCrawler
from markdownify import markdownify
from pyquery import PyQuery
import json

class Mission10:

    __name = "arxiv"
    __llm = LLMs()
    __report_analysis_prompt = ""
    __HEADQUARTERS_SYSTEM_URL = getenv("HEADQUARTERS_SYSTEM_URL")
    __ARTICLE_URL = getenv("S02E05_ARTICLE_URL")

    async def run(self) -> None:
        logging.info("Mission 10 - arxiv")

        if True == path.exists("missions/mission10/article/answers.json"):
            with open("missions/mission10/article/answers.json", "r") as file:
                answers = json.load(file)
        else:
            if True == path.exists("missions/mission10/article/article-modified.md"):
                with open("missions/mission10/article/article-modified.md", "r") as file:
                    markdown = file.read()
            else:
                article_html = await self.download_body()
                pq = PyQuery(article_html)

                # split into sections
                for heading in pq("h1,h2"):
                    title = pq(heading).text()
                    content = pq(heading).next_until("h2")

                    for figure in pq(content)("figure"):
                        img_src = pq(figure)("img").attr("src")
                        img_description_filename = f"missions/mission10/article/{img_src.replace("/", "_")}.md"
                        img_url = f"{self.__HEADQUARTERS_SYSTEM_URL}/dane/{img_src}"
                        img_caption = pq(figure)("figcaption").text()

                        if True == path.exists(img_description_filename):
                            with open(img_description_filename, "r") as file:
                                description = file.read()
                        else:
                            description = self.__llm.describe_image(
                                [img_url],
                                """
                                You are an image description generator. Your task is to generate a description for the image provided in the input taking also into account the provided caption.
            
                                - Focus on objects, landmarks, features.
                                - Don't describe atmosphere or mood.
                                - Use concise language.
                                - Analyze the caption and the image to generate a coherent description - the caption shouldn't contradict the image.
                                - The description should be 1-3 sentences long.
                                - The description should incorporate the information from caption.
                                - Description must be in Polish language.
                                """,
                                f"Describe the image. The image caption is: <CAPTION>{img_caption}</CAPTION>. The image context is: <CONTEXT>{content.text()}</CONTEXT>"
                            )

                            with open(img_description_filename, "w") as file:
                                file.write(description)

                        pq(figure).html(f"<p>{description}</p>")

                    for audio in pq(content)("audio"):
                        audio_src = pq(audio)("source").attr("src")
                        audio_description_filename = f"missions/mission10/article/{audio_src.replace("/", "_")}.md"
                        audio_url = f"{self.__HEADQUARTERS_SYSTEM_URL}/dane/{audio_src}"

                        if True == path.exists(audio_description_filename):
                            with open(audio_description_filename, "r") as file:
                                description = file.read()
                        else:
                            description = self.__llm.transcribeByOpenAI(
                                audio_url,
                                f"Specify context, be patient and make precise transcription",
                                "pl",
                                temperature=0.7,
                            )

                            with open(audio_description_filename, "w") as file:
                                file.write(description)

                        pq(audio).html(f"<p>{description}</p>")

                html = str(pq.html())
                markdown = markdownify(html).strip()

                with open("missions/mission10/article/article-modified.html", "w") as file:
                    file.write(html)

                with open("missions/mission10/article/article-modified.md", "w") as file:
                    file.write(markdown)

            response = get(f"{self.__HEADQUARTERS_SYSTEM_URL}/data/{getenv("API_KEY")}/arxiv.txt")
            questions = []
            for q in response.text.strip().split("\n"):
                splitted = q.split("=")
                questions.append(splitted[1])

            answers = {}
            for question in enumerate(questions):
                sleep(1)
                answer = self.__llm.completeOpenAI(
                    "gpt-4o",
                    f"""
                    You are a question answering model. Your task is to answer the question based on the provided information.
        
                    - The information is a collection of various objects. 
                    - Each object has an ID, type, context pointers, and content.
                    - Each object can represent a text block, an image, or an audio clip. This is stated by the "type" field.
                    - The "content" field contains the actual content of the object. In case of images and audio clips, the content is a description or transcription.
                    - The "context" field is a list of IDs of other objects that are closely related to this object. 
                    - Follow these relationships to analyze how data is interrelated but also take into account other objects in entire data.
                    - To answer the question, consider not only the content of the object but also its related objects as indicated by the "context" field.
                    - Explore the "context" field recursively to gather all relevant information, but prioritize direct relationships over distant ones.
                    - Focus on objects that directly contribute to answering the question, avoiding irrelevant details.
                    - For "image" objects, use the provided description or caption to infer information but also take into account the context pointers which may give important tips.
                    - For "audio" objects, use the transcription or description to extract relevant data.
                    - If conflicting information is found, prioritize the most directly related object in the context.
                    - If no relevant information exists, state this explicitly in the answer.
                    - Include names of objects, descriptions, and other relevant details in the answer.
                    - When searching for an acronym's explanation, consider not only the immediate context of objects but also recursively explore related objects.
                    - Use direct relationships first, and only if no explanation is found, explore more distant relationships.
                    - Always expand all acronyms and abbreviations using all information provided - make sure that you focus on finding the proper solution.
                
                    Answer the question based on entire provided information.
                    
                    Your answer must be a single sentence.
                    Be accurate based on the provided context.
                    If no relevant information is found, respond with "The information is not available in the provided context."
                
                    IMPORTANT: all answers must be in Polish.
                    IMPORTANT: look carefully at all provided data objects before answering the question.
                    
                    <CONTEXT>
                    {markdown}
                    </CONTEXT>
                    """,
                    question[1],
                    0.1,
                )
                answers[f"0{question[0]+1}"] = answer

            with open("missions/mission10/article/answers.json", "w", encoding="utf-8") as file:
                json.dump(answers, file)

        aidevs = AIDevs3()
        aidevs.send_report_to_headquarter(self.__name, answers)

    async def download_body(self) -> str:
        article_path = "missions/mission10/article/article.html"

        if True == path.exists(article_path):
            with open(article_path, "r") as file:
                return file.read()
        else:
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(
                    url=self.__ARTICLE_URL,
                )

                if not result.success:
                    raise RuntimeError(f"Crawl failed: {result.error_message}; Status code: {result.status_code}")

                content = result.html

                with open(article_path, "w") as file:
                    file.write(content)

                return content
