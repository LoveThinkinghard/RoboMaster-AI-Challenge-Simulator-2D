import enum
from box import Box
import random
import pygame
from globals import TEAM
import time

ZONE_CENTERS = [(50, 169), (190, 283), (404, 44.5), (404, 403.5), (618, 165), (758, 279)]  # Zones F1-6 (Rules 2.1)
ZONE_BOXES = [Box(54, 48, *c) for c in ZONE_CENTERS]
ICON_BOXES = [Box(20, 20, *c) for c in ZONE_CENTERS]


class ZONE_TYPE(enum.Enum):  # indices matter, names correspond with icon files
    hp_blue = 0
    hp_red = 1
    ammo_blue = 2
    ammo_red = 3
    no_move = 4
    no_shoot = 5


class Zones:
    def __init__(self, render=False):
        self.types = None
        self.activation = None

        if render:
            self.inactive_image = pygame.image.load(f'elements/area/zone_inactive.png').convert_alpha()
            self.activated_image = pygame.image.load(f'elements/area/zone_activated.png').convert_alpha()
            self.icon_images = [pygame.image.load(f'elements/icon/{t.name}.png').convert_alpha() for t in ZONE_TYPE]
            self.zone_rects = [b.to_rect() for b in ZONE_BOXES]
            self.icon_rects = [b.to_rect() for b in ICON_BOXES]

    def reset(self):
        self._randomize()
        self.activation = [False] * 6

    def apply(self, robots):
        for i, (box, type_, activated) in enumerate(zip(ZONE_BOXES, self.types, self.activation)):
            for robot in robots:
                if box.contains(robot.center) and not activated:
                    self._apply_buff_debuff(robot, robots, type_)
                    self.activation[i] = True

    def draw(self, screen):
        for zone_rect, icon_rect, type_, activated in zip(self.zone_rects, self.icon_rects, self.types, self.activation):
            zone_image = self.activated_image if activated else self.inactive_image
            screen.blit(zone_image, zone_rect)
            screen.blit(self.icon_images[type_.value], icon_rect)

    def _randomize(self):
        random.seed(time.time())
        indices = [0, 2, 4]
        random.shuffle(indices)  # randomly order zones
        side = random.choices([0, 1], k=3)  # randomly choose left/right side of field
        types = [None] * 6

        for i in range(3):
            types[i] = ZONE_TYPE(indices[i] + side[i])
            types[5 - i] = ZONE_TYPE(indices[i] + 1 - side[i])
        self.types = types

    @staticmethod
    def _apply_buff_debuff(activating_robot, robots, type_):  # Buff/Debuff (Rules 2.3.1)
        if type_ == ZONE_TYPE.hp_blue:
            for robot in robots:
                if robot.team == TEAM.blue:
                    robot.hp += 200
        elif type_ == ZONE_TYPE.hp_red:
            for robot in robots:
                if robot.team == TEAM.red:
                    robot.hp += 200
        elif type_ == ZONE_TYPE.ammo_blue:
            for robot in robots:
                if robot.team == TEAM.blue:
                    robot.ammo += 100
        elif type_ == ZONE_TYPE.ammo_red:
            for robot in robots:
                if robot.team == TEAM.red:
                    robot.ammo += 100
        elif type_ == ZONE_TYPE.no_move:
            activating_robot.can_move = False
            activating_robot.timeout = 10
        elif type_ == ZONE_TYPE.no_shoot:
            activating_robot.can_shoot = False
            activating_robot.timeout = 10
