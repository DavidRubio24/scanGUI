import sys
import logging

import hardware
from state import State
from gui import GUI
import config


log = logging.getLogger(__name__); log.setLevel(logging.INFO)
formatter = logging.Formatter('{levelname}:\t{message}', style='{')
log.addHandler(logging.StreamHandler()); log.handlers[-1].setFormatter(formatter)  # Defaults to sys.stderr.


def main():
    log.info('Connecting to camera...')
    cap = hardware.camera(config.cam)
    log.info('Connecting to lights...')
    lights = hardware.lights(config.luz)
    log.info('Starting app...')
    state = State(cap, lights)
    log.info('Starting GUI...')
    GUI(state, config.directorio_destino, intensity=config.intensidad)
    log.info('Exiting...')
    sys.exit(0)


if __name__ == '__main__':
    main()
