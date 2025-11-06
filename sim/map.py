from typing import Self
from boat import Boat
from buoy import PoleBuoy
from enums import BuoyColors
from utils import numeric, generate_rectangle
from constants import Constants as C
import numpy as np
import random

C.to_px()
C.to_rad()

class Gate:
    def __init__(self, x: numeric, y: numeric, orientation: numeric, width: numeric, height: numeric):
        self.x = x
        self.y = y
        self.orientation = orientation
        self.width = width
        self.height = height
        self.buoys = []

        points = generate_rectangle(x, y, orientation, height, width)
        colors = [BuoyColors.GREEN, BuoyColors.GREEN, BuoyColors.RED, BuoyColors.RED]
        
        for i in range(4):
            self.buoys.append(PoleBuoy(*points[i], colors[i]))
            
    @classmethod
    def random(cls, boat: Boat) -> Self:
        width = random.uniform(C.Gate.WIDTH_MIN, C.Gate.WIDTH_MAX)
        height = random.uniform(C.Gate.HEIGHT_MIN, C.Gate.HEIGHT_MAX)
        dist = random.uniform(C.Gate.GAP_MIN, C.Gate.GAP_MAX) + height / 2
        angle = random.uniform(-C.Gate.ANGLE_DEV_MAX, C.Gate.ANGLE_DEV_MAX)
        x = boat.x + (dist * np.cos(angle))
        y = boat.y + (dist * np.sin(angle)) 
        orientation = random.uniform(0.0, C.Gate.ORIENTATION_DEV_MULTIPLIER_MAX) * angle
        
        return cls(x, y, orientation, width, height)
        