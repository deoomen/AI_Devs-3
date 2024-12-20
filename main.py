import logging
import sys
import asyncio
from importlib import import_module

def init_loggers() -> None:
    level = logging.INFO
    root = logging.getLogger()
    root.setLevel(level)

    stdout_formatter = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] - %(message)s - [%(module)s/%(filename)s::%(funcName)s:%(lineno)d]')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(level)
    stdout_handler.setFormatter(stdout_formatter)

    root.addHandler(stdout_handler)

async def main() -> None:
    init_loggers()

    try:
        if 1 == len(sys.argv):
            mission_number = input("""
Which mission do you want to run?
00 - POLIGON
01
02
03 - JSON
04
06 - mp3
07
08 - robotid
09 - kategorie
10 - arxiv
11 - dokumenty
""")
        else:
            mission_number = sys.argv[1]

        try:
            mission_module = import_module(f"missions.mission{mission_number}.mission{mission_number}")
            mission_class = getattr(mission_module, f"Mission{mission_number}")

            mission = mission_class()
            await mission.run()

        except (ModuleNotFoundError):
            raise RuntimeError('Unknown mission "{}"'.format(mission_number))

    except Exception as exception:
        logging.exception(exception)
        exit(1)

if __name__ == '__main__':
    asyncio.run(main())
