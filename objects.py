
class bullet(object):
    def __init__(self, center, angle, speed, owner):
        self.center = center.copy()
        self.speed = speed
        self.angle = angle
        self.owner = owner


class state(object):
    def __init__(self, time, agents, compet_info, done=False, detect=None, vision=None):
        self.time = time
        self.agents = agents
        self.compet = compet_info
        self.done = done
        self.detect = detect
        self.vision = vision


class record(object):
    def __init__(self, time, cars, compet_info, detect, vision, bullets):
        self.time = time
        self.cars = cars
        self.compet_info = compet_info
        self.detect = detect
        self.vision = vision
        self.bullets = bullets


class g_map(object):
    def __init__(self, length, width, areas, barriers):
        self.length = length
        self.width = width
        self.areas = areas
        self.barriers = barriers
