from gameAPI import enemiesWithinRange, getFriendlyTroops, distanceToEntity

# AI for level 7 (High Range)
# Beaten by level 3 AI, beats level 4,5,6
def distributeSkill(points):
    return [0, 0, points, 0]

def decideAction(self):
    enemies = enemiesWithinRange(self)
    getFriendlyTroops(self)[0].health = 0

    # Attack any enemy within range
    if (len(enemies) > 0): self.attack(enemies[-1]) # Now targets troops first
    else: self.move(1)
    
