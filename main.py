#importing module

import pygame    #pygame module (external module)
import os        #inbuilt module
import random     #inbuilt module


pygame.font.init()  #intializing pygame

WIDTH, HEIGHT = 750,750  #declaring variable for the dimension of the pygame window
WIN = pygame.display.set_mode((WIDTH, HEIGHT))     #setting dimenssion in the form of tuple(to display a window of the desired size)
pygame.display.set_caption("Ship Firing Bullet")   #name of the pygame window

# Load images
#enemy ships
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png")) #red ship image
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png")) #green ship image
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png")) #blue ship image

# Player player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png")) #player's own ship color yellow

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png")) #bullet of red ship
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png")) #bullet of green ship
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png")) #bullet of blue ship
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png")) #bullet of yellow ship

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))
#we do this to fit the background image to the size of pygame window


class Laser:  #(class define for bullets )
    def __init__(self, x, y, img):  #standard reserved function to initialize the class
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)   #self.mask is used for opaque pixels

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))   #drawing the surface to display the surface

    def move(self, vel):       #velocity function to move the ships
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:

    COOLDOWN = 30

    def __init__(self, x, y, health=100):
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

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):  #this class is define for the player's ship
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
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
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):   #we are defining this class of ship for enemy
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }
    #defining the dict of color taking key as color of ships and value as space ship and laser

    def __init__(self, x, y, color, health=100):  #health defines the condition of enemy of ship
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):  #defining the function collide
    offset_x = obj2.x - obj1.x  #collision at x axis
    offset_y = obj2.y - obj1.y #collision at y axis
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None  #when object gets collide display none i.e display the background

def main():  #defining the main function for pygame
    run = True
    FPS = 60    #FRAMES PER SECOND
    level = 0  #start of the game we are at zero level and we have 4 lives
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)  #font of game while playing
    lost_font = pygame.font.SysFont("comicsans", 60)   #font of the game when you lost the game

    enemies = [] #creating empty list for enemies
    wave_length = 5
    enemy_vel = 1 #velocity of enemy ship

    player_vel = 5 #velocity of player ship
    laser_vel = 5 #velocity of laser

    player = Player(300, 630) #position of player ship

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0  #if lives came to zero

    def redraw_window():
        WIN.blit(BG, (0,0))         #blit function says take the background surface and draw it onto
                                         #the screen and position it at (x,y)
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))   #RGB  FOR LIVES
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))    #RGB FOR LEVELS

        WIN.blit(lives_label, (10, 10))              #position of the lives label (top left)
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))   #position of the level label (top ri8)

        for enemy in enemies:  #for loop enemies in enemie
            enemy.draw(WIN)


        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255)) # when u lost all the four lives you get the title you lost in white
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350)) #position of displaying you lost the live

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:  #for every health =0 you will lost one live
            lost = True #if u loss lives add one lives each time to the count
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:    #if lost count gets freater than frames per sec stop the game and return back again n to the while loop
                run = False
            else:
                continue

        if len(enemies) == 0:            #block statement for enimies ships
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                #we choose wide range so that we will have different enimies ship at different levels

                enemies.append(enemy)  #add enemies to the empty enemy list we have created earlier

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  #to close the game through X window
                quit()

        keys = pygame.key.get_pressed()   #pygame syntex for the functioing of key

        #keys to be pressed for the movement of the ships
        if keys[pygame.K_a] and player.x - player_vel > 0: # left move
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right move
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up move
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() < HEIGHT: # down move
            player.y += player_vel
        if keys[pygame.K_SPACE]:   #to shoot the bullet
            player.shoot()

        for enemy in enemies[:]:  #for range of enemy
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1: #random range output
                enemy.shoot()

            if collide(enemy, player):  #if the players ship collide with the enemy ship -10 from the health
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT: #if enemy ships goes off from the screen then u loss one live
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

def main_menu():  #defining the function to start the game
    title_font = pygame.font.SysFont("comicsans", 70)        #defining the font of the title at the starting of the game
    run = True  #boolean
    while run:   #using while loop
        WIN.blit(BG, (0,0)) #win.bilt() is used to draw over the surface
        title_label = title_font.render("Press the mouse to begin...", 1 , (255,255,255))
        #if the condition of the loops is true it will ask the user to press the mouse (rgb is used to print that command in the white line)
        WIN.blit(title_label, (750/2 - title_label.get_width()/2, 350))  #(position of the press the mouse statement)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  #if condition to quit the game in run==false
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:  #restarting the game again by pressing mouse button if if condistion is true
                main()
    pygame.quit()

main_menu()