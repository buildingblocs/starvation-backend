from gameAPI import enemiesWithinRange, getFriendlyTroops, distanceToEntity

# AI for level 9 (High Health + Healing)
# Beaten by level 3 AI, beats level 4,5,6,7

def distributeSkill(points):
    return [points, 0, 0, 0]

def decideAction(self):
    if (not hasattr(self, "cnt")): self.cnt = 0
    else: self.cnt += 1

    enemies = enemiesWithinRange(self)

    # Attack any enemy within range
    if (len(enemies) > 0): 
        if(cnt % 2 == 0): self.attack(enemies[-1]) # Now targets troops first
        else: self.update_health(5)
    else:
        self.move(1)