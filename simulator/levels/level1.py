# AI for level 1
def distributeSkill(points):
    return [points//4, points//4, points//4, points//4 - 1]

def decideAction(self):
    attackable = enemiesWithinRange(self)
    if (len(attackable) != 0): attack(self, attackable[0])
    else: move(self, 1)
