from ttkbootstrap import Toplevel, LEFT, Entry, IntVar, Label
from tkinter import Message, Checkbutton, Button
from src.variables import *

import json


class PortSelectionWindow(Toplevel):
    def __init__(self):
        super().__init__()
        self.grab_set()
        self.wm_title("Port Selection")
        Label(self, text="Receiving PORT :", font=("Arial", 16)).grid(row=0, column=0, sticky="we", padx=30)

        self.entry = Entry(self, font=("Arial", 16))
        self.entry.insert(0, dictionnary_settings["port"])
        self.entry.grid(row=1, column=0, padx=30)

        self.bind('<Return>', lambda e: self.button())
        self.bind('<KP_Enter>', lambda e: self.button())
        b = Button(self, text="Confirm", font=("Arial", 16), command=self.button)
        b.grid(row=2, column=0, pady=10)


    def button(self):
        PORT[0] = self.entry.get()
        if not PORT[0].isdigit() or not 1000 <= int(PORT[0]) <= 65536:
            Message(self, text="The PORT must be an integer between 1000 and 65536", fg="red",
                    font=("Arial", 16)).grid(
                row=3, column=0)
        else:
            listener.socket.close()
            listener.port = int(PORT[0])
            listener.reset()
            Label(self, text="").grid(row=3, column=0)
            dictionnary_settings["port"] = str(PORT[0])
            with open("../../settings.txt", "w") as f:
                json.dump(dictionnary_settings, f)
            self.destroy()