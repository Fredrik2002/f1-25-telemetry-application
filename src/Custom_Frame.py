from ttkbootstrap import Frame, Label
from Player import Player
from src.dictionnaries import teams_color_dictionary, packetDictionnary, tyres_dictionnary, tyres_color_dictionnary, grey
from Session import Session


class Custom_Frame(Frame): # Frame Tableau
    def __init__(self, parent, name, id, n_lines):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.name = name
        self.id = id
        self.n_lines = n_lines
        self.liste_frame = []
        for i in range(n_lines):
            frame = Frame(self)
            frame.grid(row=i, column=0, sticky="nsew", pady=2, padx=5)
            label = Label(frame, text="Driver"+str(i), font="Helvetica 12")
            label.pack(side='left')
            self.liste_frame.append((frame, label))
        self.pack(expand=True, fill="both")


class Players_Frame(Custom_Frame):
    def __init__(self, parent, name, id):
        super().__init__(parent, name, id, 20)
        self.label_tyres = []
        for i in range(self.n_lines):
            label = Label(self.liste_frame[i][0], text="S", foreground="#FF0000", font="Helvetica 12")
            label.pack(side='left')
            self.liste_frame[i][1].pack_forget()
            self.liste_frame[i][1].pack(side='left')
            self.label_tyres.append(label)

    def update(self, LISTE_JOUEURS:list[Player], session):
        if session.Seance != 18:
            for i in range(22):
                joueur = LISTE_JOUEURS[i]
                if joueur.position == 0:
                    continue
                frame, label = self.liste_frame[joueur.position-1]
                label.config(text=joueur.printing(self.id, LISTE_JOUEURS, session.Seance), foreground=teams_color_dictionary[joueur.teamId])
                self.label_tyres[joueur.position-1].config(text=tyres_dictionnary[joueur.tyres], foreground=tyres_color_dictionnary[joueur.tyres])
            for i in range(session.nb_players, self.n_lines):
                self.liste_frame[i][1].config(text="")
                self.label_tyres[i].config(text="")
        else:
            joueur = LISTE_JOUEURS[0]
            record = LISTE_JOUEURS[1]
            rival = LISTE_JOUEURS[3]

            frame, label = self.liste_frame[0]
            label.config(text=joueur.printing(self.id, LISTE_JOUEURS, session.Seance), foreground=teams_color_dictionary[joueur.teamId])
            self.label_tyres[0].config(text=tyres_dictionnary[joueur.tyres], foreground=tyres_color_dictionnary[joueur.tyres])

            frame, label = self.liste_frame[1]
            label.config(text=record.printing(self.id, LISTE_JOUEURS, session.Seance), foreground=teams_color_dictionary[record.teamId])
            self.label_tyres[1].config(text=tyres_dictionnary[record.tyres], foreground=tyres_color_dictionnary[record.tyres])

            frame, label = self.liste_frame[2]
            label.config(text=rival.printing(self.id, LISTE_JOUEURS, session.Seance), foreground=teams_color_dictionary[rival.teamId])
            self.label_tyres[2].config(text=tyres_dictionnary[rival.tyres], foreground=tyres_color_dictionnary[rival.tyres])

            for i in range(3, self.n_lines):
                frame, label = self.liste_frame[i]
                label.config(text="")
                self.label_tyres[i].config(text="")


class Packet_Reception_Frame(Custom_Frame):
    def __init__(self, parent, name, id):
        super().__init__(parent, name, id, 15)

    def update(self, packet_received):
        for i in range(self.n_lines):
            frame, label = self.liste_frame[i]
            label.config(text=f"{packetDictionnary[i]} : {packet_received[i]}/s")


class Weather_Forecast_Frame(Custom_Frame):
    def __init__(self, parent, name, id, n_lines):
        super().__init__(parent, name, id, n_lines)

    def update(self, session : Session):
        try:
            for i in range(session.nb_weatherForecastSamples):
                frame, label = self.liste_frame[i]
                label.config(text=session.weatherList[i])
            for i in range(session.nb_weatherForecastSamples, 20):
                frame, label = self.liste_frame[i]
                label.config(text="")
        except: pass
        

