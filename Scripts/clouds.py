# Program 4 - Mark Masenda

import random

# Creates the clouds in the background of the game 

class Cloud:
    def __init__(self, pos, img, speed, depth) :
        self.pos = list(pos)
        self.img = img
        self.speed = speed
        self.depth = depth

    # Updates the clouds every frame

    def update(self):
        self.pos[0] += self.speed
    
    # Renders the position of the clouds based off of an offset with the camera

    def render(self, surf, offset = (0, 0)):
        render_pos = (self.pos[0] - offset[0] * self.depth, self.pos[1] - offset[1] * self.depth)
        surf.blit(self.img, (render_pos[0] % (surf.get_width() + self.img.get_width()) - self.img.get_width(), render_pos[1] % (surf.get_height() + self.img.get_height()) - self.img.get_height()))

# Uses the cloud object to render multiple clouds and to create the layering and random effect of the clouds; 
# and adjusts how they spawn randomly and move at different intervals of speed

class Clouds:
    def __init__(self, cloud_images, count = 16):
        self.clouds = []

        for i in range(count):
            self.clouds.append(Cloud((random.random() * 99999, random.random() * 99999), random.choice(cloud_images), random.random() * 0.05 + 0.05, random.random() * 0.6 + 0.2))

        self.clouds.sort(key = lambda x: x.depth)

    # Updates the clouds every frame

    def update(self):
        for cloud in self.clouds:
            cloud.update()

    # Renders the clouds to the display

    def render(self, surf, offset = (0,0)):
        for cloud in self.clouds:
            cloud.render(surf, offset = offset)