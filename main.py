import pygame
import os
import time
import random

pygame.init()

# Maximum height and width of the game surface
WIDTH, HEIGHT = (750, 750)

# To create the display surface
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

# Set the surface caption
pygame.display.set_caption("MyGame")

# Background image
BG = pygame.image.load(os.path.join("assets", "background-black.png"))
# Scaling the background image to max width and height as game surface
BG = pygame.transform.scale(BG, (WIDTH, HEIGHT))

# Enemy Load image
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player ship image
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))


# Generalized class
class Ship:

    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        # keep track of the lasers shoot
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

    # used to initiate time to control of the next laser shooting time
    def cooldown(self):
        # if cool_down_counter exceed the COOL DOWN =30 --> allow to create laser
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        # increment of the cool_down_counter
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    # used to initiate time for new laser
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_height(self):
        return self.ship_img.get_width()

    def get_width(self):
        return self.ship_img.get_height()


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    # moves the laser to the certain velocity ratio
    def move(self, vel):
        self.y += vel

    # check if the laser is off the screen
    # for player it checks laser y position > 0
    # for enemy it checks laser y position < HEIGHT
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


'''
    Player():
        draw() --> ship.draw()
        Move_laser() --> ship.cool_down()
        health_bar()
        Ship ---- > ship.shoot()
'''


# Player class
class Player(Ship):
    # Takes the x and y position to located the player character
    def __init__(self, x, y, health=100):
        super().__init__(x, y)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        # masking take only the weighted pixel and ignore the other pixel
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    # Shoot the laser when the user press the space bar
    def move_lasers(self, vel, objs):
        self.cooldown()
        # Loop over the laser shoot by the player
        for laser in self.lasers:
            # Change the x and y pos of the laser
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                # If the laser is out off the screen -- destroy the laser object
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    # Render the player object to the game surface ---> responsible for the movement of the character
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0),(self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health),10))


'''
    Enemy();
        move()
        shoot() ---> Laser()
        move_laser()
        Ship() ---> draw() 
'''


class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER)
    }

    def __init__(self, x, y, color, health=100):
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


def main():
    # Flag to track the game  status
    run = True

    # frame to be rendered per second
    FPS = 60

    # pygame clock initialisation
    clock = pygame.time.Clock()

    # Initial level of the game
    level = 0

    # Total lives of the player
    lives = 5

    # Font surface to render the level and lives
    main_font = pygame.font.SysFont('comicsans', 50)

    # Font surface to render the lost message
    lost_font = pygame.font.SysFont('comicsans', 60)

    # Player declaration
    player = Player(375, 600)

    # Player movement velocity
    player_vel = 5

    # laser movement velocity
    laser_vel = 5

    # Track of total enemy created
    enemies = []

    # Update number of enemy after a level
    wave_length = 0

    # Enemy spaceship velocity
    enemy_vel = 1

    # Flag to Tracking the game status of the player on basis of the health
    lost = False

    # Counting the lost
    lost_count = 0

    # Function to render the game objects onto the game surface
    def render_window():

        # Creating the font surface to render onto the game surface
        # For Lives rendering
        lives_label = main_font.render(f"Lives : {lives}", 1, (255, 255, 255))

        # For Level rendering
        level_label = main_font.render(f"Level : {level}", 1, (255, 255, 255))

        # blit the background image to the game surface
        WIN.blit(BG, (0, 0))
        # blit the lives status to the game screen/surface
        WIN.blit(lives_label, (10, 10))
        # blit the level status to the game screen/surface
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        # Rendering the player  character to the surface
        player.draw(WIN)

        # TO render the enemy onto the game surface
        # This will draw the enemy if exist in the enemies list
        for enemy in enemies:
            # Calling the Enemy.draw function of the Enemy class
            enemy.draw(WIN)

        # If the lost flag is toggled ---> player lost
        if lost:
            # Creating the lost font surface to be rendered on the screen after the lost of the game
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            # Render the lost font surface to the game surface
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        # used to update the whole screen per frame
        pygame.display.update()

    def player_activity():
        # Used to get the activity of the user/player
        keys = pygame.key.get_pressed()

        #  <-- left movement
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel

        # --> right
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel

        # ^^^^^ up movement
        if keys[pygame.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel

        # Down movement
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 10 < HEIGHT:
            player.y += player_vel

        # Used to fire the laser shoots
        if keys[pygame.K_SPACE]:
            player.shoot()

    # Main Game Loop
    while run:
        # sets the number frame to be loaded per second and run this loop 60 time per second
        clock.tick(FPS)

        # used to render all the surfaces onto the screen
        render_window()
        # Check to track the game status as lost or win
        if lives <= 0 or player.health <= 0:
            # Toggle the lost flag
            lost = True
            # increase the lost count
            lost_count += 1

        # if the player lost toggle the game(run) for 3 seconds
        if lost:
            # to display the lost font surface for 3 seconds
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        # Used to get the activity of the user/player
        for event in pygame.event.get():
            # Trigger when the QUIT is pressed
            if event.type == pygame.QUIT:
                # run = False
                quit()
            print(event)

        # To level up when NO enemy left
        if len(enemies) == 0:
            # Level up by 1
            level += 1
            # adding 5 additional enemy
            wave_length += 5

            # Declaration of enemy as per wave_length
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100),
                              random.randrange(-1500, -100),
                              random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        player_activity()
        '''
            Player():
                draw() --> ship.draw()
                Move_laser() --> ship.cool_down()
                health_bar()
                Ship() ---- > ship.shoot()
                
             Enemy():
                move()
                shoot() ---> Laser()
                Ship() ---> move_laser()
                Ship() ---> draw()
        '''
        for enemy in enemies[:]:
            # moving enemy itself
            enemy.move(enemy_vel)
            # moving enemy laser
            enemy.move_lasers(laser_vel, player)

            # setting the probability to shoot a laser
            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            # Check for collision of the enemy and the player
            if collide(enemy, player):
                # if collide decrease the player health by 10
                player.health -= 10
                # Deleting the enemy who collide with the player
                enemies.remove(enemy)
            # destroying the enemy if the enemy passes the MAX_HEIGHT
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        # used to fire the laser and check the collision of the player laser with the enemy object
        player.move_lasers(-laser_vel, enemies)


# check if the objects collide or not
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main_menu():
    # Initialisation of the font surface
    title_font = pygame.font.SysFont("comicsans", 70)

    # Used to show main menu after complietion of the game
    run = True

    while run:
        # Blit the background surface to the screen surface
        WIN.blit(BG, (0, 0))

        # Setting the font to be rendered on the font surface
        title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))

        # blit the font on the game surface
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))

        # used to update the screen surface at every second according to the FPS
        pygame.display.update()

        # loop to handle the start or the close of the game
        for event in pygame.event.get():

            # triggered when the game screen is closed --> close the game
            if event.type == pygame.QUIT:
                run = False

            # Triggered when the mouse is clicked --> Start game
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    # Quit the pygame instance
    pygame.quit()


# Starting the game main menu
main_menu()