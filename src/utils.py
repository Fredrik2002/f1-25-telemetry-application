import datetime


def format_minutes(millis):
    texte = str(datetime.timedelta(seconds=millis))
    liste = texte.split(":")
    return f"{liste[1]} min {liste[2]}s"


def format_milliseconds(ms):
    ms = int(ms)
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    milliseconds = ms % 1000
    if minutes > 0:
        return f"{minutes}:{seconds:02d}.{milliseconds:03d}"
    else:
        return f"{seconds:02d}.{milliseconds:03d}"



def file_len(fname):
    with open(fname) as file:
        for i, l in enumerate(file):
            pass
    return i + 1
