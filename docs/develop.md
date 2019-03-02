# Kernal 开发指南

## 开发须知

开发时注意参考参数格式说明：[params.md](./docs/params.md)

## 可以改进的地方

### 1、运行速度

以下为当前的测试速度：
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

### 2、并行比赛

在`kernal`层面同时进行多场比赛，这样可以不用专门开多个进程，可以提高学习速度

### 3、联机对抗

一个电脑同时操作四个车不太方便，所以如果人与人想进行对抗，需要联机操作，而实现人与人对抗的目的在于可以进行模仿学习，模仿学习的想法来源于[DeepMind](https://deepmind.com/)的[AlphaStar](https://deepmind.com/blog/alphastar-mastering-real-time-strategy-game-starcraft-ii/)

### 4、增加随机误差

模拟器毕竟不是真实世界，增加一些随机性有助于提高模拟到实际迁移能力，想法来源于[OpenAI](https://openai.com/)的研究[Generalizing from Simulation](https://blog.openai.com/generalizing-from-simulation/)

### 5、视野

激光雷达和摄像头的视野用来表示能检测到车，当某个车在摄像头视野内时，可以自动瞄准这个车。现在使用的视野算法为：首先检测角度是不是符合，再检查两车中心联线上是否有阻碍（障碍物或车）。这样做的问题是：在有些刁钻的角度，会出现不合理的视野