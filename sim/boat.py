from time import time

class Boat:
    def __init__(
        self,
        length: int,
        width: int,
        color="#000000",
        x=0.0,
        y=0.0,
        orientation=0.0,
        linear_velocity=0.0,
        angular_velocity=0.0
    ):
        # Properties
        self.length = length
        self.width = width
        self.color = color
        self.x = x
        self.y = y
        self.orientation = orientation
        self.linear_velocity = linear_velocity
        self.angular_velocity = angular_velocity
        self.time = time()
        self.dt = 0
        
    def set_linear_velocity(self, velocity):
        self.linear_velocity = velocity

    def set_angular_velocity(self, velocity):
        self.angular_velocity = velocity
        
    def update_delta_time(self):
        current_time = time()
        self.dt = current_time - self.time
        self.time = current_time        

    def move(self):
        update_delta_time()
        self.x += np.cos(self.orientation) * self.linear_velocity * self.dt
        self.y += np.sin(self.orientation) * self.linear_velocity * self.dt
        self.orientation += self.angular_velocity * self.dt