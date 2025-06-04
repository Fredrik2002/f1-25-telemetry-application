from ttkbootstrap import Toplevel, LEFT, Entry, IntVar, Label
from tkinter import Message, Checkbutton, Button
import json
from src.dictionnaries import valid_ip_address
from src.variables import dictionnary_settings, listener, PORT


class UDPRedirectWindow(Toplevel):
    def __init__(self):
        super().__init__()
        self.grab_set()
        self.wm_title("UDP Redirect")
        self.var1 = IntVar(value=dictionnary_settings["redirect_active"])
        checkbutton = Checkbutton(self, text="UDP Redirect", variable=var1, onvalue=1, offvalue=0, font=("Arial", 16))
        checkbutton.grid(row=0, column=0, sticky="W", padx=30, pady=10)
        Label(self, text="IP Address", font=("Arial", 16), justify=LEFT).grid(row=1, column=0, pady=10)

        self.entry1 = Entry(self, font=("Arial", 16))
        self.entry1.insert(0, dictionnary_settings["ip_adress"])
        self.entry1.grid(row=2, column=0)
        Label(self, text="Port", font=("Arial", 16)).grid(row=3, column=0, pady=(10, 5))
        self.entry2 = Entry(self, font=("Arial", 16))
        self.entry2.insert(0, dictionnary_settings["redirect_port"])
        self.entry2.grid(row=4, column=0, padx=30)

        self.bind('<Return>', lambda e: self.button())
        self.bind('<KP_Enter>', lambda e: self.button())
        b = Button(self, text="Confirm", font=("Arial", 16), command=self.button)
        b.grid(row=5, column=0, pady=10)

    def button(self):
        redirect_port = self.entry2.get()
        if not redirect_port.isdigit() or not 1000 <= int(redirect_port) <= 65536:
            Message(self, text="The PORT must be an integer between 1000 and 65536", fg="red", font=("Arial", 16)).grid(
                row=6, column=0)
        elif not valid_ip_address(self.entry1.get()):
            Label(self, text="IP Address incorrect", foreground="red", font=("Arial", 16)).grid(
                row=6, column=0)
        else:
            listener.port = int(PORT[0])
            listener.redirect = int(self.var1.get())
            listener.adress = self.entry1.get()
            listener.redirect_port = int(self.entry2.get())
            Label(self, text="").grid(row=3, column=0)

            dictionnary_settings["redirect_active"] = self.var1.get()
            dictionnary_settings["ip_adress"] = self.entry1.get()
            dictionnary_settings["redirect_port"] = self.entry2.get()
            with open("../settings.txt", "w") as f:
                json.dump(dictionnary_settings, f)
            self.destroy()



