# Main Game Loop + Global Variables

import os  # I didn't even use this lol
import pygame  # not really necessary, but might be easier to use. Currently pygame is a placeholder to show that the loop works.

# Gotta split up gameAPI, circular import moments
from troop import *


pygame.font.init()  # Initialize font library, idk why it still says not initialized

WIDTH, HEIGHT = 900, 500  # Display size
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))  # Game screen, exists to show that the clock works
TIMER_FONT = pygame.font.SysFont("comicsans", 100)  # Haha comic sans go brr
BLUE = (0, 0, 255)  # Blue color
background = pygame.Rect(0, 0, WIDTH, HEIGHT)  # Background
pygame.display.update()


pygame.display.set_caption("CodeCombat placeholder screen")

FPS = 60  # Limits game to run at 60FPS, game will run at <= 60 FPS max


def display_clock(seconds_passed):  # placeholder for screen
    pygame.draw.rect(WINDOW, (0, 0, 255), background)  # Wipe away last frame
    timer_text = TIMER_FONT.render("Time passed: " + str(seconds_passed), 1, (255, 255, 255))  # Render timer
    WINDOW.blit(timer_text, (100, 160))  # Paint timer onto screen
    pygame.display.update()  # Update screen (very essential)


def main():
    # Initialisation
    clock = pygame.time.Clock()
    pygame.font.init()
    running = True
    time_passed = 0
    seconds_passed = 0
    pause = False

    # Add bases (which are secretly troops)
    leftTroops. append(Base(id =  1, health = 250, position = LEFT_BASE_POS))   # Left base, Id = 1, health = 1000
    rightTroops.append(Base(id = -1, health = 250, position = RIGHT_BASE_POS))  # Right base, Id = -1, health = 1000

    # Game Loop
    while running:
        clock.tick(FPS)
        display_clock(seconds_passed)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
        
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
        # TODO: @iamnumber4#0655


main()
