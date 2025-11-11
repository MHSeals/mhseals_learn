import pygame
import numpy as np
from time import time
from typing import Union
from mhseals_learn.sim.utils import numeric, generate_rectangle
from mhseals_learn.sim.gui import Drawable
from mhseals_learn.sim.constants import Constants as C

C.to_px()
C.to_rad()

class Boat(Drawable):
    def __init__(
        self,
        length: numeric,
        width: numeric,
        x: numeric=0,
        y: numeric=0,
        orientation: numeric=0,
        linear_velocity: numeric=0,
        angular_velocity: numeric=0,
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
        
    def __str__(self) -> str:
        return f"(length: {self.length}, width: {self.width}, x: {self.x}, y: {self.y}, orientation: {self.orientation}, linear_vel: {self.linear_velocity}, angular_vel: {self.angular_velocity}, color: {self.color})"
        
    def set_linear_velocity(self, velocity):
        velocity = max(-C.Boat.DPS_MAX, min(C.Boat.DPS_MAX, velocity))
        self.linear_velocity = velocity

    def set_angular_velocity(self, velocity):
        velocity = max(-C.Boat.APS_MAX, min(C.Boat.APS_MAX, velocity))
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
        points = generate_rectangle(self.x, self.y, self.orientation, self.length, self.width, self.translate_draw_point, screen)
        points.append(self.translate_draw_point((self.x + np.cos(self.orientation) * self.length * 0.8, 
                                                 self.y + np.sin(self.orientation) * self.length * 0.8
                                              ), screen))
        pygame.draw.polygon(screen, pygame.Color(self.color), points)