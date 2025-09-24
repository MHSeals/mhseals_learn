import numpy as np
import pygame
from boat import Boat
from time import time

pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

def draw_boat():
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
                        boat.y + np.sin(angles[i]) * diagonal / 2
                    )))

    print(points)

    pygame.draw.polygon(screen, "black", points)

def move(dt):
    boat.x += np.cos(boat.orientation) * boat.linear_velocity * dt
    boat.y += np.sin(boat.orientation) * boat.linear_velocity * dt
    
def turn(dt):
    boat.orientation += boat.angular_velocity * dt

def translate_draw_point(point):
    return (point[0], SCREEN_HEIGHT - point[1])

boat = Boat(100, 50)
start_time = time()
prev_t = start_time

while True:
    t = time() - start_time
    dt = t - prev_t
    prev_t = t
    move(dt)
    turn(dt)

    screen.fill("white")

    draw_boat()

    pygame.display.update()