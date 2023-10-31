import pygame
import os
import time
import random

pygame.font.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invader")
# load image assets

# enemy ship
RED_ENEMY_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_ENEMY_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_ENEMY_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# player ship
PLAYER_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# lasers

RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# background and scale to Window dimension
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "space2.jpg")), (WIDTH, HEIGHT))


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


# check if the mask objects overlaps
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y))


class Ship:
    COOLDOWN = 10

    def __init__(self, x, y, ship_img, laser_img, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = health
        self.ship_img = ship_img
        self.laser_img = laser_img
        self.lasers = []
        self.cool_down_counter = 0
        self.mask = pygame.mask.from_surface(self.ship_img)

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(WIN)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    enemy_kills = 0

    def __int__(self, x, y, ship_img, laser_img, health=100):
        super().__init__(x, y, ship_img, laser_img, health)

    # removing enemies
    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                if laser in self.lasers:
                    self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        self.enemy_kills += 1
                        if obj in objs:
                            objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10,
                                               self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10,
                                               self.ship_img.get_width() * (self.health / self.max_health), 10))

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)


class Enemy(Ship):

    def __int__(self, x, y, ship_img, laser_img, health=100):
        super().__init__(x, y, ship_img, laser_img, health)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 10, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def main(main_menu_score):
    run = True
    FPS = 60
    clock = pygame.time.Clock()

    main_font = pygame.font.Font(os.path.join("assets", "INVASION2000.TTF"), 50)
    lost_font = pygame.font.Font(os.path.join("assets", "INVASION2000.TTF"), 80)

    level = 0
    lives = 5

    player_vel = 10
    player = Player(300, 630, PLAYER_SHIP, YELLOW_LASER)

    enemies = []
    enemy_vel = 0.25
    laser_vel = 6
    wave_length = 3
    lost = False
    lost_count = 0

    previous_level_score = main_menu_score[:]
    highest_score_render = 0

    # draws all objects
    def redraw_window(render):
        # draw background
        WIN.blit(BG, (0, 0))
        # draw text
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        enemy_kills = main_font.render(f"Kills: {player.enemy_kills}", 1, (255, 255, 255))
        prev_level = main_font.render(f"Highest Level: {previous_level_score[0]}", 1, (0, 0, 255))
        prev_enemy_kills = main_font.render(f"Highest Kill: {previous_level_score[1]}", 1, (0, 0, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(enemy_kills, (WIDTH - enemy_kills.get_width() - 10, 50))

        if render <= FPS * 5:
            WIN.blit(prev_level, (WIDTH - prev_level.get_width() - 10, 110))
            WIN.blit(prev_enemy_kills, (WIDTH - prev_enemy_kills.get_width() - 10, 150))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render(f"You lost!!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window(highest_score_render)
        highest_score_render += 1

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                return [level, player.enemy_kills]
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 4
            if enemy_vel <= 2.5:
                enemy_vel += 0.5
            for i in range(wave_length):
                COLOUR_MAP = {
                    "red": (RED_ENEMY_SHIP, RED_LASER),
                    "green": (GREEN_ENEMY_SHIP, GREEN_LASER),
                    "blue": (BLUE_ENEMY_SHIP, BLUE_LASER)
                }
                enemy = Enemy(random.randrange(50, WIDTH - 100),
                              random.randrange(-1500, -100),
                              COLOUR_MAP[random.choice(["red", "blue", "green"])][0],
                              COLOUR_MAP[random.choice(["red", "blue", "green"])][1])
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        # creates a copy of enemy array
        for enemy in enemies[:]:

            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 4 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)


main_menu_scores = [0,0]

def main_menu(main_menu_scores):
    title_font = pygame.font.Font(os.path.join("assets", "INVASION2000.TTF"), 40)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render(f"Press the mouse to begin...", 1,
                                        (255, 255, 255))
        highest_score = title_font.render(
            f"HIGHEST SCORE: LVL {main_menu_scores[0]}",
            1,
            (255, 255, 255))
        highest_kills = title_font.render(
            f"HIGHEST KILLS: {main_menu_scores[1]}",
            1,
            (255, 255, 255))
        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))
        WIN.blit(highest_score, (WIDTH / 2 - title_label.get_width() / 2, 400))
        WIN.blit(highest_kills, (WIDTH / 2 - title_label.get_width() / 2, 450))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                current_level = main(main_menu_scores)

                if current_level[0] >= main_menu_scores[0]:
                    main_menu_scores[0] = current_level[0]

                if current_level[1] >= main_menu_scores[1]:
                    main_menu_scores[1] = current_level[1]

    pygame.quit()


main_menu(main_menu_scores)
