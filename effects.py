import math

CAPTURE_RADIUS = 35

def distance(pos1, pos2):
    return math.hypot(pos1[0] - pos2[0], pos1[1] - pos2[1])

def ifcatch(players_data):
    cops = []
    thief = None

    for player_id, data in players_data.items():
        role = data['role']
        pos = data['pos']
        if role == 'cop':
            cops.append(pos)
        elif role == 'thief':
            thief = pos

    if thief is None:
        return False

    for cop_pos in cops:
        if distance(cop_pos, thief) <= CAPTURE_RADIUS:
            print(f"🚨 The thief has been caught!")
            return True

    return False

