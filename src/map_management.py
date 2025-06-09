from src.dictionnaries import track_dictionary, color_flag_dict, teams_color_dictionary
from src.variables import *

def create_map(map_canvas):
    cmi = 1
    L0, L1 = [], []
    L = []
    name, d, x_const, z_const = track_dictionary[session.track]
    with open(f"../tracks/{name}_2020_racingline.txt", "r") as file:
        for index, line in enumerate(file):
            if index not in [0, 1]:
                dist, z, x, y, _, _ = line.strip().split(",")
                if cmi == 1:
                    L0.append((float(z) / d + x_const, float(x) / d + z_const))
                elif cmi == session.num_marshal_zones:
                    L1.append((float(z) / d + x_const, float(x) / d + z_const))
                else:
                    L.append((float(z) / d + x_const, float(x) / d + z_const))
                if (float(dist) / session.trackLength) > session.marshalZones[
                    cmi].m_zone_start and cmi != session.num_marshal_zones:
                    if cmi != 1:
                        session.segments.append(map_canvas.create_line(L, width=3))
                        L = []
                    cmi += 1
    session.segments.insert(0, map_canvas.create_line(L1 + L0, width=3))
    for i in range(20):
        joueur = PLAYERS_LIST[i]
        if session.Seance == 18 and i != 0:
            joueur.oval = map_canvas.create_oval(-1000 / d + x_const - WIDTH_POINTS,
                                                 -1000 / d + z_const - WIDTH_POINTS,
                                                 -1000 / d + x_const + WIDTH_POINTS,
                                                 -1000 / d + z_const + WIDTH_POINTS, outline="")
        else:
            joueur.oval = map_canvas.create_oval(joueur.worldPositionX / d + x_const - WIDTH_POINTS,
                                                 joueur.worldPositionZ / d + z_const - WIDTH_POINTS,
                                                 joueur.worldPositionX / d + x_const + WIDTH_POINTS,
                                                 joueur.worldPositionZ / d + z_const + WIDTH_POINTS, outline="")

            joueur.etiquette = map_canvas.create_text(joueur.worldPositionX / d + x_const + 25,
                                                      joueur.worldPositionZ / d + z_const - 25,
                                                      text=joueur.name, font=("Cousine", 13))
            map_canvas.moveto(joueur.oval, joueur.worldPositionX / d + x_const - WIDTH_POINTS,
                              joueur.worldPositionZ / d + z_const - WIDTH_POINTS)


def delete_map(map_canvas):
    for element in session.segments:
        map_canvas.delete(element)
    session.segments = []
    for joueur in PLAYERS_LIST:
        map_canvas.delete(joueur.oval)
        map_canvas.delete(joueur.etiquette)
        joueur.oval = None


def update_map(map_canvas):
    if session.track == -1: return
    _, d, x, z = track_dictionary[session.track]
    for joueur in PLAYERS_LIST:
        if joueur.position != 0:
            map_canvas.moveto(joueur.oval, round(joueur.worldPositionX / d + x - WIDTH_POINTS),
                              round(joueur.worldPositionZ / d + z - WIDTH_POINTS))
            map_canvas.itemconfig(joueur.oval, fill=teams_color_dictionary[joueur.teamId])
            map_canvas.moveto(joueur.etiquette, round(joueur.worldPositionX / d + x - 35),
                              round(joueur.worldPositionZ / d + z - 30))
            map_canvas.itemconfig(joueur.etiquette, fill=teams_color_dictionary[joueur.teamId], text=joueur.name)

    for i in range(len(session.segments)):
        map_canvas.itemconfig(session.segments[i], fill=color_flag_dict[session.marshalZones[i].m_zone_flag])
    session.anyYellow = any(item.m_zone_flag == 3 for item in session.marshalZones)