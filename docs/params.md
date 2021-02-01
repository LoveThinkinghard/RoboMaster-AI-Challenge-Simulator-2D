# Parameter format description

Many parameters are represented by arrays, and the corresponding index is needed to know what each represents. 

Note: The variables representing the same thing may be named differently in `rmaics.py` and `kernel.py`

|rmaics|kernel|Meaning|
|-|-|-|
|[state](#state)|N/A|Total State|
|[agents](#agents)|[robots](#agents)|Robot status|
|[compet](#compet)|[compet_info](#compet)|competition information|
|[detect](#detect)|[detect](#detect)|Robots that can be detected by lidar|
|[vision](#vision)|[vision](#vision)|Robots that the camera can see|
|[actions](#actions)|[orders](#actions)|Instructions to control the car|
|[g_map](#g_map)|[g_map](#g_map)|Map information|
|[areas](#areas)|[areas](#areas)|Area Information|
|[barriers](#barriers)|[barriers](#barriers)|Barrier Information|
|N/A|[acts](#acts)|Lower-level actions|

The variables are explained as follows:

## state

`State` is a custom class, representing the state of the simulation environment:

```python
class State(object):
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
|time|int|0~180|The remaining time for the game|
|[agents](#agents)|float|array|Robot status|
|[compet](#compet)|int|array|competition information|
|done|bool|0~1|Is the game over|
|[detect](#detect)|int|array|Which cars can be detected|
|[vision](#vision)|int|array|Can see those cars|

## agents/cars

`agents`/`cars` is a two-dimensional numpy array containing all the robots and the status of each. It 
has `shape` (car_num, 15), where `car_num` denotes the number of robots and the second index denotes a
property for the robot from its status.
The status format of each robot is as follows:

|Index|Name|Type|Scope|Explanation|
|---|---|---|---|---|
|0|owner|int|0~1|Team, 0: red side, 1: blue side|
|1|x|float|0~800|x coordinate<sup>1</sup>|
|2|y|float|0~500|y coordinate|
|3|angle|float|-180~180|Absolute chassis angle<sup>2</sup>|
|4|yaw|float|-90~90|Gimbal angle relative to chassis|
|5|heat|int|0~|Muzzle Heat|
|6|hp|int|0~2000|HP|
|7|freeze_time|int|0~600|Remaining time to complete the refill<sup>3</sup>, it takes 3s|
|8|is_supply|bool|0~1|0: in replenishment, 1: not in replenishment|
|9|can_shoot|bool|0~1|The decision frequency is higher than the highest frequency of ejection (10Hz)|
|10|bullet|int|0~|Remaining bullets|
|11|stay_time|int|0~1000|The time spent in the defensive bonus zone in epochs, it takes 5s|
|12|wheel_hit|int|0~|Number of times the wheel hits the wall|
|13|armor_hit|int|0~|Number of times the armor plate hits the wall|
|14|car_hit|int|0~|Number of wheel or armor plate crashes|

<sup>1</sup> Take the starting corner of the car as the origin, and make all of the map fall on the positive semi-axis

<sup>2</sup> The origin is the same as above, the polar axis falls in the positive direction of the x-axis, and the 
direction of rotation to the positive direction of the y-axis is positive

<sup>3</sup> Calculated in epoch, 200epoch=1s

## compet/compet_info

`compet`/`compet_info` is a two-dimensional array, of type `int` and `shape` (2, 4) that stores
the competition information, as follows:

NOTE: The stay_time field has been deprecated for this variable, and is stored in agents instead. The index
corresponding to stay_time does not store anything

|First Index|Second Index|Name|Scope|Explanation|Team|
|-|-|-|-|-|-|
|0|0|supply|0~2|Remaining supply times|Red|
|0|1|bonus|0~1|Remaining times of bonus|Red|
|0|2|stay_time(deprecated)|0~1000|Deprecated, go to `agents`|Red|
|0|3|bonus_time|0~6000|Bonus remaining time|Red|
|1|0|supply|0~2|Supply remaining times|Blue|
|1|1|bonus|0~1|Remaining times of bonus|Blue|
|1|2|stay_time(deprecated)|0~1000|Deprecated, go to `agents`|Blue|
|1|3|bonus_time|0~6000|Bonus remaining time|Blue|


## detect&vision


`detect` and `vision` are 2D arrays that determine if a particular robot can detect another robot for shooting.
The shape for both is (car_num, car_num), where the first indices determines the robot's visibility, and the second
indices determines the robots that cna be seen.
 
`detect` refers to the robot that can be seen by a robot's lidar, `vision` refers to the robot that can be seen by,
 for example

```python
         # 0  1  2  3
detect = [[0, 1, 0, 0], # 0
          [0, 0, 1, 1], # 1
          [0, 0, 0, 0], # 2
          [1, 0, 0, 0]] # 3
```

Means:

Robot_0 can detect Robot_1

Robot_1 can detect Robot_2 and Robot_3

Robot_2 detects no robots

Robot_3 can detect Robot_0

## actions/orders

`actions`/`orders` is a 2D array representing the instructions passed to each robot of`shape` (car_num, 8),
where the first index represents the robot_number, and the second index represents the particular robot instruction
from the following list:

|Second Index|Name|Scope|Explanation|Hand control buttons|
|-|-|-|-|-|
|0|x|-1~1|-1: back, 0: not moving, 1: forward<sup>1</sup>|s/w|
|1|y|-1~1|-1: move left, 0: do not move, 1: move right |q/e|
|2|rotate|-1~1|Chassis, -1: turn left, 0: do not move, 1: turn right|a/d|
|3|yaw|-1~1|Yaw, -1: turn left, 0: do not move, 1: turn right|b/m|
|4|shoot|0~1|Whether to shoot, 0: No, 1: Yes |space|
|5|supply|0~1|When the supply is triggered, 0: No, 1: Yes |f|
|6|shoot_mode|0~1|Shooting mode, 0: single shot, 1: continuous shot|r|
|7|auto_aim|0~1|Whether to enable self-aim, 0: No, 1: Yes|n|


<sup>1</sup> It will continue to accelerate, the maximum speed of x is 3m/s, and the maximum speed of y is 2m/s.

## GameMap

`GameMap` is a custom class representing a map of the environment:

```python
class GameMap(object):
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

## areas & barriers

The location details of a single area or obstacle is stored in the following array format:

|Index|Name|Scope|Explanation|
|---|---|---|---|
|0|border_x0|0~800|Left border|
|1|border_x1|0~800|Right border|
|2|border_y0|0~500|Upper border|
|3|border_y1|0~500|Lower border|

Where the upper left corner of the map is the origin

### areas

`areas` is a three-dimensional array, `shape` is (2, 4, 4), where the first index represents the team,
second index represents the area type, and the third index represents a value from the location array described above

|First Index|Second Index|Name|Type|Team|
|-|-|-|-|-|
|0|0|bonus|Defense bonus area|Red|
|0|1|supply|Supply Area|Red|
|0|2|start0|starting area 1|Red|
|0|3|start1|starting area 2|Red|
|1|0|bonus|Defense bonus area|Blue|
|1|1|supply|Supply Area|Blue|
|1|2|start0|starting area 1|Blue|
|1|3|start1|starting area 2|Blue|

### barriers

`barriers` is a two-dimensional array, `shape` (7, 4), the first index representing the barrier type,
and the second index representing a value from the location array described above

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

`acts` is a 2D array in `kernel.py` representing the actions to be taken by each robot upon each game step,
which is different from [`actions`](#actions) in `rmaics`. 
The type is `float`, and the `shape` is (Car_num, 8), and the possible actions for each robot are as follows:

|Index|Name|Explanation|
|-|-|-|
|0|rotate_speed|Chassis rotation speed|
|1|yaw_speed|Gimbal rotation speed|
|2|x_speed|forward and backward speed|
|3|y_speed|Left and right translation speed|
|4|shoot|Whether to shoot or not|
|5|shoot_mutiple|Burst shooting or not|
|6|supply|Whether to trigger supply|
|7|auto_aim|Auto aim or not|