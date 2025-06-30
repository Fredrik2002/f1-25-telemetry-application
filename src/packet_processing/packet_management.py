import time

from PyQt5.QtWidgets import QListWidget

import src
from src.packet_processing.dictionnaries import *
from src.packet_processing.variables import format_milliseconds
from src.packet_processing.variables import *


def update_motion(packet, *args):  # Packet 0
    for i in range(22):
        PLAYERS_LIST[i].worldPositionX = packet.m_car_motion_data[i].m_world_position_x
        PLAYERS_LIST[i].worldPositionZ = packet.m_car_motion_data[i].m_world_position_z


def update_session(packet):  # Packet 1
    session.trackTemperature = packet.m_weather_forecast_samples[0].m_track_temperature
    session.airTemperature = packet.m_weather_forecast_samples[0].m_air_temperature
    session.nbLaps = packet.m_total_laps
    session.time_left = packet.m_session_time_left
    if session.track != packet.m_track_id or session.Session != packet.m_session_type: # Track or session has changed
        session.track = packet.m_track_id
        src.packet_processing.variables.REDRAW_MAP = True
    session.Session = packet.m_session_type
    session.marshalZones = packet.m_marshal_zones  # Array[21]
    session.marshalZones[0].m_zone_start = session.marshalZones[0].m_zone_start - 1
    session.num_marshal_zones = packet.m_num_marshal_zones
    session.safetyCarStatus = packet.m_safety_car_status
    session.trackLength = packet.m_track_length
    session.clear_slot()
    if packet.m_num_weather_forecast_samples != session.nb_weatherForecastSamples:
        session.nb_weatherForecastSamples = packet.m_num_weather_forecast_samples
    session.weatherList = packet.m_weather_forecast_samples


def update_lap_data(packet):  # Packet 2
    global POSITION_CHANGED
    mega_array = packet.m_lap_data
    for index in range(22):
        element = mega_array[index]
        joueur = PLAYERS_LIST[index]

        if joueur.position != element.m_car_position:
            POSITION_CHANGED = True
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
        joueur.resultStatus = element.m_result_status

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


def update_event(packet, qlist : QListWidget):  # Packet 3
    code = "".join(map(chr, packet.m_event_string_code))
    if code == "STLG" and packet.m_event_details.m_start_lights.m_num_lights >= 2: # Start Lights
        session.formationLapDone = True
        qlist.insertItem(0, f"{packet.m_event_details.m_start_lights.m_num_lights} red lights ")
    elif code == "LGOT" and session.formationLapDone: # Lights out
        qlist.insertItem(0, "Lights out !")
        session.formationLapDone = False
        session.startTime = time.time()
        for joueur in PLAYERS_LIST:  # We reset all the datas (which were from qualifying)
            joueur.reset()
    elif code == "RTMT":  # Retirement
        PLAYERS_LIST[packet.m_event_details.m_retirement.m_vehicle_idx].hasRetired = True
        qlist.insertItem(0, f"{PLAYERS_LIST[packet.m_event_details.m_retirement.m_vehicle_idx].name} retired : " +
                         f"{retirements_dictionnary[packet.m_event_details.m_retirement.m_reason]}")
    elif code == "FTLP":  # Fastest Lap
        qlist.insertItem(0, f"Fastest Lap : {PLAYERS_LIST[packet.m_event_details.m_fastest_lap.m_vehicle_idx].name} - "
                            f"{format_milliseconds(packet.m_event_details.m_fastest_lap.m_lap_time*1000)}")
    elif code == "DRSD":  # DRS Disabled
        qlist.insertItem(0, f"DRS Disabled : {drs_disabled_reasons[packet.m_event_details.m_drs_disabled.m_reason]}")
    elif code == "DRSE":  # DRS Enabled
        qlist.insertItem(0, "DRS Enabled")
    elif code == "CHQF":
        qlist.insertItem(0, "Chequered Flag")


def update_participants(packet):  # Packet 4
    if session.nb_players != packet.m_num_active_cars:
        src.packet_processing.variables.REDRAW_MAP = True
        session.nb_players = packet.m_num_active_cars

    for index in range(22):
        element = packet.m_participants[index]
        joueur = PLAYERS_LIST[index]
        joueur.raceNumber = element.m_race_number
        joueur.teamId = element.m_team_id
        joueur.aiControlled = element.m_ai_controlled
        joueur.yourTelemetry = element.m_your_telemetry
        if joueur.networkId != element.m_network_id:
            joueur.networkId = element.m_network_id
            src.packet_processing.variables.REDRAW_MAP = True
        try:
            joueur.name = element.m_name.decode("utf-8")
        except:
            joueur.name = element.m_name

        if joueur.name in ['Pilote', 'Driver']: # More translations appreciated
            joueur.name = teams_name_dictionary[joueur.teamId] + "#" + str(joueur.raceNumber)

def update_car_setups(packet): # Packet 5
    array = packet.m_car_setups
    for index in range(22):
        PLAYERS_LIST[index].setup_array = array[index]

def update_car_telemetry(packet):  # Packet 6
    for index in range(22):
        element = packet.m_car_telemetry_data[index]
        joueur = PLAYERS_LIST[index]
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
        joueur = PLAYERS_LIST[index]
        joueur.fuelMix = element.m_fuel_mix
        joueur.fuelRemainingLaps = element.m_fuel_remaining_laps
        joueur.tyresAgeLaps = element.m_tyres_age_laps
        if joueur.tyres != element.m_visual_tyre_compound:
            joueur.tyres = element.m_visual_tyre_compound
        joueur.ERS_mode = element.m_ers_deploy_mode
        joueur.ERS_pourcentage = round(element.m_ers_store_energy / 40_000)
        joueur.DRS_allowed = element.m_drs_allowed
        joueur.DRS_activation_distance = element.m_drs_activation_distance

def update_car_damage(packet):  # Packet 10
    for index in range(22):
        element = packet.m_car_damage_data[index]
        joueur = PLAYERS_LIST[index]
        joueur.tyre_wear = ['%.2f'%tyre for tyre in element.m_tyres_wear]
        joueur.tyre_blisters = ['%.2f'%tyre for tyre in element.m_tyre_blisters]
        joueur.frontLeftWingDamage = element.m_front_left_wing_damage
        joueur.frontRightWingDamage = element.m_front_right_wing_damage
        joueur.rearWingDamage = element.m_rear_wing_damage
        joueur.floorDamage = element.m_floor_damage
        joueur.diffuserDamage = element.m_diffuser_damage
        joueur.sidepodDamage = element.m_sidepod_damage

def nothing(packet):# Packet 8, 9, 11, 12, 13
    pass










