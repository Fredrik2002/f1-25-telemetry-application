import sys
import os

# Ajouter le dossier parent au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.parsers.parser2025 import Listener
track = "silverstone"

PORT=20777
file=open(f"../tracks/{track}_2020_racingline.txt", "a")
file.write(f'"Track file for {track}","2020-07-01 19:31:18",0.000,4,1,v3" \n')
file.write(f'"dist","pos_z","pos_x","pos_y","drs","sector" \n')

listener = Listener(port = PORT)
lap_packet, motion_packet, tel_packet = None, None, None
last_lap_distance = 0

while True:
    a = listener.get()
    if a is not None:
        header, packet = a
        car_index = header.m_player_car_index
        if header.m_packet_id == 2 and packet.m_lap_data[car_index].m_lap_distance<500:
            break

print("démarrage")

while True:
    a = listener.get()
    if a is not None:
        header, packet = a
        if header.m_packet_id == 0:
            motion_packet = (packet.m_car_motion_data[car_index].m_world_position_z,
            packet.m_car_motion_data[car_index].m_world_position_x,
            packet.m_car_motion_data[car_index].m_world_position_y)
        elif header.m_packet_id == 2:
            lap_packet = packet.m_lap_data[car_index].m_lap_distance, packet.m_lap_data[car_index].m_sector
            if last_lap_distance>lap_packet[0]:
                break
            last_lap_distance=lap_packet[0]
        elif header.m_packet_id == 6:
            tel_packet = packet.m_car_telemetry_data[car_index].m_drs
        if not (lap_packet is None or motion_packet is None or tel_packet is None):
            a, f = lap_packet
            b,c,d = motion_packet
            e = tel_packet
            file.write(f"{a},{c},{b},{d},{e},{f}\n")
            lap_packet, motion_packet, tel_packet = None, None, None

listener.close()





