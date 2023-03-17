# Game Object Functions

# Troop actions (array because need to sort by action type)
troop_actions_list = []

def sign(x): return 1 if x > 0 else 0 if x == 0 else -1

class Troop:
    """
    troop_id: id of the troop
    health: troop health
    position: x coordinate

    "Hidden" Variables
    _rng: the range of the troop (can attack if distance is <= range)
    _dmg: the dmg of the troop (when attack, enemy.health -= self.dmg)
    _spd: the speed of the troop (px per second)
    _hlt: the real health of the troop
    _pos: the real position of the troop
    _action: if True, troop can use an action
    """

    def __init__(self, troop_id, skill_points, position):
        self._pos = self.position = position
        self.troop_id = troop_id
        self._action = True

        # Health points, damage points, range points, speed points
        hp, dp, rp, sp = type(self).setSkill(skill_points)

        # Check if points are valid
        if hp + dp + rp + sp > skill_points:
            raise ValueError("Conservation of Points violated")
        if hp < 0 or dp < 0 or rp < 0 or sp < 0:
            raise ValueError("Negative Points allocated!?")

        # Calculating and setting actual values
        # TODO: Make values balanced maybe
        self._hlt = self.health = 5 + (hp * 5)
        self._dmg = (1 + (dp * 2)) / 30
        self._rng = 50 + (rp * 25)
        self._spd = (10 + (sp * 5)) / 30

    def attack(self, enemy):
        # Action Used already
        if not self._action: return

        # Passes the "attack" action, the troop attacking and the troop attacked
        troop_actions_list.append(["attack", self, enemy, self._dmg])
        self._action = False

    def move(self, dir):
        # Action Used already
        if not self._action: return

        # Passes the "move" action, the troop that will be moved and how much by
        troop_actions_list.append(["move", self, sign(dir)])
        self._action = False

    def update_health(self, change):
        self._hlt += change

        self.health = self._hlt

    def update_position(self, direction):
        if self.troop_id < 0:  # move the other way
            self._pos -= self._spd * direction
        else:
            self._pos += self._spd * direction
        
        self.position = self._pos

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
        self._hlt = self.health = health
        self._pos = self.position = position

    def update(self):
        pass


# Getting player code


# Subclass for left player's functions
class LeftPlayerTroop(Troop):
    # Set the player's functions (I hope)
    def update(self):
        pass


# Subclass for right player's functions
class RightPlayerTroop(Troop):
    # Set the player's functions (I hope)
    def update(self):
        pass
