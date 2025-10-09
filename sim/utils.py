from typing import Union
import math
import pygame
from typing import List, Tuple

numeric = Union[int, float]


def clamp(value: float, min_value: float, max_value: float) -> float:
	return max(min_value, min(max_value, value))


def wrap_angle(angle: float) -> float:
	"""Wrap angle to [-pi, pi]."""
	return (angle + math.pi) % (2 * math.pi) - math.pi


def angle_to_target(x: float, y: float, tx: float, ty: float) -> float:
	return math.atan2(ty - y, tx - x)


def draw_waypoints(screen: pygame.Surface, waypoints: list[tuple[float, float]], current_index: int = 0):
	"""Draw waypoints as small circles with lines between them."""
	if not waypoints:
		return
	# Convert to screen coordinates using a basic center transform: use GUI.translate_draw_point externally if needed
	width, height = screen.get_size()
	def to_screen(pt):
		return (pt[0] + width / 2, height / 2 - pt[1])

	# Lines
	for i in range(len(waypoints) - 1):
		pygame.draw.line(screen, pygame.Color("#555555"), to_screen(waypoints[i]), to_screen(waypoints[i + 1]), 1)
	# Points
	for i, (wx, wy) in enumerate(waypoints):
		color = pygame.Color("#ff7f0e") if i == current_index else pygame.Color("#1f77b4")
		pygame.draw.circle(screen, color, to_screen((wx, wy)), 5)


def draw_path(screen: pygame.Surface, path_points: list[tuple[float, float]], color: Union[str, pygame.Color] = "#8a2be2", width: int = 2):
	"""Draw the boat path as a polyline. Expects world coordinates like boat.x/y.
	Use a simple center transform consistent with draw_waypoints.
	"""
	if len(path_points) < 2:
		return
	width_px, height_px = screen.get_size()
	def to_screen(pt):
		return (pt[0] + width_px / 2, height_px / 2 - pt[1])
	transformed = [to_screen(p) for p in path_points]
	pygame.draw.lines(screen, pygame.Color(color), False, transformed, width)


# --- Geometry helpers for Pure Pursuit ---
def closest_point_on_segment(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> Tuple[float, float, float]:
    """Return the closest point on segment AB to P and the param t in [0,1]."""
    abx, aby = bx - ax, by - ay
    apx, apy = px - ax, py - ay
    ab2 = abx * abx + aby * aby
    if ab2 == 0:
        return ax, ay, 0.0
    t = (apx * abx + apy * aby) / ab2
    t = clamp(t, 0.0, 1.0)
    cx, cy = ax + t * abx, ay + t * aby
    return cx, cy, t


def closest_point_on_polyline(px: float, py: float, pts: List[Tuple[float, float]]):
    """Return (closest_point(x,y), segment_index, t_along_segment) to P on a piecewise linear path."""
    best_d2 = float('inf')
    best = (pts[0], 0, 0.0)
    for i in range(len(pts) - 1):
        ax, ay = pts[i]
        bx, by = pts[i + 1]
        cx, cy, t = closest_point_on_segment(px, py, ax, ay, bx, by)
        d2 = (px - cx) ** 2 + (py - cy) ** 2
        if d2 < best_d2:
            best_d2 = d2
            best = ((cx, cy), i, t)
    return best


def advance_along_polyline(pts: List[Tuple[float, float]], seg_index: int, seg_t: float, distance: float):
    """Advance along the polyline by 'distance' starting from (seg_index, seg_t).
    Return (point(x,y), new_seg_index, new_seg_t).
    """
    i = seg_index
    t = seg_t
    while distance > 0 and i < len(pts) - 1:
        ax, ay = pts[i]
        bx, by = pts[i + 1]
        seg_vec_x, seg_vec_y = (bx - ax), (by - ay)
        seg_len = math.hypot(seg_vec_x, seg_vec_y)
        if seg_len == 0:
            i += 1
            t = 0.0
            continue
        # Remaining distance on this segment
        rem = (1.0 - t) * seg_len
        if distance <= rem:
            # Within this segment
            new_t = t + distance / seg_len
            x = ax + new_t * seg_vec_x
            y = ay + new_t * seg_vec_y
            return (x, y), i, new_t
        else:
            # Move to next segment
            distance -= rem
            i += 1
            t = 0.0
    # End of path: clamp to end point
    end = pts[-1]
    return end, len(pts) - 2 if len(pts) >= 2 else 0, 1.0


# --- Water current helpers ---
def make_sinusoidal_current(
    amplitude: float,
    direction_angle: float,
    spatial_wavelength: float | None = None,
    temporal_period: float | None = None,
    phase: float = 0.0,
    bias: Tuple[float, float] = (0.0, 0.0),
):
    """Create a sinusoidal water current field function.

    The current vector oscillates along the given direction with optional spatial
    and temporal variation:

    - amplitude: peak speed (px/s)
    - direction_angle: radians, direction of both propagation and flow
    - spatial_wavelength: pixels; if None or 0, no spatial variation
    - temporal_period: seconds; if None or 0, no temporal variation
    - phase: radians, initial phase offset
    - bias: constant drift vector (px/s)

    Returns a function (x, y, t) -> (cx, cy).
    """
    ux = math.cos(direction_angle)
    uy = math.sin(direction_angle)
    # Wave number and angular frequency
    k = (2.0 * math.pi / spatial_wavelength) if spatial_wavelength and spatial_wavelength != 0 else 0.0
    omega = (2.0 * math.pi / temporal_period) if temporal_period and temporal_period != 0 else 0.0

    def field(x: float, y: float, t: float) -> Tuple[float, float]:
        # Project position onto propagation direction
        s = x * ux + y * uy
        phi = k * s + omega * t + phase
        mag = math.sin(phi) * amplitude
        return bias[0] + mag * ux, bias[1] + mag * uy

    return field


# --- Vector drawing helpers ---
def draw_vector(
    screen: pygame.Surface,
    origin_world: Tuple[float, float],
    vec_world: Tuple[float, float],
    color: Union[str, pygame.Color] = "#00aaff",
    scale: float = 1.0,
    width: int = 2,
    head_len: float = 8.0,
    head_angle_deg: float = 25.0,
):
    """Draw an arrow representing a world-space vector from a world origin.
    'scale' scales the vector length for drawing only.
    """
    width_px, height_px = screen.get_size()
    def to_screen(pt):
        return (pt[0] + width_px / 2, height_px / 2 - pt[1])

    ox, oy = origin_world
    vx, vy = vec_world
    end_world = (ox + vx * scale, oy + vy * scale)
    pygame.draw.line(screen, pygame.Color(color), to_screen((ox, oy)), to_screen(end_world), width)

    # Arrow head
    ang = math.atan2(vy, vx)
    left = (
        end_world[0] - head_len * math.cos(ang - math.radians(head_angle_deg)),
        end_world[1] - head_len * math.sin(ang - math.radians(head_angle_deg)),
    )
    right = (
        end_world[0] - head_len * math.cos(ang + math.radians(head_angle_deg)),
        end_world[1] - head_len * math.sin(ang + math.radians(head_angle_deg)),
    )
    pygame.draw.line(screen, pygame.Color(color), to_screen(end_world), to_screen(left), width)
    pygame.draw.line(screen, pygame.Color(color), to_screen(end_world), to_screen(right), width)


def draw_current_field(
    screen: pygame.Surface,
    field_fn,
    time_seconds: float,
    spacing: int = 120,
    scale: float = 0.6,
    color: Union[str, pygame.Color] = "#00aa00",
    width: int = 1,
):
    """Draw a grid of arrows representing the current field. Assumes center-origin world mapping."""
    width_px, height_px = screen.get_size()
    def to_world(i, j):
        return (i - width_px / 2, height_px / 2 - j)
    for i in range(spacing // 2, width_px, spacing):
        for j in range(spacing // 2, height_px, spacing):
            xw, yw = to_world(i, j)
            cx, cy = field_fn(xw, yw, time_seconds)
            draw_vector(screen, (xw, yw), (cx, cy), color=color, scale=scale, width=width)