import playerLeft
import playerRight
from gameAPI import *

LeftPlayerTroop.update = playerLeft.decideAction
LeftPlayerTroop.setSkill = playerLeft.distributeSkill
RightPlayerTroop.update = playerRight.decideAction
RightPlayerTroop.setSkill = playerRight.distributeSkill
