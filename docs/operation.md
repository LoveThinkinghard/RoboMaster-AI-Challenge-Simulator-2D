# Control instruction description

## Robot action instructions

A single instruction is a one-dimensional array, the type is: `int`, as follows

|Citation|Name|Scope|Explanation|Hand control buttons|
|-|-|-|-|-|
|0|x|-1~1|-1: back, 0: not moving, 1: forward |s/w|
|1|y|-1~1|-1: move left, 0: do not move, 1: move right |q/e|
|2|rotate|-1~1|Chassis, -1: turn left, 0: do not move, 1: turn right|a/d|
|3|yaw|-1~1|Yaw, -1: turn left, 0: do not move, 1: turn right|b/m|
|4|shoot|0~1|Whether to shoot, 0: No, 1: Yes |space|
|5|supply|0~1|When the supply is triggered, 0: No, 1: Yes |f|
|6|shoot_mode|0~1|Shooting mode, 0: single shot, 1: continuous shot|r|
|7|auto_aim|0~1|Whether to enable self-aim, 0: No, 1: Yes|n|

## Assist button

|Button|Explanation|Example|
|-|-|-|
|The number above the keyboard|Switch operation object|For example, press `2` to control `car2`|
|Tab|Show more information|-|

## Record Player buttons

`Record Player` can be used to reproduce previous games. For more information, please 
refer to [record_player.md](./record_player.md)

|Key|Explanation|
|-|-|
|Tab|Show more information|
|←|Back|
|→|fast forward|
|space|Pause|