import time

from dictionnaries import *
from src.map_management import *


def update_motion(packet, map_canvas, *args):  # Packet 0
    for i in range(22):
        LISTE_JOUEURS[i].worldPositionX = packet.m_car_motion_data[i].m_world_position_x
        LISTE_JOUEURS[i].worldPositionZ = packet.m_car_motion_data[i].m_world_position_z
    try:
        update_map(map_canvas)
    except Exception as e: # The map is not created yet
        create_map(map_canvas)


def update_session(packet, top_frame1, top_frame2, screen, map_canvas):  # Packet 1
    global created_map
    session.trackTemperature = packet.m_weather_forecast_samples[0].m_track_temperature
    session.airTemperature = packet.m_weather_forecast_samples[0].m_air_temperature
    session.nbLaps = packet.m_total_laps
    session.time_left = packet.m_session_time_left
    if session.track != packet.m_track_id or session.Seance != packet.m_session_type: # Track or session has changed
        session.track = packet.m_track_id
        delete_map(map_canvas)
    session.Seance = packet.m_session_type
    session.marshalZones = packet.m_marshal_zones  # Array[21]
    session.marshalZones[0].m_zone_start = session.marshalZones[0].m_zone_start - 1
    session.num_marshal_zones = packet.m_num_marshal_zones
    session.safetyCarStatus = packet.m_safety_car_status
    session.trackLength = packet.m_track_length
    session.clear_slot()
    if packet.m_num_weather_forecast_samples != session.nb_weatherForecastSamples:
        session.nb_weatherForecastSamples = packet.m_num_weather_forecast_samples
    for i in range(session.nb_weatherForecastSamples):
        slot = packet.m_weather_forecast_samples[i]
        session.add_slot(slot)

def update_lap_data(packet):  # Packet 2
    mega_array = packet.m_lap_data
    for index in range(22):
        element = mega_array[index]
        joueur = LISTE_JOUEURS[index]
        joueur.position = element.m_car_position
        joueur.lastLapTime = round(element.m_last_lap_time_in_ms, 3)
        joueur.pit = element.m_pit_status
        joueur.driverStatus = element.m_driver_status
        joueur.penalties = element.m_penalties
        joueur.warnings = element.m_corner_cutting_warnings
        joueur.speed_trap = round(element.m_speedTrapFastestSpeed, 2)
        joueur.currentLapTime = element.m_current_lap_time_in_ms
        joueur.gap_to_leader=element.m_deltaToCarInFrontMSPart
        joueur.currentLapInvalid = element.m_current_lap_invalid

        if element.m_sector1_time_in_ms == 0 and joueur.currentSectors[0] != 0:  # On attaque un nouveau tour
            joueur.lastLapSectors = joueur.currentSectors[:]
            joueur.lastLapSectors[2] = joueur.lastLapTime / 1_000 - joueur.lastLapSectors[0] - joueur.lastLapSectors[1]

        joueur.currentSectors = [element.m_sector1_time_in_ms / 1000, element.m_sector2_time_in_ms / 1000, 0]
        if joueur.fastestLapTime > element.m_last_lap_time_in_ms != 0 or joueur.fastestLapTime == 0:
            joueur.fastestLapTime = element.m_last_lap_time_in_ms
            joueur.bestLapSectors = joueur.lastLapSectors[:]
        if joueur.fastestLapTime < session.fastestLapTime and element.m_last_lap_time_in_ms != 0 or joueur.fastestLapTime == 0:
            session.fastestLapTime = joueur.fastestLapTime
            session.idxBestLapTime = index
        if element.m_car_position == 1:
            session.currentLap = mega_array[index].m_current_lap_num
            session.tour_precedent = session.currentLap - 1

def warnings(packet):  # Packet 3
    if packet.m_event_string_code[3] == 71 and packet.m_event_details.m_start_lights.m_num_lights >= 2: # Starts lights : STLG
        session.formationLapDone = True
        print(f"{packet.m_event_details.m_start_lights.m_num_lights} red lights ")
    elif packet.m_event_string_code[0] == 76 and session.formationLapDone: #Lights out : LGOT
        print("Lights out !")
        session.formationLapDone = False
        session.startTime = time.time()
        for joueur in LISTE_JOUEURS:
            joueur.S200_reached = False
            joueur.warnings = 0
            joueur.lastLapSectors = [0] * 3
            joueur.bestLapSectors = [0] * 3
            joueur.lastLapTime: float = 0
            joueur.currentSectors = [0] * 3
            joueur.fastestLapTime = 0
    elif packet.m_event_string_code[2] == 82:
        LISTE_JOUEURS[packet.m_event_details.m_vehicle_idx].hasRetired = True

def update_participants(packet):  # Packet 4
    for index in range(22):
        element = packet.m_participants[index]
        joueur = LISTE_JOUEURS[index]
        joueur.raceNumber = element.m_race_number
        joueur.teamId = element.m_team_id
        joueur.aiControlled = element.m_ai_controlled
        joueur.yourTelemetry = element.m_your_telemetry
        try:
            joueur.name = element.m_name.decode("utf-8")
        except:
            joueur.name = element.m_name
        session.nb_players = packet.m_num_active_cars
        if joueur.name in ['Pilote', 'Driver']: # More translations appreciated
            joueur.name = teams_name_dictionary[joueur.teamId] + "#" + str(joueur.raceNumber)

def update_car_setups(packet): # Packet 5
    array = packet.m_car_setups
    for index in range(22):
        LISTE_JOUEURS[index].setup_array = array[index]

def update_car_telemetry(packet):  # Packet 6
    for index in range(22):
        element = packet.m_car_telemetry_data[index]
        joueur = LISTE_JOUEURS[index]
        joueur.drs = element.m_drs
        joueur.tyres_temp_inner = element.m_tyres_inner_temperature
        joueur.tyres_temp_surface = element.m_tyres_surface_temperature
        joueur.speed = element.m_speed
        if joueur.speed >= 200 and not joueur.S200_reached:
            print(f"{joueur.position} {joueur.name}  = {time.time() - session.startTime}")
            joueur.S200_reached = True

def update_car_status(packet):  # Packet 7
    for index in range(22):
        element = packet.m_car_status_data[index]
        joueur = LISTE_JOUEURS[index]
        joueur.fuelMix = element.m_fuel_mix
        joueur.fuelRemainingLaps = element.m_fuel_remaining_laps
        joueur.tyresAgeLaps = element.m_tyres_age_laps
        if joueur.tyres != element.m_visual_tyre_compound:
            joueur.tyres = element.m_visual_tyre_compound
        joueur.ERS_mode = element.m_ers_deploy_mode
        joueur.ERS_pourcentage = round(element.m_ers_store_energy / 40_000)

def update_car_damage(packet):  # Packet 10
    for index in range(22):
        element = packet.m_car_damage_data[index]
        joueur = LISTE_JOUEURS[index]
        joueur.tyre_wear = '[' + ', '.join('%.2f'%truc for truc in element.m_tyres_wear) + ']'
        joueur.tyre_blisters = '[' + ', '.join(str(truc) for truc in element.m_tyre_blisters) + ']'
        joueur.FrontLeftWingDamage = element.m_front_left_wing_damage
        joueur.FrontRightWingDamage = element.m_front_right_wing_damage
        joueur.rearWingDamage = element.m_rear_wing_damage
        joueur.floorDamage = element.m_floor_damage
        joueur.diffuserDamage = element.m_diffuser_damage
        joueur.sidepodDamage = element.m_sidepod_damage

def nothing(packet):# Packet 8, 9, 11, 12, 13
    pass










