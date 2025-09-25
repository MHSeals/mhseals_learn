import pygame
import numpy as np
from time import time
from typing import Union
from utils import numeric
from gui import Drawable

class Boat(Drawable):
    def init(
        self,
        length: int,
        width: int,
        x: "numeric"=0,
        y: "numeric"=0,
        orientation: "numeric"=0,
        linear_velocity: "numeric"=0,
        angular_velocity: "numeric"=0,
        color: Union[str, pygame.Color]="#000000"
    ):
        # Properties
        self.length = length
        self.width = width
        self.x = x
        self.y = y
        self.orientation = orientation
        self.linear_velocity = linear_velocity
        self.angular_velocity = angular_velocity
        self.color = color
        self.time = time()
        self.dt = 0
        
    def set_linear_velocity(self, velocity):
        self.linear_velocity = velocity

    def set_angular_velocity(self, velocity):
        self.angular_velocity = velocity
        
    def update_delta_time(self):
        current_time = time()
        self.dt = current_time - self.time
        self.time = current_time        

    def move(self):
        self.update_delta_time()
        self.x += np.cos(self.orientation) * self.linear_velocity * self.dt
        self.y += np.sin(self.orientation) * self.linear_velocity * self.dt
        self.orientation += self.angular_velocity * self.dt

    def draw(self, screen: pygame.Surface):
        diagonal = (self.length ** 2 + self.width ** 2) ** (1 / 2)
        a1 = np.arctan2(self.width, self.length) * 2
        a2 = np.pi - a1
        angles = [self.orientation + a1 / 2]
        angles.append(angles[0] + a2)
        angles.append(angles[1] + a1)
        angles.append(angles[2] + a2)

        points = []
        for i in range(4):
            points.append(self.translate_draw_point((
                            self.x - np.cos(angles[i]) * diagonal / 2,
                            self.y + np.sin(angles[i]) * diagonal
                         ), screen))

        points.append(self.translate_draw_point((self.x + np.cos(self.orientation) * self.length * 0.8, 
                                            self.y + np.sin(self.orientation) * self.length * 0.8
                     ), screen))

        pygame.draw.polygon(screen, pygame.Color(self.color), points)