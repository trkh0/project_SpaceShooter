import pygame
import os
from random import randint
from time import time

from pygame.constants import KEYDOWN

pygame.font.init()
pygame.display.set_caption("Space Shooter")

WIDTH = 1200
HEIGHT = 900
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

SHIP_WIDTH = 50
SHIP_HEIGHT = 60
METEOR_WIDTH = 30
METEOR_HEIGHT = 30
MISSLE_HEIGHT = 15
MISSLE_WIDTH = 5


RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (220, 220, 220)
FPS = 60

METEOR_HIT = pygame.USEREVENT + 1
MISSLE_HIT = pygame.USEREVENT + 2

PLAYER_SPEED = 5
METEOR_SPEED = 7
GAME_SPEED = 0.3
MISSLE_SPEED = 15
HEALTH_TEXT_SIZE = 20

RUNNING, PAUSE, LOST, MAIN = 0, 1, 2, 3
MODE_EASY, MODE_MEDIUM, MODE_HARD = 0, 1, 2

FONT = pygame.font.SysFont('comicsans', HEALTH_TEXT_SIZE)
PAUSE_FONT = pygame.font.SysFont('comicsans', 50)

SHIP_IMAGE = pygame.image.load("spaceship.png")
SHIP = pygame.transform.scale(SHIP_IMAGE, (SHIP_WIDTH, SHIP_HEIGHT))

METEOR_IMAGE = pygame.image.load("meteor.png")
METEOR = pygame.transform.scale(METEOR_IMAGE, (METEOR_WIDTH, METEOR_HEIGHT))

BACKGROUND_IMAGE = pygame.image.load("space.jpg")
BACKGROUND = pygame.transform.scale(BACKGROUND_IMAGE, (WIDTH, HEIGHT))

MISSLE_IMAGE = pygame.image.load("missle.png")
MISSLE = pygame.transform.scale(MISSLE_IMAGE, (MISSLE_WIDTH, MISSLE_HEIGHT))




def meteor_spawn(meteors):
    posX = randint(10, WIDTH - 10)
    meteor = pygame.Rect(posX, 20, METEOR_WIDTH, METEOR_HEIGHT)
    meteors.append(meteor)

def missle_spawn(missles, player):
    missle = pygame.Rect(player.x + SHIP_WIDTH//2, player.y, MISSLE_WIDTH, MISSLE_HEIGHT)
    missles.append(missle)


def meteor_move(meteors, mode):
    for meteor in meteors:
        meteor.y += mode[1]
        if meteor.y > HEIGHT:
            meteors.remove(meteor)

def missle_move(missles):
    for missle in missles:
        missle.y -= MISSLE_SPEED
        if missle.y < 0:
            missles.remove(missle)


def collision(player, meteors, missles):
    for meteor in meteors:
        if player.colliderect(meteor):
            pygame.event.post(pygame.event.Event(METEOR_HIT))
            meteors.remove(meteor)
        for missle in missles:
            if missle.colliderect(meteor):
                pygame.event.post(pygame.event.Event(MISSLE_HIT))
                meteors.remove(meteor)
                missles.remove(missle)
    



def draw_window(player, meteors, missles, player_health, player_score):
    WINDOW.blit(BACKGROUND, (0, 0))
    for meteor in meteors:
        WINDOW.blit(METEOR, meteor)
    for missle in missles:
        WINDOW.blit(MISSLE, missle)
    WINDOW.blit(SHIP, player)
    health = FONT.render("Health: " + str(player_health), 1, WHITE)
    score = FONT.render("Score: " + str(player_score), 1, WHITE)
    WINDOW.blit(health, (10, HEIGHT - HEALTH_TEXT_SIZE - 10))
    WINDOW.blit(score, (WIDTH - score.get_width() -
                5, HEIGHT - HEALTH_TEXT_SIZE - 10))
    pygame.display.update()


def player_movement(keys_pressed, player):
    if keys_pressed[pygame.K_UP] and player.y - PLAYER_SPEED > 10:
        player.y -= PLAYER_SPEED
    if keys_pressed[pygame.K_DOWN] and player.y + SHIP_HEIGHT < HEIGHT - 10:
        player.y += PLAYER_SPEED
    if keys_pressed[pygame.K_LEFT] and player.x - PLAYER_SPEED > 10:
        player.x -= PLAYER_SPEED
    if keys_pressed[pygame.K_RIGHT] and player.x + SHIP_WIDTH < WIDTH - 10:
        player.x += PLAYER_SPEED


def draw_pause():
    pause = PAUSE_FONT.render("PASUED", 1, WHITE)
    WINDOW.blit(pause, (WIDTH//2 - pause.get_width() //
                2, HEIGHT//2 - pause.get_height()//2))
    pygame.display.update()

def draw_loseScreen(player_score, high_score):
    draw_text = PAUSE_FONT.render("You lost!", 1, WHITE)
    WINDOW.blit(draw_text, (WIDTH//2 - draw_text.get_width() //
                2, HEIGHT//2 - draw_text.get_height()//2))
    if player_score > high_score:
        highS = FONT.render("New highscore!", 1, WHITE)
        WINDOW.blit(highS, (WIDTH//2 - highS.get_width()//2,
                    HEIGHT//2 - highS.get_height()//2 + 100))        
    space = FONT.render("Press space to restart!", 1, WHITE)
    WINDOW.blit(space, (WIDTH//2 - space.get_width()//2,
                HEIGHT//2 - space.get_height()//2 + 200))
    quit = FONT.render("Press ESC to quit", 1, WHITE)
    WINDOW.blit(quit, (20, 20))
    main = FONT.render("Press M to go back", 1, WHITE)
    WINDOW.blit(main, (WIDTH - main.get_width() - 20, 20))

    pygame.display.update()


def draw_main(mode, high_score):
    WINDOW.blit(BACKGROUND, (0, 0))
    title = PAUSE_FONT.render("Space shooter", 1, WHITE)
    WINDOW.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    space = FONT.render("Press space to start!", 1, WHITE)
    WINDOW.blit(space, (WIDTH//2 - space.get_width() //
                2, HEIGHT//2 - space.get_height()//2))
    quit = FONT.render("Press ESC to quit", 1, WHITE)
    WINDOW.blit(quit, (20, 20))
    mode = FONT.render("[H] Mode: " + str(mode[0]), 1, WHITE)
    WINDOW.blit(mode, (WIDTH - mode.get_width() -20 , 20))
    high = FONT.render("High score: " + str(high_score), 1, WHITE)
    WINDOW.blit(high, (WIDTH//2 - high.get_width()//2 , HEIGHT - 150))

    pygame.display.update()


def main(restarted, modeSel = 1):
    player = pygame.Rect(WIDTH/2 - SHIP_WIDTH/2, HEIGHT -
                         100, SHIP_WIDTH, SHIP_HEIGHT)
    meteors = []
    missles = []
    f = open("highscore.txt", "r")
    high_score = int(f.readline())
    f.close()
    modes = [["Easy", 8, 0.3], ["Medium", 9, 0.1], ["Hard", 11, 0.05]]
    mode = modes[modeSel]

    player_health = 3
    player_score = 0
    clock = pygame.time.Clock()
    run = True
    time_last = time()
    if restarted == 0:
        state = MAIN
    else:
        state = RUNNING

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == METEOR_HIT:
                player_health -= 1
            if event.type == MISSLE_HIT:
                player_score += 2
            if event.type == KEYDOWN:
                if event.key == pygame.K_p:
                    if state == RUNNING:
                        state = PAUSE
                    elif state == PAUSE:
                        state = RUNNING
                if event.key == pygame.K_SPACE and state == MAIN:
                    state = RUNNING
                if event.key == pygame.K_SPACE and state == LOST:
                    main(1,modeSel)
                if event.key == pygame.K_ESCAPE and (state == LOST or state == MAIN):
                    run = False
                if event.key == pygame.K_m and state == LOST:
                    main(0,modeSel)                    
                if event.key == pygame.K_LCTRL and state == RUNNING:
                    missle_spawn(missles, player)
                if event.key == pygame.K_h and state == MAIN:
                    if mode == modes[1]:
                        modeSel = 2
                        mode = modes[2]
                    elif mode == modes[2]:
                        modeSel = 0
                        mode = modes[0]
                    elif mode == modes[0]:
                        modeSel = 1
                        mode = modes[1]

                    

        if state == RUNNING:
            if player_health <= 0:
                state = LOST

            keys_pressed = pygame.key.get_pressed()

            current = time()
            if (current - time_last > mode[2]):
                meteor_spawn(meteors)
                time_last = current
                player_score += 1
            meteor_move(meteors, mode)
            missle_move(missles)
            collision(player, meteors, missles)
            player_movement(keys_pressed, player)
            draw_window(player, meteors, missles, player_health, player_score)

        elif state == PAUSE:
            draw_pause()

        elif state == LOST:
            draw_loseScreen(player_score, high_score)
            if player_score > high_score:
                f = open("highscore.txt", "w")
                high_score = player_score
                f.write(str(high_score))
                f.close()

        elif state == MAIN:
            draw_main(mode, high_score)

    pygame.quit()


if __name__ == "__main__":
    main(0)
