import datetime


def conversion(millis, mode):  # mode 1 = titre, mode 2 = last lap
    if mode == 1:
        texte = str(datetime.timedelta(seconds=millis))
        liste = texte.split(":")
        return f"{liste[1]} min {liste[2]}s"
    elif mode == 2:
        seconds, millis = millis // 1000, millis % 1000
        minutes, seconds = seconds // 60, seconds % 60
        if (minutes != 0 or seconds != 0 or millis != 0) and (minutes >= 0 and seconds < 10):
            seconds = "0" + str(seconds)

        if millis // 10 == 0:
            millis = "00" + str(millis)
        elif millis // 100 == 0:
            millis = "0" + str(millis)

        if minutes != 0:
            return f"{minutes}:{seconds}.{millis}"
        else:
            return f"{seconds}.{millis}"


def file_len(fname):
    with open(fname) as file:
        for i, l in enumerate(file):
            pass
    return i + 1


def string_code(packet):
    string = ""
    for i in range(4):
        string += packet.m_event_string_code[i]
    return string