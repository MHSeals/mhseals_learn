import pygame
import numpy as np
from time import time
from typing import Union, Optional, Callable, Tuple
from utils import numeric
from gui import Drawable

class Boat(Drawable):
    def __init__(
        self,
        length: int,
        width: int,
        x: "numeric"=0,
        y: "numeric"=0,
        orientation: "numeric"=0,
        linear_velocity: "numeric"=0,
        angular_velocity: "numeric"=0,
        linear_acceleration: "numeric"=0,
        angular_acceleration: "numeric"=0,
        color: Union[str, pygame.Color]="#000000"
    ):
        # Properties
        self.length = length
        self.width = width
        self.x = x
        self.y = y
        self.orientation = orientation
        # Kinematics
        self.linear_velocity = linear_velocity
        self.angular_velocity = angular_velocity
        self.linear_acceleration = linear_acceleration
        self.angular_acceleration = angular_acceleration
        self.color = color
        self.time = time()
        self.dt = 0
        # Time step clamp for stability
        self.max_dt: float = 0.05  # seconds
        # Simple hydrodynamic damping (tunable)
        self.drag_linear: float = 0.5        # 1/s
        self.drag_quadratic: float = 0.02    # 1/(s·px)
        self.ang_damp_linear: float = 1.0    # 1/s
        self.ang_damp_quadratic: float = 0.05 # 1/s
        # Optional hard cap on surge speed (px/s); None disables
        self.max_linear_speed: Optional[float] = None
        # Environment: water current (world frame)
        # Either a constant vector or a function (x, y, t) -> (cx, cy)
        self._water_current_vec: Tuple[float, float] = (0.0, 0.0)
        self._water_current_fn: Optional[Callable[[float, float, float], Tuple[float, float]]] = None
        
    # New acceleration-based control
    def set_linear_acceleration(self, acceleration):
        self.linear_acceleration = acceleration

    def set_angular_acceleration(self, acceleration):
        self.angular_acceleration = acceleration

    # Backwards-compatible velocity setters (still allowed for setting initial values)
    def set_linear_velocity(self, velocity):
        self.linear_velocity = velocity

    def set_angular_velocity(self, velocity):
        self.angular_velocity = velocity
    
    # Tuning helpers
    def set_drag(self, linear: Optional[float] = None, quadratic: Optional[float] = None):
        if linear is not None:
            self.drag_linear = float(linear)
        if quadratic is not None:
            self.drag_quadratic = float(quadratic)

    def set_angular_damping(self, linear: Optional[float] = None, quadratic: Optional[float] = None):
        if linear is not None:
            self.ang_damp_linear = float(linear)
        if quadratic is not None:
            self.ang_damp_quadratic = float(quadratic)

    def set_max_linear_speed(self, vmax: Optional[float]):
        self.max_linear_speed = None if vmax is None else float(vmax)

    def set_max_dt(self, max_dt: float):
        self.max_dt = float(max_dt)
    
    # Water current configuration
    def set_water_current_vector(self, cx: float, cy: float):
        """Set a constant water current vector in world frame (px/s)."""
        self._water_current_vec = (float(cx), float(cy))
        self._water_current_fn = None

    def set_water_current_field(self, fn: Callable[[float, float, float], Tuple[float, float]]):
        """Set a function to compute water current at (x, y, t) in world frame.
        Signature: fn(x, y, t_seconds) -> (cx, cy) in px/s
        """
        self._water_current_fn = fn

    def get_water_current(self) -> Tuple[float, float]:
        if self._water_current_fn is not None:
            try:
                return self._water_current_fn(self.x, self.y, self.time)
            except Exception:
                # Fallback to zero current if fn fails
                return (0.0, 0.0)
        return self._water_current_vec
        
    def update_delta_time(self):
        current_time = time()
        self.dt = current_time - self.time
        if self.dt > self.max_dt:
            self.dt = self.max_dt
        self.time = current_time        

    def move(self):
        """Integrate acceleration -> velocity -> position/orientation."""
        self.update_delta_time()
        # Precompute orientation and current
        ctheta = np.cos(self.orientation)
        stheta = np.sin(self.orientation)
        cx, cy = self.get_water_current()
        # Relative surge speed along hull forward (speed through water along x-body)
        v_rel_along = self.linear_velocity - (cx * ctheta + cy * stheta)

        # Linear/quadratic drag along surge direction (acts opposite v_rel_along)
        a_drag = - self.drag_linear * v_rel_along - self.drag_quadratic * abs(v_rel_along) * v_rel_along

        # Integrate velocities with damping (semi-implicit Euler)
        self.linear_velocity += (self.linear_acceleration + a_drag) * self.dt
        # Optional surge speed cap
        if self.max_linear_speed is not None:
            if self.linear_velocity > self.max_linear_speed:
                self.linear_velocity = self.max_linear_speed
            elif self.linear_velocity < -self.max_linear_speed:
                self.linear_velocity = -self.max_linear_speed

        a_ang_drag = - self.ang_damp_linear * self.angular_velocity - self.ang_damp_quadratic * abs(self.angular_velocity) * self.angular_velocity
        self.angular_velocity += (self.angular_acceleration + a_ang_drag) * self.dt

        # Integrate pose from velocities plus water current (world frame)
        vx_world = ctheta * self.linear_velocity + cx
        vy_world = stheta * self.linear_velocity + cy
        self.x += vx_world * self.dt
        self.y += vy_world * self.dt
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
                            self.x + np.cos(angles[i]) * diagonal / 2,
                            self.y + np.sin(angles[i]) * diagonal / 2
                         ), screen))

        points.append(self.translate_draw_point((self.x + np.cos(self.orientation) * self.length * 0.8, 
                                            self.y + np.sin(self.orientation) * self.length * 0.8
                     ), screen))

        pygame.draw.polygon(screen, pygame.Color(self.color), points)