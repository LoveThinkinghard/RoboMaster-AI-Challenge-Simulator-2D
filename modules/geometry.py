import pygame
import numpy as np
from modules.cache import Cache
from modules.constants import *


def distance(p1, p2):
    return np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def ccw(p1, p2, p3):  # check if three points p1, p2, p3 are oriented CCW
    return (p2[1] - p1[1]) * (p3[0] - p1[0]) <= (p3[1] - p1[1]) * (p2[0] - p1[0])


def transform(point, shift=(0, 0), angle=0):
    angle = -np.deg2rad(angle)
    rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    return np.matmul(point, rotation_matrix) + shift


def mirror(point, flip_x=True, flip_y=True):
    x_factor = -1 if flip_x else 1
    y_factor = -1 if flip_y else 1
    return x_factor * point[0], y_factor * point[1]


class Line:
    def __init__(self, point1, point2, color=COLOR.black):
        self.p1 = point1
        self.p2 = point2
        self.color = color
        self.cache = None

    def mirrored(self, flip_x=True, flip_y=True):
        return Line(mirror(self.p1, flip_x=flip_x, flip_y=flip_y), mirror(self.p2, flip_x=flip_x, flip_y=flip_y), color=self.color)

    def transformed(self, shift=(0, 0), angle=0):
        angle = -np.deg2rad(angle)
        rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        p1 = np.matmul(self.p1, rotation_matrix) + shift
        p2 = np.matmul(self.p2, rotation_matrix) + shift
        return Line(p1, p2, color=self.color)

    def draw(self, screen):
        if self.cache is None:
            self.cache = Cache(
                start=(self.p1[0] + FIELD.half_dims[0], self.p1[1] + FIELD.half_dims[1]),
                end=(self.p2[0] + FIELD.half_dims[0], self.p2[1] + FIELD.half_dims[1]))
        pygame.draw.line(screen, self.color, self.cache.start, self.cache.end)

    def intersects(self, line: 'Line'):
        return ccw(self.p1, line.p1, line.p2) != ccw(self.p2, line.p1, line.p2) and \
               ccw(self.p1, self.p2, line.p1) != ccw(self.p1, self.p2, line.p2)

    def get_side(self, point):  # 1/-1/0 for a point on right/left/top of line
        side = (self.p2[1] - self.p1[1]) * (point[0] - self.p1[0]) - (self.p2[0] - self.p1[0]) * (point[1] - self.p1[1])
        if side > 0:
            return 1
        elif side < 0:
            return -1
        else:
            return 0


class Rectangle:
    def __init__(self, width, height, x_center=None, y_center=None, image=None, padding=0):
        width, height = width + 2 * padding, height + 2 * padding
        x_center = 0 if x_center is None else x_center
        y_center = 0 if y_center is None else y_center
        self.padding = padding
        self.dimensions = (width, height)
        self.center = (x_center, y_center)
        self.left = x_center - width / 2
        self.right = x_center + width / 2
        self.top = y_center - height / 2
        self.bottom = y_center + height / 2
        self.image = image
        self.cache = None

    def mirrored(self, flip_x=True, flip_y=True):
        return Rectangle(self.dimensions[0] - 2 * self.padding, self.dimensions[1] - 2 * self.padding,
                         *mirror(self.center, flip_x=flip_x, flip_y=flip_y), image=self.image, padding=self.padding)

    def pygame_rect(self):
        return pygame.Rect(self.left + self.padding + FIELD.half_dims[0], self.top + self.padding + FIELD.half_dims[1],
                           self.dimensions[0] - 2 * self.padding, self.dimensions[1] - 2 * self.padding)

    def draw(self, screen: pygame.Surface):
        if self.cache is None:
            assert self.image is not None, 'need an image file to draw'
            self.cache = Cache(
                rect=self.pygame_rect(),
                image=pygame.image.load(self.image))
        screen.blit(self.cache.image, self.cache.rect)

    def contains(self, point, strict=False):
        if strict:
            return self.left <= point[0] <= self.right and self.top <= point[1] <= self.bottom
        return self.left < point[0] < self.right and self.top < point[1] < self.bottom

    def intersects(self, line: Line):
        if any([line.p1[0] < self.left and line.p2[0] < self.left, line.p1[0] > self.right and line.p2[0] > self.right,
                line.p1[1] < self.top and line.p2[1] < self.top, line.p1[1] > self.bottom and line.p2[1] > self.bottom]):
            return False
        if all([self.left < line.p1[0] < self.right, self.left < line.p2[0] < self.right,
                self.top < line.p1[1] < self.bottom, self.top < line.p2[1] < self.bottom]):
            return False
        sides = [line.get_side((x, y)) for x in (self.left, self.right) for y in (self.top, self.bottom)]
        if all(s < 0 for s in sides) or all(s > 0 for s in sides):
            return False
        return True
