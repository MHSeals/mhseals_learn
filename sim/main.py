import pygame
import numpy as np
from boat import Boat
from buoy import BallBuoy, PoleBuoy
from enums import BuoyColors
from gui import GUI
from map import Gate
from constants import Constants as C

C.to_px()
C.to_rad()

gui = GUI(1200, 800)
boat = Boat(length=C.Boat.LENGTH, width=C.Boat.WIDTH, x=-gui.width/3, y=0, orientation=C.Boat.START_ORIENTATION, color="#1f1f1f")
print(boat)
gate = Gate.random(boat)
running = True

while running:
    for event in gui.get_events():
        if event.type == pygame.QUIT:
            running = False

    boat.set_linear_velocity(5 * C.Conversions.METERS2PX)
    boat.set_angular_velocity(0)
    boat.move()

    gui.clear("#b2d8d8")
    
    for buoy in gate.buoys:
        buoy.draw(gui.screen)
    boat.draw(gui.screen)

    gui.update()
    
gui.quit()