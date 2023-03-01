# Troop actions (array because need to sort by action type)
troop_actions_list = []


# Game Object Functions
class Troop:
    '''
    troop_id: id of the troop
    health: troop health
    position: x coordinate

    "Hidden" Variables
    _rng: the range of the troop (can attack if distance is <= range)
    _dmg: the dmg of the troop (when attack, enemy.health -= self.dmg)
    _spd: the speed of the troop (px per second)
    '''

    def __init__(self, troop_id, skill_points, position):
        self.position = position
        self.troop_id = troop_id
        # Health points, damage points, range points, speed points
        hp, dp, rp, sp = type(self).setSkill(skill_points)

        # Check if points are valid
        if (hp + dp + rp + sp > skill_points): raise ValueError("Conservation of Points violated")
        if (hp < 0 or dp < 0 or rp < 0 or sp < 0): raise ValueError("Negative Points allocated!?")

        # Calculating and setting actual values
        # TODO: Make values balanced maybe
        self.health = 5 + (hp * 5)
        self._dmg = 1 + (dp * 2)
        self._rng = 50 + (rp * 25)
        self._spd = 10 + (sp * 5)


    def attack(self, enemy_id):
        # Passes the "attack" action, the troop attacking and the troop attacked
        # check if in range
        troop_actions_list.append(["attack", self.troop_id, enemy_id, self._dmg])

    def move(self, move_amount):
        # Passes the "move" action, the troop that will be moved and how much by
        troop_actions_list.append(["move", self.troop_id, move_amount])

    def update_health(self, change):
        self.health += change

    def update_position(self, direction):
        if self.troop_id < 0: # move the other way
            self.position -= self._spd * direction
        else:
            self.position += self._spd * direction

    def setSkill(skill):
        print("Called setSkill Parent")
        return [0, 0, 0, 0]


class Base(Troop):
    """
    Base is secretly a troop
    It has all the functions of a troop, but user code is not written
    """
    def __init__(self, id, health, position):
        self.troop_id = id
        self.health = health
        self.position = position 
    
    def update(self): pass


# Subclass for left player's functions
class LeftPlayerTroop(Troop):
    # Set the player's functions (I hope)
    def update(self): pass

# Subclass for right player's functions
class RightPlayerTroop(Troop):
    # Set the player's functions (I hope)
    def update(self): pass