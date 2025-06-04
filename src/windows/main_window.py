from ttkbootstrap import Window, Notebook, Frame, Canvas, Menu, Label
from src.Custom_Frame import Players_Frame, Weather_Forecast_Frame, Packet_Reception_Frame
from src.windows.UDP_redirect_window import UDPRedirectWindow
from src.windows.port_selection_window import PortSelectionWindow
from src.variables import *
from src.packet_management import *
import time

class MainWindow(Window):
    def __init__(self):
        self.running = True

        super().__init__(themename="darkly")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, pad=75)
        self.rowconfigure(1, weight=1)

        self.title("Telemetry Application")

        self.top_frame = Frame(self)
        self.main_frame = Frame(self)

        self.top_label1 = Label(self.top_frame, text="Race ", font=("Arial", 24))  # title label, needs to be accessed by update_session
        self.top_label2 = Label(self.top_frame, text="", font=("Arial", 24), width=10)  # Flag label, needs to be accessed by update_session

        self.top_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")
        self.main_frame.grid(row=1, column=0, sticky="nsew")

        self.notebook = Notebook(self.main_frame)
        self.notebook.pack(expand=True, fill="both")

        LISTE_FRAMES.append(Players_Frame(self.notebook, "Main Menu", 0))
        LISTE_FRAMES.append(Players_Frame(self.notebook, "Damage", 1))
        LISTE_FRAMES.append(Players_Frame(self.notebook, "Temperatures", 2))
        LISTE_FRAMES.append(Players_Frame(self.notebook, "Laps", 3))
        LISTE_FRAMES.append(Players_Frame(self.notebook, "ERS & Fuel", 4))

        self.map = Frame(self.notebook)
        LISTE_FRAMES.append(self.map)
        self.map.pack(expand=True, fill="both")
        self.map_canvas = Canvas(self.map)
        self.map_canvas.pack(expand=True, fill='both')

        LISTE_FRAMES.append(Weather_Forecast_Frame(self.notebook, "Weather Forecast", 6, 20))
        LISTE_FRAMES.append(Packet_Reception_Frame(self.notebook, "Packet Reception", 7))

        for i in range(8):
            if i != 5:
                self.notebook.add(LISTE_FRAMES[i], text=LISTE_FRAMES[i].name)
            else:
                self.notebook.add(LISTE_FRAMES[5], text="Map")

        self.top_label1.place(relx=0.0, rely=0.5, anchor='w')
        self.top_label2.place(relx=1, rely=0.5, anchor='e', relheight=1)
        self.top_frame.columnconfigure(0, weight=3)

        self.geometry("1480x800")
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        menubar = Menu(self)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="PORT Selection", command=PortSelectionWindow)
        filemenu.add_command(label="UDP Redirect", command=UDPRedirectWindow)
        menubar.add_cascade(label="Settings", menu=filemenu)
        self.config(menu=menubar)

    def close_window(self):
        self.running = False

    def run(self):
        function_hashmap = {  # PacketId : (fonction, arguments)
            0: (update_motion, (self.map_canvas, None)),  # PacketMotion
            1: (update_session, (self.top_label1, self.top_label2, self, self.map_canvas)),  # PacketSession
            2: (update_lap_data, ()),  # PacketLapData
            3: (warnings, ()),  # PacketEvent
            4: (update_participants, ()),  # PacketParticipants
            5: (update_car_setups, ()),  # PacketCarSetup
            6: (update_car_telemetry, ()),  # PacketCarTelemetry
            7: (update_car_status, ()),  # PacketCarStatus
            8: (nothing, ()),  # PacketFinalClassification
            9: (nothing, ()),  # PacketLobbyInfo
            10: (update_car_damage, ()),  # PacketCarDamage
            11: (nothing, ()),  # PacketSessionHistory
            12: (nothing, ()),
            13: (nothing, ()),
            14: (nothing, ()),
            15: (nothing, ())
        }

        packet_received = [0] * 16
        last_update = time.time()

        while self.running:
            a = listener.get()
            if a is not None:
                header, packet = a
                packet_received[header.m_packet_id] += 1
                func, args = function_hashmap[header.m_packet_id]
                func(packet, *args)
            if time.time() > last_update + 1:
                last_update = time.time()
                LISTE_FRAMES[7].update(packet_received)  # Packet Received tab
                session.packet_received = packet_received[:]
                packet_received = [0] * 16
            self.update()
            self.update_idletasks()

        listener.socket.close()
        quit()

