import pygame
from boat import Boat
from buoy import BallBuoy, PoleBuoy
from enums import BuoyColors
from gui import GUI
from mission import Mission, Waypoint
from controller import WaypointFollower, ControlLimits, PurePursuitFollower
from pid import PID
from utils import draw_waypoints, draw_path, make_sinusoidal_current, draw_current_field, draw_vector
import math

waypoints = []

# Generate waypoints on a sinusoidal path
for x in range(-300, 301, 20):
    y = 100 * math.sin(x / 50.0)
    waypoints.append(Waypoint(x, y, tolerance=15.0))

mission = Mission(waypoints)

starting_orientation = math.atan2(waypoints[1].y - waypoints[0].y, waypoints[1].x - waypoints[0].x)

boat = Boat(50, 30, waypoints[0].x, waypoints[0].y, orientation=starting_orientation, color="#1f1f1f")
buoys = [BallBuoy(-250, -150, BuoyColors.BLUE), PoleBuoy(100, 100, BuoyColors.GREEN)]
gui = GUI(800, 600)
running = True

# Path history for trail plotting
path_points: list[tuple[float, float]] = [(boat.x, boat.y)]

limits = ControlLimits(max_speed=50.0)  # px/s

# Pure pursuit setup (tunable)
speed_pid = PID(kp=1.0, ki=0.2, kd=0.0, output_limit=50.0, integral_limit=200.0)
lookahead_base = 40.0            # pixels, base lookahead
lookahead_speed_gain = 0.3       # pixels per (px/s), grows with speed
k_omega = 3.0                    # how aggressively to achieve desired angular velocity
controller = PurePursuitFollower(
    [(wp.x, wp.y) for wp in mission.waypoints],
    lookahead_base,
    speed_pid,
    limits,
    lookahead_speed_gain,
    k_omega,
)

# Set a sinusoidal water current field: amplitude 8 px/s, direction 30°, spatial wavelength 400 px, temporal period 12 s,
# with a small constant drift bias of (2, 0).
current_fn = make_sinusoidal_current(
    amplitude=4.0,
    direction_angle=math.pi/6,
    spatial_wavelength=400.0,
    temporal_period=2.0,
    phase=0.0,
    bias=(2.0, 0.0),
)
boat.set_water_current_field(current_fn)

while running:
    for event in gui.get_events():
        if event.type == pygame.QUIT:
            running = False

    # Compute control accelerations to follow waypoints
    # Estimate dt from boat's internal dt once per update call
    # We need dt for PID; we'll peek at boat.dt after calling update_delta_time.
    # Call update_delta_time without moving pose to get dt.
    prev_time = boat.time
    boat.update_delta_time()
    dt = boat.dt
    # Rewind time so move() still uses correct dt once.
    boat.time = prev_time

    # Not needed for pure pursuit path; we operate on the continuous polyline

    lin_acc, ang_acc = controller.compute_controls(
        boat.x,
        boat.y,
        boat.orientation,
        boat.linear_velocity,
        boat.angular_velocity,
        dt if dt > 0 else 1/60,
    )
    boat.set_linear_acceleration(lin_acc)
    boat.set_angular_acceleration(ang_acc)
    boat.move()

    # Append to path history (thin out by adding only when moved a bit)
    if not path_points or (abs(boat.x - path_points[-1][0]) + abs(boat.y - path_points[-1][1])) > 1.0:
        path_points.append((boat.x, boat.y))

    # Check waypoint progress
    mission.advance_if_reached(boat.x, boat.y)

    gui.clear("#b2d8d8")
    # Draw current field grid (vector field)
    draw_current_field(gui.screen, current_fn, time_seconds=boat.time, spacing=60, scale=2.0, color="#0025aa", width=1)
    
    for buoy in buoys:
        buoy.draw(gui.screen)
    # Draw boat path
    draw_path(gui.screen, path_points, color="#8a2be2", width=2)
    # Draw waypoints
    draw_waypoints(gui.screen, [(wp.x, wp.y) for wp in mission.waypoints], current_index=0)
    # Draw lookahead line and target point (if available)
    if getattr(controller, 'lookahead_start', None) and getattr(controller, 'lookahead_end', None):
        # Transform and draw
        width, height = gui.screen.get_size()
        def to_screen(pt):
            return (pt[0] + width / 2, height / 2 - pt[1])
        pygame.draw.line(gui.screen, pygame.Color('#00aa00'), to_screen(controller.lookahead_start), to_screen(controller.lookahead_end), 2)
    if getattr(controller, 'target_point', None):
        width, height = gui.screen.get_size()
        def to_screen(pt):
            return (pt[0] + width / 2, height / 2 - pt[1])
        pygame.draw.circle(gui.screen, pygame.Color('#ff0000'), to_screen(controller.target_point), 6)
    boat.draw(gui.screen)

    # Boat-local current arrow and HUD
    try:
        cx, cy = current_fn(boat.x, boat.y, boat.time)
    except Exception:
        cx, cy = (0.0, 0.0)
    draw_vector(gui.screen, (boat.x, boat.y), (cx, cy), color="#ff9900", scale=2.0, width=2)

    # HUD text showing current magnitude and direction
    speed = (cx * cx + cy * cy) ** 0.5
    ang_deg = math.degrees(math.atan2(cy, cx))
    font = pygame.font.SysFont(None, 18)
    text = font.render(f"Current: {speed:.1f} px/s  @ {ang_deg:.0f}°", True, pygame.Color("#003300"))
    gui.screen.blit(text, (10, 10))

    gui.update()
    
gui.quit()