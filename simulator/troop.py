# Troop class
from queue import Queue
troop_actions_queue = Queue()
class troop:
    '''
    troop_id: id of the troop
    health: troop health
    position: x coordinate
    current_level: the current level of the truth
    '''
    def __init__(self, troop_id, health, position, current_level):
        self.troop_id = troop_id
        self.health = health
        self.position = position
        self.current_level = current_level
    def attack(self, enemy_id):
        # Passes the "attack" action, the troop attacking and the troop attacked
        troop_actions_queue.put(["attack", self.troop_id, enemy_id])
    def move(self, move_amount):
        # Passes the "move" action, the troop that will be moved and how much by
        troop_actions_queue.put(["move", self.troop_id, move_amount])
    def update_health(self, change):
        self.health += change
    def update_position(self, change):
        self.position += change
    def increment_level(self):
        self.current_level += 1
        