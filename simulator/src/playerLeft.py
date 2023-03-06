from troop import distanceToEntity, enemiesWithinRange, getFriendlyTroops

# Insert the import statements above programatically (user not supposed to write this)


# Sample player code
def distributeSkill(points):
    return [points // 4, points // 4, points // 4, points // 4]


def decideAction(self):
    attackable = enemiesWithinRange(self)
    if len(attackable) != 0:
        self.attack(attackable[0])
    else:
        self.move(1)
