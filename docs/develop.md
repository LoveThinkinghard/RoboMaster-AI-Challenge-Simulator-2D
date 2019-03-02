# Kernal 开发指南

## 一、开发须知

开发时注意参考参数格式说明：[params.md](./params.md)

## 二、结构介绍

`kernal`的核心函数是：`one_epoch`，表示运行一个周期，一个周期里会调用：`move_car`，`move_bullet`，同时会更新视野信息，比赛信息等，并更新游戏画面（如果显示画面）

可以调用`one_epoch`的有两个函数：`step`和`play`。`step`做的是获取用户传入的指令`orders`，把`orders`转换为`acts`，然后运行10个周期；`play`的唯一区别在于：它会一直运行，然后每十个周期会从键盘获得一次`orders`。注意：`kernal`里的`acts`与`rmaics`里的`actions`不同，而`kernal`里的`orders`与`rmaics`里的`actions`相同

## 三、可以改进的地方

### 1、运行速度

以下为当前不开启可视化的测试结果：

|车数量|动作指令|模拟时间|程序运行时间|
|-|-|-|-|
|1|full|3min|8.2s|
|2|full|3min|17.1s|
|3|full|3min|25.5s|
|4|full|3min|51.2s|

测试环境为：Windows 10，八核i5-8250U CPU 1.60GHz；CPU占用：~20%，注意，无论运行什么程序，CPU占用均在20%左右，在这里只是表明测试时实际使用的CPU算力

测试代码：

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

#### 一些可能的实现方法

使用numba或Cython

### 2、并行比赛

在`kernal`层面同时进行多场比赛，这样可以不用专门开多个进程，可以提高学习速度

### 3、联机对抗

一个电脑同时操作四个车不太方便，所以如果人与人想进行对抗，需要联机操作，而实现人与人对抗的目的在于可以进行模仿学习，模仿学习的想法来源于[DeepMind](https://deepmind.com/)的[AlphaStar](https://deepmind.com/blog/alphastar-mastering-real-time-strategy-game-starcraft-ii/)

#### 操作指南

其他的部分基本不用动，改变获取指令的方法，改为联网获取，另外还可以在`get_order`函数里将云台的控制方式改为用鼠标控制

### 4、增加随机误差

模拟器毕竟不是真实世界，增加一些随机性有助于提高模拟到实际迁移能力，想法来源于[OpenAI](https://openai.com/)的研究[Generalizing from Simulation](https://blog.openai.com/generalizing-from-simulation/)

#### 操作指南

在函数`move_car`的开头，对`self.acts`增加一些误差，关于`acts`的具体细节，可参见[params.md](./params.md)，注意是`kernal`里的`acts`

### 5、视野

激光雷达和摄像头的视野用来表示能检测到车，当某个车在摄像头视野内时，可以自动瞄准这个车。现在使用的视野算法为：首先检测角度是不是符合，再检查两车中心联线上是否有阻碍（障碍物或车）。这样做的问题是：在有些刁钻的角度，会出现不合理的视野
