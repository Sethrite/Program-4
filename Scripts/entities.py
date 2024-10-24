# Program 4 - Mark Masenda

import math
import random

import pygame

from Scripts.particle import Particle
from Scripts.spark import Spark

# Creates the Physics properties of the all the entities in the game

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')

        self.last_movement = [0, 0]

    # Creates the hitboxs for the entities

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    # Sets the current action for the entity

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    # Updates the entity based on the previous action and what the current action is

    def update(self, tilemap, movement = (0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        # Controls the movement, using the current position (movement[0]) and the velocity (self.velocity[0])
        # Inside these variables the [0] is for x and the [1] is for y

        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        # Checks if the entities hitboxes are colliding with anything else (left and rigtht)

        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x

        # Checks if the entities hitboxes are colliding with anything else(top and bottom)

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        # Checks for the orientation of the entity and whether the enemy should be facing left or right

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.last_movement = movement

        # Sets the maximum velocity in the y-direction to be 5

        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        # Will reset the velocity if the player is touching the ground or hits the roof

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        self.animation.update()

    # Renders the animations of the entities

    def render(self, surf, offset = (0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))

# Class for the enemy entities (specifically) 

class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)

        self.walking = 0
    
    # Updates the actions and checks if the enemy is on top of a block. 
    # Also checks if the player is near the enemy or dashing into the enemy

    def update(self, tilemap, movement = (0,0)):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)

            # Checks if the player is near the enemy, if the enemy is facing the same way as the player
            # And the distance the player is away from the enemy
            # If the player is within 16 pixels of the enemy then shoot

            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if (abs(dis[1]) < 16):
                    if (self.flip and dis[0] < 0):
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))
                    elif (not self.flip and dis[0] > 0):
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random()))
                        
        # If the player is not near the enemy randomly move around

        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)

        super().update(tilemap, movement = movement)

        # If the enemy moves consider it running
        # If the enemy does not move consider it idle

        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        # If the player hits the enemy while dashing, kill the enemy and create particles in different directions

        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                self.game.screenshake =  max(16, self.game.screenshake)
                self.game.sfx['hit'].play()
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity = [math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame = random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                return True

    # Rendering the enemy onto the surface

    def render(self, surf, offset = (0, 0)):
            super().render(surf, offset = offset)

            if self.flip:
                surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False), (self.rect().centerx - 4 - self.game.assets['gun'].get_width() - offset[0], self.rect().centery - offset[1]))
            else:
                surf.blit(self.game.assets['gun'], (self.rect().centerx + 4 - offset[0], self.rect().centery - offset[1]))
        
# Class for the player entity (specifically)

class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 2
        self.wall_slide = False
        self.dashing = 0

    # Checks for the player status to update it

    def update(self, tilemap, movement = (0, 0)):
        super().update(tilemap, movement = movement)

        self.air_time += 1

        # Checks if the player is meeting the requirements of death: in the air for more than 150 seconds (falling off the island)

        if self.air_time > 150:
            if self.wall_slide:
                self.air_time = 5
            if self.air_time > 150:
                if not self.game.dead:
                    self.game.sfx['hit'].play()
                    self.game.screenshake =  max(16, self.game.screenshake)
                self.game.dead += 1

        # Checks if the player is on the ground to reset the jumps

        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 2

        
        # Checks if the player is touching a wall, in the air, and not already wall sliding
        # Sets the maximum velocity to 0.5 for a wall slide, makes the player slower while on the wall

        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')

        # If the player is not wall sliding then if they are in the air then consider it a jump
        # If the player is moving then consider it them running
        # If the player is not moving then consider them idle

        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')

        # Sets the parameters for how long a dash is and spawns the particles for the dash

        if abs(self.dashing) in {60, 50}:
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity = pvelocity, frame = random.randint(0, 7)))

        # Creates the bounds for dashing, and causes the dash to constantly decrease
        # So like a timer which can be used to determine how long the dash should be and the cooldown for the dash

        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)

        # Controls how long the dashing effect occurs for and creates the particles for the dash

        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
            pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity = pvelocity, frame = random.randint(0, 7)))

        #       ^       ^       ^       ^
        #       |       |       |       |
        # Since the players dashing effect starts at 60 and goes down constantly, there is a 10 second window of dashing
        # When the window reaches the 9th second [ abs(self.dashing) == 51 ] then it decreases the velocity so they slow down and fall
        # Then since the code before would decrease the dash from 50 till 0, there is a 50 second cooldown between dashes

        # Creates the bounds for how fast the player can go, in the x direction for both moving left and right

        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)
        
    # Renders the player onto the surface

    def render(self, surf, offset = (0, 0)):
        if abs(self.dashing) <= 50:
            super().render(surf, offset = offset)

    # Determines what is considered a jump and adds specification for jumping off of a wall
    # Since you have to be in the wall sliding to wall jump

    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5  # Move the player 3.5 out in the y direction
                self.velocity[1] = -2.5 # Move the player -2.5 out in the x direction
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            
        elif self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5
            return True
    
    # Determines what is considered a dash
    # Will set the players dash to 60 
    # And from the code before will constantly decrease until it gets to 0
        
    def dash(self):
        if not self.dashing:
            self.game.sfx['dash'].play()
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60
