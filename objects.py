
class Bullet(object):
    def __init__(self, center, angle, id_):
        self.center = center.copy()
        self.angle = angle
        self.id_ = id_


class State(object):
    def __init__(self, time, agents, compet_info, done=False):
        self.time = time
        self.agents = agents
        self.compet = compet_info
        self.done = done


class Record(object):
    def __init__(self, time, cars, compet_info, bullets):
        self.time = time
        self.cars = cars
        self.compet_info = compet_info
        self.bullets = bullets


class GameMap(object):
    def __init__(self, dimensions, zones, barriers):
        self.dimensions = dimensions
        self.zones = zones
        self.barriers = barriers
