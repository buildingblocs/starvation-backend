from gameAPI import enemiesWithinRange, getFriendlyTroops, distanceToEntity

# AI for level 5 (Grouping, same as 4)
cnt = 0

def distributeSkill(points):
    global cnt
    cnt = (cnt + 1) % 6

    # Nerf their speed power, so that player can actl win
    return [points//4, points//4 - 1, points//4, points//4]

def decideAction(self):
    global cnt
    enemies = enemiesWithinRange(self)

    # Charge forward if enemy is within range
    if (len(enemies) > 0): self.attack(enemies[0])
    elif distanceToEntity(self, 1) > 0 or (len(enemies) == 0) and cnt >= 5: self.move(1)
    
