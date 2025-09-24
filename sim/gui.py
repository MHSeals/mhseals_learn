import numpy as np
import pygame
from boat import Boat
from time import time

def draw_boat(boat: Boat, screen):
    a1 = np.arctan2(boat.width, boat.length) * 2
    a2 = np.pi - a1
    angles = [boat.orientation + a1 / 2]
    angles.append(angles[0] + a2)
    angles.append(angles[1] + a1)
    angles.append(angles[2] + a2)
    diagonal = (boat.length ** 2 + boat.width ** 2) ** (1 / 2)

    points = []
    for i in range(4):
        points.append(translate_draw_point((
                        boat.x + np.cos(angles[i]) * diagonal / 2,
                        boat.y + np.sin(angles[i]) * diagonal / 2,
                    )))

    pygame.draw.polygon(screen, "black", points)

def translate_draw_point(point):
    return (point[0] + screen_width / 2, screen_height / 2 - point[1])

class GUI:
    def __init__(self, boat: Boat, height: int, width: int):
        global screen_height
        global screen_width
        screen_height = height
        screen_width = width

        pygame.init()
        self.boat = boat
        self.screen = pygame.display.set_mode((screen_width, screen_height))

    def run(self):
        self.screen.fill("white")
        draw_boat(self.boat, self.screen)
        pygame.display.update()