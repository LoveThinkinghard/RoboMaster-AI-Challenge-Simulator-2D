import numpy as np
from box import Box
import enum


# note the ordering of the following definitions
SPAWNS = [Box(100, 100, *c) for c in [(50, 50), (50, 398), (758, 398), (758, 50)]]
LOW_BARRIERS = [Box(80, 20, 190, 224), Box(35.4, 35.4, 404, 224), Box(80, 20, 618, 224)]
HIGH_BARRIERS = [Box(100, 20, 50, 110), Box(20, 100, 160, 398), Box(100, 20, 404, 103.5), Box(100, 20, 404, 344.5), Box(20, 100, 648, 50), Box(100, 20, 758, 338)]

STATIC_IMAGES = ['area/blue', 'area/blue', 'area/red', 'area/red'] + \
                [f'barrier/{b}' for b in ('lhm', 'lcm', 'lhm', 'hhu', 'hvu', 'hhm', 'hhm', 'hvu', 'hhu')]

FIELD = Box(808, 448)
ROBOT = Box(60, 43, 0, 0)
ROBOT_BLOCK = Box(54, 36, 0, 0)

INFO_PANEL = Box(440, 340, 404, 224)
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

COLOR_GRAY = (112, 119, 127)
COLOR_RED = (210, 0, 0)
COLOR_BLUE = (0, 0, 210)
COLOR_BLACK = (0, 0, 0)


class TEAM(enum.Enum):
    blue = 0
    red = 1


def normalize_angle(angle):
    if angle > 180:
        angle -= 360
    if angle <= -180:
        angle += 360
    return angle


def lines_intersect(p11, p12, p21, p22):  # check if two line segments (p11, p12) and (p21, p22) intersect
    return ccw(p11, p21, p22) != ccw(p12, p21, p22) and ccw(p11, p12, p21) != ccw(p11, p12, p22)


def ccw(p1, p2, p3):  # check if three points p1, p2, p3 are oriented CCW
    return (p2[1] - p1[1]) * (p3[0] - p1[0]) < (p3[1] - p1[1]) * (p2[0] - p1[0])
