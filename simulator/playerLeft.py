from troop import enemiesWithinRange, getFriendlyTroops, distanceToEntity
# Insert the import statements above programatically (user not supposed to write this)

# Sample player code
def distributeSkill(points):
    return [points//4, points//4, points//4, points//4]

def decideAction(self):
    # TODO: Fix the import problem
    attackable = enemiesWithinRange(self)
    if (len(attackable) != 0): self.attack(attackable[0])
    else: self.move(1)
