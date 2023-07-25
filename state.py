import os
import time
from enum import Enum

import cv2
import numpy as np
from threading import Thread

import config
import utils
from calibrate import Calibration, equidistant
from hardware import Lights

os.chdir(os.path.dirname(os.path.realpath(__file__)))

IMAGE_WAIT = cv2.imread('./wait_message.png')


class Mode(Enum):
    CAPTURE = 0
    CALIBRATE = 1
    CHECK = 2


mode_prefix = {Mode.CAPTURE: 'TEN_',
               Mode.CALIBRATE: 'CALIBRATE_',
               Mode.CHECK: 'CHECK_'}


class State:
    def __init__(self, cam, lights):
        self.gui = None
        self.lights: Lights = lights
        self.cam: cv2.VideoCapture = cam
        self.calibrations = {'dafault': Calibration()}
        self.mode = Mode.CAPTURE
        self.image_size = (480, 640)
        self.image: np.ndarray = None
        self.image_updated: bool = True  # When True, the GUI needs to be updated
        Thread(target=self.update, daemon=True).start()

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
        """Continously get images from the camera and rotate them for the GUI."""
        time.sleep(5)
        image_buffer = None  # Use always the same buffer to avoid memory allocation.
        while True:
            success, image_buffer = self.cam.read(image_buffer)  # This waits for a new image.
            if not success or image_buffer is None or not np.any(image_buffer):
                time.sleep(.2)
                continue
            # Orient appropriately.
            image = cv2.rotate(image_buffer, cv2.ROTATE_90_COUNTERCLOCKWISE)
            self.image = cv2.flip(image, 1)
            self.image_updated = True

    def get_image(self, rgb=False):
        """Returns the image to be displayed in the GUI."""
        if self.image is None:
            # There is no image yet, so return the wait image message.
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
            color = (0, 0, 255)  # Color for the last captured pattern.
            r = 1
            for points in list(self.calibrations.values())[-1].points[::-1]:
                for point in points:
                    x, y = point[0]
                    x, y = int(x * image.shape[1] // self.image.shape[1]), int(y * image.shape[0] // self.image.shape[0])
                    image[y-r:y+r+1, x-r:x+r+1] = color
                color = (0, 255, 0)  # Color for the previous captured patterns.

        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if rgb else image

    def change_mode(self, mode: Mode):
        self.gui.text.configure(foreground='black')  # Make sure is not red.
        if mode == Mode.CAPTURE:
            big_id = ''
            # Show M1 and M2 buttons and hide the capture button.
            self.gui.capturar.grid_forget()
            self.gui.m1.grid(column=1, row=4, sticky='SW')
            self.gui.m2.grid(column=1, row=4, sticky='SE')
        else:
            big_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
            # Show the capture button and hide M1 and M2 buttons.
            self.gui.capturar.grid(column=0, row=4, sticky='SW')
            self.gui.m1.grid_forget()
            self.gui.m2.grid_forget()
        self.gui.prefix.set('Serie: ' + mode_prefix[mode])
        self.gui.big_id.set(big_id)
        self.gui.little_id.set('M1' if mode == Mode.CAPTURE else '0')
        self.mode = mode
        self.gui.set_mode(mode.value)  # Color the buttons appropriately.
        self.gui.update()
        self.gui.text_time_to_live = float('inf')

    def new_capture(self):
        self.change_mode(Mode.CAPTURE)
        self.gui.text.configure(text='')

    def calibrate(self):
        self.change_mode(Mode.CALIBRATE)
        self.gui.text.configure(text='Captura el patrón de calibración de 7x10.')

    def check(self):
        self.change_mode(Mode.CHECK)
        self.gui.text.configure(text='Captura el patrón de comprobación de {}x{}.'
                                .format(*config.dimensiones_patron_comprobacion))

    def capture_action(self, capture_name: str = None):
        """Save the image to the destination directory."""
        path_id = self.gui.path_id.get()
        big_id = self.gui.big_id.get()
        
        # Remove the mode prefix if the user has (reduntdantly) typed it.
        for prefix in mode_prefix.values():
            if big_id.upper().startswith(prefix):
                big_id = big_id[len(prefix):]
                break
        
        # Use the name of the button the user pressed or the contents of the little_id if the user pressed enter.
        little_id = capture_name if isinstance(capture_name, str) else self.gui.little_id.get()
        if not os.path.isdir(path_id): os.mkdir(path_id)
        extension = 'png' if self.mode != Mode.CAPTURE else time.strftime("%Y%m%d", time.localtime()) + '.png'
        filepath = os.path.join(path_id, f'{mode_prefix[self.mode]}{"0" * (4 - len(big_id))}{big_id}-{little_id}.{extension}')
        
        # If there's already a file with the same name, add a number at the end with parenthesis.
        i = 2
        while os.path.isfile(filepath):
            filepath = os.path.join(path_id, f'{mode_prefix[self.mode]}{"0" * (4 - len(big_id))}{big_id}-{little_id}({i}).{extension}')
            i += 1
        self.gui.text.configure(text=f"Capturado en:\n{path_id}\n{filepath[len(path_id):]}", font=('Arial', 9, 'bold'))
        self.gui.text.configure(foreground='red' if '00000'.startswith(big_id) else 'black')  # Red if the ID is empty or zeros.
        self.gui.text_time_to_live = time.time() + 2
        self.gui.text.update()
        self.gui.text.after(100, self.gui.unbold_text)
        clear_id = self.gui.text.after(2050, self.gui.clear_text)
        Thread(target=lambda: cv2.imwrite(filepath, self.image)).start()

        if isinstance(capture_name, str):
            self.gui.little_id.set(capture_name)  # If the user pressed a button, set the little_id to the button's name.
        elif self.mode != Mode.CAPTURE:
            self.gui.little_id.set(utils.increase_name(little_id))

        if self.mode == Mode.CALIBRATE:
            calibration = self.calibrations.get(big_id, Calibration())
            self.calibrations[big_id] = calibration
            success = calibration.add_points(self.image, (6, 9))
            if not success:
                return
            calibration.calibrate()
            with open(os.path.join(path_id, f'{mode_prefix[self.mode]}{big_id}.json'), 'w') as file:
                file.write(str(calibration))
        elif self.mode == Mode.CHECK:
            # If we write text, it's going to be deleted by the scheduled self.gui.clear_text function.
            # Cancel that function before writing.
            self.gui.text.after_cancel(clear_id)
            
            calibration = list(self.calibrations.values())[-1]  # Take the last (most updated) calibration.
            undistorted = calibration.undistort(self.image)
            cv2.imwrite(os.path.join(path_id, f'{mode_prefix[self.mode]}{big_id}-{little_id}.undistorted.png'), undistorted)
            error = equidistant(undistorted, pattern_size=config.dimensiones_patron_comprobacion)
            if error is None:
                text = 'Mueve el patron de {}x{} para poder detectarlo.'.format(*config.dimensiones_patron_comprobacion)
            else:
                text = f'Error: {error:.2f} mm'
            self.gui.text.configure(text=text)
            self.gui.text.update()

    def __del__(self):
        self.gui = None
        self.cam.release()
        self.lights.off()
        del self.lights
