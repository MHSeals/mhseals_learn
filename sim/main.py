import pygame
from boat import Boat
from gui import GUI

boat = Boat(50, 30, 0, 0)
gui = GUI(boat, 600, 800)

while True:
    gui.run()