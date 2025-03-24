import os
import pygame
import random
from widgets import Player, Enemy
from collision import collide

# Set up the pygame window
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Game")

BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

def main():
    run = True
    fps = 60 # higher/lower number of frames is faster/slower
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1
    player_vel = 5
    laser_vel = 5
    player = Player(300, 630) # Located at the bottom of the screen

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0)) # blit obtains background object and place it at top-left corner of the screen
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        WIN.blit(lives_label, (10,10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy_ in enemies:
            enemy_.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350)) # Places text at center of the screen

        pygame.display.update() # Refresh displays every 60 FPS

    while run:
        clock.tick(fps) # Set the clock speed at 60 FPS
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count +=1

        if lost:
            if lost_count > fps * 3: # 3 seconds timer
                run = False
            else:
                continue # if else is true, while loop above will restart and below are ignored

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(
                    random.randrange(50, WIDTH-100),
                    random.randrange(-1500, -100),
                    random.choice(["red", "blue", "green"])
                )
                enemies.append(enemy)

        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed() # Return all keys and confirms whether a key is pressed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            if player.x - player_vel >0:
                player.x -= player_vel
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            if player.x + player_vel + player.get_width() < WIDTH:
                player.x += player_vel
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            if player.y - player_vel > 0:
                player.y -= player_vel
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            if player.y + player_vel + player.get_height() + 15 < HEIGHT:
                player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]: # '[:]' copies the list you're looping through as sometimes it can cause an issue when you modify the original list
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT: # elif instead of if so there's no need to check if enemy has already collided with the player
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 50)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label =  title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()