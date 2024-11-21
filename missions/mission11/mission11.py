import os
import json
from services.AIDevs3 import AIDevs3
from services.LLMs import LLMs

class Mission11:

    __name = "dokumenty"
    __HEADQUARTERS_SYSTEM_URL = os.getenv("HEADQUARTERS_SYSTEM_URL")
    __llm = LLMs()

    async def run(self) -> None:
        report = {}

        # about who is each fact
        facts_about_who = self.about_who("facts_about_who.json", "pliki_z_fabryki/facts")

        # about who is each report
        reports_about_who = self.about_who("reports_about_who.json", "pliki_z_fabryki")

        # match facts with reports and reports with other reports
        files_matches: list[list[str]] = []
        for who in reports_about_who.keys():
            for report_filename in reports_about_who[who]:
                files_to_load = [report_filename] + (facts_about_who[who] if who in facts_about_who.keys() else [])
                files_matches.append(files_to_load)

        # gen keywords for each report with facts and other reports
        if True == os.path.exists("missions/mission11/report.json"):
            with open("missions/mission11/report.json", "r") as f:
                report = json.load(f)
        else:
            for report_files in files_matches:
                report_filename = ""
                files_content = "<files>\n"
                for file in report_files:
                    if -1 < file.find("report"):
                        report_filename = file
                    files_content += "<file>\n"
                    with open(f"missions/pliki_z_fabryki/{file}", "r") as f:
                        files_content += f"<filename>{file.split("/")[-1]}</filename><content>{f.read()}</content>\n"
                    files_content += "</file>\n"
                files_content += "</files>\n"

                keywords = self.__llm.completeOpenAI(
                    "gpt-4o",
                    "Your task is to prepare keywords that accurately describe the content of the data provided by the user."
                    "The content will be inside <files></files> tags and may contain multiple <file></file> tags."
                    "The keywords will be used as tags associated with the file, which should help you find these documents later."
                    "Make sure that the generated keywords include all the most important information from the content."
                    "Think step-by-step about the content to make sure you have all the information."
                    "Take your time, take your time."
                    "Keywords MUST be in Polish."
                    "Return ONLY keywords, separated by a comma and nothing else.",
                    files_content,
                    1.0,
                )
                report[report_filename] = keywords

            with open("missions/mission11/report.json", "w") as f:
                json.dump(report, f)

        aidevs = AIDevs3()
        aidevs.send_report_to_headquarter(self.__name, report)

    def about_who(self, cache_file: str, files_directory: str) -> dict:
        if True == os.path.exists(f"missions/mission11/{cache_file}"):
            with open(f"missions/mission11/{cache_file}", "r") as file:
                data_about_who = json.load(file)
        else:
            data_about_who = {}
            directory = f"missions/{files_directory}"
            files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.txt')]
            for file_path in files:
                with open(file_path, "r") as file:
                    content = file.read().strip()

                if "entry deleted" == content:
                    continue

                about_who = self.__llm.completeOpenAI(
                    "gpt-4o-mini",
                    "Your role is to analyse given text and tell about who is text. Return only name in Polish language and nothing else. If you don't know about who is text return \"none\".",
                    content,
                    0.7,
                )

                filename = file_path.split("/")[-1]
                if about_who in data_about_who.keys():
                    data_about_who[about_who].append(filename)
                else:
                    data_about_who[about_who] = [filename]

            with open(f"missions/mission11/{cache_file}", "w") as file:
                json.dump(data_about_who, file)

        return data_about_who
