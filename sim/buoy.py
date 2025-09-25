import pygame
from typing import Literal, Union
from utils import numeric
from enums import BuoyColors
from abc import ABC, abstractmethod
from gui import Drawable

BUOY_RADIUS = 12

class Buoy(ABC):
    def __init__(self, x: "numeric", y: "numeric", color: BuoyColors):
        self.x = x
        self.y = y
        self.color = color

    @abstractmethod
    def draw(self, screen: pygame.Surface):
        pass

class PoleBuoy(Buoy):
    def __init__(self, x: "numeric", y: "numeric", color: Literal[BuoyColors.RED, BuoyColors.GREEN]):
        super().__init__(x, y, color)
        
    def draw(self, screen: pygame.Surface):
        center = self.translate_draw_point((self.x, self.y), screen)
        pygame.draw.circle(screen, pygame.Color(self.color.value), center, BUOY_RADIUS)
        pygame.draw.circle(screen, self.darken_color(pygame.Color(self.color.value), 0.7), center, BUOY_RADIUS * 0.8)
        pygame.draw.circle(screen, pygame.Color(self.color), center, BUOY_RADIUS * 0.5)

class BallBuoy(Buoy):
    def __init__(self, x: "numeric", y: "numeric", color: BuoyColors):
        super().__init__(x, y, color)

    def draw(self, screen: pygame.Surface):
        center = (self.x, self.y)
        pygame.draw.circle(screen, pygame.Color(self.color.value), center, BUOY_RADIUS)
        pygame.draw.circle(screen, self.darken_color(pygame.Color(self.color.value), 0.25), center, BUOY_RADIUS * 0.5)