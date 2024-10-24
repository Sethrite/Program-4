# Program 4 - Mark Masenda

import os
import sys
import math
import random

import pygame

from Scripts.entities import PhysicsEntity, Player, Enemy
from Scripts.utils import load_image, load_images, Animation
from Scripts.tilemap import Tilemap
from Scripts.clouds import Clouds
from Scripts.particle import Particle
from Scripts.spark import Spark

# Creates the setup for the game

class Game:
    def __init__(self):
        
        pygame.init()

        # Pygame GUI settings

        pygame.display.set_caption("Ninja Game")
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        # All the assets we will be using and the references to their paths

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'file': load_image('file.png'),
            'clouds': load_images('clouds'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=8),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=8),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump'), img_dur=5),
            'player/slide': Animation(load_images('entities/player/slide'), img_dur=5),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide'), img_dur=5),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur = 20, loop = False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur = 6, loop = False),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
        }

        # All the sound effects and the references to their paths

        self.sfx = {
            'jump': pygame.mixer.Sound('Ninja Game/data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('Ninja Game/data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('Ninja Game/data/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('Ninja Game/data/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('Ninja Game/data/sfx/ambience.wav'),
        }
        
        # Sets the volume of the sounds

        self.sfx['ambience'].set_volume(0.2)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.7)
        self.sfx['dash'].set_volume(0.1)
        self.sfx['jump'].set_volume(0.6)

        # Instantiates the clouds, player, and tilemap (level)

        self.clouds = Clouds(self.assets['clouds'], count = 16)

        self.collision_area = pygame.Rect(50, 50, 300, 50)

        self.player = Player(self, (50, 50), (8, 15))

        self.tilemap = Tilemap(self, tile_size = 16)

        # This will begin the game at the level number in front of the .json file in the data and maps folders 

        self.level = 0
        self.load_level(self.level)
        
        self.screenshake = 0

    # Will reference the path of the maps and the leaf spawners
    # The leaf spawners will use the extract class to generate areas where the trees are to spawn particles (reference tilemap.py)

    def load_level(self, map_id):
        self.tilemap.load('Ninja Game/data/maps/' + str(map_id) + '.json')
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep = True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))


    # Both the players and enemies are on off grid tiles so the extract class is needed to get their information and spawn the player and the number of enemies

        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))
        
        self.projectiles = []
        self.particles = []
        self.sparks = []

        self.scroll = [0, 0]
        self.dead = 0
        self.transition = -30

    # Will run the code for the game to start

    def run(self):
        pygame.mixer.music.load('Ninja Game/data/music.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.sfx['ambience'].play(-1)

        # The game loop: Contains all the update functions for all the objects to constantly
        # provide updates to the current position of things based on 60 fps

        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.blit(self.assets['background'], (0, 0))

            self.screenshake = max(0, self.screenshake - 1)

            # Checks if all the enemies are killed, if they are then it will start the transition
            # and start the next level

            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    self.level = min(self.level + 1, len(os.listdir('Ninja Game/data/maps')) - 1)
                    self.load_level(self.level)
            if self.transition < 0:
                self.transition += 1

            # Checks if the player is dead,
            # if they are start the transition and restart the level

            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.dead > 40:
                    self.load_level(self.level)

            # These are the parameters for the camera to follow the player based on their position in the level
            # Then they are used to calculate how the camera should move around the level to follow the player

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # Will spawn many random leaf particles at the location for the leaf spawners, the top's of the trees

            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity = [-0.1, 0.3], frame = random.randint(0, 20)))

            # Constantly updates the clouds and shows them if they are in the camera

            self.clouds.update()
            self.clouds.render(self.display_2, offset = render_scroll)

            # Shows the parts of the map that are in the camera

            self.tilemap.render(self.display, offset = render_scroll)

            # Checks if the enemy is killed by the player, if so
            # removes the enemy from the screen

            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset = render_scroll)
                if kill:
                    self.enemies.remove(enemy)

            # If the player is alive it will continually update the position of the player
            # and continuatlly show the updated positions of the player, based on keyboard input

            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset = render_scroll)

            # Creates the particles for the shooting effect, bullets, and death effects

            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        self.sfx['hit'].play()
                        self.screenshake =  max(16, self.screenshake)
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity = [math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame = random.randint(0, 7)))

            # This will despawn the particles once they have hit their time limit or touched a physical block

            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset = render_scroll)
                if kill:
                    self.sparks.remove(spark)

            # This is used for the after effects on the characters and items to create an outline
            # Using maskes and sillhoutes we can copy the outlines and make them larger and change the color
            # Creating a stylized and cartoony outline around the objects

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                self.display_2.blit(display_sillhouette, offset)

            # This just despawns the particles for the leaves and makes them move like they are blowing in the wind
            # Creates a more natural look, that's why we use sin for the wave like properties

            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset = render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)

            # Receives the inputs of the game and changes the actions of the player 

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    elif event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    elif event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    elif event.key == pygame.K_SPACE:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    elif event.key == pygame.K_w:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_x:
                        self.player.dash()
                    elif event.key == pygame.K_LSHIFT:
                        self.player.dash()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    elif event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    elif event.key == pygame.K_d:
                        self.movement[1] = False

            # Creates a transition by making the color white invinsible through colorkey and placing black around it in a expanding circle
            # So the level reveals itself as the black strinks and increases

            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))

            # Display 2 is everything that the objects are on, while display is the background

            self.display_2.blit(self.display, (0, 0))

            # Uses 60 fps to constantly update the screen and uses the offsets to place the objects in the right place

            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake/ 2)
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), (screenshake_offset))
            pygame.display.update()
            self.clock.tick(60)

Game().run()