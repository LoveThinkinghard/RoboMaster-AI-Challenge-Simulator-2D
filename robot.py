import numpy as np
from globals import *

MOTION = 6
ROTATE_MOTION = 4
YAW_MOTION = 1
WHEEL_POINTS = ((-29, -22.5), (-29, 22.5), (-14, -22.5), (-14, 22.5), (14, -22.5), (14, 22.5), (29, -22.5), (29, 22.5))
ARMOR_POINTS = ((-30, -6.5), (-30, 6.5), (-7, -18.5), (-7, 18.5), (0, -18.5), (0, 18.5), (6, -18.5), (6, 18.5), (30, -6.5), (30, 6.5))
OUTLINE_POINTS = ((-30, -22.5), (30, 22.5), (30, -22.5), (-30, 22.5))
ARMOR_CENTERS = ((-30, 0), (18.0, 5), (30, 0), (0, -18.5))


class Robot:
    count_blue = 0
    count_red = 0

    def __init__(self):
        assert Robot.count_red + Robot.count_blue <= 3, 'maximum 4 robots'

        blue = Robot.count_blue <= Robot.count_red
        self.id_ = Robot.count_red + Robot.count_blue
        self.team = TEAM.blue if blue else TEAM.red
        self.center = np.array(SPAWNS[Robot.count_blue if blue else 3 - Robot.count_red].center, dtype=np.float32)
        self.angle = np.float32(0 if blue else 180)
        self.gimbal_yaw = np.float32(0)
        self.heat = 0
        self.hp = 2000
        self.can_shoot = True
        self.can_move = True
        self.timeout = 0
        self.ammo = 50 if self.id_ <= 1 else 0
        self.wheel_hit = 0
        self.armor_hit = 0
        self.robot_hit = 0
        # self.status = 0    1  2    3     4    5    6        7           8          9        10       11         12         13         14
        #              team, x, y, angle, yaw, heat, hp, freeze_time, is_supply, can_shoot, bullet, stay_time, wheel_hit, armor_hit, robot_hit
        self.commands = np.zeros(8, dtype=np.int8)  # x, y, rotate, yaw, shoot, supply, shoot_mode, auto_aim
        self.actions = np.zeros(8, dtype=np.float32)  # rotate_speed, yaw_speed, x_speed, y_speed, shoot, shoot_multiple, supply, auto_aim

        if blue:
            Robot.count_blue += 1
        else:
            Robot.count_red += 1

    def get_armor_center(self, index):
        return np.matmul(ARMOR_CENTERS[index], self.rotation_matrix()) + self.center

    def get_armor_points(self):
        return [np.matmul(p, self.rotation_matrix()) + self.center for p in ARMOR_POINTS]

    def get_wheel_points(self):
        return [np.matmul(p, self.rotation_matrix()) + self.center for p in WHEEL_POINTS]

    def get_outline_points(self):
        return [np.matmul(p, self.rotation_matrix()) + self.center for p in OUTLINE_POINTS]

    def transfer_to_car_coordinate(self, points):
        return np.matmul(points - self.center, self.rotation_matrix())

    def rotation_matrix(self):
        return np.array([[np.cos(-np.deg2rad(self.angle)), -np.sin(-np.deg2rad(self.angle))],
                         [np.sin(-np.deg2rad(self.angle)), np.cos(-np.deg2rad(self.angle))]])

    def commands_to_actions(self):
        self.actions[2] += self.commands[0] * 1.5 / MOTION
        if self.commands[0] == 0:
            if self.actions[2] > 0:
                self.actions[2] -= 1.5 / MOTION
            if self.actions[2] < 0:
                self.actions[2] += 1.5 / MOTION
        if abs(self.actions[2]) < 1.5 / MOTION:
            self.actions[2] = 0
        if self.actions[2] >= 1.5:
            self.actions[2] = 1.5
        if self.actions[2] <= -1.5:
            self.actions[2] = -1.5
        # x, y
        self.actions[3] += self.commands[1] * 1 / MOTION
        if self.commands[1] == 0:
            if self.actions[3] > 0:
                self.actions[3] -= 1 / MOTION
            if self.actions[3] < 0:
                self.actions[3] += 1 / MOTION
        if abs(self.actions[3]) < 1 / MOTION:
            self.actions[3] = 0
        if self.actions[3] >= 1:
            self.actions[3] = 1
        if self.actions[3] <= -1:
            self.actions[3] = -1
        # rotate chassis
        self.actions[0] += self.commands[2] * 1 / ROTATE_MOTION
        if self.commands[2] == 0:
            if self.actions[0] > 0:
                self.actions[0] -= 1 / ROTATE_MOTION
            if self.actions[0] < 0:
                self.actions[0] += 1 / ROTATE_MOTION
        if abs(self.actions[0]) < 1 / ROTATE_MOTION:
            self.actions[0] = 0
        if self.actions[0] > 1:
            self.actions[0] = 1
        if self.actions[0] < -1:
            self.actions[0] = -1
        # rotate yaw
        self.actions[1] += self.commands[3] / YAW_MOTION
        if self.commands[3] == 0:
            if self.actions[1] > 0:
                self.actions[1] -= 1 / YAW_MOTION
            if self.actions[1] < 0:
                self.actions[1] += 1 / YAW_MOTION
        if abs(self.actions[1]) < 1 / YAW_MOTION:
            self.actions[1] = 0
        if self.actions[1] > 3:
            self.actions[1] = 3
        if self.actions[1] < -3:
            self.actions[1] = -3
        self.actions[4:] = self.commands[4:]

    def status_dict(self):
        return {
            'x': self.center[0],
            'y': self.center[1],
            'angle': self.angle,
            'gimbal yaw': self.gimbal_yaw,
            'heat': self.heat,
            'hp': self.hp,
            'can_shoot': self.can_shoot,
            'can_move': self.can_move,
            'ammo': self.ammo,
            'wheel hits': self.wheel_hit,
            'armor hits': self.armor_hit,
            'robot hits': self.robot_hit
        }
