import numpy as np

FIELD_DIMENSIONS = [808, 448]
ZONE_DIMENSIONS = [54, 48]
SPAWN_DIMENSIONS = [100, 100]
HIGH_OBSTACLE_HEIGHT = 40
LOW_BARRIER_HEIGHT = 15

SPAWNS = {
  ((0, 0), (100, 100)): 'spawn_blue',
  ((0, 348), (100, 448)): 'spawn_blue',
  ((708, 0), (808, 100)): 'spawn_red',
  ((708, 348), (808, 448)): 'spawn_red',
}
ZONES = {
  ((731, 255), (785, 303)): 'zone',
  ((591, 141), (645, 189)): 'zone',
  ((377, 20.5), (431, 68.5)): 'zone',
  ((23, 145), (77, 193)): 'zone',
  ((160, 259), (214, 307)): 'zone',
  ((377, 379.5), (431, 427.5)): 'zone'
}
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

THETA = np.rad2deg(np.arctan(45 / 60))

# below parameters can be modified
BULLET_SPEED = 12.5
MOTION = 6
ROTATE_MOTION = 4
YAW_MOTION = 1
CAMERA_ANGLE = 75 / 2
LIDAR_ANGLE = 120 / 2
MOVE_DISCOUNT = 0.6

# colors
GRAY = (180, 180, 180)
RED = (190, 20, 20)
BLUE = (10, 125, 181)


def find_rect_center(rect_coords):
    x_center = np.mean(rect_coords[:, 0])
    y_center = np.mean(rect_coords[:, 1])
    return [x_center, y_center]


def cross(p1, p2, p3):
    x1 = p2[0] - p1[0]
    y1 = p2[1] - p1[1]
    x2 = p3[0] - p1[0]
    y2 = p3[1] - p1[1]
    return x1 * y2 - x2 * y1
