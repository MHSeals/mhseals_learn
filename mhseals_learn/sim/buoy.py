import pygame
from typing import Literal
from abc import ABC, abstractmethod
from mhseals_learn.sim.utils import numeric
from mhseals_learn.sim.enums import BuoyColors
from mhseals_learn.sim.gui import Drawable
from mhseals_learn.sim.constants import Constants as C

C.to_px()

class Buoy(Drawable, ABC):
    def __init__(self, x: numeric, y: numeric, color: BuoyColors):
        self.x = x
        self.y = y
        self.color = color

    @abstractmethod
    def draw(self, screen: pygame.Surface):
        pass

class PoleBuoy(Buoy):
    def __init__(self, x: numeric, y: numeric, color: Literal[BuoyColors.RED, BuoyColors.GREEN]):
        super().__init__(x, y, color)
        
    def draw(self, screen: pygame.Surface):
        radius = C.Buoy.RADIUS
        center = self.translate_draw_point((self.x, self.y), screen)
        pygame.draw.circle(screen, pygame.Color(self.color.value), center, radius)
        pygame.draw.circle(screen, self.darken_color(pygame.Color(self.color.value), 0.7), center, radius * 0.8)
        pygame.draw.circle(screen, pygame.Color(self.color.value), center, radius * 0.5)

class BallBuoy(Buoy):
    def __init__(self, x: "numeric", y: "numeric", color: BuoyColors):
        super().__init__(x, y, color)

    def draw(self, screen: pygame.Surface):
        radius = C.Buoy.RADIUS
        center = self.translate_draw_point((self.x, self.y), screen)
        pygame.draw.circle(screen, pygame.Color(self.color.value), center, radius)
        pygame.draw.circle(screen, self.darken_color(pygame.Color(self.color.value), 0.25), center, radius * 0.5)