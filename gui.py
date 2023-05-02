import sys
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk


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
        button_names    = ['Nuevo usuario', 'Calibración', 'Comprobar calibración', 'Encender luces', 'Apagar luces', 'Zoom +', 'Zoom -', 'Zoom reset']
        button_commands = [s.new_capture, s.calibrate, s.check, self.lights_on, s.lights.off, s.zoom_in, s.zoom_out, s.zoom_reset]
        buttons = [tk.Button(mode_frame, text=txt, command=cmd) for txt, cmd in zip(button_names, button_commands)]
        for index, button in enumerate(buttons):
            button.grid(column=0, row=index, sticky='W')
            button.configure(width=30)
        self.buttons = buttons[:3]
        self.set_mode(state.mode.value)

        # Capture path and name
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
        ttk.Button(path_frame, text="M1", command=lambda: state.capture_action('M1')).grid(column=1, row=4, sticky='SE')
        ttk.Button(path_frame, text="M2", command=lambda: state.capture_action('M2')).grid(column=1, row=4, sticky='SW')
        # Add text below the button
        self.text = ttk.Label(path_frame, text=self.state.text)
        self.text.grid(column=0, row=5, columnspan=2, sticky='SWE')

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

    def update(self, period=10, update_state=True):
        """Updates the state and, afterwads, the GUI."""
        self.state.update()

        self.text.configure(text=self.state.text)
        # Okay, bear with me. So, self.state.capture_action adds a bunch of '\0' to the end of the string.
        # Every time that we update the GUI, we remove one of them. When all of them are removed, we remove the text.
        # This is basically a timer to remove the text. A poorly implemented one, I know.
        if len(self.state.text) > 2 and self.state.text[-1] == '\0':
            if self.state.text[-2] == '\0':
                self.state.text = self.state.text[:-1]
            else:
                self.state.text = ''

        # Only when the state modifys the image, do we update it in the GUI.
        if self.state.image_updated:
            self.state.image_updated = False
            self.image = ImageTk.PhotoImage(Image.fromarray(self.state.get_image()[..., ::-1]))
            self.image_label.configure(image=self.image)

        self.root.update()

        self.root.after(period, self.update)

    def __del__(self):
        self.root.destroy()
        del self.state

    def set_mode(self, value: int):
        """Color the buttons according to the mode. Blue for the current one, grey for the others."""
        for index, button in enumerate(self.buttons):
            color = 'blue' if index == value else 'gray'
            button.configure(bg=color)
