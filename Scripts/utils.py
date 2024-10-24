# Program 4 - Mark Masenda

import os

import pygame

# Constant for the relative image path

BASE_IMG_PATH = 'Ninja Game/data/images/'

# Uses pygame commands to load the image and the actual path
# Sets the color to black because all the images have black suroundings
# So the black areas turn invinsible and it is only the image left 

def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

# Uses os to get the path of all the images that are needed because they will all have different paths
# Iterates through the multiple images in the directory, these are used for the paths to the images

def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images

# Creates the class to manage the animations of the entities

class Animation:
    def __init__(self, images, img_dur = 5, loop = True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0

    # Used so we can create an instance every time we want an animation
    # This helps preserve memory because when we reference the Animation class all the recursive versions are still referencing the same images
    # Since the copy function uses the instance variables of the Animation class.

    # Which means they are not calling the Animation class multiple times for the same animation to occur; Which takes memory

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    
    # Creates a loop using modulation of the duration
    # This means that when the frames reach the same amount of time as the duration and image length then it will restart at 0
    # So the frame will keep restarting at 0 at the end of the line of images until a different action is given
    
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    # Returns the current frame of the animation
    
    def img(self):
        return self.images[int(self.frame / self.img_duration)]