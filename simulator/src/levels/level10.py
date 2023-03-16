from gameAPI import enemiesWithinRange, getFriendlyTroops, distanceToEntity

# AI for level 10 (High Health + Healing)
# Beaten by level 3 AI, beats level 4,5,6,7
cnt = 0

def distributeSkill(points):
    global cnt
    cnt = (cnt + 1) % 10

    return [points - points // 4, 0, 0, points // 4] if cnt < 2 or cnt > 6 else [0, points - points // 4, points // 4, 0]

def decideAction(self):
    global cnt
    enemies = enemiesWithinRange(self)

    # Charge forward if enemy is within range
    if (len(enemies) > 0): self.attack(enemies[0])
    elif distanceToEntity(self, 1) > 0 or (len(enemies) == 0) and cnt >= 9: self.move(1)