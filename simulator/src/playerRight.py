from gameAPI import enemiesWithinRange, getFriendlyTroops, distanceToEntity

# Level 3 - Default Player Code lol
def distributeSkill(points):
    return [points//4, points//4, points//4, points//4]

def decideAction(self):
    attackable = enemiesWithinRange(self)
    if (len(attackable) != 0): self.attack(attackable[0])
    else: self.move(1)
