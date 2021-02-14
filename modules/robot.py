import numpy as np
import pygame
from typing import Union
from modules.cache import Cache
from modules.constants import *
from modules.geometry import mirror, Line, Rectangle

chassis_outline = [Line(mirror(ROBOT.chassis_points[0], flip_x=x, flip_y=y),
                        mirror(ROBOT.chassis_points[1], flip_x=x, flip_y=y), COLOR.green) for x in [0, 1] for y in [0, 1]] + \
                  [Line(mirror(ROBOT.chassis_points[2], flip_x=x, flip_y=y),
                        mirror(ROBOT.chassis_points[3], flip_x=x, flip_y=y), COLOR.green) for x in [0, 1] for y in [0, 1]]
shield_outline = [Line(ROBOT.shield_dims, mirror(ROBOT.shield_dims, flip_y=False), COLOR.green),
                  Line(ROBOT.shield_dims, mirror(ROBOT.shield_dims, flip_x=False), COLOR.green),
                  Line(mirror(ROBOT.shield_dims), mirror(ROBOT.shield_dims, flip_y=False), COLOR.green),
                  Line(mirror(ROBOT.shield_dims), mirror(ROBOT.shield_dims, flip_x=False), COLOR.green)]
armor_panels = [Line(ROBOT.armor_points[0], mirror(ROBOT.armor_points[0], flip_x=False), COLOR.orange),
                Line(ROBOT.armor_points[1], mirror(ROBOT.armor_points[1], flip_y=False), COLOR.orange),
                Line(mirror(ROBOT.armor_points[1]), mirror(ROBOT.armor_points[1], flip_x=False), COLOR.orange),
                Line(mirror(ROBOT.armor_points[0]), mirror(ROBOT.armor_points[0], flip_y=False), COLOR.orange)]  # front/right/left/back armors


class Robot:
    count_blue = 0
    count_red = 0
    cache = None

    def __init__(self):
        assert Robot.count_red + Robot.count_blue <= 3, 'maximum 4 robots'
        self.id_ = Robot.count_red + Robot.count_blue + 1
        self.is_blue = Robot.count_blue <= Robot.count_red
        self.center = np.array(mirror(FIELD.spawn_center, flip_x=self.is_blue, flip_y=self.id_ in {1, 4}), dtype=np.float32)
        self.angle = 0 if self.is_blue else 180
        self.yaw = 0
        self.heat = 0
        self.hp = 2000
        self.can_shoot = True
        self.can_move = True
        self.timeout = 0
        self.ammo = 50 if self.id_ <= 1 else 0
        self.barrier_hits = 0
        self.bullet_hits = 0
        self.robot_hits = 0
        self.commands = np.zeros(8, dtype=np.int8)  # x, y, rotate, yaw, shoot, supply, shoot_mode, auto_aim
        self.actions = np.zeros(8, dtype=np.float32)  # rotate_speed, yaw_speed, x_speed, y_speed, shoot

        if self.is_blue:
            Robot.count_blue += 1
        else:
            Robot.count_red += 1

    def draw(self, screen: pygame.Surface, font: pygame.font.Font, stat=False):
        if Robot.cache is None:
            Robot.cache = Cache(
                blue_chassis_image=pygame.image.load(IMAGE.blue_robot).convert_alpha(),
                red_chassis_image=pygame.image.load(IMAGE.red_robot).convert_alpha(),
                dead_chassis_image=pygame.image.load(IMAGE.dead_robot).convert_alpha(),
                gimbal_image=pygame.image.load(IMAGE.gimbal).convert_alpha())

        chassis_image = Robot.cache.blue_chassis_image if self.is_blue else Robot.cache.red_chassis_image
        if self.hp <= 0:
            chassis_image = Robot.cache.dead_chassis_image

        chassis_image = pygame.transform.rotate(chassis_image, -self.angle)
        gimbal_image = pygame.transform.rotate(Robot.cache.gimbal_image, -self.yaw - self.angle)
        chassis_rect = chassis_image.get_rect()
        gimbal_rect = gimbal_image.get_rect()
        chassis_rect.center = self.center + FIELD.half_dims
        gimbal_rect.center = self.center + FIELD.half_dims
        screen.blit(chassis_image, chassis_rect)
        screen.blit(gimbal_image, gimbal_rect)
        label = font.render(f'{self.id_} | {self.hp:.0f}', False, COLOR.blue if self.is_blue else COLOR.red)
        screen.blit(label, self.center + TEXT.robot_label_offset + FIELD.half_dims)

        if stat:
            for line in [*chassis_outline, *shield_outline, *armor_panels]:
                line.transformed(self.center, self.angle).draw(screen)

    def collides_chassis(self, rect: Rectangle):
        lines = [l.transformed(self.center, self.angle) for l in chassis_outline]
        if any(rect.intersects(l) for l in lines):
            self.barrier_hits += 1
            return True
        return False

    def collides_armor(self, rect: Rectangle):
        if self._check_armor(rect):
            self.barrier_hits += 1
            return True
        return False

    def hits_armor(self, line: Line):
        if self._check_armor(line):
            self.bullet_hits += 1
            return True
        lines = [l.transformed(self.center, self.angle) for l in shield_outline]
        return any(line.intersects(l) for l in lines)

    def _check_armor(self, geometry: Union[Line, Rectangle]):
        lines = [l.transformed(self.center, self.angle) for l in armor_panels]
        if geometry.intersects(lines[0]):
            self.hp -= 20
        elif geometry.intersects(lines[1]) or geometry.intersects(lines[2]):
            self.hp -= 40
        elif geometry.intersects(lines[3]):
            self.hp -= 60
        else:
            return False
        return True

    def commands_to_actions(self):
        self.actions[2] += self.commands[0] * 1.5 / ROBOT.motion
        if self.commands[0] == 0:
            if self.actions[2] > 0:
                self.actions[2] -= 1.5 / ROBOT.motion
            if self.actions[2] < 0:
                self.actions[2] += 1.5 / ROBOT.motion
        if abs(self.actions[2]) < 1.5 / ROBOT.motion:
            self.actions[2] = 0
        self.actions[2] = np.clip(self.actions[2], -1.5, 1.5)
        # x, y
        self.actions[3] += self.commands[1] * 1 / ROBOT.motion
        if self.commands[1] == 0:
            if self.actions[3] > 0:
                self.actions[3] -= 1 / ROBOT.motion
            if self.actions[3] < 0:
                self.actions[3] += 1 / ROBOT.motion
        if abs(self.actions[3]) < 1 / ROBOT.motion:
            self.actions[3] = 0
        self.actions[3] = np.clip(self.actions[3], -1, 1)
        # rotate chassis
        self.actions[0] += self.commands[2] * 1 / ROBOT.rotate_motion
        if self.commands[2] == 0:
            if self.actions[0] > 0:
                self.actions[0] -= 1 / ROBOT.rotate_motion
            if self.actions[0] < 0:
                self.actions[0] += 1 / ROBOT.rotate_motion
        if abs(self.actions[0]) < 1 / ROBOT.rotate_motion:
            self.actions[0] = 0
        self.actions[0] = np.clip(self.actions[0], -1, 1)
        # rotate yaw
        self.actions[1] += self.commands[3] / ROBOT.yaw_motion
        if self.commands[3] == 0:
            if self.actions[1] > 0:
                self.actions[1] -= 1 / ROBOT.yaw_motion
            if self.actions[1] < 0:
                self.actions[1] += 1 / ROBOT.yaw_motion
        if abs(self.actions[1]) < 1 / ROBOT.yaw_motion:
            self.actions[1] = 0
        self.actions[1] = np.clip(self.actions[1], -3, 3)
        self.actions[4:] = self.commands[4:]

    def status_dict(self):
        return {
            'x': self.center[0],
            'y': self.center[1],
            'angle': self.angle,
            'yaw': self.yaw,
            'heat': self.heat,
            'hp': self.hp,
            'can_shoot': self.can_shoot,
            'can_move': self.can_move,
            'timeout': self.timeout,
            'ammo': self.ammo,
            'barrier_hits': self.barrier_hits,
            'bullet_hits': self.bullet_hits,
            'robot_hits': self.robot_hits
        }
