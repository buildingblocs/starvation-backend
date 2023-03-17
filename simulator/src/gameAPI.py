# Variables from other files
from troop import Base, ImmutableTroop, LeftPlayerTroop, RightPlayerTroop, troop_actions_list, Troop

# Preparing API functions
LEFT_BASE_POS = 0
RIGHT_BASE_POS = 1000

leftTroops = []
rightTroops = []

LEFT_CNT = 1
RIGHT_CNT = 1


def summonTroops(level):
    # TODO: Balance skill point scaling
    skill_points = 4 + 2 * level
    
    # Create and append
    global LEFT_CNT, RIGHT_CNT
    LEFT_CNT += 1
    RIGHT_CNT += 1

    leftTroops.append(LeftPlayerTroop(LEFT_CNT, skill_points, LEFT_BASE_POS))
    rightTroops.append(RightPlayerTroop(-RIGHT_CNT, skill_points, RIGHT_BASE_POS))
    pass


def enemiesWithinRange(troop):
    if troop.troop_id > 0:
        enemies = rightTroops
    else:
        enemies = leftTroops
    attackable = [ImmutableTroop(i) for i in enemies if distanceToEntity(troop, i) <= troop._rng]
    return attackable


def getFriendlyTroops(troop):
    troops = leftTroops if troop.troop_id > 0 else rightTroops
    return [ImmutableTroop(i) for i in troops]


def distanceToEntity(troop1, id):
    # Incase they pass in a troop instead
    if not isinstance(id, int): return abs(troop1.position - id.position)

    # Flip the id if they are on the right side (id ref is usually for base)
    if (troop1.troop_id < 0): id = -id

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


def getTroopById(troop):
    pos = 0
    if troop.troop_id < 0:
        for i in rightTroops:
            if i.troop_id == troop.troop_id:
                return pos
            pos += 1
    else:
        for i in leftTroops:
            if i.troop_id == troop.troop_id:
                return pos
            pos += 1
    raise ValueError("Troop does not exist")

def cheatUpdateHealth(target_troop: ImmutableTroop, amount: int):
    for troop in leftTroops:
        if troop.troop_id == target_troop.troop_id:
            troop.update_health(amount)
    for troop in rightTroops:
        if troop.troop_id == target_troop.troop_id:
            troop.update_health(amount)