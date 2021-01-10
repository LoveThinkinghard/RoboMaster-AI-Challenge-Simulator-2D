# Kernal Development Guide

## One, development instructions

Please refer to the parameter format description during development: [params.md](./params.md)

## Two, structure introduction

The core function of `kernal` is: `one_epoch`, which means to run a cycle. In a cycle, it 
will call: `move_car`, `move_bullet`, and at the same time update visual field information, game information, etc.,
and update the game screen (if the screen is displayed)

There are two functions that can call `one_epoch`: `step` and `play`. What `step` does is to get the 
command `orders` passed in by the user, convert `orders` to `acts`, and then run for 10 cycles; the only 
difference of `play` is that it will always run, then every ten cycles You will get an order from 
the keyboard once. Note: `acts` in `kernal` is different from `actions` in `rmaics`, and `orders` in `kernal` 
is the same as `actions` in `rmaics`

## Three, what can be improved

### 1. Running speed

The following are the current test results without visualization:

|Car Number|Motion Command|Simulation Time|Program Running Time|
|-|-|-|-|
|1|full|3min|8.2s|
|2|full|3min|17.1s|
|3|full|3min|25.5s|
|4|full|3min|51.2s|

The test environment is: Windows 10, octa-core i5-8250U CPU 1.60GHz; CPU usage: ~20%. Note that no matter 
what program is running, the CPU usage is about 20%. This is just to show the actual CPU power used during the test.


Test Code：

```python
from rmaics import rmaics
import numpy as np
import time

game = rmaics(agent_num=2, render=True)
game.reset()
actions = np.array([[1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1]])

t1 = time.time()
for _ in range(3600): # 3600epoch = 180s
    obs = game.step(actions)
t2 = time.time()
print(t2-t1)
```

#### Some possible implementation methods

Use numba or Cython

### 2. Parallel competition

At the `kernal` level, multiple games are played at the same time, so that you don’t need to 
open multiple processes, which can improve the learning speed

### 3. Online confrontation

It is not convenient for a computer to operate four cars at the same time, so if people want to fight 
against each other, they need to operate online, and the purpose of realizing the confrontation between 
people is to allow imitation learning. The idea of imitation learning comes 
from [DeepMind](https: //deepmind.com/)[AlphaStar](https://deepmind.com/blog/alphastar-mastering-real-time-strategy-game-starcraft-ii/)

#### Operation Guide

The other parts basically don’t need to be moved. Change the method of obtaining instructions to 
network access. In addition, you can change the control method of the pan/tilt to the mouse control in 
the `get_order` function.

### 4. Increase random error

The simulator is not the real world after all. Adding some randomness will help improve the ability 
of simulation to actual migration. The idea comes from the research 
of [OpenAI](https://openai.com/) [Generalizing from Simulation](https://blog .openai.com/generalizing-from-simulation/)

#### Operation Guide

At the beginning of the function `move_car`, some errors are added to `self.acts`. For the specific 
details of `acts`, please refer to [params.md](./params.md). Note that it is `acts in `kernal` `

### 5. Vision

The field of view of the lidar and the camera is used to indicate that the car can be detected. When a car 
is within the field of view of the camera, the car can be automatically targeted. The current vision 
algorithm is: firstly, check whether the angle is consistent, and then check whether there is 
an obstacle (obstacle or car) on the center line of the two cars. The problem with this is: in some 
tricky angles, there will be unreasonable vision