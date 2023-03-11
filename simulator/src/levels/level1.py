from gameAPI import enemiesWithinRange, getFriendlyTroops, distanceToEntity

# AI for level 1 (Stands still and defends)
def distributeSkill(points):
    return [1,1,1,1]

def decideAction(self):
    attackable = enemiesWithinRange(self)
    if (len(attackable) != 0): self.attack(attackable[0])
