import requests

print(requests.post("http://34.142.168.126:3000/sendCode", json=dict(code="""
cnt = 0

def distributeSkill(points):
    global cnt
    cnt = (cnt + 1) % 5

    # Nerf their speed power, so that player can actl win
    return [points//4, points//4 - 1, points//4, points//4]

def decideAction(self):
    global cnt
    enemies = enemiesWithinRange(self)

    # Charge forward if enemy is within range
    if (len(enemies) > 0): self.attack(enemies[0])
    elif distanceToEntity(self, 1) > 0 or (len(enemies) == 0) and cnt >= 4: self.move(1)
""")).json())