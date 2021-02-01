# kernel Manual

### 1. Kernel Configuration variables

|Item|Value|Description|
|-|-|-|
|Game operating frequency|200Hz|A cycle is called an epoch, that is, 200epoch/s|
|The highest frequency of decision (operation)|20Hz|that is 20 times/s|
|Size ratio|10mm/pixel|The map of 8m×5m corresponds to the game screen of 800p×500p|
|Car size|60p×45p|that is 600mm×450mm|
|Maximum speed of car forward and backward|1.5p/epoch|that is 3m/s|
|Maximum speed of car left and right panning|1p/epoch|that is 2m/s|
|Maximum Chassis Rotation Speed|200°/s|Accurate measurement has not been carried out yet, to be determined|
|Maximum speed of gimbal rotation|600°/s|Accurate measurement has not been performed yet, to be determined|
|Bullet flying speed|12.5p/epoch|that is 25m/s, can be set|
|Muzzle heat settlement and the resulting blood deduction frequency|10Hz||

### 2. Implementation Details

a. The speed of the chassis and pan/tilt will gradually increase to the maximum after pressing 
the corresponding command, and the speed will gradually decrease after the command is stopped.
For specific control instructions, please refer to [operation.md](./operation.md)

b. The default team is divided into red side: car1, car3, blue side: car2, car4. The reason for 
this design is that you can change the confrontation mode only by changing the number of cars.
For example, when car_num = 3, the game mode is: 2v1

c. The role of `pygame` is only visualization, that is, logical operations do not rely on `pygame`, 
and network training does not rely on `pygame`

d. In manual operation, the game time is not subject to the actual time, but the in-game time

e. In manual operation, only one car can be controlled at a time

f. There is a rebound effect, but it does not fully comply with the laws of physics

g. Replenishment can only be triggered within a certain distance from the replenishment point. After 
the replenishment is triggered, it will be out of control for 3 seconds

h. When the center of the car is within the square area of the defense bonus zone, the defense 
bonus timing will be performed

## 3. Parameters that can be modified

In the `__init__` function of the `kernel` class, there are some quantities that can be changed 
depending on the environment such as the site, as follows

``` python
        self.bullet_speed = 12.5 # Bullet speed, the unit is pixel
        self.motion = 6 # The inertial size of the movement
        self.rotate_motion = 4 # Inertial size of chassis rotation
        self.yaw_motion = 1 # The inertial size of the pan/tilt rotation
        self.camera_angle = 75/2 # The field of view of the camera
        self.lidar_angle = 120/2 # The field of view of the lidar
        self.move_discount = 0.6 # The strength of the rebound after hitting the wall
```

## 4. Functions to be used externally

### To obtain map information

`kernel.get_map()`, returns `g_map`, see the parameter format: [params.md](./params.md#GameMap)

### Setting car coordinates

`kernel.set_car_loc(n, loc)`, `n` is the number of the car, 0~3, `loc` is the coordinate of the car,
 two-dimensional array, has no return value