# Main Game Loop + Global Variables

import os  # I didn't even use this lol

# import pygame  # not really necessary, but might be easier to use. Currently pygame is a placeholder to show that the loop works.
import json
import time

# Gotta split up gameAPI, circular import moments
from troop import *
from user import *

# pygame.font.init()  # Initialize font library, idk why it still says not initialized

# WIDTH, HEIGHT = 900, 500  # Display size
# WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))  # Game screen, exists to show that the clock works
# TIMER_FONT = pygame.font.SysFont("comicsans", 100)  # Haha comic sans go brr
# BLUE = (0, 0, 255)  # Blue color
# background = pygame.Rect(0, 0, WIDTH, HEIGHT)  # Background
# pygame.display.update()

# pygame.display.set_caption("CodeCombat placeholder screen")

# FPS = 60  # Limits game to run at 60FPS, game will run at <= 60 FPS max


# def display_clock(seconds_passed):  # placeholder for screen
#     pygame.draw.rect(WINDOW, (0, 0, 255), background)  # Wipe away last frame
#     timer_text = TIMER_FONT.render("Time passed: " + str(seconds_passed), 1, (255, 255, 255))  # Render timer
#     WINDOW.blit(timer_text, (100, 160))  # Paint timer onto screen
#     pygame.display.update()  # Update screen (very essential)


def main():
    # Initialisation
    details = []
    # clock = pygame.time.Clock()
    # pygame.font.init()
    result = "draw"
    running = True
    time_passed = 0
    seconds_passed = 0
    pause = False

    # Add bases (which are secretly troops)
    leftTroops.append(Base(id=1, health=250, position=LEFT_BASE_POS))  # Left base, Id = 1, health = 1000
    rightTroops.append(Base(id=-1, health=250, position=RIGHT_BASE_POS))  # Right base, Id = -1, health = 1000

    start = time.time()

    # Game Loop
    for i in range(5400): # 3 minutes at 30fps
        # clock.tick(FPS)
        # display_clock(seconds_passed)

        # Check if base is still alive
        if len(leftTroops) == 0 or leftTroops[0].troop_id != 1:
            result = "right"
            print("Right Wins")
            break
        if len(rightTroops) == 0 or rightTroops[0].troop_id != -1:
            result = "left"
            print("Left Wins")
            break

        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         run = False
        #         json_object = json.dumps(details, indent=4)
        #         with open("results.json", "w") as outfile:
        #             outfile.write(json_object)
        #         pygame.quit()

        # Skip game if paused (why is this here!?)
        # if pause:
        #     continue

        time_passed += 1

        if time_passed % 60 == 0:
            seconds_passed += 1  # Timer in seconds for normal humans

        if time_passed % 300 == 0:
            # Calculate the current number of points, and pass to user function
            summonTroops(seconds_passed // 30)

        # For every troop, run update function
        for troop in leftTroops:
            troop.update()
        for troop in rightTroops:
            troop.update()
        
        # For every action in queue
        # sort to process attack first
        troop_actions_list.sort(key=lambda x: x[0])

        for action in troop_actions_list:
            if action[0] == "attack":  # Process attack: [str, Troop, Troop]
                # Skip the attack if not possible (ie out of range)
                if distanceToEntity(action[1], action[2]) > action[1]._rng: continue

                action[2].update_health(-action[1]._dmg)

            else:  # Process move: [str, Troop, int]
                if action[1].troop_id < 0:
                    rightTroops[getTroopById(action[1])].update_position(action[2])
                else:
                    leftTroops[getTroopById(action[1])].update_position(action[2])

            # Troop regains action ability
            action[1]._action = True

        troop_actions_list.clear()

        # Prepare Big JSON for all that has happened in the simulator
        troops = dict()
        for troop in rightTroops + leftTroops:
            troops[str(troop.troop_id)] = {"h": troop.health, "p": troop.position}
        details.append(troops)

        # Delete all dead troops
        for ind, troop in enumerate(rightTroops):
            if troop.health <= 0:
                rightTroops.pop(ind)
        for ind, troop in enumerate(leftTroops):
            if troop.health <= 0:
                leftTroops.pop(ind)
    else:
        # sudden death
        left_health = leftTroops[0].health
        right_health = rightTroops[0].health
        if left_health > right_health:
            result = "left"
            print("Left Wins")
        elif right_health > left_health:
            result = "right"
            print("Right Wins")
        else:
            print("Draw")

    # Debugging Code to show every troop and their position
    for i in leftTroops: print(i.troop_id, i.position, i.health)
    for i in rightTroops: print(i.troop_id, i.position, i.health)
    print("================================================================")
    
    json_object = json.dumps({"details": details, "result": result, "runtime": time.time() - start}, separators=(',', ':'))
    with open("results.json", "w") as outfile:
        outfile.write(json_object)


main()
