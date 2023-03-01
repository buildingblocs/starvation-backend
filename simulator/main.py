# Main Game Loop + Global Variables
import json

from troop import *
from user import *

def main():
    # Initialisation
    details = []
    running = True
    time_passed = 0
    seconds_passed = 0
    pause = False

    # Add bases (which are secretly troops)
    leftTroops.append(Base(id=1, health=250, position=LEFT_BASE_POS))  # Left base, Id = 1, health = 1000
    rightTroops.append(Base(id=-1, health=250, position=RIGHT_BASE_POS))  # Right base, Id = -1, health = 1000

    # Game Loop
    while running:
        clock.tick(FPS)
        display_clock(seconds_passed)

        # Check if base is still alive
        if len(leftTroops) == 0 or leftTroops[0].troop_id != 1: break
        if len(rightTroops) == 0 or rightTroops[0].troop_id != -1: break

#        for event in pygame.event.get():
#            if event.type == pygame.QUIT:
#                run = False
#                json_object = json.dumps(details, indent=4)
#                with open("results.json", "w") as outfile:
#                    outfile.write(json_object)
#                pygame.quit()

        # Skip game if paused (why is this here!?)
        if pause: continue

        time_passed += 1

        if time_passed % 60 == 0:
            seconds_passed += 1  # Timer in seconds for normal humans

        if time_passed % 300 == 0:
            # Calculate the current number of points, and pass to user function
            summonTroops(seconds_passed // 30)

        # For every troop, run update function
        for troop in leftTroops: troop.update()
        for troop in rightTroops: troop.update()
        # For every action in queue
        # sort to process attack first
        troop_actions_list.sort(key=lambda x: x[0])
        for action in troop_actions_list:  # type: [str, int, int, int]
            if action[0] == "attack":  # Process attack
                if action[2].troop_id < 0:
                    # attack right troops
                    pos = getTroopById(action[2].troop_id)
                    action[2].update_health(-action[3])
                else:
                    print(action[2].troop_id)
                    pos = getTroopById(action[2].troop_id)
                    rightTroops[pos].update_health(-action[3])
            else:  # Process move
                if action[1] < 0: rightTroops[getTroopById(action[1])].update_position(action[2])
                else: leftTroops[getTroopById(action[1])].update_position(action[2])

        troop_actions_list.clear()

        # Debugging COde to show every troop and their position
        # for i in leftTroops: print(i.troop_id, i.position)
        # for i in rightTroops: print(i.troop_id, i.position)
        
        # Prepare Big JSON for all that has happened in the simulator
        troops = dict()
        for troop in (rightTroops + leftTroops):
            troops[troop.troop_id] = {'Health' : troop.health, 'Position' : troop.position}
        details.append(troops)
        
        # Delete all dead troops
        for ind, troop in enumerate(rightTroops): 
            if troop.health < 0: rightTroops.pop(ind)
        for ind, troop in enumerate(leftTroops): 
            if troop.health < 0: leftTroops.pop(ind)


    json_object = json.dumps(details, indent=4)
    with open("results.json", "w") as outfile:
        outfile.write(json_object)

main()
