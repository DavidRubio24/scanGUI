import os
import time
from enum import Enum

import cv2
import numpy as np

import utils
from calibrate import Calibration, equidistant
from gui import GUI
from hardware import Lights

os.chdir(os.path.dirname(os.path.realpath(__file__)))

IMAGE_WAIT = cv2.imread('./wait_message.png')


class Mode(Enum):
    CAPTURE = 0
    CALIBRATE = 1
    CHECK = 2


mode_names = {Mode.CAPTURE: 'TEN_',
              Mode.CALIBRATE: 'CALIBRATE_',
              Mode.CHECK: 'CHECK_'}


class State:
    def __init__(self, cam, lights):
        self.gui: GUI = None
        self.lights: Lights = lights
        self.cam: cv2.VideoCapture = cam
        self.calibrations = {'dafault': Calibration()}
        self.mode = Mode.CAPTURE
        self.image_size = (480, 640)
        self.image: np.ndarray = None
        self.image_updated: bool = True  # When True, the GUI needs to be updated
        self.text: str = ''

    def zoom_out(self):
        """Update the size to be displayed."""
        self.image_size = [int(d * .9) for d in self.image_size]
        self.image_updated = True

    def zoom_in(self):
        """Update the size to be displayed."""
        self.image_size = [int(d // .9) for d in self.image_size]
        self.image_updated = True

    def zoom_reset(self):
        """Update the size to be displayed."""
        self.image_size = (480, 640)
        self.image_updated = True

    def cam_properties(self):
        self.cam.set(cv2.CAP_PROP_SETTINGS, 0)

    def update(self):
        """Ask for a new image from the camera and rotate it for the GUI."""
        success, image = self.cam.read()
        if not success or image is None or not np.any(image):
            return
        # Orient appropriately
        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        self.image = cv2.flip(image, 1)
        self.image_updated = True

    def get_image(self, rgb=False):
        """Returns the image to be displayed in the GUI."""
        if self.image is None:
            # There is no image, so return the wait image message.
            if IMAGE_WAIT.shape[:2] != self.image_size:
                return cv2.resize(IMAGE_WAIT, self.image_size)
            return IMAGE_WAIT
        image = cv2.resize(self.image, self.image_size)
        if self.mode == Mode.CAPTURE:
            # Draw a line in the middle for reference
            cv2.line(image,
                     (int(self.image_size[0] * .49), 0),
                     (int(self.image_size[0] * .51), self.image_size[1]),
                     (255, 30, 30), 2)
        elif self.mode == Mode.CALIBRATE:
            # Draw points over the calibration pattern.
            color = (0, 0, 255)
            r = 1
            for points in list(self.calibrations.values())[-1].points[::-1]:
                for point in points:
                    x, y = point[0]
                    x, y = int(x * image.shape[1] // self.image.shape[1]), int(y * image.shape[0] // self.image.shape[0])
                    image[y-r:y+r+1, x-r:x+r+1] = color
                color = (0, 255, 0)

        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if rgb else image

    def change_mode(self, mode: Mode):
        if mode == Mode.CAPTURE:
            big_id = ''
        else:
            big_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
        self.gui.prefix.set('Serie: ' + mode_names[mode])
        self.gui.big_id.set(big_id)
        self.gui.little_id.set('M1' if mode == Mode.CAPTURE else '0')
        self.text = ''
        self.mode = mode
        self.gui.set_mode(mode.value)
        self.gui.update()

    def new_capture(self):
        self.change_mode(Mode.CAPTURE)

    def calibrate(self):
        self.change_mode(Mode.CALIBRATE)
        self.text = 'Captura el patrón de calibración de 7x10.'

    def check(self):
        self.change_mode(Mode.CHECK)
        self.text = 'Captura el patrón de comprobación de 36x54.'

    def capture_action(self, capture_name=None):
        """Save the image to the destination directory."""
        path_id = self.gui.path_id.get()
        big_id = self.gui.big_id.get()
        # Remove the mode prefix if the user has inputed it.
        for prefix in mode_names.values():
            if big_id.upper().startswith(prefix):
                big_id = big_id[len(prefix):]
                break
        little_id = capture_name or self.gui.little_id.get()
        if not os.path.isdir(path_id): os.mkdir(path_id)
        extension = 'png' if self.mode != Mode.CAPTURE else time.strftime("%Y%m%d", time.localtime()) + '.bmp'
        filepath = os.path.join(path_id, f'{mode_names[self.mode]}{"0" * (4 - len(big_id))}{big_id}-{little_id}.{extension}')
        if os.path.isfile(filepath):
            i = 2
            while os.path.isfile(filepath):
                filepath = os.path.join(path_id, f'{mode_names[self.mode]}{"0" * (4 - len(big_id))}{big_id}-{little_id}({i}).{extension}')
                i += 1
        self.text = f"Capturado en:\n{path_id}\n{filepath[len(path_id):]}" + '\0' * 30
        self.gui.text.configure(text=self.text)
        self.gui.text.update()
        cv2.imwrite(filepath, self.image)

        if self.mode == Mode.CALIBRATE:
            calibration = self.calibrations.get(big_id, Calibration())
            self.calibrations[big_id] = calibration
            calibration.add_points(self.image, (6, 9))
            calibration.calibrate()
            camera_matrix = str(calibration.camera_matrix).replace("\n", "\n" + " " * 18)
            dist_coeffs = str(calibration.dist_coeffs.squeeze().tolist())
            with open(os.path.join(path_id, f'{big_id}.json'), 'w') as file:
                file.write(f'{{"camera_matrix": {camera_matrix},\n"distortion_coefficients": {dist_coeffs}\n}}\n')
                file.truncate()
        elif self.mode == Mode.CHECK:
            calibration = list(self.calibrations.values())[-1]
            undistorted = calibration.undistort(self.image)
            cv2.imwrite(os.path.join(path_id, f'{big_id}-{little_id}-undistorted.png'), undistorted)
            error = equidistant(undistorted)
            if error is None:
                self.text = 'Mueve el patron de 36x54 para poder detectarlo.'
            else:
                self.text = f'Error: {error:.2f} mm'
            self.gui.update()

        if capture_name is None:
            self.gui.little_id.set(utils.increase_name(little_id))

    def __del__(self):
        self.gui = None
        self.cam.release()
        self.lights.off()
        del self.lights
