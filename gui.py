import time
import tkinter as tk
from tkinter import ttk

import cv2
from PIL import Image, ImageTk

import config
from state import Mode


WB_MESSAGE = ('¡ALERTA!\nRevisar:\nPropiedades de cámara > \n'
              '> White balance > \n> {white_balance} NO Auto > OK')


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

        # Buttons
        mode_frame = ttk.Frame(self.left_frame)
        mode_frame.grid(column=0, row=0, sticky='W')

        buttons = [('Nuevo usuario', self.state.new_capture),
                   ('Calibración', self.state.calibrate),
                   ('Comprobar calibración', self.state.check),
                   ('Encender luces', self.lights_on),
                   ('Apagar luces', self.state.lights.off),
                   # ('Zoom +', self.state.zoom_in),
                   # ('Zoom -', self.state.zoom_out),
                   # ('Zoom reset', self.state.zoom_reset),
                   ('Propiedades de cámara', self.state.cam_properties),
                   ]
        buttons = [tk.Button(mode_frame, text=text, command=function) for text, function in buttons]
        for index, button in enumerate(buttons):
            button.grid(column=0, row=index, sticky='W')
            button.configure(width=31)
        self.buttons = buttons[:3]
        self.properties_button = buttons[-1]
        self.set_mode(state.mode.value)

        # Fields
        self.intensity = tk.StringVar(value=str(intensity))
        self.path_id   = tk.StringVar(value=path_id)
        self.prefix    = tk.StringVar(value='Serie: TEN_')
        self.big_id    = tk.StringVar(value='')
        self.little_id = tk.StringVar(value='M1')
        
        self.turn = 0
        """Turn to change intensity of lights. We don't want to change it to 1 and 10 while writting 100."""
        
        def update_intensity(intensity, my_turn):
            # Only update the intensity if this is the last turn assigned.
            if my_turn + 1 != self.turn:
                return
            self.state.lights.on(int(intensity))
        
        def on_intensity_change(*args):
            # Assign a turn to this callback.
            my_turn = self.turn
            self.turn += 1
            text = self.intensity.get()
            if text.isdigit() and 0 <= int(text) <= 100:
                self.root.after(300,  # Delay before callback.
                                update_intensity,  # Callback to change intensity.
                                int(int(text) * 255 / 100), my_turn)  # Callback arguments.
        
        self.intensity.trace_add('write', on_intensity_change)

        path_frame = tk.Frame(self.left_frame)
        path_frame.grid(column=0, row=1, sticky='W')
        ttk.Label(path_frame, text="Iluminación:").        grid(column=0, row=0, sticky='SW')
        ttk.Spinbox(path_frame, textvariable=self.intensity,
                    increment=5, from_=0, to=100).         grid(column=1, row=0, sticky='SW')
        ttk.Label(path_frame, text="%").                   grid(column=1, row=0, sticky='SE')
        ttk.Label(path_frame, text="Carpeta:").            grid(column=0, row=1, sticky='SW')
        ttk.Label(path_frame, text=path_id).               grid(column=1, row=1, sticky='SW')
        ttk.Label(path_frame, textvariable=self.prefix).   grid(column=0, row=2, sticky='SW')
        ttk.Entry(path_frame, textvariable=self.big_id).   grid(column=1, row=2, sticky='SW')
        ttk.Label(path_frame, text="Captura:").            grid(column=0, row=3, sticky='SW')
        ttk.Entry(path_frame, textvariable=self.little_id).grid(column=1, row=3, sticky='SW')

        for key, entry in path_frame.children.items():
            if '!spinbox' == key:
                entry.configure(width=19)
            elif '!entry' in key:
                entry.configure(width=24)

        # Capture buttons
        self.capturar = ttk.Button(path_frame, text="Capturar", command=state.capture_action)
        # self.capturar.grid(column=0, row=4, sticky='SE')
        self.m1 = ttk.Button(path_frame, text="M1", command=lambda: state.capture_action('M1'))
        self.m1.grid(column=1, row=4, sticky='SW')
        self.m2 = ttk.Button(path_frame, text="M2", command=lambda: state.capture_action('M2'))
        self.m2.grid(column=1, row=4, sticky='SE')
        
        # Add text below the buttons
        self.text = ttk.Label(path_frame, text='')
        self.text.grid(column=0, row=5, columnspan=2, sticky='SWE')
        self.text_time_to_live = float('inf')
        self.properties_text = ttk.Label(path_frame, text='')
        self.properties_text.grid(column=0, row=6, columnspan=2, sticky='SWE')
        self.properties_text_time_to_live = 0
        """
        Time to live for the properties text message in seconds.
        
        -1 means that the user just set the property to it's correct value. But now the user has to press OK.
        Show a message for 1.5 seconds indicating so.
        """

        # Image
        self.image = None
        """Image to be displayed. If not saved, it will be garbage collected."""
        self.image_label = ttk.Label(self.mainframe)
        self.image_label.grid(row=0, column=1)

        # Actions on close and enter.
        self.root.protocol("WM_DELETE_WINDOW", self.__del__)
        self.root.bind("<Return>", state.capture_action)

        self.update()
        self.root.after(1800, self.state.lights.on)  # It doesn't work if done inmediately. ¯\_(ツ)_/¯
        if loop:
            self.root.mainloop()

    def lights_on(self):
        intensity = float(self.intensity.get()) * 255 / 100
        intensity = min(255, intensity)
        intensity = max(0, intensity)
        self.state.lights.on(int(intensity))

    def update(self, period=100):
        """Updates the state and, afterwads, the GUI."""

        if abs(self.state.cam.get(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U) - config.balance_de_blancos) <= 40:
            # Change the settings button color to gray: the camera has the appropriate settings.
            self.properties_button.configure(bg='gray')
            if self.properties_text_time_to_live == -1:
                # The user just corrected the settings.
                # Ask them to press OK for a while (we can't know when OK is pressed).
                self.properties_text.configure(text='Pulsa OK',
                                               font=('Helvetica', 15, 'bold'))
                self.properties_text_time_to_live = time.time() + 1.5  # 1.5 s is enough to press OK.
                self.properties_button.after(2000, self.clear_properties_text)
        else:
            # Change the settings button color to red: the camera doesn't have the appropriate settings.
            self.properties_button.configure(bg='#FF5957')  # Shade of red.
            self.properties_text.configure(text=WB_MESSAGE.format(white_balance=config.balance_de_blancos),
                                           font=('Helvetica', 15, 'bold'))
            self.properties_text_time_to_live = -1
        
        # Only when the state modifys the image, do we update it in the GUI.
        if self.state.image_updated:
            self.state.image_updated = False
            self.update_image(self.state.get_image(rgb=True))

        self.root.update()  # Ask tkinter to update the GUI.

        self.root.after(period, self.update)  # Schedule the next update.
    
    def update_image(self, image):
        # Tkinter takes PIL images.
        self.image = ImageTk.PhotoImage(Image.fromarray(image))
        self.image_label.configure(image=self.image)
        self.root.update()

    def unbold_text(self):
        text = self.text.cget('text')
        self.text.configure(text=text, font=('Arial', 9, 'normal'))
    
    def clear_text(self):
        """Clear the text about the file location if its time to live has expired."""
        if self.text_time_to_live < time.time():
            self.text.configure(foreground='black')
            if self.state.mode == Mode.CAPTURE:
                self.text.configure(text='')
            elif self.state.mode == Mode.CALIBRATE:
                self.text.configure(text='Captura el patrón de calibración de 7x10.')
            elif self.state.mode == Mode.CHECK:
                self.text.configure(text='Captura el patrón de comprobación de {}x{}.'
                                    .format(*config.dimensiones_patron_comprobacion))
            self.text.update()
    
    def clear_properties_text(self):
        """Clear the properties text if its time to live has expired."""
        if self.properties_text_time_to_live < time.time():
            self.properties_text.configure(text='')
            self.properties_text.update()

    def __del__(self):
        self.root.destroy()
        del self.state

    def set_mode(self, value: int):
        """Color the buttons according to the mode. Blue for the current one, gray for the others."""
        for index, button in enumerate(self.buttons):
            # Sade of blue or gray.
            color = '#ADD8E6' if index == value else 'gray'
            button.configure(bg=color)
