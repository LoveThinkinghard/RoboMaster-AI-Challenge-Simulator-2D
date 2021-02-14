

class FIELD:
    dims = (808, 448)
    half_dims = (404, 224)
    spawn_center = (354, 174)
    spawn_dims = (100, 100)
    match_duration = 180


class BARRIER:
    size = 102


class ROBOT:
    size = 40
    dims = (30, 25)
    shield_dims = (25, 20)
    chassis_points = [(9, 25), (29, 25), (30, 24), (30, 13)]  # order is important
    armor_points = [(29, 7), (7, 24)]  # order is important
    motion = 6
    rotate_motion = 4
    yaw_motion = 1
    bullet_speed = 12.5
    rebound_coeff = 0.6


class ZONE:
    centers = [(354, 55), (214, -59), (0, 179.5)]  # F1-3
    dims = (54, 48)
    activation_dims = (36, 32)
    types = {'hp_blue': 0, 'hp_red': 1, 'ammo_blue': 2, 'ammo_red': 3, 'no_move': 4, 'no_shoot': 5}  # order is important


class TEXT:
    robot_label_offset = (-20, -45)
    time_position = (375, 3)
    stat_position = (160, 70)
    stat_increment = (125, 17)


class COLOR:
    blue = (0, 0, 210)
    red = (210, 0, 0)
    green = (0, 210, 0)
    orange = (255, 165, 0)
    gray = (112, 119, 127)
    black = (0, 0, 0)


class IMAGE:
    bullet = 'images/robot/bullet.png'
    inactive_zone = 'images/zone/inactive.png'
    activated_zone = 'images/zone/activated.png'
    zone_icon = 'images/zone/{}.png'
    blue_robot = 'images/robot/blue.png'
    red_robot = 'images/robot/red.png'
    dead_robot = 'images/robot/dead.png'
    gimbal = 'images/robot/gimbal.png'
    stats_panel = 'images/stats_panel.png'
    logo = 'images/logo.png'
