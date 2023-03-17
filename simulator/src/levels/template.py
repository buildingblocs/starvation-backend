def distributeSkill(skill_points):\n    '''\n    Mario's Clones have 4 main properties:\n        - Health\n        - Damage\n        - Range\n        - Speed\n        \n    Skill points increase as the game goes on!\n    You start with 4 and gain more as Luigi fights on!\n    '''\n    health = 0\n    damage = 0\n    range = 0\n    speed = 0\n    return [health, damage, range, speed]
\ndef decideAction(self):
\n    '''
\n    Code out what the clones will do!
\n
\n    self - the clone to consider
\n    
\n    self has values you might want to use
\n    - health = self.health
\n    - position = self.position
\n    '''
\n
\n    # Returns a list of enemies in the range of the current troop
\n    # Enemies also have the values above!
\n    enemies = enemiesWithinRange(self)
\n
\n    #######################################################
\n    # To attack, pass in one of the enemies you found above
\n    # self.attack(enemies[0])
\n
\n    # To move, pass in the direction you want to move in
\n    # self.move( 1) - Towards the enemy
\n    # self.move(-1) - Away from the enemy [Towards your own base]
\n    # self.move( 0) - Stay still
\n
\n    # You can only call attack/move once this function
\n    # If you are attacking, you will not move until you call the move function again