import logging
import sys
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

if __name__ == '__main__':
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
""")
        else:
            mission_number = sys.argv[1]

        try:
            mission_module = import_module(f"missions.mission{mission_number}.mission{mission_number}")
            mission_class = getattr(mission_module, f"Mission{mission_number}")

            mission = mission_class()
            mission.run()

        except (ModuleNotFoundError, AttributeError):
            raise RuntimeError('Unknown mission "{}"'.format(mission_number))

    except Exception as exception:
        logging.exception(exception)
        exit(1)
