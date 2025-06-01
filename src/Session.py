from dictionnaries import session_dictionary, conversion, track_dictionary, weather_dictionary, color_flag_dict


class WeatherForecastSample:
    def __init__(self, time, weather, tktp, airtp, rainP):
        self.time = time
        self.weather = weather
        self.trackTemp = tktp
        self.airTemp = airtp
        self.rainPercentage = rainP
        self.weatherForecastAccuracy = -1

    def __repr__(self):
        return f"{self.time}m : {weather_dictionary[self.weather]}, Track : {self.trackTemp}°C, " \
               f"Air : {self.airTemp}°C, Humidity : {self.rainPercentage}% "

    def __str__(self):
        return f"{self.time}m : {weather_dictionary[self.weather]}, Track : {self.trackTemp}°C, " \
               f"Air : {self.airTemp}°C, Humidity : {self.rainPercentage}% "

class Session:
    def __init__(self):
        self.airTemperature = 0
        self.trackTemperature = 0
        self.nbLaps = 0
        self.currentLap = 0
        self.tour_precedent = 0
        self.Seance = 0
        self.Finished = False
        self.time_left = 0
        self.legende = ""
        self.track = -1
        self.marshalZones = []
        self.idxBestLapTime = -1
        self.bestLapTime = 5000
        self.safetyCarStatus = 0
        self.trackLength = 0
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
        self.anyYellow = False

    def add_slot(self, slot):
        self.weatherList.append(WeatherForecastSample(slot.m_time_offset, slot.m_weather, slot.m_track_temperature,
                                                      slot.m_air_temperature, slot.m_rain_percentage))

    def clear_slot(self):
        self.weatherList = []

    def title_display(self):
        if self.Seance == 18:
            string = f"Time Trial : {track_dictionary[self.track][0]}"
        elif self.Seance in [15,16,17]:
            string = f"Session : {session_dictionary[self.Seance]}, Lap : {self.currentLap}/{self.nbLaps}, " \
                        f"Air : {self.airTemperature}°C / Track : {self.trackTemperature}°C"
        elif self.Seance in [5,6,7,8,9]:
            string = f" Qualy : {conversion(self.time_left, 1)}"
        else:
            string = f" FP : {conversion(self.time_left, 1)}"
        return string

    def update_marshal_zones(self, map_canvas):
        for i in range(len(self.segments)):
            map_canvas.itemconfig(self.segments[i], fill=color_flag_dict[self.marshalZones[i].m_zone_flag])



