from src.packet_processing.dictionnaries import session_dictionary, track_dictionary, weather_dictionary, color_flag_dict
from src.parsers.parser2025 import WeatherForecastSample
import src


class Session:
    def __init__(self):
        self.airTemperature = 0
        self.trackTemperature = 0
        self.nbLaps = 0
        self.currentLap = 0
        self.tour_precedent = 0
        self.Session = 0
        self.Finished = False
        self.time_left = 0
        self.legende = ""
        self.track = -1
        self.marshalZones = []
        self.idxBestLapTime = -1
        self.bestLapTime = 5000
        self.safetyCarStatus = 0
        self.trackLength = 1
        self.weatherList: list[WeatherForecastSample] = []
        self.nb_weatherForecastSamples = 0
        self.weatherForecastAccuracy = 0
        self.startTime = 0
        self.nb_players = 22
        self.formationLapDone = False
        self.circuit_changed = False
        self.segments = []
        self.num_marshal_zones = 0
        self.packet_received = [0]*14
        self.flag = ""

    def show_weather_sample(self, i):
        if self.weatherList[i].m_air_temperature_change == 0:
            emoji_air = "🔼"
        elif self.weatherList[i].m_air_temperature_change == 1:
            emoji_air = "🔽"
        elif self.weatherList[i].m_air_temperature_change == 2:
            emoji_air = "▶️"
        else:
            emoji_air = ""

        if self.weatherList[i].m_track_temperature_change == 0:
            emoji_track = "🔼"
        elif self.weatherList[i].m_track_temperature_change == 1:
            emoji_track = "🔽"
        elif self.weatherList[i].m_track_temperature_change == 2:
            emoji_track = "▶️"
        else:
            emoji_track = ""

        return [session_dictionary[self.weatherList[i].m_session_type],
         "+" + str(self.weatherList[i].m_time_offset) + "min",
         str(self.weatherList[i].m_rain_percentage) + "%",
         weather_dictionary[self.weatherList[i].m_weather],
         emoji_air + str(self.weatherList[i].m_air_temperature) + "°C",
         emoji_track + str(self.weatherList[i].m_track_temperature) + "°C"]

    def clear_slot(self):
        self.weatherList = []

    def title_display(self):
        if self.Session == 18:
            string = f"Time Trial : {track_dictionary[self.track][0]}"
        elif self.Session in [15, 16, 17]:
            string = f" {session_dictionary[self.Session]}, Lap : {self.currentLap}/{self.nbLaps}, " \
                        f"Air : {self.airTemperature}°C / Track : {self.trackTemperature}°C"
        elif self.Session in [5, 6, 7, 8, 9]:
            string = (f" {session_dictionary[self.Session]} : "
                      f"{src.packet_processing.variables.format_minutes(self.time_left)}")
        else:
            string = f" FP : {src.packet_processing.variables.format_minutes(self.time_left)}"
        return self.flag + " " + string + " " + self.flag

    def update_marshal_zones(self, map_canvas):
        for i in range(len(self.segments)):
            map_canvas.itemconfig(self.segments[i], fill=color_flag_dict[self.marshalZones[i].m_zone_flag])



