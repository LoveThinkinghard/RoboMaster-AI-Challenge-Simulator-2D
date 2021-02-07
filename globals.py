import numpy as np
import pygame

TEAM_RED = 0
TEAM_BLUE = 1

FIELD_DIMENSIONS = (808, 448)
ROBOT_DIMENSIONS = (60, 45)
SPAWN_HLENGTH = 50
HIGH_OBSTACLE_HEIGHT = 40
LOW_BARRIER_HEIGHT = 15

# top left (x, y), bottom right (x, y)
SPAWNS = {
  ((0, 0), (100, 100)): 'spawn_blue',
  ((0, 348), (100, 448)): 'spawn_blue',
  ((708, 0), (808, 100)): 'spawn_red',
  ((708, 348), (808, 448)): 'spawn_red'
}
ZONES = {
  ((23, 145), (77, 193)): 'zone',
  ((163, 259), (217, 307)): 'zone',
  ((377, 20.5), (431, 68.5)): 'zone',
  ((731, 255), (785, 303)): 'zone',
  ((591, 141), (645, 189)): 'zone',
  ((377, 379.5), (431, 427.5)): 'zone'
}
ZONE_TYPES = [
    'hp',
    'ammo',
    'no_shoot',
    'no_move'
]
LOW_BARRIERS = {
  ((150, 214), (230, 234)): 'barrier_low_horizontal_marked',
  ((578, 214), (658, 234)): 'barrier_low_horizontal_marked',
  ((386.3, 206.3), (421.7, 241.7)): 'barrier_low_center_marked'
}
HIGH_BARRIERS = {
  ((708, 328), (808, 348)): 'barrier_high_horizontal_unmarked',
  ((0, 100), (100, 120)): 'barrier_high_horizontal_unmarked',
  ((638, 0), (658, 100)): 'barrier_high_vertical_unmarked',
  ((150, 348), (170, 448)): 'barrier_high_vertical_unmarked',
  ((354, 93.5), (454, 113.5)): 'barrier_high_horizontal_marked',
  ((354, 334.5), (454, 354.5)): 'barrier_high_horizontal_marked'
}
BARRIERS = {**LOW_BARRIERS, **HIGH_BARRIERS}
FIELD = ((0, 0), FIELD_DIMENSIONS)
ROBOT = ((-ROBOT_DIMENSIONS[0] / 2, -ROBOT_DIMENSIONS[1] / 2), (ROBOT_DIMENSIONS[0] / 2, ROBOT_DIMENSIONS[1] / 2))
INFO_PANEL = ((184, 54), (624, 394))
INFO_SPACING = (105, 17)
INFO_START = (200, 70)

MATCH_DURATION = 180
ZONE_RESET = 60
THETA = np.rad2deg(np.arctan(45 / 60))

# below parameters can be modified
BULLET_SPEED = 12.5
CAMERA_ANGLE = 75 / 2
LIDAR_ANGLE = 120 / 2
COLLISION_COEFFICENT = 0.6

# colors
COLOR_GRAY = (112, 119, 127)
COLOR_RED = (210, 0, 0)
COLOR_BLUE = (0, 0, 210)
COLOR_BLACK = (0, 0, 0)


def normalize_angle(angle):
    if angle > 180:
        angle -= 360
    if angle <= -180:
        angle += 360
    return angle


def find_rect_center(rect):
    x_center = (rect[0][0] + rect[1][0]) / 2
    y_center = (rect[0][1] + rect[1][1]) / 2
    return [x_center, y_center]


def rect_to_pygame(rect):  # convert rectangle (p_top_left, p_bottom_right) to pygame Rect(left, top, width, height)
    width = rect[1][0] - rect[0][0]
    height = rect[1][1] - rect[0][1]
    return pygame.Rect(*rect[0], width, height)


def point_inside_rect(p, rect, check_on=False):  # check if point is inside rectangle (and on rectangle if check_on=True)
    if check_on:
        return rect[0][0] <= p[0] <= rect[1][0] and rect[0][1] <= p[1] <= rect[1][1]
    return rect[0][0] < p[0] < rect[1][0] and rect[0][1] < p[1] < rect[1][1]


def line_intersects_rect(p1, p2, rect):  # check if line (p1, p2) intersects rectangle (p_top_left, p_bottom_right)
    p_top_right = (rect[1][0], rect[0][1])
    p_bottom_left = (rect[0][1], rect[1][0])
    return any([lines_intersect(p1, p2, rect[0], p_top_right), lines_intersect(p1, p2, p_top_right, rect[1]),
                lines_intersect(p1, p2, rect[1], p_bottom_left), lines_intersect(p1, p2, p_bottom_left, rect[0])])


def lines_intersect(p11, p12, p21, p22):  # check if two line segments (p11, p12) and (p21, p22) intersect
    return ccw(p11, p21, p22) != ccw(p12, p21, p22) and ccw(p11, p12, p21) != ccw(p11, p12, p22)


def ccw(p1, p2, p3):  # check if three points p1, p2, p3 are oriented CCW
    return (p2[1] - p1[1]) * (p3[0] - p1[0]) < (p3[1] - p1[1]) * (p2[0] - p1[0])
