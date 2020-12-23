import pygame
import os
import random
import time

# Initialize the font
pygame.font.init()

WIDTH, HEIGHT = 800, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Space Invaders')

print(os.getcwd())

red_space_ship = pygame.image.load(os.path.join('assets', "pixel_ship_red_small.png"))
green_space_ship = pygame.image.load(os.path.join('assets', "pixel_ship_green_small.png"))
blue_space_ship = pygame.image.load(os.path.join('assets', "pixel_ship_blue_small.png"))

# player ship
yellow_space_ship = pygame.image.load(os.path.join('assets', "pixel_ship_yellow.png"))

# Lasers
red_laser = pygame.image.load(os.path.join('assets', 'pixel_laser_red.png'))
green_laser = pygame.image.load(os.path.join('assets', 'pixel_laser_green.png'))
blue_laser = pygame.image.load(os.path.join('assets', 'pixel_laser_blue.png'))
yellow_laser = pygame.image.load(os.path.join('assets', 'pixel_laser_yellow.png'))

# Load background image
BG = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'background-black.png')), (WIDTH, HEIGHT))


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
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(obj, self)


# ABSTRACT CLASS: Not gonna actually use the class, but inherit from it in other classes
class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, color, health=100):
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

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    # Define a method that gets the width of the spaceships image
    def get_width(self):
        return self.ship_img.get_width()

    # Define a method that gets the height of the spaceship's image
    def get_height(self):
        return self.ship_img.get_height()


# Define a class player that inherits from Ship class
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)  # super uses all the attributes of the Ship class
        self.ship_img = yellow_space_ship
        self.laser_img = yellow_laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health), 10))


# Define an enemy class that will inherit from Ship class
class Enemy(Ship):
    color_map = {"red": (red_space_ship, red_laser),
                 "green": (green_space_ship, green_laser),
                 "blue": (blue_space_ship, blue_laser)
                 }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.color_map[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 25, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x  # tells us the distance between the objects horizontally
    offset_y = obj2.y - obj1.y   # tells us the distance between the objects vertically
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


# Main function that runs the game
def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont('comiscans', 50)
    lost_fond = pygame.font.SysFont('comiscans', 60)  # appears when the game ends
    enemies = []
    wave_length = 5

    player = Player(300, 650)

    player_vel = 5  # speed that the player's ship is moving
    enemy_vel = 1  # speed that the enemy ship is moving
    laser_vel = 4

    clock = pygame.time.Clock()
    lost = False
    lost_count = 0

    def redraw_window():
        # Draw the background image, so the whole screen is filled
        WIN.blit(BG, (0, 0))
        lives_label = main_font.render(f"Lives:{lives}", 1, (255, 0, 0))
        level_label = main_font.render(f"Level:{level}", 1, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        player.draw(WIN)

        for enemy in enemies:
            enemy.draw(WIN)

        if lost:
            lost_label = lost_fond.render("You lost!!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                              random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:  # move left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  # move right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:  # move up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() < HEIGHT:  # move down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

        redraw_window()


main()
