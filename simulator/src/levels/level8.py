from gameAPI import enemiesWithinRange, getFriendlyTroops, distanceToEntity

# AI for level 8 (Alternating attack and heal)
# Beaten by level 3 AI, beats level 4,5,6
def distributeSkill(points):
    return [0, 0, points, 0]

def decideAction(self):
    global cnt
    enemies = enemiesWithinRange(self)

    # Attack any enemy within range
    if (len(enemies) > 0): 
        if(cnt % 2 == 0):
            self.attack(enemies[-1]) # Now targets troops first
        else:
            self.update_health(5)
    else: self.move(1)
    