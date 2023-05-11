import time
import tkinter as tk
from tkinter import ttk

import cv2
from PIL import Image, ImageTk

from state import Mode


class GUI:
    def __init__(self, state, path_id='D:/HANDSCANNER_DATA/', loop=True, intensity=30):
        state.gui = self
        self.state = state

        self.root = tk.Tk()
        self.root.title("Escaner de manos IBV")
        self.root.iconbitmap('ibv_logo.ico')
        self.mainframe = ttk.Frame(self.root)
        self.mainframe.grid(column=0, row=0, sticky='NWES')

        # Left frame
        self.left_frame = ttk.Frame(self.mainframe)
        self.left_frame.grid(column=0, row=0, sticky='NWES')
        self.left_frame.columnconfigure(0, weight=1)

        # Mode selection
        mode_frame = ttk.Frame(self.left_frame)
        mode_frame.grid(column=0, row=0, sticky='W')

        s = self.state
        button_names    = ['Nuevo usuario', 'Calibración', 'Comprobar calibración', 'Encender luces', 'Apagar luces',
                           # 'Zoom +', 'Zoom -', 'Zoom reset',
                           'Propiedades de cámara']
        button_commands = [s.new_capture, s.calibrate, s.check, self.lights_on, s.lights.off,
                           # s.zoom_in, s.zoom_out, s.zoom_reset,
                           s.cam_properties]
        buttons = [tk.Button(mode_frame, text=txt, command=cmd) for txt, cmd in zip(button_names, button_commands)]
        for index, button in enumerate(buttons):
            button.grid(column=0, row=index, sticky='W')
            button.configure(width=30)
        self.buttons = buttons[:3]
        self.properties_button = buttons[-1]
        self.set_mode(state.mode.value)

        # Capture the path and name
        self.intensity = tk.StringVar(value=str(intensity))
        self.path_id   = tk.StringVar(value=path_id)
        self.prefix    = tk.StringVar(value='Serie: TEN_')
        self.big_id    = tk.StringVar(value='')
        self.little_id = tk.StringVar(value='M1')

        path_frame = tk.Frame(self.left_frame)
        path_frame.grid(column=0, row=1, sticky='W')
        ttk.Label(path_frame, text="Iluminación:").        grid(column=0, row=0, sticky='SW')
        ttk.Entry(path_frame, textvariable=self.intensity).grid(column=1, row=0, sticky='SW')
        ttk.Label(path_frame, text="%").                   grid(column=2, row=0, sticky='SW')
        ttk.Label(path_frame, text="Carpeta:").            grid(column=0, row=1, sticky='SW')
        ttk.Label(path_frame, text=path_id).               grid(column=1, row=1, sticky='SW')
        ttk.Label(path_frame, textvariable=self.prefix).   grid(column=0, row=2, sticky='SW')
        ttk.Entry(path_frame, textvariable=self.big_id).   grid(column=1, row=2, sticky='SW')
        ttk.Label(path_frame, text="Captura:").            grid(column=0, row=3, sticky='SW')
        ttk.Entry(path_frame, textvariable=self.little_id).grid(column=1, row=3, sticky='SW')

        for key, entry in path_frame.children.items():
            if '!entry' in key:
                entry.configure(width=28)

        ttk.Button(path_frame, text="Capturar", command=state.capture_action).grid(column=0, row=4, sticky='SE')
        ttk.Button(path_frame, text="M2", command=lambda: state.capture_action('M2')).grid(column=1, row=4, sticky='SE')
        ttk.Button(path_frame, text="M1", command=lambda: state.capture_action('M1')).grid(column=1, row=4, sticky='SW')
        # Add text below the button
        self.text = ttk.Label(path_frame, text=self.state.text)
        self.text.grid(column=0, row=5, columnspan=2, sticky='SWE')
        self.text_time_to_live = float('inf')
        self.properties_text = ttk.Label(path_frame, text='')
        self.properties_text.grid(column=0, row=6, columnspan=2, sticky='SWE')
        self.properties_text_time_to_live = 0

        # Image
        self.image = None
        self.image_label = ttk.Label(self.mainframe)
        self.image_label.grid(row=0, column=1)

        # Actions on close and intro.
        self.root.protocol("WM_DELETE_WINDOW", self.__del__)
        self.root.bind("<Return>", state.capture_action)

        self.update()
        self.root.after(10, self.update)
        self.root.after(1000, self.state.lights.on)  # It doesn't work if done inmediately. ¯\_(ツ)_/¯
        if loop:
            self.root.mainloop()

    def lights_on(self):
        intensity = float(self.intensity.get()) * 255 / 100
        intensity = min(255, intensity)
        intensity = max(0, intensity)
        self.state.lights.on(int(intensity))

    def update(self, period=10):
        """Updates the state and, afterwads, the GUI."""

        # Change the settongs button color if the camera doesn't have the appropriate settings.
        if abs(self.state.cam.get(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U) - 3000) <= 110:
            self.properties_button.configure(bg='gray')
            if self.properties_text_time_to_live == -1:
                self.properties_text.configure(text='Pulsa OK',
                                               font=('Helvetica', 15, 'bold'))
                self.properties_text_time_to_live = time.time() + 1.5
                self.properties_button.after(2000, self.clear_properties_text)
        else:
            self.properties_button.configure(bg='#FF5957')  # Shade of red.
            self.properties_text.configure(text='¡ALERTA!\nRevisar:\nPropiedades de cámara > \n'
                                                '> White balance > \n> 3000 NO Auto > OK',
                                           font=('Helvetica', 15, 'bold'))
            self.properties_text_time_to_live = -1
        
        # Only when the state modifys the image, do we update it in the GUI.
        if self.state.image_updated:
            self.state.image_updated = False
            self.image = ImageTk.PhotoImage(Image.fromarray(self.state.get_image(rgb=True)))
            self.image_label.configure(image=self.image)

        self.root.update()

        self.root.after(period, self.update)

    def unbold_text(self):
        text = self.text.cget('text')
        self.text.configure(text=text, font=('Arial', 9, 'normal'))
    
    def clear_text(self):
        if self.text_time_to_live < time.time():
            if self.state.mode == Mode.CAPTURE:
                self.text.configure(text='')
            elif self.state.mode == Mode.CALIBRATE:
                self.text.configure(text='Captura el patrón de calibración de 7x10.')
            elif self.state.mode == Mode.CHECK:
                self.text.configure(text='Captura el patrón de comprobación de 36x54.')
            self.text.update()
    
    def clear_properties_text(self):
        if self.properties_text_time_to_live < time.time():
            self.properties_text.configure(text='')
            self.properties_text.update()

    def __del__(self):
        self.root.destroy()
        del self.state

    def set_mode(self, value: int):
        """Color the buttons according to the mode. Blue for the current one, grey for the others."""
        for index, button in enumerate(self.buttons):
            # Sade of blue or gray.
            color = '#ADD8E6' if index == value else 'gray'
            button.configure(bg=color)
