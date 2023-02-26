from gameAPI import *
import playerLeft
import playerRight

LeftPlayerTroop.update = playerLeft.decideAction
LeftPlayerTroop.setSkill = playerLeft.distributeSkill
RightPlayerTroop.update = playerRight.decideAction
RightPlayerTroop.setSkill = playerRight.distributeSkill