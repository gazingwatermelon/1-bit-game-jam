import pygame
from utils import load_image, load_images, Animation

def fill_map(depth, type, map):
    for i in range(0, 352, 16):
        solid = pygame.Rect((i, depth), (16, 16))
        map.append([solid, type])
    
    return map
