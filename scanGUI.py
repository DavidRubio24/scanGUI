import sys

import hardware
from state import State
from gui import GUI
import config


def main(*_):
    state = State(hardware.camera(config.cam),
                  hardware.lights(config.luz))
    gui = GUI(state, config.directorio_destino, intensity=config.intensidad)


if __name__ == '__main__':
    main(*sys.argv[1:])
