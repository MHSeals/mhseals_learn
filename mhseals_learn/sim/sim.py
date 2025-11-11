#!/usr/bin/env python3

import pygame
import numpy as np
from mhseals_learn.sim.boat import Boat
from mhseals_learn.sim.buoy import BallBuoy, PoleBuoy
from mhseals_learn.sim.enums import BuoyColors
from mhseals_learn.sim.gui import GUI
from mhseals_learn.sim.map import Gate
from mhseals_learn.sim.constants import Constants as C
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

C.to_px()
C.to_rad()


class BoatControl(Node):
    def __init__(self, boat: Boat, gui: GUI, gate: Gate):
        self.boat = boat
        self.gui = gui
        self.gate = gate

        super().__init__('boat_control')
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.control_callback,
            10
        )
        self.timer = self.create_timer(0, self.timer_callback)

    def timer_callback(self):
        for event in self.gui.get_events():
            if event.type == pygame.QUIT:
                running = False
    
        self.boat.set_linear_velocity(5 * C.Conversions.METERS2PX)
        self.boat.set_angular_velocity(0)
        self.boat.move()
    
        self.gui.clear("#b2d8d8")
        
        for buoy in self.gate.buoys:
            buoy.draw(self.gui.screen)
        self.boat.draw(self.gui.screen)
    
        self.gui.update()

    def control_callback(self, msg):
        self.boat.set_angular_velocity(msg.angular.z)    
        self.boat.set_linear_velocity(msg.linear.x)

def main(args=None):
    rclpy.init(args=args)

    gui = GUI(1200, 800)
    boat = Boat(length=C.Boat.LENGTH, width=C.Boat.WIDTH, x=-gui.width/3, y=0, orientation=C.Boat.START_ORIENTATION, color="#1f1f1f")
    gate = Gate.random(boat)
    boat_control = BoatControl(boat, gui, gate)

    rclpy.spin(boat_control)

    boat_control.destroy_node()
    rclpy.shutdown()
    gui.quit()

if __name__ == '__main__':
    main()
