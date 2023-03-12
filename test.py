import requests

print(requests.post("http://127.0.0.1:35897/sendCode", json=dict(code="""
def distributeSkill(points):
    return [points//4, points//4, points//4, points//4]

def decideAction(self):
    attackable = enemiesWithinRange(self)
    if (len(attackable) != 0): self.attack(attackable[0])
    else: self.move(1)
""")).json())