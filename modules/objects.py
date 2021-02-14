
class State(object):
    def __init__(self, time, robots):
        self.time = time
        self.robots = robots


class Record(object):
    def __init__(self, time, robots, bullets):
        self.time = time
        self.robots = robots
        self.bullets = bullets
