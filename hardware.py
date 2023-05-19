import cv2
import serial
import serial.tools.list_ports
import numpy as np

import config


class Lights:
    """An object to deal with the Arduino controlled lights."""
    def __init__(self, port='COM3', baudrate=57600, timeout=.1):
        self.arduino = serial.Serial(port, baudrate, timeout=timeout)
        self.turned_on = False  # This is not necessarily true. It works anyway after the first interaction.
        self.__del__ = self.arduino.close

    def on(self, intensity=100, duration=255):
        # Duration is in minutes. 255 min == 4h15.
        intensity = int.to_bytes(intensity, 1, 'little') if isinstance(intensity, int) else intensity
        duration  = int.to_bytes(duration,  1, 'little') if isinstance(duration,  int) else duration

        self.arduino.write(b'I' + intensity + duration + b' ')
        self.turned_on = True

    def off(self):
        self.arduino.write(b'TP ')
        self.turned_on = False

    def toggle(self, intensity=255, duration=255):
        self.off() if self.turned_on else self.on(intensity, duration)


class DummyLights:
    def __init__(self, *_, **__): pass

    def on(self, *_, **__):
        print('DummyLights.on()', _, __)

    def off(self, *_, **__):
        print('DummyLights.off()', _, __)

    def toggle(self, *_, **__):
        print('DummyLights.toggle()', _, __)


def lights(port='COM3', baudrate=57600, timeout=.1):
    port = port if isinstance(port, str) and not port.isdigit() else f'COM{port}'
    ports = serial.tools.list_ports.comports()
    if port in [p.device for p in ports]:
        return Lights(port, baudrate, timeout)
    
    print(f'Lights port {port} not found.\nPorts available:')
    for port in sorted(ports, key=lambda port: port.device):
        print('    · ', port.device, ': ', port.description, sep='')
    print('Enter the port for the lights (', end='')
    print(*sorted([port.device for port in ports]), sep=', ', end='')
    port = input('... or press <Enter> for no lights): ')
    
    if port.strip():
        return lights(port, baudrate, timeout)
    print('Not using lights.')
    return DummyLights()


def camera(camera_number=0, resolution=(4208, 3120), fourcc='UYVY', exposure=-5, gain=0, settings=False):
    """
    Return a VideoCapture object for the camera.

    :param camera_number:
    :param resolution: Tuple of (width, height) of desired resolution.
                       If it's higher than the max resolution, it will be set to the max resolution.
    :param fourcc: Str of four character code for the codec. Either 'UYVY' or 'MJPG'.
    :param settings: Bool to open the camera settings window.
    :return: OpenCV's VideoCapture object.
    """
    cap = cv2.VideoCapture(camera_number, cv2.CAP_DSHOW)  # This flag allows configuring the camera.

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

    if fourcc is not None:
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc(*fourcc))  # Avoid .jpg.

    if exposure is not None:
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)  # Turn off auto exposure.
        cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
    
    if gain is not None:
        cap.set(cv2.CAP_PROP_GAIN, gain)
    
    if settings or abs(cap.get(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U) - config.balance_de_blancos) > 40:
        cap.set(cv2.CAP_PROP_SETTINGS, 0)

    return cap


def warm_up(cap, extra_frames=0):
    """For some reason we need to ask the camera for a few frames bfore it actually starts working."""  # Best camera ever.
    success, image = cap.read()
    i = 1
    cR_ = '\x1B[0;31m'
    _c = '\x1B[0m'
    while not success or np.all(image == 0):
        print(f'{i: >2}' if success else cR_ + f'{i: >2}' + _c, 'warm-up frames taken.', end='\r')
        success, image = cap.read()
        i += 1
    if i > 1: print()

    for j in range(extra_frames):
        success, image = cap.read()
        print(f'{j+1: >2}' if success else cR_ + f'{j+1: >2}' + _c, ' extra  frames taken.', end='\r')
    if extra_frames > 0: print()

    return success, image
