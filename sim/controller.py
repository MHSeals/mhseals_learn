from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple, List, Optional

from pid import PID
from mission import Mission
from utils import wrap_angle, angle_to_target, clamp, closest_point_on_polyline, advance_along_polyline


@dataclass
class ControlLimits:
    max_linear_accel: float = 50.0     # px/s^2
    max_angular_accel: float = 2.0     # rad/s^2
    max_speed: float = 150.0           # px/s (for speed target limiting)
    max_angular_speed: float = math.pi  # rad/s


class WaypointFollower:
    def __init__(self, mission: Mission,
                 heading_pid: PID,
                 speed_pid: PID,
                 limits: ControlLimits = ControlLimits()):
        self.mission = mission
        self.heading_pid = heading_pid
        self.speed_pid = speed_pid
        self.limits = limits

    def compute_controls(self,
                         x: float, y: float,
                         orientation: float,
                         linear_velocity: float,
                         dt: float) -> Tuple[float, float]:
        """Return (linear_accel, angular_accel)."""
        wp = self.mission.current()
        if wp is None:
            # No mission: brake to stop
            target_speed = 0.0
            heading_error = 0.0
        else:
            # Heading control to waypoint
            desired_heading = angle_to_target(x, y, wp.x, wp.y)
            heading_error = wrap_angle(desired_heading - orientation)

            # Distance-based speed target: slow down near waypoint
            dx, dy = (wp.x - x), (wp.y - y)
            dist = math.hypot(dx, dy)
            # Speed ramps down within ~2x tolerance
            if dist < 2 * wp.tolerance:
                target_speed = self.limits.max_speed * (dist / (2 * wp.tolerance))
            else:
                target_speed = self.limits.max_speed

        # Heading PID -> angular acceleration command
        ang_acc = self.heading_pid.update(heading_error, dt)
        ang_acc = clamp(ang_acc, -self.limits.max_angular_accel, self.limits.max_angular_accel)

        # Speed PID on speed error -> linear acceleration
        speed_error = target_speed - linear_velocity
        lin_acc = self.speed_pid.update(speed_error, dt)
        lin_acc = clamp(lin_acc, -self.limits.max_linear_accel, self.limits.max_linear_accel)

        return lin_acc, ang_acc


class PurePursuitFollower:
    def __init__(self,
                 path_points: List[Tuple[float, float]],
                 lookahead_base: float,
                 speed_pid: PID,
                 limits: ControlLimits = ControlLimits(),
                 lookahead_speed_gain: float = 0.2,
                 k_omega: float = 2.0):
        self.path_points = path_points
        self.lookahead_base = lookahead_base
        self.lookahead_speed_gain = lookahead_speed_gain
        self.k_omega = k_omega
        self.speed_pid = speed_pid
        self.limits = limits

        # For visualization
        self.lookahead_start: Optional[Tuple[float, float]] = None
        self.lookahead_end: Optional[Tuple[float, float]] = None
        self.target_point: Optional[Tuple[float, float]] = None

    def compute_controls(self,
                         x: float, y: float,
                         orientation: float,
                         linear_velocity: float,
                         angular_velocity: float,
                         dt: float) -> Tuple[float, float]:
        # Find closest point on path to current position
        (cx, cy), seg_idx, seg_t = closest_point_on_polyline(x, y, self.path_points)

        # Dynamic lookahead based on speed
        Ld = max(1e-3, self.lookahead_base + self.lookahead_speed_gain * abs(linear_velocity))

        # Advance along path by lookahead distance to get the target point
        (tx, ty), n_idx, n_t = advance_along_polyline(self.path_points, seg_idx, seg_t, Ld)

        # Save for drawing (show guidance from the boat to the target)
        self.lookahead_start = (x, y)
        self.lookahead_end = (tx, ty)
        self.target_point = (tx, ty)

        # Heading to target
        alpha = wrap_angle(math.atan2(ty - y, tx - x) - orientation)
        # Curvature for unicycle/bicycle pure pursuit
        kappa = (2.0 * math.sin(alpha)) / Ld
        # Desired angular velocity
        omega_des = clamp(linear_velocity * kappa, -self.limits.max_angular_speed, self.limits.max_angular_speed)
        # Angular acceleration command to drive current omega toward desired
        ang_acc = self.k_omega * (omega_des - angular_velocity)
        ang_acc = clamp(ang_acc, -self.limits.max_angular_accel, self.limits.max_angular_accel)

        # Speed target: constant cruise speed subject to global limit
        target_speed = self.limits.max_speed
        speed_error = target_speed - linear_velocity
        lin_acc = self.speed_pid.update(speed_error, dt)
        lin_acc = clamp(lin_acc, -self.limits.max_linear_accel, self.limits.max_linear_accel)

        return lin_acc, ang_acc
