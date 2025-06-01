import ctypes
import socket
import pprint

pp = pprint.PrettyPrinter()


class Listener:
    def __init__(self, port=20777, adress="127.0.0.1", redirect=0, redirect_port=20777):
        self.port = port
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind(('', port))
        self.socket.setblocking(0)
        self.address = adress
        self.redirect = redirect
        self.redirect_port = redirect_port

    def reset(self):
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind(('', self.port))
        self.socket.setblocking(0)

    def get(self, packet=None):
        if packet is None:
            try:
                packet = self.socket.recv(2048)
                if self.redirect == 1:
                    self.socket.sendto(packet, (self.address, self.redirect_port))
            except ConnectionResetError: #Thrown when redirecting on a localhost port that is not ready to read the datas
                return None
            except:
                return None

        header = PacketHeader.from_buffer_copy(packet)
        return header, HEADER_FIELD_TO_PACKET_TYPE[header.m_packet_id].from_buffer_copy(packet)
    
    def __str__(self) -> str:
        return str(self.__dict__)
    
    def __repr__(self) -> str:
        return str(self.__dict__)


class PacketMixin(object):
    """A base set of helper methods for ctypes based packets"""

    def get_value(self, field):
        """Returns the field's value and formats the types value"""
        return self._format_type(getattr(self, field))

    def pack(self):
        """Packs the current data structure into a compressed binary

        Returns:
            (bytes):
                - The packed binary

        """
        return bytes(self)

    @classmethod
    def size(cls):
        return ctypes.sizeof(cls)

    @classmethod
    def unpack(cls, buffer):
        """Attempts to unpack the binary structure into a python structure

        Args:
            buffer (bytes):
                - The encoded buffer to decode

        """
        return cls.from_buffer_copy(buffer)

    def to_dict(self):
        """Returns a ``dict`` with key-values derived from _fields_"""
        return {k: self.get_value(k) for k, _ in self._fields_}

    def to_json(self):
        """Returns a ``str`` of sorted JSON derived from _fields_"""
        return str(self.to_dict())

    def _format_type(self, value):
        """A type helper to format values"""
        class_name = type(value).__name__

        if class_name == "float":
            return round(value, 3)

        if class_name == "bytes":
            return value.decode()

        '''if isinstance(value, ctypes.Array):
            return _format_array_type(value)'''

        if hasattr(value, "to_dict"):
            return value.to_dict()

        return value


class Packet(ctypes.LittleEndianStructure, PacketMixin):
    _pack_ = 1

    def __str__(self):
        return pp.pformat(self.to_dict())

    def __repr__(self):
        return pp.pformat(self.to_dict())


class PacketHeader(Packet):
    _fields_ = [
        ("m_packet_format", ctypes.c_uint16),  # 2021
        ("m_game_year", ctypes.c_uint8), #23
        ("m_game_major_version", ctypes.c_uint8),  # Game major version - "X.00"
        ("m_game_minor_version", ctypes.c_uint8),  # Game minor version - "1.XX"
        ("m_packet_version", ctypes.c_uint8),
        # Version of this packet type, all start from 1
        ("m_packet_id", ctypes.c_uint8),  # Identifier for the packet type, see below
        ("m_session_uid", ctypes.c_uint64),  # Unique identifier for the session
        ("m_session_time", ctypes.c_float),  # Session timestamp
        ("m_frame_identifier", ctypes.c_uint32),
        ("m_overall_frame_identifier", ctypes.c_uint32),
        # Identifier for the frame the data was retrieved on
        ("m_player_car_index", ctypes.c_uint8),  # Index of player's car in the array
        ("m_secondary_player_car_index", ctypes.c_uint8),
        # Index of secondary player's car in the array (splitscreen)
        # 255 if no second player
    ]


class CarMotionData(Packet):
    _fields_ = [
        ("m_world_position_x", ctypes.c_float),  # World space X position
        ("m_world_position_y", ctypes.c_float),  # World space Y position
        ("m_world_position_z", ctypes.c_float),  # World space Z position
        ("m_world_velocity_x", ctypes.c_float),  # Velocity in world space X
        ("m_world_velocity_y", ctypes.c_float),  # Velocity in world space Y
        ("m_world_velocity_z", ctypes.c_float),  # Velocity in world space Z
        ("m_world_forward_dir_x", ctypes.c_int16),  # World space forward X direction
        # (normalised)a
        ("m_world_forward_dir_y", ctypes.c_int16),
        # World space forward Y direction (normalised)
        ("m_world_forward_dir_z", ctypes.c_int16),
        # World space forward Z direction (normalised)
        ("m_world_right_dir_x", ctypes.c_int16),
        # World space right X direction (normalised)
        ("m_world_right_dir_y", ctypes.c_int16),
        # World space right Y direction (normalised)
        ("m_world_right_dir_z", ctypes.c_int16),
        # World space right Z direction (normalised)
        ("m_g_force_lateral", ctypes.c_float),  # Lateral G-Force component
        ("m_g_force_longitudinal", ctypes.c_float),  # Longitudinal G-Force component
        ("m_g_force_vertical", ctypes.c_float),  # Vertical G-Force component
        ("m_yaw", ctypes.c_float),  # Yaw angle in radians
        ("m_pitch", ctypes.c_float),  # Pitch angle in radians
        ("m_roll", ctypes.c_float),  # Roll angle in radians
    ]


class PacketMotionData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_car_motion_data", CarMotionData * 22),  # Data for all cars on track
    ]


class MarshalZone(Packet):
    _fields_ = [
        ("m_zone_start", ctypes.c_float),
        # Fraction (0..1) of way through the lap the marshal zone starts
        ("m_zone_flag", ctypes.c_int8),
        # -1 = invalid/unknown, 0 = none, 1 = green, 2 = blue, 3 = yellow, 4 = red
    ]


class WeatherForecastSample(Packet):
    _fields_ = [
        ("m_session_type", ctypes.c_uint8),
        # 0 = unknown, 1 = P1, 2 = P2, 3 = P3, 4 = Short P, 5 = Q1
        # 6 = Q2, 7 = Q3, 8 = Short Q, 9 = OSQ, 10 = R, 11 = R2
        # 12 = Time Trial
        ("m_time_offset", ctypes.c_uint8),  # Time in minutes the forecast is for
        ("m_weather", ctypes.c_uint8),
        # Weather - 0 = clear, 1 = light cloud, 2 = overcast
        # 3 = light rain, 4 = heavy rain, 5 = storm
        ("m_track_temperature", ctypes.c_int8),  # Track temp. in degrees Celsius
        ("m_track_temperature_change", ctypes.c_int8),
        # Track temp. change – 0 = up, 1 = down, 2 = no change
        ("m_air_temperature", ctypes.c_int8),  # Air temp. in degrees celsius
        ("m_air_temperature_change", ctypes.c_int8),
        # Air temp. change – 0 = up, 1 = down, 2 = no change
        ("m_rain_percentage", ctypes.c_uint8),  # Rain percentage (0-100)
    ]


class PacketSessionData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_weather", ctypes.c_uint8),
        # Weather - 0 = clear, 1 = light cloud, 2 = overcast
        # 3 = light rain, 4 = heavy rain, 5 = storm
        ("m_track_temperature", ctypes.c_int8),  # Track temp. in degrees celsius
        ("m_air_temperature", ctypes.c_int8),  # Air temp. in degrees celsius
        ("m_total_laps", ctypes.c_uint8),  # Total number of laps in this race
        ("m_track_length", ctypes.c_uint16),  # Track length in metres
        ("m_session_type", ctypes.c_uint8),
        # 0 = unknown, 1 = P1, 2 = P2, 3 = P3, 4 = Short P
        # 5 = Q1, 6 = Q2, 7 = Q3, 8 = Short Q, 9 = OSQ
        # 10 = R, 11 = R2, 12 = R3, 13 = Time Trial
        ("m_track_id", ctypes.c_int8),  # -1 for unknown, 0-21 for tracks, see appendix
        ("m_formula", ctypes.c_uint8),
        # Formula, 0 = F1 Modern, 1 = F1 Classic, 2 = F2,
        # 3 = F1 Generic
        ("m_session_time_left", ctypes.c_uint16),  # Time left in session in seconds
        ("m_session_duration", ctypes.c_uint16),  # Session duration in seconds
        ("m_pit_speed_limit", ctypes.c_uint8),  # Pit speed limit in kilometres per hour
        ("m_game_paused", ctypes.c_uint8),  # Whether the game is paused
        ("m_is_spectating", ctypes.c_uint8),  # Whether the player is spectating
        ("m_spectator_car_index", ctypes.c_uint8),  # Index of the car being spectated
        ("m_sli_pro_native_support", ctypes.c_uint8),
        # SLI Pro support, 0 = inactive, 1 = active
        ("m_num_marshal_zones", ctypes.c_uint8),  # Number of marshal zones to follow
        ("m_marshal_zones", MarshalZone * 21),  # List of marshal zones – max 21
        ("m_safety_car_status", ctypes.c_uint8),  # 0 = no safety car, 1 = full
        # 2 = virtual, 3 = formation lap
        ("m_network_game", ctypes.c_uint8),  # 0 = offline, 1 = online
        ("m_num_weather_forecast_samples", ctypes.c_uint8),
        # Number of weather samples to follow
        ("m_weather_forecast_samples", WeatherForecastSample * 64),
        # Array of weather forecast samples
        ("m_forecast_accuracy", ctypes.c_uint8),  # 0 = Perfect, 1 = Approximate
        ("m_ai_difficulty", ctypes.c_uint8),  # AI Difficulty rating – 0-110
        ("m_season_link_identifier", ctypes.c_uint32),
        # Identifier for season - persists across saves
        ("m_weekend_link_identifier", ctypes.c_uint32),
        # Identifier for weekend - persists across saves
        ("m_session_link_identifier", ctypes.c_uint32),
        # Identifier for session - persists across saves
        ("m_pit_stop_window_ideal_lap", ctypes.c_uint8),
        # Ideal lap to pit on for current strategy (player)
        ("m_pit_stop_window_latest_lap", ctypes.c_uint8),
        # Latest lap to pit on for current strategy (player)
        ("m_pit_stop_rejoin_position", ctypes.c_uint8),
        # Predicted position to rejoin at (player)
        ("m_steering_assist", ctypes.c_uint8),  # 0 = off, 1 = on
        ("m_braking_assist", ctypes.c_uint8),  # 0 = off, 1 = low, 2 = medium, 3 = high
        ("m_gearbox_assist", ctypes.c_uint8),
        # 1 = manual, 2 = manual & suggested gear, 3 = auto
        ("m_pit_assist", ctypes.c_uint8),  # 0 = off, 1 = on
        ("m_pit_release_assist", ctypes.c_uint8),  # 0 = off, 1 = on
        ("m_ersassist", ctypes.c_uint8),  # 0 = off, 1 = on
        ("m_drsassist", ctypes.c_uint8),  # 0 = off, 1 = on
        ("m_dynamic_racing_line", ctypes.c_uint8),
        # 0 = off, 1 = corners only, 2 = full
        ("m_dynamic_racing_line_type", ctypes.c_uint8),  # 0 = 2D, 1 = 3D
        ("m_game_mode", ctypes.c_uint8),
        ("m_rule_set", ctypes.c_uint8),
        ("m_time_of_day", ctypes.c_uint32),
        ("m_session_length", ctypes.c_uint8),

        ("m_speed_units_lead_player", ctypes.c_uint8),
        ("m_temperature_units_lead_player", ctypes.c_uint8),
        ("m_speed_units_secondary_player", ctypes.c_uint8),
        ("m_temperature_units_secondary_player", ctypes.c_uint8),
        ("m_num_safety_car_periods", ctypes.c_uint8),
        ("m_num_virtual_safety_car_periods", ctypes.c_uint8),
        ("m_num_red_flag_periods", ctypes.c_uint8),
        ("m_equalCarPerformance", ctypes.c_uint8),
        ("m_recoveryMode", ctypes.c_uint8),
        ("m_flashbackLimit", ctypes.c_uint8),
        ("m_surfaceType", ctypes.c_uint8),
        ("m_lowFuelMode", ctypes.c_uint8),
        ("m_raceStarts", ctypes.c_uint8),
        ("m_tyreTemperature", ctypes.c_uint8),
        ("m_pitLaneTyreSim", ctypes.c_uint8),
        ("m_carDamage", ctypes.c_uint8),
        ("m_carDamageRate", ctypes.c_uint8),
        ("m_collisions", ctypes.c_uint8),
        ("m_collisionsOffForFirstLapOnly", ctypes.c_uint8),
        ("m_mpUnsafePitRelease", ctypes.c_uint8),
        ("m_mpOffForGriefing", ctypes.c_uint8),
        ("m_cornerCuttingStringency", ctypes.c_uint8),
        ("m_parcFermeRules", ctypes.c_uint8),
        ("m_pitStopExperience", ctypes.c_uint8),
        ("m_safetyCar", ctypes.c_uint8),
        ("m_safetyCarExperience", ctypes.c_uint8),
        ("m_formationLap", ctypes.c_uint8),
        ("m_formationLapExperience", ctypes.c_uint8),
        ("m_redFlags", ctypes.c_uint8),
        ("m_affectsLicenceLevelSolo", ctypes.c_uint8),
        ("m_affectsLicenceLevelMP", ctypes.c_uint8),
        ("m_numSessionsInWeekend", ctypes.c_uint8),
        ("m_weekendStructure", ctypes.c_uint8*12),
        ("m_sector2LapDistanceStart", ctypes.c_float),
        ("m_sector3LapDistanceStart", ctypes.c_float)
        

    ]


class LapData(Packet):
    _fields_ = [
        ("m_last_lap_time_in_ms", ctypes.c_uint32),  # Last lap time in milliseconds
        ("m_current_lap_time_in_ms", ctypes.c_uint32),
        # Current time around the lap in milliseconds
        ("m_sector1_time_in_ms", ctypes.c_uint16),  # Sector 1 time in milliseconds
        ("m_sector1_time_in_minutes", ctypes.c_uint8),
        ("m_sector2_time_in_ms", ctypes.c_uint16),  # Sector 2 time in milliseconds
        ("m_sector2_time_in_minutes", ctypes.c_uint8),

        ("m_deltaToCarInFrontMSPart", ctypes.c_uint16),
        ("m_deltaToCarInFrontMinutesPart", ctypes.c_uint8),

        ("m_deltaToRaceLeaderMSPart", ctypes.c_uint16),
        ("m_deltaToRaceLeaderMinutesPart", ctypes.c_uint8),

        ("m_lap_distance", ctypes.c_float),
        # Distance vehicle is around current lap in metres – could
        # be negative if line hasn’t been crossed yet
        ("m_total_distance", ctypes.c_float),
        # Total distance travelled in session in metres – could
        # be negative if line hasn’t been crossed yet
        ("m_safety_car_delta", ctypes.c_float),  # Delta in seconds for safety car
        ("m_car_position", ctypes.c_uint8),  # Car race position
        ("m_current_lap_num", ctypes.c_uint8),  # Current lap number
        ("m_pit_status", ctypes.c_uint8),  # 0 = none, 1 = pitting, 2 = in pit area
        ("m_num_pit_stops", ctypes.c_uint8),  # Number of pit stops taken in this race
        ("m_sector", ctypes.c_uint8),  # 0 = sector1, 1 = sector2, 2 = sector3
        ("m_current_lap_invalid", ctypes.c_uint8),
        # Current lap invalid - 0 = valid, 1 = invalid
        ("m_penalties", ctypes.c_uint8),
        # Accumulated time penalties in seconds to be added
        ("m_total_warnings", ctypes.c_uint8),  # Accumulated number of warnings issued
        ("m_corner_cutting_warnings", ctypes.c_uint8),
        ("m_num_unserved_drive_through_pens", ctypes.c_uint8),
        # Num drive through pens left to serve
        ("m_num_unserved_stop_go_pens", ctypes.c_uint8),
        # Num stop go pens left to serve
        ("m_grid_position", ctypes.c_uint8),
        # Grid position the vehicle started the race in
        ("m_driver_status", ctypes.c_uint8),
        # Status of driver - 0 = in garage, 1 = flying lap
        # 2 = in lap, 3 = out lap, 4 = on track
        ("m_result_status", ctypes.c_uint8),
        # Result status - 0 = invalid, 1 = inactive, 2 = active
        # 3 = finished, 4 = didnotfinish, 5 = disqualified
        # 6 = not classified, 7 = retired
        ("m_pit_lane_timer_active", ctypes.c_uint8),
        # Pit lane timing, 0 = inactive, 1 = active
        ("m_pit_lane_time_in_lane_in_ms", ctypes.c_uint16),
        # If active, the current time spent in the pit lane in ms
        ("m_pit_stop_timer_in_ms", ctypes.c_uint16),
        # Time of the actual pit stop in ms
        ("m_pit_stop_should_serve_pen", ctypes.c_uint8),
        # Whether the car should serve a penalty at this stop
        ("m_speedTrapFastestSpeed", ctypes.c_float),
        ("m_speedTrapFastestLap", ctypes.c_uint8),
    ]


class PacketLapData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_lap_data", LapData * 22),  # Lap data for all cars on track
        ("m_time_trial_pb_car_idx", ctypes.c_uint8),
        ("m_time_trial_rival_car_idx", ctypes.c_int8),
    ]


class FastestLap(Packet):
    _fields_ = [
        ("m_vehicle_idx", ctypes.c_uint8),  # Vehicle index of car achieving fastest lap
        ("m_lap_time", ctypes.c_float),  # Lap time is in seconds
    ]


class Retirement(Packet):
    _fields_ = [
        ("m_vehicle_idx", ctypes.c_uint8),  # Vehicle index of car retiring
    ]


class TeamMateInPits(Packet):
    _fields_ = [
        ("m_vehicle_idx", ctypes.c_uint8),  # Vehicle index of team mate
    ]


class RaceWinner(Packet):
    _fields_ = [
        ("m_vehicle_idx", ctypes.c_uint8),  # Vehicle index of the race winner
    ]


class Penalty(Packet):
    _fields_ = [
        ("m_penalty_type", ctypes.c_uint8),  # Penalty type – see Appendices
        ("m_infringement_type", ctypes.c_uint8),  # Infringement type – see Appendices
        ("m_vehicle_idx", ctypes.c_uint8),
        # Vehicle index of the car the penalty is applied to
        ("m_other_vehicle_idx", ctypes.c_uint8),
        # Vehicle index of the other car involved
        ("m_time", ctypes.c_uint8),
        # Time gained, or time spent doing action in seconds
        ("m_lap_num", ctypes.c_uint8),  # Lap the penalty occurred on
        ("m_places_gained", ctypes.c_uint8),  # Number of places gained by this
    ]


class SpeedTrap(Packet):
    _fields_ = [
        ("m_vehicle_idx", ctypes.c_uint8),
        # Vehicle index of the vehicle triggering speed trap
        ("m_speed", ctypes.c_float),  # Top speed achieved in kilometres per hour
        ("m_overall_fastest_in_session", ctypes.c_uint8),
        # Overall fastest speed in session = 1, otherwise 0
        ("m_driver_fastest_in_session", ctypes.c_uint8),
        # Fastest speed for driver in session = 1, otherwise 0
        ("m_fastest_vehicukle_idx_in_session", ctypes.c_uint8),
        ("m_fastestSpeedInSession", ctypes.c_float), 
    ]


class StartLights(Packet):
    _fields_ = [
        ("m_num_lights", ctypes.c_uint8),  # Number of lights showing
    ]


class DriveThroughPenaltyServed(Packet):
    _fields_ = [
        ("m_vehicle_idx", ctypes.c_uint8),
        # Vehicle index of the vehicle serving drive through
    ]


class StopGoPenaltyServed(Packet):
    _fields_ = [
        ("m_vehicle_idx", ctypes.c_uint8),
        # Vehicle index of the vehicle serving stop go
    ]


class Flashback(Packet):
    _fields_ = [
        ("m_flashback_frame_identifier", ctypes.c_uint32),
        # Frame identifier flashed back to
        ("m_flashback_session_time", ctypes.c_float),  # Session time flashed back to
    ]


class Buttons(Packet):
    _fields_ = [
        ("m_", ctypes.c_uint32),
        # Bit flags specifying which buttons are being pressed
        # currently - see appendices
    ]


class Overtake(Packet):
    _fields_ = [
        ("m_overtakingVehicleIdx", ctypes.c_uint8),
        ("m_beingOvertakenVehicleIdx", ctypes.c_uint8),
    ]

class SafetyCar(Packet):
    _fields_ = [
        ("m_safetyCarType", ctypes.c_uint8),
        ("m_eventType", ctypes.c_uint8),
    ]


class Collision(Packet):
    _fields_ = [
        ("m_vehicle1Idx", ctypes.c_uint8),
        ("m_vehicle2Idx", ctypes.c_uint8),
    ]


class EventDataDetails(ctypes.Union, PacketMixin):  # Potentiel Problème ici
    _fields_ = [
        ("m_fastest_lap", FastestLap),
        ("m_retirement", Retirement),
        ("m_team_mate_in_pits", TeamMateInPits),
        ("m_race_winner", RaceWinner),
        ("m_penalty", Penalty),
        ("m_speed_trap", SpeedTrap),
        ("m_start_lights", StartLights),
        ("m_drive_through_penalty_served", DriveThroughPenaltyServed),
        ("m_stop_go_penalty_served", StopGoPenaltyServed),
        ("m_flashback", Flashback),
        ("m_buttons", Buttons),
        ("m_overtake", Overtake),
        ("m_satefy_car", SafetyCar),
        ("m_collision", Collision)
    ]


class PacketEventData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_event_string_code", ctypes.c_uint8 * 4),  # Event string code, see below
        ("m_event_details", EventDataDetails),
        # Event details - should be interpreted differently
        # for each type
    ]


class ParticipantData(Packet):
    _fields_ = [
        ("m_ai_controlled", ctypes.c_uint8),
        # Whether the vehicle is AI (1) or Human (0) controlled
        ("m_driver_id", ctypes.c_uint8),
        # Driver id - see appendix, 255 if network human
        ("m_network_id", ctypes.c_uint8),
        # Network id – unique identifier for network players
        ("m_team_id", ctypes.c_uint8),  # Team id - see appendix
        ("m_my_team", ctypes.c_uint8),  # My team flag – 1 = My Team, 0 = otherwise
        ("m_race_number", ctypes.c_uint8),  # Race number of the car
        ("m_nationality", ctypes.c_uint8),  # Nationality of the driver
        ("m_name", ctypes.c_char * 48),
        # Name of participant in UTF-8 format – null terminated
        # Will be truncated with … (U+2026) if too long
        ("m_your_telemetry", ctypes.c_uint8),
        # The player's UDP setting, 0 = restricted, 1 = public
        ("m_show_online_names", ctypes.c_uint8),
        ("m_tech_level", ctypes.c_uint16),
        ("m_platform", ctypes.c_uint8)
    ]


class PacketParticipantsData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_num_active_cars", ctypes.c_uint8),
        # Number of active cars in the data – should match number of
        # cars on HUD
        ("m_participants", ParticipantData * 22),
    ]


class CarSetupData(Packet):
    _fields_ = [
        ("m_front_wing", ctypes.c_uint8),  # Front wing aero
        ("m_rear_wing", ctypes.c_uint8),  # Rear wing aero
        ("m_on_throttle", ctypes.c_uint8),
        # Differential adjustment on throttle (percentage)
        ("m_off_throttle", ctypes.c_uint8),
        # Differential adjustment off throttle (percentage)
        ("m_front_camber", ctypes.c_float),  # Front camber angle (suspension geometry)
        ("m_rear_camber", ctypes.c_float),  # Rear camber angle (suspension geometry)
        ("m_front_toe", ctypes.c_float),  # Front toe angle (suspension geometry)
        ("m_rear_toe", ctypes.c_float),  # Rear toe angle (suspension geometry)
        ("m_front_suspension", ctypes.c_uint8),  # Front suspension
        ("m_rear_suspension", ctypes.c_uint8),  # Rear suspension
        ("m_front_anti_roll_bar", ctypes.c_uint8),  # Front anti-roll bar
        ("m_rear_anti_roll_bar", ctypes.c_uint8),  # Front anti-roll bar
        ("m_front_suspension_height", ctypes.c_uint8),  # Front ride height
        ("m_rear_suspension_height", ctypes.c_uint8),  # Rear ride height
        ("m_brake_pressure", ctypes.c_uint8),  # Brake pressure (percentage)
        ("m_brake_bias", ctypes.c_uint8),  # Brake bias (percentage)
        ("m_engine_braking", ctypes.c_uint8),
        ("m_rear_left_tyre_pressure", ctypes.c_float),  # Rear left tyre pressure (PSI)
        ("m_rear_right_tyre_pressure", ctypes.c_float),
        # Rear right tyre pressure (PSI)
        ("m_front_left_tyre_pressure", ctypes.c_float),
        # Front left tyre pressure (PSI)
        ("m_front_right_tyre_pressure", ctypes.c_float),
        # Front right tyre pressure (PSI)
        ("m_ballast", ctypes.c_uint8),  # Ballast
        ("m_fuel_load", ctypes.c_float),  # Fuel load
    ]

    def __str__(self):
        string = ""
        for i in range(20):
            string += str(self.get_value(self._fields_[i][0])) + " "
        return string

    def __repr__(self):
        string = ""
        for i in range(20):
            string += str(self.get_value(self._fields_[i][0])) + " "
        return string


class PacketCarSetupData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_car_setups", CarSetupData * 22),
        ("m_nextFrontWingValue", ctypes.c_float)
    ]


class CarTelemetryData(Packet):
    _fields_ = [
        ("m_speed", ctypes.c_uint16),  # Speed of car in kilometres per hour
        ("m_throttle", ctypes.c_float),  # Amount of throttle applied (0.0 to 1.0)
        ("m_steer", ctypes.c_float),
        # Steering (-1.0 (full lock left) to 1.0 (full lock right))
        ("m_brake", ctypes.c_float),  # Amount of brake applied (0.0 to 1.0)
        ("m_clutch", ctypes.c_uint8),  # Amount of clutch applied (0 to 100)
        ("m_gear", ctypes.c_int8),  # Gear selected (1-8, N=0, R=-1)
        ("m_engine_rpm", ctypes.c_uint16),  # Engine RPM
        ("m_drs", ctypes.c_uint8),  # 0 = off, 1 = on
        ("m_rev_lights_percent", ctypes.c_uint8),  # Rev lights indicator (percentage)
        ("m_rev_lights_bit_value", ctypes.c_uint16),
        # Rev lights (bit 0 = leftmost LED, bit 14 = rightmost LED)
        ("m_brakes_temperature", ctypes.c_uint16 * 4),  # Brakes temperature (celsius)
        ("m_tyres_surface_temperature", ctypes.c_uint8 * 4),
        # Tyres surface temperature (celsius)
        ("m_tyres_inner_temperature", ctypes.c_uint8 * 4),
        # Tyres inner temperature (celsius)
        ("m_engine_temperature", ctypes.c_uint16),  # Engine temperature (celsius)
        ("m_tyres_pressure", ctypes.c_float * 4),  # Tyres pressure (PSI)
        ("m_surface_type", ctypes.c_uint8 * 4),  # Driving surface, see appendices
    ]


class PacketCarTelemetryData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_car_telemetry_data", CarTelemetryData * 22),
        ("m_mfd_panel_index", ctypes.c_uint8),
        # Index of MFD panel open - 255 = MFD closed
        # Single player, race – 0 = Car setup, 1 = Pits
        # 2 = Damage, 3 =  Engine, 4 = Temperatures
        # May vary depending on game mode
        ("m_mfd_panel_index_secondary_player", ctypes.c_uint8),  # See above
        ("m_suggested_gear", ctypes.c_int8),  # Suggested gear for the player (1-8)
        # 0 if no gear suggested
    ]


class CarStatusData(Packet):
    _fields_ = [
        ("m_traction_control", ctypes.c_uint8),
        # Traction control - 0 = off, 1 = medium, 2 = full
        ("m_anti_lock_brakes", ctypes.c_uint8),  # 0 (off) - 1 (on)
        ("m_fuel_mix", ctypes.c_uint8),
        # Fuel mix - 0 = lean, 1 = standard, 2 = rich, 3 = max
        ("m_front_brake_bias", ctypes.c_uint8),  # Front brake bias (percentage)
        ("m_pit_limiter_status", ctypes.c_uint8),
        # Pit limiter status - 0 = off, 1 = on
        ("m_fuel_in_tank", ctypes.c_float),  # Current fuel mass
        ("m_fuel_capacity", ctypes.c_float),  # Fuel capacity
        ("m_fuel_remaining_laps", ctypes.c_float),
        # Fuel remaining in terms of laps (value on MFD)
        ("m_max_rpm", ctypes.c_uint16),  # Cars max RPM, point of rev limiter
        ("m_idle_rpm", ctypes.c_uint16),  # Cars idle RPM
        ("m_max_gears", ctypes.c_uint8),  # Maximum number of gears
        ("m_drs_allowed", ctypes.c_uint8),  # 0 = not allowed, 1 = allowed
        ("m_drs_activation_distance", ctypes.c_uint16),
        # 0 = DRS not available, non-zero - DRS will be available
        # in [X] metres
        ("m_actual_tyre_compound", ctypes.c_uint8),
        # F1 Modern - 16 = C5, 17 = C4, 18 = C3, 19 = C2, 20 = C1
        # 7 = inter, 8 = wet
        # F1 Classic - 9 = dry, 10 = wet
        # F2 – 11 = super soft, 12 = soft, 13 = medium, 14 = hard
        # 15 = wet
        ("m_visual_tyre_compound", ctypes.c_uint8),
        # F1 visual (can be different from actual compound)
        # 16 = soft, 17 = medium, 18 = hard, 7 = inter, 8 = wet
        # F1 Classic – same as above
        # F2 ‘19, 15 = wet, 19 – super soft, 20 = soft
        # 21 = medium , 22 = hard
        ("m_tyres_age_laps", ctypes.c_uint8),  # Age in laps of the current set of tyres
        ("m_vehicle_fia_flags", ctypes.c_int8),
        # -1 = invalid/unknown, 0 = none, 1 = green
        # 2 = blue, 3 = yellow, 4 = red
        ("m_engine_power_ice", ctypes.c_float),
        ("m_engine_power_mguk", ctypes.c_float),
        ("m_ers_store_energy", ctypes.c_float),  # ERS energy store in Joules
        ("m_ers_deploy_mode", ctypes.c_uint8),
        # ERS deployment mode, 0 = none, 1 = medium
        # 2 = hotlap, 3 = overtake
        ("m_ers_harvested_this_lap_mguk", ctypes.c_float),
        # ERS energy harvested this lap by MGU-K
        ("m_ers_harvested_this_lap_mguh", ctypes.c_float),
        # ERS energy harvested this lap by MGU-H
        ("m_ers_deployed_this_lap", ctypes.c_float),  # ERS energy deployed this lap
        ("m_network_paused", ctypes.c_uint8),
        # Whether the car is paused in a network game
    ]


class PacketCarStatusData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_car_status_data", CarStatusData * 22),
    ]


class FinalClassificationData(Packet):
    _fields_ = [
        ("m_position", ctypes.c_uint8),  # Finishing position
        ("m_num_laps", ctypes.c_uint8),  # Number of laps completed
        ("m_grid_position", ctypes.c_uint8),  # Grid position of the car
        ("m_points", ctypes.c_uint8),  # Number of points scored
        ("m_num_pit_stops", ctypes.c_uint8),  # Number of pit stops made
        ("m_result_status", ctypes.c_uint8),
        # Result status - 0 = invalid, 1 = inactive, 2 = active
        # 3 = finished, 4 = didnotfinish, 5 = disqualified
        # 6 = not classified, 7 = retired
        # Best lap time of the session in milliseconds
        ("m_best_lap_time_in_ms", ctypes.c_uint32),
        # Total race time in seconds without penalties
        ("m_total_race_time", ctypes.c_double),
        ("m_penalties_time", ctypes.c_uint8),  # Total penalties accumulated in seconds
        # Number of penalties applied to this driver
        ("m_num_penalties", ctypes.c_uint8),
        ("m_num_tyre_stints", ctypes.c_uint8),  # Number of tyres stints up to maximum
        # Actual tyres used by this driver
        ("m_tyre_stints_actual", ctypes.c_uint8 * 8),
        # Visual tyres used by this driver
        ("m_tyre_stints_visual", ctypes.c_uint8 * 8),
        ("m_tyreStintsEndLaps", ctypes.c_uint8 * 8),
    ]


class PacketFinalClassificationData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_num_cars", ctypes.c_uint8),  # Number of cars in the final classification
        ("m_classification_data", FinalClassificationData * 22),
    ]


class LobbyInfoData(Packet):
    _fields_ = [
        ("m_ai_controlled", ctypes.c_uint8),
        # Whether the vehicle is AI (1) or Human (0) controlled
        ("m_team_id", ctypes.c_uint8),
        # Team id - see appendix (255 if no team currently selected)
        ("m_nationality", ctypes.c_uint8),  # Nationality of the driver
        ("m_platform", ctypes.c_uint8),
        # Name of participant in UTF-8 format – null terminated
        ("m_name", ctypes.c_char * 48),
        # Will be truncated with ... (U+2026) if too long
        ("m_car_number", ctypes.c_uint8),  # Car number of the player
        ("m_your_telemetry", ctypes.c_uint8),
        ("m_show_online_names", ctypes.c_uint8),
        ("m_tech_level", ctypes.c_uint16),
        ("m_ready_status", ctypes.c_uint8),  # 0 = not ready, 1 = ready, 2 = spectating
    ]


class PacketLobbyInfoData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        # Packet specific data
        ("m_num_players", ctypes.c_uint8),  # Number of players in the lobby data
        ("m_lobby_players", LobbyInfoData * 22),
    ]


class CarDamageData(Packet):
    _fields_ = [
        ("m_tyres_wear", ctypes.c_float * 4),  # Tyre wear (percentage)
        ("m_tyres_damage", ctypes.c_uint8 * 4),  # Tyre damage (percentage)
        ("m_brakes_damage", ctypes.c_uint8 * 4),  # Brakes damage (percentage)
        # Front left wing damage (percentage)
        ("m_front_left_wing_damage", ctypes.c_uint8),
        # Front right wing damage (percentage)
        ("m_front_right_wing_damage", ctypes.c_uint8),
        ("m_rear_wing_damage", ctypes.c_uint8),  # Rear wing damage (percentage)
        ("m_floor_damage", ctypes.c_uint8),  # Floor damage (percentage)
        ("m_diffuser_damage", ctypes.c_uint8),  # Diffuser damage (percentage)
        ("m_sidepod_damage", ctypes.c_uint8),  # Sidepod damage (percentage)
        ("m_drs_fault", ctypes.c_uint8),  # Indicator for DRS fault, 0 = OK, 1 = fault
        ("m_ers_fault", ctypes.c_uint8),
        ("m_gear_box_damage", ctypes.c_uint8),  # Gear box damage (percentage)
        ("m_engine_damage", ctypes.c_uint8),  # Engine damage (percentage)
        ("m_engine_mguhwear", ctypes.c_uint8),  # Engine wear MGU-H (percentage)
        ("m_engine_eswear", ctypes.c_uint8),  # Engine wear ES (percentage)
        ("m_engine_cewear", ctypes.c_uint8),  # Engine wear CE (percentage)
        ("m_engine_icewear", ctypes.c_uint8),  # Engine wear ICE (percentage)
        ("m_engine_mgukwear", ctypes.c_uint8),  # Engine wear MGU-K (percentage)
        ("m_engine_tcwear", ctypes.c_uint8),  # Engine wear TC (percentage)
        ("m_engine_blown", ctypes.c_uint8),
        ("m_engine_seized", ctypes.c_uint8),
    ]


class PacketCarDamageData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_car_damage_data", CarDamageData * 22),
    ]


class LapHistoryData(Packet):
    _fields_ = [
        ("m_lap_time_in_ms", ctypes.c_uint32),  # Lap time in milliseconds
        ("m_sector1_time_in_ms", ctypes.c_uint16),  # Sector 1 time in milliseconds
        ("m_sector1_time_in_minutes_part", ctypes.c_uint8),
        ("m_sector2_time_in_ms", ctypes.c_uint16),  # Sector 2 time in milliseconds
        ("m_sector2_time_in_minutes_part", ctypes.c_uint8),
        ("m_sector3_time_in_ms", ctypes.c_uint16),  # Sector 3 time in milliseconds
        ("m_sector3_time_in_minutes_part", ctypes.c_uint8),
        ("m_lap_valid_bit_flags", ctypes.c_uint8),
        # 0x01 bit set-lap valid,      0x02 bit set-sector 1 valid
        # 0x04 bit set-sector 2 valid, 0x08 bit set-sector 3 valid
    ]


class TyreStintHistoryData(Packet):
    _fields_ = [
        # Lap the tyre usage ends on (255 of current tyre)
        ("m_end_lap", ctypes.c_uint8),
        ("m_tyre_actual_compound", ctypes.c_uint8),  # Actual tyres used by this driver
        ("m_tyre_visual_compound", ctypes.c_uint8),  # Visual tyres used by this driver
    ]


class PacketSessionHistoryData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        ("m_car_idx", ctypes.c_uint8),  # Index of the car this lap data relates to
        # Num laps in the data (including current partial lap)
        ("m_num_laps", ctypes.c_uint8),
        ("m_num_tyre_stints", ctypes.c_uint8),  # Number of tyre stints in the data
        # Lap the best lap time was achieved on
        ("m_best_lap_time_lap_num", ctypes.c_uint8),
        # Lap the best Sector 1 time was achieved on
        ("m_best_sector1_lap_num", ctypes.c_uint8),
        # Lap the best Sector 2 time was achieved on
        ("m_best_sector2_lap_num", ctypes.c_uint8),
        # Lap the best Sector 3 time was achieved on
        ("m_best_sector3_lap_num", ctypes.c_uint8),
        ("m_lap_history_data", LapHistoryData * 100),  # 100 laps of data max
        ("m_tyre_stints_history_data", TyreStintHistoryData * 8),
    ]

class TyreSetData(Packet):
    _fields_ = [
        ("m_actual_tyre_compound", ctypes.c_uint8),
        ("m_visual_tyre_compound", ctypes.c_uint8),
        ("m_wear", ctypes.c_uint8),
        ("m_available", ctypes.c_uint8),
        ("m_recommanded_session", ctypes.c_uint8),
        ("m_life_span", ctypes.c_uint8),
        ("m_usable_life", ctypes.c_uint8),
        ("m_lap_delta_time", ctypes.c_uint16),
        ("m_fitted", ctypes.c_uint8)
    ]

class PacketTyreSetsData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),
        ("m_car_idx", ctypes.c_uint8),
        ("m_tyre_set_data", TyreSetData*20),
        ("m_fitted_idx", ctypes.c_uint8)
    ]

class PacketMotionExData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),  # Header
        # Extra player car ONLY data
        ("m_suspension_position", ctypes.c_float * 4),
        # Note: All wheel arrays have the following order:
        ("m_suspension_velocity", ctypes.c_float * 4),  # RL, RR, FL, FR
        ("m_suspension_acceleration", ctypes.c_float * 4),  # RL, RR, FL, FR
        ("m_wheel_speed", ctypes.c_float * 4),  # Speed of each wheel
        ("m_wheel_slip_ratio", ctypes.c_float * 4),  # Slip ratio for each wheel
        ("m_wheel_slip_angle", ctypes.c_float * 4),
        ("m_wheel_lat_force", ctypes.c_float * 4),
        ("m_wheel_long_force", ctypes.c_float * 4),
        ("m_height_of_cog_above_ground", ctypes.c_float),
        ("m_local_velocity_x", ctypes.c_float),  # Velocity in local space
        ("m_local_velocity_y", ctypes.c_float),  # Velocity in local space
        ("m_local_velocity_z", ctypes.c_float),  # Velocity in local space
        ("m_angular_velocity_x", ctypes.c_float),  # Angular velocity x-component
        ("m_angular_velocity_y", ctypes.c_float),  # Angular velocity y-component
        ("m_angular_velocity_z", ctypes.c_float),  # Angular velocity z-component
        ("m_angular_acceleration_x", ctypes.c_float),  # Angular velocity x-component
        ("m_angular_acceleration_y", ctypes.c_float),  # Angular velocity y-component
        ("m_angular_acceleration_z", ctypes.c_float),  # Angular velocity z-component
        ("m_front_wheels_angle", ctypes.c_float),
        ("m_wheelVertForce", ctypes.c_float*4),
        # Current front wheels angle in radians
        ("m_front_aero_height", ctypes.c_float),
        ("m_rear_aero_height", ctypes.c_float),  
        ("m_front_roll_angle", ctypes.c_float),
        ("m_rear_roll_angle", ctypes.c_float),
        ("m_m_chassis_yaw", ctypes.c_float),  
    ]


class TimeTrialDataSet(Packet):
    _fields_ = [
        ("m_car_idx", ctypes.c_uint8),
        ("m_team_id", ctypes.c_uint8),
        ("m_lap_time_in_ms", ctypes.c_uint32),
        ("m_sector1_time_in_ms", ctypes.c_uint32),
        ("m_sector2_time_in_ms", ctypes.c_uint32),
        ("m_sector3_time_in_ms", ctypes.c_uint32),
        ("m_traction_control", ctypes.c_uint8),
        ("m_gearbox_assis", ctypes.c_uint8),
        ("m_anti_lock_brakes", ctypes.c_uint8),
        ("m_equal_car_performance", ctypes.c_uint8),
        ("m_custom_setup", ctypes.c_uint8),
        ("m_valid", ctypes.c_uint8),
    ]

class PacketTimeTrialData(Packet):
    _fields_ = [
        ("m_header", PacketHeader),
        ("m_playerSessionBestDataSet", TimeTrialDataSet),
        ("m_personalBestDataSet", TimeTrialDataSet),
        ("m_rivalDataSet", TimeTrialDataSet)
    ]

HEADER_FIELD_TO_PACKET_TYPE = {
    0: PacketMotionData,
    1: PacketSessionData,
    2: PacketLapData,
    3: PacketEventData,
    4: PacketParticipantsData,
    5: PacketCarSetupData,
    6: PacketCarTelemetryData,
    7: PacketCarStatusData,
    8: PacketFinalClassificationData,
    9: PacketLobbyInfoData,
    10: PacketCarDamageData,
    11: PacketSessionHistoryData,
    12:PacketTyreSetsData,
    13:PacketMotionExData,
    14:PacketTimeTrialData
}
