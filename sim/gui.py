import pygame
import numpy as np
from time import time
from typing import Tuple, List, Union
from utils import numeric
from abc import ABC, abstractmethod

class Drawable(ABC):
    @abstractmethod
    def draw(self, screen: pygame.Surface):
        pass

    def translate_draw_point(self, point: Tuple[numeric, numeric], screen) -> Tuple[numeric, numeric]:
        width, height = screen.get_size()
        return (point[0] + width / 2, height / 2 - point[1])

    def darken_color(self, color: pygame.Color, factor: float) -> pygame.Color:
        r = int(color.r * factor)
        g = int(color.g * factor)
        b = int(color.b * factor)
        return pygame.Color(r, g, b, color.a)

class GUI:
    def __init__(self, screen_width: int, screen_height: int):
        pygame.init()
        self.width = screen_width
        self.height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))

    def clear(self, color: Union[str, pygame.Color]="white"):
        self.screen.fill(color)

    def update(self):
        pygame.display.update()
        
    def get_events(self) -> List[pygame.event.Event]:
        return pygame.event.get()
        
    def quit(self):
        pygame.quit()