import numpy as np
from objects import *
from globals import *


class kernal(object):
    def __init__(self, car_num, render=False, record=True):
        self.car_num = car_num
        self.render = render
        self.record = record

        self.areas = np.array([[[580.0, 680.0, 275.0, 375.0],
                                [350.0, 450.0, 0.0, 100.0],
                                [700.0, 800.0, 400.0, 500.0],
                                [0.0, 100.0, 400.0, 500.0]],
                               [[120.0, 220.0, 125.0, 225.0],
                                [350.0, 450.0, 400.0, 500.0],
                                [0.0, 100.0, 0.0, 100.0],
                                [700.0, 800.0, 0.0, 100.0]]], dtype='float32')
        # TODO - these are flipped over horizontal axis
        self.barriers = np.array([[0.0, 100.0, 328.0, 348.0],
                                [354.0, 454.0, 93.5, 113.5],
                                [354.0, 454.0, 334.5, 354.5],
                                [708.0, 808.0, 100.0, 120.0],
                                [150.0, 230.0, 214.0, 234.0],
                                [368.6, 439.4, 188.6, 259.4],
                                [578.0, 658.0, 214.0, 234.0],
                                [150.0, 170.0, 0.0, 100.0],
                                [638.0, 658.0, 348.0, 448.0]], dtype='float32')

        if render:
            global pygame
            import pygame
            pygame.init()
            self.screen = pygame.display.set_mode(FIELD_DIMENSIONS)
            pygame.display.set_caption('RM AI Challenge Simulator')

            self.barrier_imgs = []
            self.barrier_rects = []
            for barrier, image_file in {**LOW_BARRIERS, **HIGH_BARRIERS, **SPAWNS, **ZONES}.items():
                self.barrier_imgs.append(pygame.image.load(f'./elements/{image_file}.png'))
                self.barrier_rects.append(pygame.Rect(barrier))

            # load areas imgs
            self.areas_img = []
            self.areas_rect = []
            # for oi, o in enumerate(['red', 'blue']):
            #     for ti, t in enumerate(['bonus', 'supply', 'start', 'start']):
            #         self.areas_img.append(pygame.image.load('./imgs/area_{}_{}.png'.format(t, o)))
            #         self.areas_rect.append(self.areas_img[-1].get_rect())
            #         self.areas_rect[-1].center = [self.areas[oi, ti][0:2].mean(), self.areas[oi, ti][2:4].mean()]
            # load supply head imgs
            self.head_img = [pygame.image.load('./imgs/area_head_{}.png'.format(i)) for i in ['red', 'blue']]
            self.head_rect = [self.head_img[i].get_rect() for i in range(len(self.head_img))]
            self.head_rect[0].center = [self.areas[0, 1][0:2].mean(), self.areas[0, 1][2:4].mean()]
            self.head_rect[1].center = [self.areas[1, 1][0:2].mean(), self.areas[1, 1][2:4].mean()]
            self.chassis_img = pygame.image.load('./imgs/chassis_g.png')
            self.gimbal_img = pygame.image.load('./imgs/gimbal_g.png')
            self.bullet_img = pygame.image.load('./imgs/bullet_s.png')
            self.info_bar_img = pygame.image.load('./imgs/info_bar.png')
            self.bullet_rect = self.bullet_img.get_rect()
            self.info_bar_rect = self.info_bar_img.get_rect()
            self.info_bar_rect.center = [200, FIELD_DIMENSIONS[1]/2]
            pygame.font.init()
            self.font = pygame.font.SysFont('info', 20)
            self.clock = pygame.time.Clock()

    def reset(self):
        self.time = 180
        self.orders = np.zeros((4, 8), dtype='int8')
        self.acts = np.zeros((self.car_num, 8),dtype='float32')
        self.obs = np.zeros((self.car_num, 17), dtype='float32')
        self.compet_info = np.array([[2, 1, 0, 0], [2, 1, 0, 0]], dtype='int16')
        self.vision = np.zeros((self.car_num, self.car_num), dtype='int8')
        self.detect = np.zeros((self.car_num, self.car_num), dtype='int8')
        self.bullets = []
        self.epoch = 0
        self.n = 0
        self.dev = False
        self.memory = []
        cars = np.array([[1, 50, 50, 0, 0, 0, 2000, 0, 0, 1, 0, 0, 0, 0, 0],
                         [0, 50, 450, 0, 0, 0, 2000, 0, 0, 1, 0, 0, 0, 0, 0],
                         [1, 750, 50, 0, 0, 0, 2000, 0, 0, 1, 0, 0, 0, 0, 0],
                         [0, 750, 450, 0, 0, 0, 2000, 0, 0, 1, 0, 0, 0, 0, 0]], dtype='float32')
        self.cars = cars[0:self.car_num]
        return state(self.time, self.cars, self.compet_info, self.time <= 0)

    def play(self):
        # human play mode, only when render == True
        assert self.render, 'human play mode, only when render == True'
        while True:
            if not self.epoch % 10:
                if self.get_order():
                    break
            self.one_epoch()

    def step(self, orders):
        self.orders[0:self.car_num] = orders
        self.orders = orders
        for _ in range(10):
            self.one_epoch()
        return state(self.time, self.cars, self.compet_info, self.time <= 0, self.detect, self.vision)

    def one_epoch(self):
        for n in range(self.car_num):
            if not self.epoch % 10:
                self.orders_to_acts(n)
            # move car one by one
            self.move_car(n)
            if not self.epoch % 20:
                if self.cars[n, 5] >= 720:
                    self.cars[n, 6] -= (self.cars[n, 5] - 720) * 40
                    self.cars[n, 5] = 720
                elif self.cars[n, 5] > 360:
                    self.cars[n, 6] -= (self.cars[n, 5] - 360) * 4
                self.cars[n, 5] -= 12 if self.cars[n, 6] >= 400 else 24
            if self.cars[n, 5] <= 0: self.cars[n, 5] = 0
            if self.cars[n, 6] <= 0: self.cars[n, 6] = 0
            if not self.acts[n, 5]: self.acts[n, 4] = 0
        if not self.epoch % 200:
                self.time -= 1
                if not self.time % 60:
                    self.compet_info[:, 0:3] = [2, 1, 0]
        self.get_camera_vision()
        self.get_lidar_vision()
        self.stay_check()
        # move bullet one by one
        i = 0
        while len(self.bullets):
            if self.move_bullet(i):
                del self.bullets[i]
                i -= 1
            i += 1
            if i >= len(self.bullets): break
        self.epoch += 1
        bullets = []
        for i in range(len(self.bullets)):
            bullets.append(bullet(self.bullets[i].center, self.bullets[i].angle, self.bullets[i].speed, self.bullets[i].owner))
        if self.record: self.memory.append(record(self.time, self.cars.copy(), self.compet_info.copy(), self.detect.copy(), self.vision.copy(), bullets))
        if self.render: self.update_display()

    def move_car(self, n):
        if not self.cars[n, 7]:
            # move chassis
            if self.acts[n, 0]:
                p = self.cars[n, 3]
                self.cars[n, 3] += self.acts[n, 0]
                if self.cars[n, 3] > 180: self.cars[n, 3] -= 360
                if self.cars[n, 3] < -180: self.cars[n, 3] += 360
                if self.check_interface(n):
                    self.acts[n, 0] = -self.acts[n, 0] * MOVE_DISCOUNT
                    self.cars[n, 3] = p
            # move gimbal
            if self.acts[n, 1]:
                self.cars[n, 4] += self.acts[n, 1]
                if self.cars[n, 4] > 90: self.cars[n, 4] = 90
                if self.cars[n, 4] < -90: self.cars[n, 4] = -90
            # print(self.acts[n, 7])
            if self.acts[n, 7]:
                if self.car_num > 1:
                    select = np.where((self.vision[n] == 1))[0]
                    if select.size:
                        angles = np.zeros(select.size)
                        for ii, i in enumerate(select):
                            x, y = self.cars[i, 1:3] - self.cars[n, 1:3]
                            angle = np.angle(x+y*1j, deg=True) - self.cars[i, 3]
                            if angle >= 180: angle -= 360
                            if angle <= -180: angle += 360
                            if angle >= -THETA and angle < THETA:
                                armor = self.get_armor(self.cars[i], 2)
                            elif angle >= THETA and angle < 180-THETA:
                                armor = self.get_armor(self.cars[i], 3)
                            elif angle >= -180+THETA and angle < -THETA:
                                armor = self.get_armor(self.cars[i], 1)
                            else: armor = self.get_armor(self.cars[i], 0)
                            x, y = armor - self.cars[n, 1:3]
                            angle = np.angle(x+y*1j, deg=True) - self.cars[n, 4] - self.cars[n, 3]
                            if angle >= 180: angle -= 360
                            if angle <= -180: angle += 360
                            angles[ii] = angle
                        m = np.where(np.abs(angles) == np.abs(angles).min())
                        self.cars[n, 4] += angles[m][0]
                        if self.cars[n, 4] > 90: self.cars[n, 4] = 90
                        if self.cars[n, 4] < -90: self.cars[n, 4] = -90
            # move x and y
            if self.acts[n, 2] or self.acts[n, 3]:
                angle = np.deg2rad(self.cars[n, 3])
                # x
                p = self.cars[n, 1]
                self.cars[n, 1] += (self.acts[n, 2]) * np.cos(angle) - (self.acts[n, 3]) * np.sin(angle)
                if self.check_interface(n):
                    self.acts[n, 2] = -self.acts[n, 2] * MOVE_DISCOUNT
                    self.cars[n, 1] = p
                # y
                p = self.cars[n, 2]
                self.cars[n, 2] += (self.acts[n, 2]) * np.sin(angle) + (self.acts[n, 3]) * np.cos(angle)
                if self.check_interface(n):
                    self.acts[n, 3] = -self.acts[n, 3] * MOVE_DISCOUNT
                    self.cars[n, 2] = p
            # fire or not
            if self.acts[n, 4] and self.cars[n, 10]:
                if self.cars[n, 9]:
                    self.cars[n, 10] -= 1
                    self.bullets.append(bullet(self.cars[n, 1:3], self.cars[n, 4] + self.cars[n, 3], BULLET_SPEED, n))
                    self.cars[n, 5] += BULLET_SPEED
                    self.cars[n, 9] = 0
                else:
                    self.cars[n, 9] = 1
            else:
                self.cars[n, 9] = 1
        elif self.cars[n, 7] < 0: assert False
        else:
            self.cars[n, 7] -= 1
            if self.cars[n, 7] == 0:
                self.cars[n, 8] == 0
        # check supply
        if self.acts[n, 6]:
            dis = np.abs(self.cars[n, 1:3] - [self.areas[int(self.cars[n, 0]), 1][0:2].mean(), \
                                   self.areas[int(self.cars[n, 0]), 1][2:4].mean()]).sum()
            if dis < 23 and self.compet_info[int(self.cars[n, 0]), 0] and not self.cars[n, 7]:
                self.cars[n, 8] = 1
                self.cars[n, 7] = 600 # 3 s
                self.cars[n, 10] += 50
                self.compet_info[int(self.cars[n, 0]), 0] -= 1

    def move_bullet(self, n):
        '''
        move bullet No.n, if interface with wall, barriers or cars, return True, else False
        if interface with cars, cars'hp will decrease
        '''
        old_point = self.bullets[n].center.copy()
        self.bullets[n].center[0] += self.bullets[n].speed * np.cos(np.deg2rad(self.bullets[n].angle))
        self.bullets[n].center[1] += self.bullets[n].speed * np.sin(np.deg2rad(self.bullets[n].angle))
        # bullet wall check
        if self.bullets[n].center[0] <= 0 or self.bullets[n].center[0] >= FIELD_DIMENSIONS[0] \
            or self.bullets[n].center[1] <= 0 or self.bullets[n].center[1] >= FIELD_DIMENSIONS[1]: return True
        # bullet barrier check
        for b in self.barriers:
            if self.line_barriers_check(self.bullets[n].center, old_point): return True
        # bullet armor check
        for i in range(len(self.cars)):
            if i == self.bullets[n].owner: continue
            if np.abs(np.array(self.bullets[n].center) - np.array(self.cars[i, 1:3])).sum() < 52.5:
                points = self.transfer_to_car_coordinate(np.array([self.bullets[n].center, old_point]), i)
                if self.segment(points[0], points[1], [-18.5, -5], [-18.5, 6]) \
                or self.segment(points[0], points[1], [18.5, -5], [18.5, 6]) \
                or self.segment(points[0], points[1], [-5, 30], [5, 30]) \
                or self.segment(points[0], points[1], [-5, -30], [5, -30]):
                    if self.compet_info[int(self.cars[i, 0]), 3]: self.cars[i, 6] -= 25
                    else: self.cars[i, 6] -= 50
                    return True
                if self.line_rect_check(points[0], points[1], [-18, -29, 18, 29]): return True
        return False

    def update_display(self):
        assert self.render, 'only render mode need update_display'
        self.screen.fill(GRAY)
        for i in range(len(self.barrier_rects)):
            self.screen.blit(self.barrier_imgs[i], self.barrier_rects[i])
        for i in range(len(self.areas_rect)):
            self.screen.blit(self.areas_img[i], self.areas_rect[i]) 
        for i in range(len(self.bullets)):
            self.bullet_rect.center = self.bullets[i].center
            self.screen.blit(self.bullet_img, self.bullet_rect)
        for n in range(self.car_num):
            chassis_rotate = pygame.transform.rotate(self.chassis_img, -self.cars[n, 3]-90)
            gimbal_rotate = pygame.transform.rotate(self.gimbal_img, -self.cars[n, 4]-self.cars[n, 3]-90)
            chassis_rotate_rect = chassis_rotate.get_rect()
            gimbal_rotate_rect = gimbal_rotate.get_rect()
            chassis_rotate_rect.center = self.cars[n, 1:3]
            gimbal_rotate_rect.center = self.cars[n, 1:3]
            self.screen.blit(chassis_rotate, chassis_rotate_rect)
            self.screen.blit(gimbal_rotate, gimbal_rotate_rect)
        self.screen.blit(self.head_img[0], self.head_rect[0])
        self.screen.blit(self.head_img[1], self.head_rect[1])
        for n in range(self.car_num):
            select = np.where((self.vision[n] == 1))[0]+1
            select2 = np.where((self.detect[n] == 1))[0]+1
            info = self.font.render('{} | {}: {} {}'.format(int(self.cars[n, 6]), n+1, select, select2), True, BLUE if self.cars[n, 0] else RED)
            self.screen.blit(info, self.cars[n, 1:3]+[-20, -60])
            info = self.font.render('{} {}'.format(int(self.cars[n, 10]), int(self.cars[n, 5])), True, BLUE if self.cars[n, 0] else RED)
            self.screen.blit(info, self.cars[n, 1:3]+[-20, -45])
        info = self.font.render('time: {}'.format(self.time), False, (0, 0, 0))
        self.screen.blit(info, (8, 8))
        if self.dev: self.dev_window()
        pygame.display.flip()

    def dev_window(self):
        for n in range(self.car_num):
            wheels = self.check_points_wheel(self.cars[n])
            for w in wheels:
                pygame.draw.circle(self.screen, BLUE if self.cars[n, 0] else RED, w.astype(int), 3)
            armors = self.check_points_armor(self.cars[n])
            for a in armors:
                pygame.draw.circle(self.screen, BLUE if self.cars[n, 0] else RED, a.astype(int), 3)
        self.screen.blit(self.info_bar_img, self.info_bar_rect)
        for n in range(self.car_num):
            tags = ['owner', 'x', 'y', 'angle', 'yaw', 'heat', 'hp', 'freeze_time', 'is_supply', 
                    'can_shoot', 'bullet', 'stay_time', 'wheel_hit', 'armor_hit', 'car_hit']
            info = self.font.render('car {}'.format(n), False, (0, 0, 0))
            self.screen.blit(info, (8+n*100, 100))
            for i in range(self.cars[n].size):
                info = self.font.render('{}: {}'.format(tags[i], int(self.cars[n, i])), False, (0, 0, 0))
                self.screen.blit(info, (8+n*100, 117+i*17))
        info = self.font.render('red   supply: {}   bonus: {}   bonus_time: {}'.format(self.compet_info[0, 0], \
                                self.compet_info[0, 1], self.compet_info[0, 3]), False, (0, 0, 0))
        self.screen.blit(info, (8, 372))
        info = self.font.render('blue   supply: {}   bonus: {}   bonus_time: {}'.format(self.compet_info[1, 0], \
                                self.compet_info[1, 1], self.compet_info[1, 3]), False, (0, 0, 0))
        self.screen.blit(info, (8, 389))

    def get_order(self): 
        # get order from controler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_1]: self.n = 0
        if pressed[pygame.K_2]: self.n = 1
        if pressed[pygame.K_3]: self.n = 2
        if pressed[pygame.K_4]: self.n = 3
        self.orders[self.n] = 0
        if pressed[pygame.K_w]: self.orders[self.n, 0] += 1
        if pressed[pygame.K_s]: self.orders[self.n, 0] -= 1
        if pressed[pygame.K_q]: self.orders[self.n, 1] -= 1
        if pressed[pygame.K_e]: self.orders[self.n, 1] += 1
        if pressed[pygame.K_a]: self.orders[self.n, 2] -= 1
        if pressed[pygame.K_d]: self.orders[self.n, 2] += 1
        if pressed[pygame.K_b]: self.orders[self.n, 3] -= 1
        if pressed[pygame.K_m]: self.orders[self.n, 3] += 1
        if pressed[pygame.K_SPACE]: self.orders[self.n, 4] = 1
        else: self.orders[self.n, 4] = 0
        if pressed[pygame.K_f]: self.orders[self.n, 5] = 1
        else: self.orders[self.n, 5] = 0
        if pressed[pygame.K_r]: self.orders[self.n, 6] = 1
        else: self.orders[self.n, 6] = 0
        if pressed[pygame.K_n]: self.orders[self.n, 7] = 1
        else: self.orders[self.n, 7] = 0
        if pressed[pygame.K_TAB]: self.dev = True
        else: self.dev = False
        return False

    def orders_to_acts(self, n):
        # turn orders to acts
        self.acts[n, 2] += self.orders[n, 0] * 1.5 / MOTION
        if self.orders[n, 0] == 0:
            if self.acts[n, 2] > 0: self.acts[n, 2] -= 1.5 / MOTION
            if self.acts[n, 2] < 0: self.acts[n, 2] += 1.5 / MOTION
        if abs(self.acts[n, 2]) < 1.5 / MOTION: self.acts[n, 2] = 0
        if self.acts[n, 2] >= 1.5: self.acts[n, 2] = 1.5
        if self.acts[n, 2] <= -1.5: self.acts[n, 2] = -1.5
        # x, y
        self.acts[n, 3] += self.orders[n, 1] * 1 / MOTION
        if self.orders[n, 1] == 0:
            if self.acts[n, 3] > 0: self.acts[n, 3] -= 1 / MOTION
            if self.acts[n, 3] < 0: self.acts[n, 3] += 1 / MOTION
        if abs(self.acts[n, 3]) < 1 / MOTION: self.acts[n, 3] = 0
        if self.acts[n, 3] >= 1: self.acts[n, 3] = 1
        if self.acts[n, 3] <= -1: self.acts[n, 3] = -1
        # rotate chassis
        self.acts[n, 0] += self.orders[n, 2] * 1 / ROTATE_MOTION
        if self.orders[n, 2] == 0:
            if self.acts[n, 0] > 0: self.acts[n, 0] -= 1 / ROTATE_MOTION
            if self.acts[n, 0] < 0: self.acts[n, 0] += 1 / ROTATE_MOTION
        if abs(self.acts[n, 0]) < 1 / ROTATE_MOTION: self.acts[n, 0] = 0
        if self.acts[n, 0] > 1: self.acts[n, 0] = 1
        if self.acts[n, 0] < -1: self.acts[n, 0] = -1
        # rotate yaw
        self.acts[n, 1] += self.orders[n, 3] / YAW_MOTION
        if self.orders[n, 3] == 0:
            if self.acts[n, 1] > 0: self.acts[n, 1] -= 1 / YAW_MOTION
            if self.acts[n, 1] < 0: self.acts[n, 1] += 1 / YAW_MOTION
        if abs(self.acts[n, 1]) < 1 / YAW_MOTION: self.acts[n, 1] = 0
        if self.acts[n, 1] > 3: self.acts[n, 1] = 3
        if self.acts[n, 1] < -3: self.acts[n, 1] = -3
        self.acts[n, 4] = self.orders[n, 4]
        self.acts[n, 6] = self.orders[n, 5]
        self.acts[n, 5] = self.orders[n, 6]
        self.acts[n, 7] = self.orders[n, 7]

    def set_car_loc(self, n, loc):
        self.cars[n, 1:3] = loc

    def get_map(self):
        return g_map(*FIELD_DIMENSIONS, self.areas, self.barriers)

    def stay_check(self):
        # check bonus stay
        for n in range(self.cars.shape[0]):
            a = self.areas[int(self.cars[n, 0]), 0]
            if self.cars[n, 1] >= a[0] and self.cars[n, 1] <= a[1] and self.cars[n, 2] >= a[2] \
            and self.cars[n, 2] <= a[3] and self.compet_info[int(self.cars[n, 0]), 1]:
                self.cars[n, 11] += 1 # 1/200 s
                if self.cars[n, 11] >= 1000: # 5s
                    self.cars[n, 11] = 0
                    self.compet_info[int(self.cars[n, 0]), 3] = 6000 # 30s
            else: self.cars[n, 11] = 0
        for i in range(2):
            if self.compet_info[i, 3] > 0:
                self.compet_info[i, 3] -= 1

    def segment(self, p1, p2, p3, p4):
        # this part code came from: https://www.jianshu.com/p/a5e73dbc742a
        if (max(p1[0], p2[0])>=min(p3[0], p4[0]) and max(p3[0], p4[0])>=min(p1[0], p2[0])
        and max(p1[1], p2[1])>=min(p3[1], p4[1]) and max(p3[1], p4[1])>=min(p1[1], p2[1])):
            if (cross(p1,p2,p3)*cross(p1,p2,p4)<=0 and cross(p3,p4,p1)*cross(p3,p4,p2)<=0): return True
            else: return False
        else: return False

    def line_rect_check(self, l1, l2, sq):
        # this part code came from: https://www.jianshu.com/p/a5e73dbc742a
        # check if line cross rect, sq = [x_leftdown, y_leftdown, x_rightup, y_rightup]
        p1 = [sq[0], sq[1]]
        p2 = [sq[2], sq[3]]
        p3 = [sq[2], sq[1]]
        p4 = [sq[0], sq[3]]
        if self.segment(l1,l2,p1,p2) or self.segment(l1,l2,p3,p4): return True
        else: return False

    def line_barriers_check(self, l1, l2):
        for b in self.barriers:
            sq = [b[0], b[2], b[1], b[3]]
            if self.line_rect_check(l1, l2, sq): return True
        return False

    def line_cars_check(self, l1, l2):
        for car in self.cars:
            if (car[1:3] == l1).all() or (car[1:3] == l2).all():
                continue
            p1, p2, p3, p4 = self.get_car_outline(car)
            if self.segment(l1, l2, p1, p2) or self.segment(l1, l2, p3, p4): return True
        return False

    def get_lidar_vision(self):
        for n in range(self.car_num):
            for i in range(self.car_num-1):
                x, y = self.cars[n-i-1, 1:3] - self.cars[n, 1:3]
                angle = np.angle(x+y*1j, deg=True)
                if angle >= 180: angle -= 360
                if angle <= -180: angle += 360
                angle = angle - self.cars[n, 3]
                if angle >= 180: angle -= 360
                if angle <= -180: angle += 360
                if abs(angle) < LIDAR_ANGLE:
                    if self.line_barriers_check(self.cars[n, 1:3], self.cars[n-i-1, 1:3]) \
                    or self.line_cars_check(self.cars[n, 1:3], self.cars[n-i-1, 1:3]):
                        self.detect[n, n-i-1] = 0
                    else: self.detect[n, n-i-1] = 1
                else: self.detect[n, n-i-1] = 0

    def get_camera_vision(self):
        for n in range(self.car_num):
            for i in range(self.car_num-1):
                x, y = self.cars[n-i-1, 1:3] - self.cars[n, 1:3]
                angle = np.angle(x+y*1j, deg=True)
                if angle >= 180: angle -= 360
                if angle <= -180: angle += 360
                angle = angle - self.cars[n, 4] - self.cars[n, 3]
                if angle >= 180: angle -= 360
                if angle <= -180: angle += 360
                if abs(angle) < CAMERA_ANGLE:
                    if self.line_barriers_check(self.cars[n, 1:3], self.cars[n-i-1, 1:3]) \
                    or self.line_cars_check(self.cars[n, 1:3], self.cars[n-i-1, 1:3]):
                        self.vision[n, n-i-1] = 0
                    else: self.vision[n, n-i-1] = 1
                else: self.vision[n, n-i-1] = 0

    def transfer_to_car_coordinate(self, points, n):
        pan_vecter = -self.cars[n, 1:3]
        rotate_matrix = np.array([[np.cos(np.deg2rad(self.cars[n, 3]+90)), -np.sin(np.deg2rad(self.cars[n, 3]+90))],
                                  [np.sin(np.deg2rad(self.cars[n, 3]+90)), np.cos(np.deg2rad(self.cars[n, 3]+90))]])
        return np.matmul(points + pan_vecter, rotate_matrix)

    def check_points_wheel(self, car):
        rotate_matrix = np.array([[np.cos(-np.deg2rad(car[3]+90)), -np.sin(-np.deg2rad(car[3]+90))],
                                  [np.sin(-np.deg2rad(car[3]+90)), np.cos(-np.deg2rad(car[3]+90))]])
        xs = np.array([[-22.5, -29], [22.5, -29], 
                       [-22.5, -14], [22.5, -14], 
                       [-22.5, 14], [22.5, 14],
                       [-22.5, 29], [22.5, 29]])
        return [np.matmul(xs[i], rotate_matrix) + car[1:3] for i in range(xs.shape[0])]

    def check_points_armor(self, car):
        rotate_matrix = np.array([[np.cos(-np.deg2rad(car[3]+90)), -np.sin(-np.deg2rad(car[3]+90))],
                                  [np.sin(-np.deg2rad(car[3]+90)), np.cos(-np.deg2rad(car[3]+90))]])
        xs = np.array([[-6.5, -30], [6.5, -30], 
             [-18.5,  -7], [18.5,  -7],
             [-18.5,  0], [18.5,  0],
             [-18.5,  6], [18.5,  6],
             [-6.5, 30], [6.5, 30]])
        return [np.matmul(x, rotate_matrix) + car[1:3] for x in xs]

    def get_car_outline(self, car):
        rotate_matrix = np.array([[np.cos(-np.deg2rad(car[3]+90)), -np.sin(-np.deg2rad(car[3]+90))],
                                  [np.sin(-np.deg2rad(car[3]+90)), np.cos(-np.deg2rad(car[3]+90))]])
        xs = np.array([[-22.5, -30], [22.5, 30], [-22.5, 30], [22.5, -30]])
        return [np.matmul(xs[i], rotate_matrix) + car[1:3] for i in range(xs.shape[0])]

    def check_interface(self, n):
        # car barriers assess
        wheels = self.check_points_wheel(self.cars[n])
        for w in wheels:
            if w[0] <= 0 or w[0] >= FIELD_DIMENSIONS[0] or w[1] <= 0 or w[1] >= FIELD_DIMENSIONS[1]:
                self.cars[n, 12] += 1
                return True
            for b in self.barriers:
                if w[0] >= b[0] and w[0] <= b[1] and w[1] >= b[2] and w[1] <= b[3]:
                    self.cars[n, 12] += 1
                    return True
        armors = self.check_points_armor(self.cars[n])
        for a in armors:
            if a[0] <= 0 or a[0] >= FIELD_DIMENSIONS[0] or a[1] <= 0 or a[1] >= FIELD_DIMENSIONS[1]:
                self.cars[n, 13] += 1
                self.cars[n, 6] -= 10
                return True
            for b in self.barriers:
                if a[0] >= b[0] and a[0] <= b[1] and a[1] >= b[2] and a[1] <= b[3]:
                    self.cars[n, 13] += 1
                    self.cars[n, 6] -= 10
                    return True
        # car car assess
        for i in range(self.car_num):
            if i == n: continue
            wheels_tran = self.transfer_to_car_coordinate(wheels, i)
            for w in wheels_tran:
                if w[0] >= -22.5 and w[0] <= 22.5 and w[1] >= -30 and w[1] <= 30:
                    self.cars[n, 14] += 1
                    return True
            armors_tran = self.transfer_to_car_coordinate(armors, i)
            for a in armors_tran:
                if a[0] >= -22.5 and a[0] <= 22.5 and a[1] >= -30 and a[1] <= 30:
                    self.cars[n, 14] += 1
                    self.cars[n, 6] -= 10
                    return True
        return False

    def get_armor(self, car, i):
        rotate_matrix = np.array([[np.cos(-np.deg2rad(car[3]+90)), -np.sin(-np.deg2rad(car[3]+90))],
                                  [np.sin(-np.deg2rad(car[3]+90)), np.cos(-np.deg2rad(car[3]+90))]])
        xs = np.array([[0, -30], [18.5, 0], [0, 30], [-18.5,  0]])
        return np.matmul(xs[i], rotate_matrix) + car[1:3]

    def save_record(self, file):
        np.save(file, self.memory)

            
''' important indexs
areas_index = [[{'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 0 bonus red
                {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 1 supply red
                {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 2 start 0 red
                {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}], # 3 start 1 red

               [{'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 0 bonus blue
                {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 1 supply blue
                {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 2 start 0 blue
                {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}]] # 3 start 1 blue
                            

barriers_index = [{'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 0 horizontal
                  {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 1 horizontal
                  {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 2 horizontal
                  {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 3 vertical
                  {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 4 vertical
                  {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}, # 5 vertical
                  {'border_x0': 0, 'border_x1': 1,'border_y0': 2,'border_y1': 3}] # 6 vertical

armor编号：0：前，1：右，2：后，3左，车头为前

act_index = {'rotate_speed': 0, 'yaw_speed': 1, 'x_speed': 2, 'y_speed': 3, 'shoot': 4, 'shoot_mutiple': 5, 'supply': 6,
             'auto_aim': 7}

bullet_speed: 12.5


compet_info_index = {'red': {'supply': 0, 'bonus': 1, 'bonus_stay_time(deprecated)': 2, 'bonus_time': 3}, 
                     'blue': {'supply': 0, 'bonus': 1, 'bonus_stay_time(deprecated)': 2, 'bonus_time': 3}}
int, shape: (2, 4)

order_index = ['x', 'y', 'rotate', 'yaw', 'shoot', 'supply', 'shoot_mode', 'auto_aim']
int, shape: (8,)
    x, -1: back, 0: no, 1: head
    y, -1: left, 0: no, 1: right
    rotate, -1: anti-clockwise, 0: no, 1: clockwise, for chassis
    shoot_mode, 0: single, 1: mutiple
    shoot, 0: not shoot, 1: shoot
    yaw, -1: anti-clockwise, 0: no, 1: clockwise, for gimbal
    auto_aim, 0: not, 1: auto aim

car_index = {"owner": 0, 'x': 1, 'y': 2, "angle": 3, "yaw": 4, "heat": 5, "hp": 6, 
             "freeze_time": 7, "is_supply": 8, "can_shoot": 9, 'bullet': 10, 'stay_time': 11,
             'wheel_hit': 12, 'armor_hit': 13, 'car_hit': 14}
float, shape: (14,)

'''

    
