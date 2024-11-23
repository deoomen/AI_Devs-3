import tools.utils as utils
from services.AIDevs3 import AIDevs3
from services.LLMs import LLMs
from services.VectorDatabase import VectorDatabase, Point

class Mission12:
    __name = "wektory"
    __llm = LLMs()
    __vector_db = VectorDatabase()
    __vector_size = 1024
    __embedding_model = "text-embedding-3-small"

    async def run(self) -> None:
        report = {}
        self.__vector_db.set_vector_size(self.__vector_size).set_collection_name("aidevs3-mission12").create_collection_if_not_exist()
        self.fill_vector_collection()

        question = "W raporcie, z którego dnia znajduje się wzmianka o kradzieży prototypu broni?"
        question_embedding = self.__llm.createEmbedding(self.__embedding_model, question, self.__vector_size)
        result = self.__vector_db.search(question_embedding, 1)

        report = result[0].payload["filename"].strip(".txt").replace("_", "-")
        aidevs = AIDevs3()
        aidevs.send_report_to_headquarter(self.__name, report)

    def fill_vector_collection(self) -> None:
        if not self.__vector_db.is_collection_empty():
            return

        vector_points: list[Point] = []
        directory = "missions/pliki_z_fabryki/weapons_tests/do-not-share"
        weapon_reports_files = utils.get_filenames_from_directory(directory)
        for weapon_report_file in weapon_reports_files:
            with open(f"{directory}/{weapon_report_file}", "r") as file:
                weapon_report_content = file.read().strip()
                embedding = self.__llm.createEmbedding(self.__embedding_model, weapon_report_content, self.__vector_size)
                vector_points.append(Point(None, embedding, { "filename": weapon_report_file }))

        self.__vector_db.add_points(vector_points)
