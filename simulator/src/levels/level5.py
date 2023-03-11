from gameAPI import enemiesWithinRange, getFriendlyTroops, distanceToEntity

# AI for level 5 (Grouping, same as 4)

def distributeSkill(points):
    cnt = (cnt + 1) % 5

    # Nerf their attacking power, so that player can actl win
    return [points//4, points//4 - 1, points//4, points//4]

cnt = 0

def decideAction(self):
    enemies = enemiesWithinRange(self)

    # Charge forward if enemy is within range
    if (len(enemies) == 0) and cnt >= 5: self.move(1)
    if (len(enemies)): self.attack(enemies[0])
    
