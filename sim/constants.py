import numpy as np
from typing import Union
from utils import numeric

class Meters(float):
    pass

class Pixels(float):
    pass

class Degrees(float):
    pass

class Radians(float):
    pass

unit = Union[float, int, Meters, Pixels, Degrees, Radians]

class Constants:
    class Conversions:
        METERS2PX: numeric = 35
        PX2METERS: numeric = 1 / METERS2PX
        DEG2RAD: numeric = np.pi / 180
        RAD2DEG: numeric = 180 / np.pi
    
    class Gate:
        WIDTH_MIN = Meters(2.0)
        WIDTH_MAX = Meters(4.0)
        HEIGHT_MIN = Meters(10.0)
        HEIGHT_MAX = Meters(25.0)
        GAP_MIN = Meters(2.0)
        GAP_MAX = Meters(4.0)
        ANGLE_DEV_MAX = Degrees(30.0)
        ORIENTATION_DEV_MULTIPLIER_MAX: numeric = 1.5
        _BASE = {k: v for k, v in locals().items() if isinstance(v, (Meters, Degrees))}
    
    class Buoy:
        RADIUS = Meters(0.2)
        _BASE = {k: v for k, v in locals().items() if isinstance(v, (Meters, Degrees))}
    
    class Boat:
        LENGTH = Meters(1.0)
        WIDTH = Meters(0.5)
        START_ORIENTATION = Degrees(0.0)
        DPS_MAX = Meters(5.0)
        APS_MAX = Degrees(10.0)
        _BASE = {k: v for k, v in locals().items() if isinstance(v, (Meters, Degrees))}
    
    @classmethod
    def convert_all(cls, factor: float, unit_from: type, unit_to: type):
        for name, inner_cls in cls.__dict__.items():
            if isinstance(inner_cls, type) and hasattr(inner_cls, "_BASE"):
                base_values = inner_cls._BASE
                for attr, value in base_values.items():
                    if isinstance(value, unit_from):
                        setattr(inner_cls, attr, unit_to(float(value) * factor))
    
    @classmethod
    def to_px(cls):
        cls.convert_all(cls.Conversions.METERS2PX, Meters, Pixels)

    @classmethod
    def to_m(cls):
        cls.convert_all(cls.Conversions.PX2METERS, Pixels, Meters)
    
    @classmethod
    def to_rad(cls):
        cls.convert_all(cls.Conversions.DEG2RAD, Degrees, Radians)

    @classmethod
    def to_deg(cls):
        cls.convert_all(cls.Conversions.RAD2DEG, Radians, Degrees)