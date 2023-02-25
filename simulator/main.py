# Main Game Loop + Global Variables


import os  # I didn't even use this lol

import pygame  # not really necessary, but might be easier to use. Currently pygame is a placeholder to show that the loop works.

from troop import troop, troop_actions_queue

pygame.font.init()  # Initialize font library, idk why it still says not initialized

WIDTH, HEIGHT = 900, 500  # Display size
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))  # Game screen, exists to show that the clock works
TIMER_FONT = pygame.font.SysFont("comicsans", 100)  # Haha comic sans go brr
BLUE = (0, 0, 255)  # Blue color
background = pygame.Rect(0, 0, WIDTH, HEIGHT)  # Background
pygame.display.update()


pygame.display.set_caption("CodeCombat placeholder screen")

FPS = 60  # Limits game to run at 60FPS, game will run at <= 60 FPS max


class Base:
    def __init__(self, Id, health):
        self.Id = Id
        self.health = health


def display_clock(seconds_passed):  # placeholder for screen
    pygame.draw.rect(WINDOW, (0, 0, 255), background)  # Wipe away last frame
    timer_text = TIMER_FONT.render("Time passed: " + str(seconds_passed), 1, (255, 255, 255))  # Render timer
    WINDOW.blit(timer_text, (100, 160))  # Paint timer onto screen
    pygame.display.update()  # Update screen (very essential)


def distributeSkill(health, dmg, range, speed):
    pass


def decideAction():
    pass


def summonTroop():
    pass


def enemiesWithinRange(self):
    pass


def getFriendlyId(self):
    pass


def distanceToEntity(self, id):
    pass


def attack(self, enemyId: int):
    pass


def move(self, dir: int):
    pass


def main():
    clock = pygame.time.Clock()
    pygame.font.init()
    running = True
    time_passed = 0
    seconds_passed = 0
    pause = False
    player_one_base = Base(1, 1000)  # Left base, Id = 1, health = 1000
    player_two_base = Base(-1, 1000)  # Right base, Id = -1, health = 1000
    while running:
        clock.tick(FPS)
        display_clock(seconds_passed)
        if pause == False:
            time_passed += 1
            if time_passed % 60 == 0:
                seconds_passed += 1  # Timer in seconds for normal humans
            if time_passed % 300 == 0:
                summonTroop()  # Summons one troop on each side every 5 seconds
                distributeSkill(
                    0, 0, 0, 0
                )  # Allows each player to modify their new troop, for the love of me I still don't get how this game works
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()


main()
