import numpy as np
from globals import *

MOTION = 6
ROTATE_MOTION = 4
YAW_MOTION = 1
WHEEL_POINTS = ((-22.5, -29), (22.5, -29), (-22.5, -14), (22.5, -14), (-22.5, 14), (22.5, 14), (-22.5, 29), (22.5, 29))
ARMOR_POINTS = ((-6.5, -30), (6.5, -30), (-18.5, -7), (18.5, -7), (-18.5, 0), (18.5, 0), (-18.5, 6), (18.5, 6), (-6.5, 30), (6.5, 30))
OUTLINE_POINTS = ((-22.5, -30), (22.5, 30), (-22.5, 30), (22.5, -30))
ARMOR_CENTERS = ((0, -30), (18.5, 0), (0, 30), (-18.5, 0))


class Robot:
    def __init__(self, id_, team, x_start, y_start):
        angle_start = 90 if (team == TEAM_RED) else -90
        bullet_start = 50 if id_ <= 1 else 0
        #  0    1  2    3     4    5    6        7           8          9        10       11         12         13         14
        # team, x, y, angle, yaw, heat, hp, freeze_time, is_supply, can_shoot, bullet, stay_time, wheel_hit, armor_hit, robot_hit
        self.status = np.array([team, x_start, y_start, angle_start, 0, 0, 2000, 0, 0, 1, bullet_start, 0, 0, 0, 0], dtype=np.float32)
        self.id_ = id_
        self.team = team
        self.color = COLOR_RED if (team == TEAM_RED) else COLOR_BLUE
        self.commands = np.zeros(8, dtype=np.int8)  # x, y, rotate, yaw, shoot, supply, shoot_mode, auto_aim
        self.actions = np.zeros(8, dtype=np.float32)  # rotate_speed, yaw_speed, x_speed, y_speed, shoot, shoot_multiple, supply, auto_aim

    def get_armor_center(self, index):
        return np.matmul(ARMOR_CENTERS[index], self.rotation_matrix()) + self.status[1:3]

    def get_armor_points(self):
        return [np.matmul(p, self.rotation_matrix()) + self.status[1:3] for p in ARMOR_POINTS]

    def get_wheel_points(self):
        return [np.matmul(p, self.rotation_matrix()) + self.status[1:3] for p in WHEEL_POINTS]

    def get_outline_points(self):
        return [np.matmul(p, self.rotation_matrix()) + self.status[1:3] for p in OUTLINE_POINTS]

    def transfer_to_car_coordinate(self, points):
        return np.matmul(points - self.status[1:3], self.rotation_matrix())

    def rotation_matrix(self):
        return np.array([[np.cos(-np.deg2rad(self.status[3])), -np.sin(-np.deg2rad(self.status[3]))],
                         [np.sin(-np.deg2rad(self.status[3])), np.cos(-np.deg2rad(self.status[3]))]])

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
