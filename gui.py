import sys
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk


class GUI:
    def __init__(self, state, path_id='D:/HANDSCANNER_DATA/', loop=True):
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
        button_names    = ['Nuevo usuario', 'Calibración', 'Comprobar calibración', 'Encender luces', 'Apagar luces', 'Zoom +',  'Zoom -',   'Zoom reset']
        button_commands = [s.new_capture,   s.calibrate,   s.check,     s.lights.on,      s.lights.off,   s.zoom_in, s.zoom_out, s.zoom_reset]
        buttons = [tk.Button(mode_frame, text=txt, command=cmd) for txt, cmd in zip(button_names, button_commands)]
        for index, button in enumerate(buttons):
            button.grid(column=0, row=index, sticky='W')
            button.configure(width=25)
        self.buttons = buttons[:3]
        self.set_mode(state.mode.value)

        # Capture path and name
        self.path_id   = tk.StringVar(value=path_id)
        self.big_id    = tk.StringVar(value='TEN_0000')
        self.little_id = tk.StringVar(value='M1')

        path_frame = tk.Frame(self.left_frame)
        path_frame.grid(column=0, row=1, sticky='W')
        ttk.Label(path_frame, text="Carpeta:").            grid(column=0, row=0, sticky='SW')
        ttk.Label(path_frame, text=path_id).               grid(column=1, row=0, sticky='SW')
        ttk.Label(path_frame, text="Serie:  ").            grid(column=0, row=1, sticky='SW')
        ttk.Entry(path_frame, textvariable=self.big_id).   grid(column=1, row=1, sticky='SW')
        ttk.Label(path_frame, text="Captura:").            grid(column=0, row=2, sticky='SW')
        ttk.Entry(path_frame, textvariable=self.little_id).grid(column=1, row=2, sticky='SW')

        for key, entry in path_frame.children.items():
            if '!entry' in key:
                entry.configure(width=28)

        ttk.Button(path_frame, text="Capturar", command=state.capture_action).grid(column=0, row=3, sticky='SE')
        # Add text below the button
        self.text = ttk.Label(path_frame, text=self.state.text)
        self.text.grid(column=1, row=4, sticky='SW')

        # Image
        self.image = None
        self.image_label = ttk.Label(self.mainframe)
        self.image_label.grid(row=0, column=1)

        self.root.protocol("WM_DELETE_WINDOW", self.__del__)
        self.root.bind("<Return>", state.capture_action)

        self.update()
        self.root.after(10, self.update)
        self.root.after(1000, self.state.lights.on)
        if loop:
            self.root.mainloop()

    def update(self, period=10, update_state=True):
        self.state.update()

        self.text.configure(text=self.state.text)

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
        for index, button in enumerate(self.buttons):
            color = 'blue' if index == value else 'gray'
            button.configure(bg=color)

