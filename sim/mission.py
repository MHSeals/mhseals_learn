from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Waypoint:
    x: float
    y: float
    tolerance: float = 10.0  # pixels


class Mission:
    def __init__(self, waypoints: List[Waypoint]):
        self.waypoints = waypoints
        self._index = 0

    @property
    def done(self) -> bool:
        return self._index >= len(self.waypoints)

    def current(self) -> Optional[Waypoint]:
        if self.done:
            return None
        return self.waypoints[self._index]

    def advance_if_reached(self, x: float, y: float):
        if self.done:
            return
        wp = self.waypoints[self._index]
        dx = wp.x - x
        dy = wp.y - y
        if (dx * dx + dy * dy) ** 0.5 <= wp.tolerance:
            self._index += 1
