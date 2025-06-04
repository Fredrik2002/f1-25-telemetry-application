from ttkbootstrap import Toplevel, LEFT, Entry, IntVar, Label
from tkinter import Message, Checkbutton, Button

def UDP_Redirect(dictionnary_settings, listener, PORT):
    win = Toplevel()
    win.grab_set()
    win.wm_title("UDP Redirect")
    var1 = IntVar(value=dictionnary_settings["redirect_active"])
    checkbutton = Checkbutton(win, text="UDP Redirect", variable=var1, onvalue=1, offvalue=0, font=("Arial", 16))
    checkbutton.grid(row=0, column=0, sticky="W", padx=30, pady=10)
    Label(win, text="IP Address", font=("Arial", 16), justify=LEFT).grid(row=1, column=0, pady=10)
    e1 = Entry(win, font=("Arial", 16))
    e1.insert(0, dictionnary_settings["ip_adress"])
    e1.grid(row=2, column=0)
    Label(win, text="Port", font=("Arial", 16)).grid(row=3, column=0, pady=(10, 5))
    e2 = Entry(win, font=("Arial", 16))
    e2.insert(0, dictionnary_settings["redirect_port"])
    e2.grid(row=4, column=0, padx=30)

    def button():
        redirect_port = e2.get()
        if not redirect_port.isdigit() or not 1000 <= int(redirect_port) <= 65536:
            Message(win, text="The PORT must be an integer between 1000 and 65536", fg="red", font=("Arial", 16)).grid(row=6, column=0)
        elif not valid_ip_address(e1.get()):
            Label(win, text="Incorrect IP Address", foreground="red", font=("Arial", 16)).grid(
                row=6, column=0)
        else:
            listener.port = int(PORT[0])
            listener.redirect = int(var1.get())
            listener.adress = e1.get()
            listener.redirect_port = int(e2.get())
            Label(win, text="").grid(row=3, column=0)

            dictionnary_settings["redirect_active"] = var1.get()
            dictionnary_settings["ip_adress"] = e1.get()
            dictionnary_settings["redirect_port"] = e2.get()
            with open("../settings.txt", "w") as f:
                json.dump(dictionnary_settings, f)
            win.destroy()

    win.bind('<Return>', lambda e: button())
    win.bind('<KP_Enter>', lambda e: button())
    b = Button(win, text="Confirm", font=("Arial", 16), command=button)
    b.grid(row=5, column=0, pady=10)

