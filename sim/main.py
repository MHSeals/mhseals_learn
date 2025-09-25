from boat import Boat
from buoy import BallBuoy
from enums import BuoyColors
from gui import GUI

boat = Boat(50, 30, 0, 0, "#1f1f1f")
buoys = [BallBuoy(-250, -150, BuoyColors.BLUE), PoleBuoy(100, 100, BuoyColors.GREEN)]
gui = GUI(800, 600)
running = True

while running:
    for event in gui.get_events():
        if event.type == pygame.QUIT:
            running = False

    boat.set_linear_velocity(90) # px/s
    boat.set_angular_velocity(0.8) # rad/s
    boat.move()

    gui.clear("#b2d8d8")
    
    for buoy in buoys:
        buoy.draw(gui.screen)
    boat.draw(gui.screen)
    
gui.quit()