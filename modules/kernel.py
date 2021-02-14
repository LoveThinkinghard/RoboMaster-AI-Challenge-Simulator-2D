import pygame
import numpy as np
import time
from modules.objects import *
from modules.bullet import Bullet
from modules.robot import Robot
from modules.zones import Zones
from modules.geometry import distance, Line, Rectangle
from modules.constants import *

C1 = Rectangle(100, 100, -354, -174, image='images/area/blue.png')
C3 = Rectangle(100, 100, 354, 174, image='images/area/red.png')
B5 = Rectangle(35.4, 35.4, 0, 0, image='images/area/lcm.png')
B2 = Rectangle(80, 20, -214, 0, image='images/area/lhm.png')
B1 = Rectangle(100, 20, -354, -114, image='images/area/hhu.png')
B3 = Rectangle(20, 100, -244, 174, image='images/area/hvu.png')
B4 = Rectangle(100, 20, 0, -120.5, image='images/area/hhm.png')

field = Rectangle(*FIELD.dims)
stats_panel = Rectangle(520, 340, image=IMAGE.stats_panel)
spawn_rects = [C1, C1.mirrored(flip_x=False), C3, C3.mirrored(flip_x=False)]  # areas C1-4
low_barriers = [B2, B2.mirrored(), B5]  # areas B2, B5, B8
high_barriers = [B1, B3, B4, B4.mirrored(), B3.mirrored(), B1.mirrored()]  # areas B1, B3, B4, B6, B7, B9


def normalize_angle(angle):
    if angle > 180:
        angle -= 360
    if angle <= -180:
        angle += 360
    return angle


class Kernel(object):
    def __init__(self, robot_count, render=False, record=True):
        self.car_count = robot_count
        self.render = render
        self.record = record
        self.time, self.obs, self.compet_info, self.bullets, self.epoch, self.n, self.stat, self.memory, self.robots = None, None, None, None, None, None, None, None, None
        self.zones = Zones()
        self.reset()

        if render:
            pygame.init()
            self.screen = pygame.display.set_mode(FIELD.dims)
            pygame.display.set_caption('UBC RoboMaster AI Challenge Simulator')
            pygame.display.set_icon(pygame.image.load(IMAGE.logo))
            pygame.font.init()
            self.font = pygame.font.SysFont('mono', 12)
            self.clock = pygame.time.Clock()

    def reset(self):
        self.time = FIELD.match_duration
        self.obs = np.zeros((self.car_count, 17), dtype=np.float32)
        self.bullets = []
        self.epoch = 0
        self.n = 0
        self.stat = False
        self.memory = []
        self.robots = [Robot() for _ in range(self.car_count)]
        self.zones.reset()
        return State(self.time, self.robots)

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
        return State(self.time, self.robots)

    def one_epoch(self):
        pygame.time.wait(2)
        for robot in self.robots:  # update robots
            if robot.hp == 0:
                continue
            if not self.epoch % 10:
                robot.commands_to_actions()
            self.zones.apply(self.robots)
            self.move_robot(robot)

            if not self.epoch % 200 and robot.timeout > 0:
                robot.timeout -= 1

            if not self.epoch % 20:  # Barrel Heat (Rules 4.1.2)
                if robot.heat >= 360:
                    robot.hp -= (robot.heat - 360) * 40
                    robot.heat = 360
                elif robot.heat > 240:
                    robot.hp -= (robot.heat - 240) * 4
                robot.heat -= 12 if robot.hp >= 400 else 24
            robot.heat = max(robot.heat, 0)
            robot.hp = max(robot.hp, 0)

        if not self.epoch % 200:
            self.time -= 1
        if not self.epoch % 12000:
            self.zones.reset()
        
        i = 0
        while i < len(self.bullets):  # update bullets
            if self.move_bullet(self.bullets[i]):
                del self.bullets[i]
            else:
                i += 1

        self.epoch += 1
        if self.record:
            bullets = [Bullet(b.center, b.angle, b.owner_id) for b in self.bullets]
            self.memory.append(Record(self.time, self.robots.copy(), bullets))
        if self.render:
            self.draw()

    def move_robot(self, robot: Robot):
        if not robot.can_shoot and robot.timeout == 0:
            robot.can_shoot = True
        if not robot.can_move and robot.timeout == 0:
            robot.can_move = True

        if robot.actions[0] and robot.can_move:  # rotate chassis
            old_angle = robot.angle
            robot.angle += robot.actions[0]
            robot.angle = normalize_angle(robot.angle)
            if self.check_interference(robot):
                robot.actions[0] = -robot.actions[0] * ROBOT.rebound_coeff
                robot.angle = old_angle

        if robot.actions[1]:  # rotate gimbal
            robot.yaw += robot.actions[1]
            robot.yaw = np.clip(robot.yaw, -90, 90)

        if (robot.actions[2] or robot.actions[3]) and robot.can_move:  # translate chassis
            angle = np.deg2rad(robot.angle)
            old_x, old_y = robot.center[0], robot.center[1]

            robot.center[0] += robot.actions[2] * np.cos(angle) - robot.actions[3] * np.sin(angle)
            if self.check_interference(robot):
                robot.actions[2] = -robot.actions[2] * ROBOT.rebound_coeff
                robot.center[0] = old_x
            robot.center[1] += robot.actions[2] * np.sin(angle) + robot.actions[3] * np.cos(angle)
            if self.check_interference(robot):
                robot.actions[3] = -robot.actions[3] * ROBOT.rebound_coeff
                robot.center[1] = old_y

        if robot.actions[4] and robot.ammo and robot.can_shoot:  # handle firing
            robot.ammo -= 1
            self.bullets.append(Bullet(robot.center, robot.yaw + robot.angle, robot.id_))
            robot.heat += ROBOT.bullet_speed

    def move_bullet(self, bullet: Bullet):
        old_center = bullet.center.copy()
        bullet.step()
        trajectory = Line(old_center, bullet.center)
        
        if not field.contains(bullet.center, strict=True):
            return True
        if any(b.intersects(trajectory) for b in high_barriers):
            return True
        
        for robot in self.robots:
            if robot.id_ == bullet.owner_id:
                continue
            if robot.hits_armor(trajectory):
                return True
        return False

    def draw(self):
        assert self.render, 'draw() requires render==True'
        self.screen.fill(COLOR.gray)
        self.zones.draw(self.screen)
        for rect in [*spawn_rects, *low_barriers, *high_barriers]:
            rect.draw(self.screen)
        for robot in self.robots:
            robot.draw(self.screen, self.font, stat=self.stat)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        time_label = self.font.render(f'time: {self.time}', False, COLOR.black)
        self.screen.blit(time_label, TEXT.time_position)

        if self.stat:
            stats_panel.draw(self.screen)
            for n, robot in enumerate(self.robots):
                x_position = TEXT.stat_position[0] + n * TEXT.stat_increment[0]
                header = self.font.render(f'robot {robot.id_}', False, COLOR.blue if robot.is_blue else COLOR.red)
                self.screen.blit(header, (x_position, TEXT.stat_position[1]))
                for i, (label, value) in enumerate(robot.status_dict().items()):
                    data = self.font.render(f'{label}: {value:.0f}', False, COLOR.black)
                    self.screen.blit(data, (x_position, TEXT.stat_position[1] + (i + 1) * TEXT.stat_increment[1]))
        pygame.display.flip()

    def receive_commands(self):
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

        if pressed[pygame.K_w]: robot.commands[0] += 1
        if pressed[pygame.K_s]: robot.commands[0] -= 1
        if pressed[pygame.K_q]: robot.commands[1] -= 1
        if pressed[pygame.K_e]: robot.commands[1] += 1
        if pressed[pygame.K_a]: robot.commands[2] -= 1
        if pressed[pygame.K_d]: robot.commands[2] += 1
        if pressed[pygame.K_b]: robot.commands[3] -= 1
        if pressed[pygame.K_m]: robot.commands[3] += 1

        robot.commands[4] = int(pressed[pygame.K_SPACE])
        self.stat = pressed[pygame.K_TAB]
        return False

    def check_interference(self, robot: Robot):
        if robot.collides_chassis(field):
            return True
        for barrier in [*low_barriers, *high_barriers]:
            if distance(robot.center, barrier.center) < ROBOT.size + BARRIER.size and \
                    (robot.collides_chassis(barrier) or robot.collides_armor(barrier)):
                return True
        for other_robot in self.robots:
            if other_robot.id_ == robot.id_:
                continue
            if distance(robot.center, other_robot.center) < 2 * ROBOT.size:
                robot.robot_hits += 1
                return True
        return False

    def save_record(self, file):
        np.save(file, self.memory)
