import pygame
import os
from collision import collide
pygame.font.init()

WIDTH, HEIGHT = 750, 750
HEALTH = 100

# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png")) # Player ship

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not height >= self.y >= 0 # not on screen

    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=HEALTH):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj=None):  # Pass an obj for collision checks (Player or Enemy)
        self.cooldown()
        for laser in self.lasers[:]:  # Iterate over a copy of the list to avoid modifying while iterating
            laser.move(vel)
            if laser.off_screen(HEIGHT):  # Remove laser if it goes off the bottom of the screen
                self.lasers.remove(laser)
            elif laser.collision(obj):  # If the laser collides with the player, reduce health
                if obj:  # Ensure collision only happens when there's an object to check against (Player or Enemy)
                    obj.health -= 10
                self.lasers.remove(laser)  # Remove laser after collision

    def cooldown(self): # A half second delay so player is not shooting too fast
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship): # Class Player inherits all the attributes and methods of class Ship

    GREEN_BAR = (255, 0, 0)
    def __init__(self, x, y, health=HEALTH):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img) # Take the surface image (e.g. ship_img) and put a mask on it. The mask tells where the pixels are and aren't in the image, which is useful in detecting collision.
        self.max_health = health

    def move_lasers(self, vel, objs=None): # Checks if laser fired by enemy hits the player object
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT): # Checks if laser is off the screen, if so, remove it
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (
            self.x, self.y + self.ship_img.get_height() + 10,
            self.ship_img.get_width() * (self.health / self.max_health), 10))

    # Here, we are defining shoot() correctly so it works as expected
    def shoot(self):
        if self.cool_down_counter == 0:  # Check if cooldown is finished
            laser = Laser(self.x + self.get_width() // 2 - self.laser_img.get_width() // 2, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1  # Start cooldown

class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=HEALTH):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel): # Note that enemy ship will only move downward
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + self.get_width() // 2 - self.laser_img.get_width() // 2, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1