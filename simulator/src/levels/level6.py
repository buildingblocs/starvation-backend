from gameAPI import enemiesWithinRange, getFriendlyTroops, distanceToEntity

# AI for level 6 (High Range)
# Beaten by level 3 AI, beats level 4,5
def distributeSkill(points):
    return [0, 0, points, 0]

def decideAction(self):
    global cnt
    enemies = enemiesWithinRange(self)

    # Attack any enemy within range
    if (len(enemies) > 0): self.attack(enemies[0]) # Attacks bases first
    else: self.move(1)
    
