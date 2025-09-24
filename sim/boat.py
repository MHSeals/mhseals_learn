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
        
    def set_linear_velocity(velocity):
        self.linear_velocity = velocity

    def set_angular_velocity(velocity):
        self.angular_velocity = velocity