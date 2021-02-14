import random
import pygame
import time
from modules.cache import Cache
from modules.constants import *
from modules.geometry import Rectangle, mirror

activation_rects = [Rectangle(*ZONE.activation_dims, *c) for ci in ZONE.centers for c in [ci, mirror(ci)]]


class Zones:
    types = None
    activation_status = None
    cache = None

    def reset(self):
        self._randomize()
        self.activation_status = [False] * 6

    def apply(self, robots):
        for i, (rect, type_, activated) in enumerate(zip(activation_rects, self.types, self.activation_status)):
            for robot in robots:
                if rect.contains(robot.center) and not activated:
                    self._apply_buff_debuff(robot, robots, type_)
                    self.activation_status[i] = True

    def draw(self, screen):
        if self.cache is None:
            self.cache = Cache(
                inactive_image=pygame.image.load(IMAGE.inactive_zone).convert_alpha(),
                activated_image=pygame.image.load(IMAGE.activated_zone).convert_alpha(),
                icon_images=[pygame.image.load(IMAGE.zone_icon.format(k)).convert_alpha() for k in ZONE.types.keys()],
                zone_rects=[Rectangle(*ZONE.dims, *c).pygame_rect() for ci in ZONE.centers for c in [ci, mirror(ci)]])
        for zone_rect, type_, activated in zip(self.cache.zone_rects, self.types, self.activation_status):
            zone_image = self.cache.activated_image if activated else self.cache.inactive_image
            screen.blit(zone_image, zone_rect)
            screen.blit(self.cache.icon_images[type_], zone_rect)

    def _randomize(self):
        random.seed(time.time())
        indices = [0, 2, 4]
        random.shuffle(indices)  # randomly order zones
        self.types = [0] * 6

        for i in range(3):
            side = random.choice([0, 1])  # choose left/right side of field
            self.types[2 * i: 2 * i + 1] = [indices[i] + side, indices[i] + 1 - side]

    @staticmethod
    def _apply_buff_debuff(activating_robot, robots, type_):  # Buff/Debuff (Rules 2.3.1)
        if type_ == ZONE.types['hp_blue']:
            for robot in robots:
                if robot.is_blue:
                    robot.hp += 200
        elif type_ == ZONE.types['hp_red']:
            for robot in robots:
                if not robot.is_blue:
                    robot.hp += 200
        elif type_ == ZONE.types['ammo_blue']:
            for robot in robots:
                if robot.is_blue:
                    robot.ammo += 100
        elif type_ == ZONE.types['ammo_red']:
            for robot in robots:
                if not robot.is_blue:
                    robot.ammo += 100
        elif type_ == ZONE.types['no_move']:
            activating_robot.can_move = False
            activating_robot.timeout = 10
        elif type_ == ZONE.types['no_shoot']:
            activating_robot.can_shoot = False
            activating_robot.timeout = 10
