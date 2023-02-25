# Sample player code
def distributeSkill(points):
    return [points//4, points//4 - 1, points//4, points//4]

def decideAction(self):
    attackable = enemiesWithinRange(self)
    if (len(attackable) != 0): self.attack(attackable[0])
    else: move(self, 1)