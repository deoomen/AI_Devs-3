import logging
import sys
from missions.mission00.mission00 import Mission00
from missions.mission01.mission01 import Mission01
from missions.mission02.mission02 import Mission02
from missions.mission03.mission03 import Mission03
from missions.mission04.mission04 import Mission04


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
""")
        else:
            mission_number = sys.argv[1]

        if '00' == mission_number or '0' == mission_number:
            mission = Mission00()
        elif '01' == mission_number or '1' == mission_number:
            mission = Mission01()
        elif '02' == mission_number or '2' == mission_number:
            mission = Mission02()
        elif '03' == mission_number or '3' == mission_number:
            mission = Mission03()
        elif '04' == mission_number or '4' == mission_number:
            mission = Mission04()
        else:
            raise RuntimeError('Unknown mission "{}"'.format(mission_number))

        mission.run()

    except Exception as exception:
        logging.exception(exception)
        exit(1)
