# Parameter format description

Many parameters are represented by arrays, and the corresponding index is needed to know what each represents. 
This is the meaning of this manual.

Note: The parameter naming methods of `kernal` and `rmaics` are not exactly the same

|rmaics|kernal|Meaning|
|-|-|-|
|[state](#state)||Total State|
|[agents](#agents)|[cars](#agents)|Car status|
|[compet](#compet)|[compet_info](#compet)|competition information|
|[detect](#detect)|[detect](#detect)|Cars that can be detected by lidar|
|[vision](#vision)|[vision](#vision)|Cars that the camera can see|
|[actions](#actions)|[orders](#actions)|Instructions to control the car|
|[g_map](#g_map)|[g_map](#g_map)|Map information|
|[areas](#areas)|[areas](#areas)|Area Information|
|[barriers](#barriers)|[barriers](#barriers)|Barrier Information|
||[acts](#acts)|Lower-level actions|

## state

`state` is a custom class, defined as follows:

```python
class state(object):
    def __init__(self, time, agents, compet_info, done=False, detect=None, vision=None):
        self.time = time
        self.agents = agents
        self.compet = compet_info
        self.done = done
        self.detect = detect
        self.vision = vision
```

|Name|Type|Scope|Explanation|
|---|---|---|---|
|time|int|0~180|The remaining time of the game|
|[agents](#agents)|float|array|Car status|
|[compet](#compet)|int|array|competition information|
|done|bool|0~1|Is the game over|
|[detect](#detect)|int|array|Which cars can be detected|
|[vision](#vision)|int|array|Can see those cars|

## agents

`agents` describes the state of the robot. It is expressed by `cars` in `kernal`. It is a two-dimensional
array (numpy.array), the type is `float`, `shape` is (car_mun, 15), and `car_num` is The number of robots.
The types in the table are theoretical types, which are actually determined by the overall type of the array.
The status format of a single robot is as follows:

|Citation|Name|Type|Scope|Explanation|
|---|---|---|---|---|
|0|owner|int|0~1|Team, 0: red side, 1: blue side|
|1|x|float|0~800|x coordinate[0]|
|2|y|float|0~500|y coordinate|
|3|angle|float|-180~180|Absolute chassis angle[1]|
|4|yaw|float|-90~90|Gimbal relative chassis angle|
|5|heat|int|0~|Muzzle Heat|
|6|hp|int|0~2000|HP|
|7|freeze_time|int|0~600|Remaining time to complete the refill [2], it takes 3s|
|8|is_supply|bool|0~1|0: in replenishment, 1: not in replenishment|
|9|can_shoot|bool|0~1|The decision frequency is higher than the highest frequency of ejection (10Hz)|
|10|bullet|int|0~|Remaining bullets|
|11|stay_time|int|0~1000|The time spent in the defensive bonus zone, it takes 5s|
|12|wheel_hit|int|0~|Number of times the wheel hits the wall|
|13|armor_hit|int|0~|Number of times the armor plate hits the wall|
|14|car_hit|int|0~|Number of wheel or armor plate crashes|

[0] Take the starting corner of the car as the origin, and make all of the map fall on the positive semi-axis

[1] The origin is the same as above, the polar axis falls in the positive direction of the x-axis, and the 
direction of rotation to the positive direction of the y-axis is positive

[2] Calculated in epoch, 200epoch=1s

## compet

`compet` refers to competition information, the full name is `competition_information`, which is represented
by `compet_info` in `kernal`, a two-dimensional array, the type is `int`, all parameter theoretical types are
also `int`, and `shape` is (2, 4), as follows:


|Reference 0|Reference 1|Name|Scope|Explanation|Team|
|-|-|-|-|-|-|
|0|0|supply|0~2|Remaining supply times|Red side|
|0|1|bonus|0~1|Remaining times of bonus|Red side|
|0|2|stay_time(deprecated)|0~1000|Deprecated, go to `agents`|Red side|
|0|3|bonus_time|0~6000|Bonus remaining time|Red side|
|1|0|supply|0~2|Supply remaining times|Lanfang|
|1|1|bonus|0~1|Remaining times of bonus|Blue party|
|1|2|stay_time(deprecated)|0~1000|Deprecated, go to `agents`|blue party|
|1|3|bonus_time|0~6000|Bonus remaining time|Blue party|


## detect&vision

### detect

### vision

`detect` refers to the car that can be seen by the lidar, `vision` refers to the car that can be seen by
the camera, both are represented by a two-dimensional array, and the `shape` is: (car_num, car_num), for example

```python
# 0 1 2 3
detect = [[0, 1, 0, 0], # 0
          [0, 0, 1, 1], # 1
          [0, 0, 0, 0], # 2
          [1, 0, 0, 0]] # 3
```

Means:

No. 0 car can detect No. 1 car

Car 1 can detect car 2 and car 3

No car is detected for car 2

Car 3 can detect car 0

## actions

`actions` is the instruction passed to the robot, called `orders` in `kernal`, a two-dimensional array, the
type is `int`, the theoretical type of all parameters is also `int`, and `shape` is (car_num, 8) , The format
of a single instruction is as follows

|Citation|Name|Scope|Explanation|Hand control buttons|
|-|-|-|-|-|
|0|x|-1~1|-1: back, 0: not moving, 1: forward [3]|s/w|
|1|y|-1~1|-1: move left, 0: do not move, 1: move right |q/e|
|2|rotate|-1~1|Chassis, -1: turn left, 0: do not move, 1: turn right|a/d|
|3|yaw|-1~1|Yaw, -1: turn left, 0: do not move, 1: turn right|b/m|
|4|shoot|0~1|Whether to shoot, 0: No, 1: Yes |space|
|5|supply|0~1|When the supply is triggered, 0: No, 1: Yes |f|
|6|shoot_mode|0~1|Shooting mode, 0: single shot, 1: continuous shot|r|
|7|auto_aim|0~1|Whether to enable self-aim, 0: No, 1: Yes|n|


[3] It will continue to accelerate, the maximum speed of x is 3m/s, and the maximum speed of y is 2m/s. In fact, 
these buttons can be understood as throttle to control whether to accelerate

`Serial multi-player mode`: You can change the operation object by pressing the number above the keyboard, 
please refer to [operation.md](./operation.md) for details

## g_map

`g_map` is an abbreviation of `game_map`, a custom class, defined as follows

```python
class g_map(object):
    def __init__(self, length, width, areas, barriers):
        self.length = length
        self.width = width
        self.areas = areas
        self.barriers = barriers
```

|Name|Type|Scope|Explanation|
|---|---|---|---|
|length|int|800|map length|
|width|int|500|map width|
|[areas](#areas)|float|array|Supply, start and bonus area location information|
|[barriers](#barriers)|float|array|location information of obstacles|

## areas&barriers

The format of a single area or obstacle is as follows

|Citation|Name|Scope|Explanation|
|---|---|---|---|
|0|border_x0|0~800|Left border|
|1|border_x1|0~800|Right border|
|2|border_y0|0~500|Upper border|
|3|border_y1|0~500|lower border|

Take the upper left corner of the map as the origin

### areas

`areas` is a three-dimensional array, `shape` is (2, 4, 4)

|Reference 0|Reference 1|Name|Type|Team|
|-|-|-|-|-|
|0|0|bonus|Defense bonus area|Red side|
|0|1|supply|Supply Area|Red Square|
|0|2|start0|starting area|red side|
|0|3|start1|starting area|red side|
|1|0|bonus|Defense bonus area|Blue side|
|1|1|supply|Supply Area|Blue Square|
|1|2|start0|starting area|blue square|
|1|3|start1|starting area|blue square|

### barriers

`barriers` is a two-dimensional array, `shape` is (7, 4)

|Citation 0|Type|
|-|-|
|0|Level|
|1|Level|
|2|Level|
|3|Vertical|
|4|Vertical|
|5|Vertical|
|6|Vertical|

## acts

This `acts` is an action in `kernal`, which is different from [`actions`](#actions) in `rmaics`. 
This `acts` is a lower-level action, the type is `float`, and the `shape` is: (Car_num, 8)

|Citation 1|Name|Explanation|
|-|-|-|
|0|rotate_speed|Chassis rotation speed|
|1|yaw_speed|Gimbal rotation speed|
|2|x_speed|forward and backward speed|
|3|y_speed|Left and right translation speed|
|4|shoot|Whether to launch|
|5|shoot_mutiple|Is it burst?
|6|supply|Whether to trigger supply|
|7|auto_aim|Whether automatic aiming|