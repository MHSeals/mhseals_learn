from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class PIDConfig:
    kp: float
    ki: float
    kd: float
    integral_limit: Optional[float] = None
    output_limit: Optional[float] = None


class PID:
    def __init__(self, kp: float, ki: float, kd: float,
                 integral_limit: Optional[float] = None,
                 output_limit: Optional[float] = None):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral_limit = integral_limit
        self.output_limit = output_limit

        self._integral = 0.0
        self._prev_error = 0.0
        self._first = True

    def reset(self):
        self._integral = 0.0
        self._prev_error = 0.0
        self._first = True

    def set_gains(self, kp: float, ki: float, kd: float):
        self.kp, self.ki, self.kd = kp, ki, kd

    def update(self, error: float, dt: float) -> float:
        if dt <= 0:
            # Degenerate dt: purely proportional output
            p = self.kp * error
            d = 0.0
            i = self.ki * self._integral
            out = p + i + d
            if self.output_limit is not None:
                out = max(-self.output_limit, min(self.output_limit, out))
            return out

        # Proportional
        p = self.kp * error

        # Integral with anti-windup
        self._integral += error * dt
        if self.integral_limit is not None:
            self._integral = max(-self.integral_limit, min(self.integral_limit, self._integral))
        i = self.ki * self._integral

        # Derivative on error
        if self._first:
            d_error = 0.0
            self._first = False
        else:
            d_error = (error - self._prev_error) / dt
        d = self.kd * d_error
        self._prev_error = error

        out = p + i + d
        if self.output_limit is not None:
            out = max(-self.output_limit, min(self.output_limit, out))
        return out
