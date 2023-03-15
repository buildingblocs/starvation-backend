import requests

url = "http://127.0.0.1:41951"

# do a bot tournament!
for i in range(2, 8): # lvl1 is broken :(
    requests.post(f"{url}/addUser", json=dict(id=f"level{i}", fullname=f"level{i}"))
    with open(f"simulator/src/levels/level{i}.py", "r") as f:
        code = f.read()
    requests.post(f"{url}/sendCode", json=dict(id=f"level{i}", code=code))


# print(requests.post("http://127.0.0.1:45427/sendCodeAI", json=dict(code="""
# cnt = 0

# def distributeSkill(points):
#     global cnt
#     cnt = (cnt + 1) % 5

#     # Nerf their speed power, so that player can actl win
#     return [points//4, points//4 - 1, points//4, points//4]

# def decideAction(self):
#     global cnt
#     enemies = enemiesWithinRange(self)

#     # Charge forward if enemy is within range
#     if (len(enemies) > 0): self.attack(enemies[0])
#     elif distanceToEntity(self, 1) > 0 or (len(enemies) == 0) and cnt >= 4: self.move(1)
# """)).json())

# code = """
# def distributeSkill(points):
#     return [0, 0, points, 0]

# def decideAction(self):
#     global cnt
#     enemies = enemiesWithinRange(self)

#     # Attack any enemy within range
#     if (len(enemies) > 0): self.attack(enemies[-1]) # Now targets troops first
#     else: self.move(1)"""

# requests.post(f"{url}/sendCode", json=dict(id="level2", code=code))