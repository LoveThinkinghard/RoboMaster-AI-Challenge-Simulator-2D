import numpy as np
from objects import *
from globals import *
from robot import Robot
import pygame


class Kernel(object):
    def __init__(self, robot_count, render=False, record=True):
        self.car_count = robot_count
        self.render = render
        self.record = record
        self.time, self.obs, self.compet_info, self.bullets, self.epoch, self.n, self.dev, self.memory, self.robots = None, None, None, None, None, None, None, None, None
        self.reset()

        if render:
            pygame.init()
            self.screen = pygame.display.set_mode(FIELD_DIMENSIONS)
            pygame.display.set_caption('RM AI Challenge Simulator')

            self.area_images = []
            self.area_rects = []
            for area, image_file in {**LOW_BARRIERS, **HIGH_BARRIERS, **SPAWNS, **ZONES}.items():
                self.area_images.append(pygame.image.load(f'elements/{image_file}.png'))
                self.area_rects.append(rect_to_pygame(area))

            self.chassis_blue_img = pygame.image.load('elements/chassis_blue.png')
            self.chassis_red_img = pygame.image.load('elements/chassis_red.png')
            self.gimbal_img = pygame.image.load('elements/gimbal.png')
            self.bullet_img = pygame.image.load('elements/bullet.png')
            self.info_bar_img = pygame.image.load('elements/info_panel.png')
            self.bullet_rect = self.bullet_img.get_rect()
            self.info_bar_rect = rect_to_pygame(INFO_PANEL)
            pygame.font.init()
            self.font = pygame.font.SysFont('mono', 12)
            self.clock = pygame.time.Clock()

    def reset(self):
        self.time = MATCH_DURATION
        self.obs = np.zeros((self.car_count, 17), dtype='float32')
        self.compet_info = np.array([[2, 1, 0, 0], [2, 1, 0, 0]], dtype='int16')
        self.bullets = []
        self.epoch = 0
        self.n = 0
        self.dev = False
        self.memory = []
        self.robots = [Robot(0, TEAM_BLUE, SPAWN_HLENGTH, SPAWN_HLENGTH),
                       Robot(2, TEAM_BLUE, SPAWN_HLENGTH, FIELD_DIMENSIONS[1] - SPAWN_HLENGTH),
                       Robot(3, TEAM_RED, FIELD_DIMENSIONS[0] - SPAWN_HLENGTH, SPAWN_HLENGTH),
                       Robot(1, TEAM_RED, FIELD_DIMENSIONS[0] - SPAWN_HLENGTH, FIELD_DIMENSIONS[1] - SPAWN_HLENGTH)][:self.car_count]
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
        for robot in self.robots:  # move robots
            if not self.epoch % 10:
                robot.commands_to_actions()
            self.move_robot(robot)

            if not self.epoch % 20:  # todo: apply new heat rules here
                if robot.status[5] >= 720:
                    robot.status[6] -= (robot.status[5] - 720) * 40
                    robot.status[5] = 720
                elif robot.status[5] > 360:
                    robot.status[6] -= (robot.status[5] - 360) * 4
                robot.status[5] -= 12 if robot.status[6] >= 400 else 24
            robot.status[5] = np.max(robot.status[5], 0)
            robot.status[6] = np.max(robot.status[6], 0)
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

        self.epoch += 1
        if self.record:
            bullets = [Bullet(b.center, b.angle, b.team) for b in self.bullets]
            self.memory.append(Record(self.time, self.robots.copy(), self.compet_info.copy(), bullets))
        if self.render:
            self.update_display()

    def move_robot(self, robot):  # reviewed
        if robot.status[7]:  # unfreeze robot if frozen
            robot.status[7] -= 1
            return

        if robot.actions[0]:  # rotate chassis
            old_angle = robot.status[3]
            robot.status[3] += robot.actions[0]
            robot.status[3] = normalize_angle(robot.status[3])
            if self.check_interference(robot):
                robot.actions[0] = -robot.actions[0] * COLLISION_COEFFICENT
                robot.status[3] = old_angle

        if robot.actions[1]:  # rotate gimbal
            robot.status[4] += robot.actions[1]
            robot.status[4] = np.clip(robot.status[4], -90, 90)

        if robot.actions[2] or robot.actions[3]:  # translate chassis
            angle = np.deg2rad(robot.status[3])
            old_x, old_y = robot.status[1], robot.status[2]

            robot.status[1] += robot.actions[2] * np.cos(angle) - robot.actions[3] * np.sin(angle)
            if self.check_interference(robot):
                robot.actions[2] = -robot.actions[2] * COLLISION_COEFFICENT
                robot.status[1] = old_x
            robot.status[2] += robot.actions[2] * np.sin(angle) + robot.actions[3] * np.cos(angle)
            if self.check_interference(robot):
                robot.actions[3] = -robot.actions[3] * COLLISION_COEFFICENT
                robot.status[2] = old_y

        if robot.actions[4] and robot.status[10]:  # handle firing
            if robot.status[9]:
                robot.status[10] -= 1
                self.bullets.append(Bullet(robot.status[1:3], robot.status[4] + robot.status[3], robot.team))
                robot.status[5] += BULLET_SPEED
                robot.status[9] = 0
            else:
                robot.status[9] = 1
        else:
            robot.status[9] = 1

        # if robot.actions[7]:  AUTOAIM IMPLEMENTATION
        #     if self.car_count > 1:
        #         select = np.where((self.vision[n] == 1))[0]
        #         if select.size:
        #             angles = np.zeros(select.size)
        #             for ii, i in enumerate(select):
        #                 x, y = self.robots[i].status[1:3] - robot.status[1:3]
        #                 angle = np.angle(x + y * 1j, deg=True) - self.robots[i].status[3]
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
        #                 x, y = armor - robot.status[1:3]
        #                 angle = np.angle(x + y * 1j, deg=True) - robot.status[4] - robot.status[3]
        #                 if angle >= 180:
        #                     angle -= 360
        #                 if angle <= -180:
        #                     angle += 360
        #                 angles[ii] = angle
        #             m = np.where(np.abs(angles) == np.abs(angles).min())
        #             robot.status[4] += angles[m][0]
        #             robot.status[4] = np.clip(robot.status[4], -90, 90)

        # check supply
        # if robot.actions[6]:
        #     dis = np.abs(robot.status[1:3] - [self.areas[int(robot.team), 1][0:2].mean(), \
        #                                       self.areas[int(robot.team), 1][2:4].mean()]).sum()
        #     if dis < 23 and self.compet_info[int(robot.team), 0] and not robot.status[7]:
        #         robot.status[8] = 1
        #         robot.status[7] = 600  # 3 s
        #         robot.status[10] += 50
        #         self.compet_info[int(robot.team), 0] -= 1

    def move_bullet(self, bullet):  # reviewed
        old_center = bullet.center.copy()
        bullet.center[0] += BULLET_SPEED * np.cos(np.deg2rad(bullet.angle))
        bullet.center[1] += BULLET_SPEED * np.sin(np.deg2rad(bullet.angle))
        
        if not point_inside_rect(bullet.center, FIELD_DIMENSIONS):
            return True
        if any([line_intersects_rects(old_center, bullet.center, b) for b in HIGH_BARRIERS]):
            return True
        
        for robot in self.robots:
            if robot.team == bullet.team:
                continue
            if np.abs(robot.status[1:3] - bullet.center).sum() < 52.5:
                points = robot.transfer_to_car_coordinate(np.array([bullet.center, old_center]))
                if any([lines_intersect(points[0], points[1], [-18.5, -5], [-18.5, 6]),
                        lines_intersect(points[0], points[1], [18.5, -5], [18.5, 6]),
                        lines_intersect(points[0], points[1], [-5, 30], [5, 30]),
                        lines_intersect(points[0], points[1], [-5, -30], [5, -30])]):
                    if self.compet_info[int(robot.team), 3]:
                        robot.status[6] -= 25
                    else:
                        robot.status[6] -= 50
                    return True
                if line_intersects_rect(points[0], points[1], [-18, -29, 18, 29]):
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
        for robot in self.robots:
            chassis_img = self.chassis_red_img if (robot.team == TEAM_RED) else self.chassis_blue_img
            chassis_rotate = pygame.transform.rotate(chassis_img, -robot.status[3] - 90)
            gimbal_rotate = pygame.transform.rotate(self.gimbal_img, -robot.status[4] - robot.status[3] - 90)
            chassis_rotate_rect = chassis_rotate.get_rect()
            gimbal_rotate_rect = gimbal_rotate.get_rect()
            chassis_rotate_rect.center = robot.status[1:3]
            gimbal_rotate_rect.center = robot.status[1:3]
            self.screen.blit(chassis_rotate, chassis_rotate_rect)
            self.screen.blit(gimbal_rotate, gimbal_rotate_rect)
        for robot in self.robots:
            info = self.font.render(f'{int(robot.status[6])}', False, COLOR_RED if (robot.team == TEAM_RED) else COLOR_BLUE)
            self.screen.blit(info, robot.status[1:3] + [-15, -50])
        info = self.font.render(f'time: {self.time}', False, COLOR_BLACK)
        self.screen.blit(info, (FIELD_DIMENSIONS[0] / 2 - 29, 3))
        if self.dev:
            self.dev_window()
        pygame.display.flip()

    def dev_window(self):  # reviewed
        for robot in self.robots:
            for point in [*robot.get_wheel_points(), *robot.get_armor_points()]:
                pygame.draw.circle(self.screen, robot.color, point.astype(int), 3)

        self.screen.blit(self.info_bar_img, self.info_bar_rect)
        for n, robot in enumerate(self.robots):
            info = self.font.render(f'robot {robot.id_}', False, robot.color)
            self.screen.blit(info, (INFO_START[0] + n * INFO_SPACING[0], INFO_START[1]), special_flags=2)
            tags = ['team', 'x', 'y', 'angle', 'yaw', 'heat', 'hp', 'freeze_time', 'is_supply',
                    'can_shoot', 'bullet', 'stay_time', 'wheel_hit', 'armor_hit', 'car_hit']
            for i, data in enumerate(robot.status):
                info = self.font.render(f'{tags[i]}: {int(data)}', False, COLOR_BLACK)
                self.screen.blit(info, (INFO_START[0] + n * INFO_SPACING[0], INFO_START[1] + (i + 1) * INFO_SPACING[1]))

        info = self.font.render(f'red supply: {self.compet_info[0, 0]}\tbonus: {self.compet_info[0, 1]}\tbonus_time: {self.compet_info[0, 3]}', False, COLOR_BLACK)
        self.screen.blit(info, (INFO_START[0], INFO_START[1] + 16 * INFO_SPACING[1]))
        info = self.font.render(f'blue supply: {self.compet_info[1, 0]}\tbonus: {self.compet_info[1, 1]}\tbonus_time: {self.compet_info[1, 3]}', False, COLOR_BLACK)
        self.screen.blit(info, (INFO_START[0], INFO_START[1] + 17 * INFO_SPACING[1]))

    def receive_commands(self):  # reviewed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_1]: self.n = 0
        if pressed[pygame.K_2]: self.n = 1
        if pressed[pygame.K_3]: self.n = 2
        if pressed[pygame.K_4]: self.n = 3
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

    # def stay_check(self):  # todo: apply new zone rules here
    #     # check bonus stay
    #     for robot in self.robots:
    #         a = ZONES.keys()[int(robot.team), 0]
    #         if robot.status[1] >= a[0] and robot.status[1] <= a[1] and robot.status[2] >= a[2] \
    #                 and robot.status[2] <= a[3] and self.compet_info[int(robot.team), 1]:
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
        if any(not point_inside_rect(w, FIELD) or any([point_inside_rect(w, b, check_on=True) for b in BARRIERS]) for w in wheels):
            robot.status[12] += 1
            return True
        armors = robot.get_armor_points()  # check armor interference with walls/barriers
        if any(not point_inside_rect(a, FIELD) or any([point_inside_rect(a, b, check_on=True) for b in BARRIERS]) for a in armors):
            robot.status[13] += 1
            robot.status[6] -= 10
            return True

        for other_robot in self.robots:
            if robot.id_ == other_robot.id_:
                continue
            wheels = other_robot.transfer_to_car_coordinate(wheels)  # check wheel interference with other robots
            if any(point_inside_rect(w, ROBOT, check_on=True) for w in wheels):
                robot.status[14] += 1
                return True
            armors = other_robot.transfer_to_car_coordinate(armors)  # check armor interference with other robots
            if any(point_inside_rect(a, ROBOT, check_on=True) for a in armors):
                robot.status[14] += 1
                robot.status[6] -= 10
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
