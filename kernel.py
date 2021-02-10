import numpy as np
from objects import *
from globals import *
from robot import Robot
from zones import Zones
import pygame
import random


class Kernel(object):
    def __init__(self, robot_count, render=False, record=True):
        self.car_count = robot_count
        self.render = render
        self.record = record
        self.time, self.obs, self.compet_info, self.bullets, self.epoch, self.n, self.dev, self.memory, self.robots = None, None, None, None, None, None, None, None, None

        if render:
            pygame.init()
            self.screen = pygame.display.set_mode(FIELD.dimensions)
            pygame.display.set_caption('RM AI Challenge Simulator')

            self.area_images = []
            self.area_rects = []

            for area, image_file in zip((*SPAWNS, *LOW_BARRIERS, *HIGH_BARRIERS), STATIC_IMAGES):
                self.area_images.append(pygame.image.load(f'elements/{image_file}.png').convert_alpha())
                self.area_rects.append(area.to_rect())

            self.chassis_blue_img = pygame.image.load('elements/robot/blue.png').convert_alpha()
            self.chassis_red_img = pygame.image.load('elements/robot/red.png').convert_alpha()
            self.gimbal_img = pygame.image.load('elements/robot/gimbal.png').convert_alpha()
            self.bullet_img = pygame.image.load('elements/robot/bullet.png').convert_alpha()
            self.info_bar_img = pygame.image.load('elements/info_panel.png').convert_alpha()
            self.bullet_rect = self.bullet_img.get_rect()
            self.info_bar_rect = INFO_PANEL.to_rect()
            pygame.font.init()
            self.font = pygame.font.SysFont('mono', 12)
            self.clock = pygame.time.Clock()

        self.zones = Zones(render=render)
        self.reset()

    def reset(self):
        self.time = MATCH_DURATION
        self.obs = np.zeros((self.car_count, 17), dtype='float32')
        self.compet_info = np.array([[2, 1, 0, 0], [2, 1, 0, 0]], dtype='int16')
        self.bullets = []
        self.epoch = 0
        self.n = 0
        self.dev = False
        self.memory = []
        self.robots = [Robot() for _ in range(self.car_count)]
        self.zones.reset()
        return State(self.time, self.robots, self.compet_info, self.time <= 0)

    def play(self):
        assert self.render, 'play() requires render==True'
        while True:
            if not self.epoch % 10:
                if self.receive_commands():
                    break
            self.one_epoch()

    def step(self, commands):
        for robot, command in zip(self.robots, commands):
            robot.commands = command
        for _ in range(10):
            self.one_epoch()
        return State(self.time, self.robots, self.compet_info, self.time <= 0)

    def one_epoch(self):  # reviewed
        pygame.time.wait(3)
        for robot in self.robots:  # move robots
            if not self.epoch % 10:
                robot.commands_to_actions()
            self.move_robot(robot)

            if not self.epoch % 20:  # todo: apply new heat rules here
                if robot.heat >= 720:
                    robot.hp -= (robot.heat - 720) * 40
                    robot.heat = 720
                elif robot.heat > 360:
                    robot.hp -= (robot.heat - 360) * 4
                robot.heat -= 12 if robot.hp >= 400 else 24
            robot.heat = np.max(robot.heat, 0)
            robot.hp = np.max(robot.hp, 0)
            if not robot.actions[5]:
                robot.actions[4] = 0

        if not self.epoch % 200:
            self.time -= 1
            if not self.time % 60:
                self.compet_info[:, 0:3] = [2, 1, 0]
        # self.stay_check()
        
        i = 0
        while i < len(self.bullets):  # move bullets
            if self.move_bullet(self.bullets[i]):
                del self.bullets[i]
            else:
                i += 1

        # randomize zones every minute
        if self.epoch == ZONE_RESET * 200 or self.epoch == 2 * ZONE_RESET * 200:
            self.zones.reset()

        self.epoch += 1
        if self.record:
            bullets = [Bullet(b.center, b.angle, b.owner_id) for b in self.bullets]
            self.memory.append(Record(self.time, self.robots.copy(), self.compet_info.copy(), bullets))
        if self.render:
            self.update_display()

    def move_robot(self, robot):  # reviewed
        # if robot.status[7]:  # unfreeze robot if frozen
        #     robot.status[7] -= 1
        #     return

        if robot.actions[0]:  # rotate chassis
            old_angle = robot.angle
            robot.angle += robot.actions[0]
            robot.angle = normalize_angle(robot.angle)
            if self.check_interference(robot):
                robot.actions[0] = -robot.actions[0] * COLLISION_COEFFICENT
                robot.angle = old_angle

        if robot.actions[1]:  # rotate gimbal
            robot.gimbal_yaw += robot.actions[1]
            robot.gimbal_yaw = np.clip(robot.gimbal_yaw, -90, 90)

        if robot.actions[2] or robot.actions[3]:  # translate chassis
            angle = np.deg2rad(robot.angle)
            old_x, old_y = robot.center[0], robot.center[1]

            robot.center[0] += robot.actions[2] * np.cos(angle) - robot.actions[3] * np.sin(angle)
            if self.check_interference(robot):
                robot.actions[2] = -robot.actions[2] * COLLISION_COEFFICENT
                robot.center[0] = old_x
            robot.center[1] += robot.actions[2] * np.sin(angle) + robot.actions[3] * np.cos(angle)
            if self.check_interference(robot):
                robot.actions[3] = -robot.actions[3] * COLLISION_COEFFICENT
                robot.center[1] = old_y

        if robot.actions[4] and robot.ammo:  # handle firing
            if robot.can_shoot:
                robot.ammo -= 1
                self.bullets.append(Bullet(robot.center, robot.gimbal_yaw + robot.angle, robot.id_))
                robot.heat += BULLET_SPEED
                robot.can_shoot = 0
            else:
                robot.can_shoot = 1
        else:
            robot.can_shoot = 1

        # if robot.actions[7]:  AUTOAIM IMPLEMENTATION
        #     if self.car_count > 1:
        #         select = np.where((self.vision[n] == 1))[0]
        #         if select.size:
        #             angles = np.zeros(select.size)
        #             for ii, i in enumerate(select):
        #                 x, y = self.robots[i].center - robot.center
        #                 angle = np.angle(x + y * 1j, deg=True) - self.robots[i].angle
        #                 if angle >= 180: angle -= 360
        #                 if angle <= -180: angle += 360
        #                 if -THETA <= angle < THETA:
        #                     armor = self.robots[i].get_armor_center(2)
        #                 elif THETA <= angle < 180 - THETA:
        #                     armor = self.robots[i].get_armor_center(3)
        #                 elif -180 + THETA <= angle < -THETA:
        #                     armor = self.robots[i].get_armor_center(1)
        #                 else:
        #                     armor = self.robots[i].get_armor_center(0)
        #                 x, y = armor - robot.center
        #                 angle = np.angle(x + y * 1j, deg=True) - robot.yaw - robot.angle
        #                 if angle >= 180:
        #                     angle -= 360
        #                 if angle <= -180:
        #                     angle += 360
        #                 angles[ii] = angle
        #             m = np.where(np.abs(angles) == np.abs(angles).min())
        #             robot.yaw += angles[m][0]
        #             robot.yaw = np.clip(robot.yaw, -90, 90)

        # check supply
        # if robot.actions[6]:
        #     dis = np.abs(robot.center - [self.areas[int(robot.team), 1][0:2].mean(), \
        #                                       self.areas[int(robot.team), 1][2:4].mean()]).sum()
        #     if dis < 23 and self.compet_info[int(robot.team), 0] and not robot.status[7]:
        #         robot.status[8] = 1
        #         robot.status[7] = 600  # 3 s
        #         robot.ammo += 50
        #         self.compet_info[int(robot.team), 0] -= 1

        # Check whether the robot n is on top of any zones, and apply the corresponding (de)buff.
        # It currently checks whether the robot is on its teams supply area, the translucent gray rhombuses top
        # and bottom middle of the field.
        self.zones.apply(self.robots)

    def move_bullet(self, bullet):  # reviewed
        old_center = bullet.center.copy()
        bullet.center[0] += BULLET_SPEED * np.cos(np.deg2rad(bullet.angle))
        bullet.center[1] += BULLET_SPEED * np.sin(np.deg2rad(bullet.angle))
        
        if not FIELD.contains(bullet.center, strict=True):
            return True
        if any(b.intersects(old_center, bullet.center) for b in HIGH_BARRIERS):
            return True
        
        for robot in self.robots:
            if robot.id_ == bullet.owner_id:
                continue
            if np.abs(robot.center - bullet.center).sum() < 52.5:
                points = robot.transfer_to_car_coordinate(np.array([bullet.center, old_center]))
                if any([lines_intersect(points[0], points[1], [-18.5, -5], [-18.5, 5]),
                        lines_intersect(points[0], points[1], [18.5, -5], [18.5, 5]),
                        lines_intersect(points[0], points[1], [-5, 30], [5, 30]),
                        lines_intersect(points[0], points[1], [-5, -30], [5, -30])]):
                    if self.compet_info[robot.team.value, 3]:
                        robot.hp -= 25
                    else:
                        robot.hp -= 50
                    return True
                if ROBOT_BLOCK.intersects(points[0], points[1]):
                    return True
        return False

    def update_display(self):  # reviewed
        assert self.render, 'update_display() requires render==True'
        self.screen.fill(COLOR_GRAY)
        for i in range(len(self.area_rects)):
            self.screen.blit(self.area_images[i], self.area_rects[i])
        for i in range(len(self.bullets)):
            self.bullet_rect.center = self.bullets[i].center
            self.screen.blit(self.bullet_img, self.bullet_rect)
        self.zones.draw(self.screen)

        for robot in self.robots:
            chassis_img = self.chassis_red_img if (robot.team == TEAM.red) else self.chassis_blue_img
            chassis_rotate = pygame.transform.rotate(chassis_img, -robot.angle)
            gimbal_rotate = pygame.transform.rotate(self.gimbal_img, -robot.gimbal_yaw - robot.angle)
            chassis_rotate_rect = chassis_rotate.get_rect()
            gimbal_rotate_rect = gimbal_rotate.get_rect()
            chassis_rotate_rect.center = robot.center
            gimbal_rotate_rect.center = robot.center
            self.screen.blit(chassis_rotate, chassis_rotate_rect)
            self.screen.blit(gimbal_rotate, gimbal_rotate_rect)
        for robot in self.robots:
            info = self.font.render(f'{int(robot.hp)}', False, COLOR_RED if (robot.team == TEAM.red) else COLOR_BLUE)
            self.screen.blit(info, robot.center + [-15, -50])
        info = self.font.render(f'time: {self.time}', False, COLOR_BLACK)
        self.screen.blit(info, (FIELD.dimensions[0] / 2 - 29, 3))
        if self.dev:
            self.dev_window()
        pygame.display.flip()

    def dev_window(self):  # reviewed
        for robot in self.robots:
            for point in [*robot.get_wheel_points(), *robot.get_armor_points()]:
                pygame.draw.circle(self.screen, COLOR_BLUE if robot.team == TEAM.blue else COLOR_RED, point.astype(int), 2)

        self.screen.blit(self.info_bar_img, self.info_bar_rect)
        for n, robot in enumerate(self.robots):
            info = self.font.render(f'robot {robot.id_}', False, COLOR_BLUE if robot.team == TEAM.blue else COLOR_RED)
            self.screen.blit(info, (INFO_START[0] + n * INFO_SPACING[0], INFO_START[1]), special_flags=2)
            for i, (label, value) in enumerate(robot.status_dict().items()):
                info = self.font.render(f'{label}: {value:.0f}', False, COLOR_BLACK)
                self.screen.blit(info, (INFO_START[0] + n * INFO_SPACING[0], INFO_START[1] + (i + 1) * INFO_SPACING[1]))

        info = self.font.render(f'red supply: {self.compet_info[0, 0]}  bonus: {self.compet_info[0, 1]}  bonus_time: {self.compet_info[0, 3]}', False, COLOR_BLACK)
        self.screen.blit(info, (INFO_START[0], INFO_START[1] + 16 * INFO_SPACING[1]))
        info = self.font.render(f'blue supply: {self.compet_info[1, 0]}  bonus: {self.compet_info[1, 1]}  bonus_time: {self.compet_info[1, 3]}', False, COLOR_BLACK)
        self.screen.blit(info, (INFO_START[0], INFO_START[1] + 17 * INFO_SPACING[1]))

    def receive_commands(self):  # reviewed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_1]:
            self.n = 0
        if pressed[pygame.K_2]:
            self.n = 1
        if pressed[pygame.K_3]:
            self.n = 2
        if pressed[pygame.K_4]:
            self.n = 3
        robot = self.robots[self.n]
        robot.commands[:] = 0

        if pressed[pygame.K_w]:
            robot.commands[0] += 1
        if pressed[pygame.K_s]:
            robot.commands[0] -= 1
        if pressed[pygame.K_q]:
            robot.commands[1] -= 1
        if pressed[pygame.K_e]:
            robot.commands[1] += 1
        if pressed[pygame.K_a]:
            robot.commands[2] -= 1
        if pressed[pygame.K_d]:
            robot.commands[2] += 1
        if pressed[pygame.K_b]:
            robot.commands[3] -= 1
        if pressed[pygame.K_m]:
            robot.commands[3] += 1

        robot.commands[4] = int(pressed[pygame.K_SPACE])
        robot.commands[5] = int(pressed[pygame.K_f])
        robot.commands[6] = int(pressed[pygame.K_r])
        robot.commands[7] = int(pressed[pygame.K_n])
        self.dev = pressed[pygame.K_TAB]
        return False

    # def stay_check(self):  # todo: apply new area rules here
    #     # check bonus stay
    #     for robot in self.robots:
    #         a = ZONES.keys()[int(robot.team), 0]
    #         if robot.center[0] >= a[0] and robot.center[0] <= a[1] and robot.center[1] >= a[2] \
    #                 and robot.center[1] <= a[3] and self.compet_info[int(robot.team), 1]:
    #             robot.status[11] += 1  # 1/200 s
    #             if robot.status[11] >= 1000:  # 5s
    #                 robot.status[11] = 0
    #                 self.compet_info[int(robot.team), 3] = 6000  # 30s
    #         else:
    #             robot.status[11] = 0
    #     for i in range(2):
    #         if self.compet_info[i, 3] > 0:
    #             self.compet_info[i, 3] -= 1

    def check_interference(self, robot):  # reviewed
        wheels = robot.get_wheel_points()  # check wheel interference with walls/barriers
        if any(not FIELD.contains(w, strict=True) or any(b.contains(w) for b in (*LOW_BARRIERS, *HIGH_BARRIERS)) for w in wheels):
            robot.wheel_hit += 1
            return True
        armors = robot.get_armor_points()  # check armor interference with walls/barriers
        if any(not FIELD.contains(a, strict=True) or any(b.contains(a) for b in (*LOW_BARRIERS, *HIGH_BARRIERS)) for a in armors):
            robot.armor_hit += 1
            robot.hp -= 10
            return True

        for other_robot in self.robots:
            if robot.id_ == other_robot.id_:
                continue
            wheels_trans = other_robot.transfer_to_car_coordinate(wheels)  # check wheel interference with other robots
            if any(ROBOT.contains(w) for w in wheels_trans):
                robot.robot_hit += 1
                return True
            armors_trans = other_robot.transfer_to_car_coordinate(armors)  # check armor interference with other robots
            if any(ROBOT.contains(a) for a in armors_trans):
                robot.robot_hit += 1
                robot.hp -= 10
                return True
        return False

    def save_record(self, file):
        np.save(file, self.memory)

# important indexs
# areas_index = [[{'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 0 bonus red
#                 {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 1 supply red
#                 {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 2 start 0 red
#                 {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}], # 3 start 1 red
#
#                [{'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 0 bonus blue
#                 {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 1 supply blue
#                 {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 2 start 0 blue
#                 {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}]] # 3 start 1 blue
#
#
# barriers_index = [{'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 0 horizontal
#                   {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 1 horizontal
#                   {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 2 horizontal
#                   {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 3 vertical
#                   {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 4 vertical
#                   {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 5 vertical
#                   {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}] # 6 vertical
#
# armor编号：0：前，1：右，2：后，3左，车头为前
#
# act_index = {'rotate_speed': 0, 'yaw_speed': 1, 'x_speed': 2, 'y_speed': 3, 'shoot': 4, 'shoot_mutiple': 5, 'supply': 6,
#              'auto_aim': 7}
#
# bullet_speed: 12.5
#
# compet_info_index = {'red': {'supply': 0, 'bonus': 1, 'bonus_stay_time(deprecated)': 2, 'bonus_time': 3},
#                      'blue': {'supply': 0, 'bonus': 1, 'bonus_stay_time(deprecated)': 2, 'bonus_time': 3}}
# int, shape: (2, 4)
#
# order_index = ['x', 'y', 'rotate', 'yaw', 'shoot', 'supply', 'shoot_mode', 'auto_aim']
# int, shape: (8,)
#     x, -1: back, 0: no, 1: head
#     y, -1: left, 0: no, 1: right
#     rotate, -1: anti-clockwise, 0: no, 1: clockwise, for chassis
#     shoot_mode, 0: single, 1: mutiple
#     shoot, 0: not shoot, 1: shoot
#     yaw, -1: anti-clockwise, 0: no, 1: clockwise, for gimbal
#     auto_aim, 0: not, 1: auto aim
#
# car_index = {"team": 0, 'x': 1, 'y': 2, "angle": 3, "yaw": 4, "heat": 5, "hp": 6,
#              "freeze_time": 7, "is_supply": 8, "can_shoot": 9, 'bullet': 10, 'stay_time': 11,
#              'wheel_hit': 12, 'armor_hit': 13, 'car_hit': 14}
# float, shape: (14,)
