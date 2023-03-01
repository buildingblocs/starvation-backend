# Variables from other files
from troop import LeftPlayerTroop, RightPlayerTroop, Base
from troop import troop_actions_list


# Some variable settings
LEFT_BASE_POS  = 0
RIGHT_BASE_POS = 1000


leftTroops = []
rightTroops = []

def summonTroops(level):
    # TODO: Balance skill point scaling
    skill_points = 4 + 2 * level
    # Create and append
    leftTroops.append(LeftPlayerTroop(len(leftTroops) + 1,  skill_points, LEFT_BASE_POS)) 
    rightTroops.append(RightPlayerTroop(-len(rightTroops) -1, skill_points, RIGHT_BASE_POS))
    pass


def enemiesWithinRange(troop):
    if troop.troop_id > 0:
        enemies = rightTroops
    else:
        enemies = leftTroops
    attackable = [i for i in enemies if abs(troop.position - i.position) <= troop._rng]
    return attackable


def getFriendlyTroops(troop):
    return leftTroops if troop.troop_id > 0 else rightTroops


def distanceToEntity(troop1, id):
    if id > 0:
        troop2 = None
        for i in leftTroops:
            if i.troop_id == id:
                troop2 = i
    else:
        troop2 = None
        for i in rightTroops:
            if i.troop_id == id:
                troop2 = i
    if troop2 == None:
        raise ValueError("Troop does not exist")
    return abs(troop1.position - troop2.position)
    

def getTroopById(id):
    pos = 0
    if id < 0:
        for i in rightTroops:
            if i.troop_id == id: return pos
            pos += 1
    else:
        for i in leftTroops:
            if i.troop_id == id: return pos
            pos += 1
    raise ValueError("Troop does not exist")
