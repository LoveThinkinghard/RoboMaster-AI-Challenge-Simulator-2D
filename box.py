import pygame


class Box:  # rectangle with translated center
    def __init__(self, width, height, x_center=None, y_center=None):
        x_center = width / 2 if x_center is None else x_center
        y_center = height / 2 if y_center is None else y_center
        self.dimensions = (width, height)
        self.center = (x_center, y_center)
        self.left = x_center - width / 2
        self.right = x_center + width / 2
        self.top = y_center - height / 2
        self.bottom = y_center + height / 2

    def to_rect(self):  # convert to pygame.Rect()
        return pygame.Rect(self.left, self.top, *self.dimensions)

    def contains(self, point, strict=False):  # check if point is inside box
        if strict:
            return self.left <= point[0] <= self.right and self.top <= point[1] <= self.bottom
        return self.left < point[0] < self.right and self.top < point[1] < self.bottom

    def intersects(self, point1, point2):  # check if line intersects box
        if any([point1[0] < self.left and point2[0] < self.left, point1[0] > self.right and point2[0] > self.right,
                point1[1] < self.top and point2[1] < self.top, point1[1] > self.bottom and point2[1] > self.bottom]):
            return False
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        offsets = [dx * (point1[1] - y) - dy * (point1[0] - x) for x in (self.left, self.right) for y in (self.top, self.bottom)]
        if all(s < 0 for s in offsets) or all(s > 0 for s in offsets):
            return False
        return True
