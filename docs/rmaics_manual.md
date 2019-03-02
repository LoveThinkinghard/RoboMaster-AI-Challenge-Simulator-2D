# RMAICS Manual

## 一、设计观测值与奖励函数

首先根据自己的需要完成封装类`rmaics`中的`get_observation`和`get_reward`部分，即下面两部分

```python
    def get_observation(self, state):
        # personalize your observation here
        obs = None
        return obs
    def get_reward(self, state):
        # personalize your observation here
        rewards = None
        return rewards
```

如需使用地图信息，可调用`kernal`的`get_map`函数，将会返回地图信息，返回数据的格式见[params.md](./params.md)。例如

```python
game = kernal(car_num=1, render=True)
g_map = game.get_map()
```

## 二、开始使用

`rmaics`的使用方式与[openai](https://openai.com/)的[gym](https://github.com/openai/gym)类似

### 1、初始化

导入，声明并初始化，`render`为`True`时显示会画面，并可以使用键盘操作，反之不行

```python
from rmaics import rmaics
car_num = 4
game = rmaics(agent_num=car_num, render=True)
game.reset()
```

### 2、执行一步

传入决策，得到观测，奖励，是否结束，和其他信息，参数的具体格式请参考：[params.md](./params.md)

```python
# action format (int, np.array): [['x', 'y', 'rotate', 'yaw', 'shoot', 'supply', 'shoot_mode', 'auto_aim'], ...]
# action.shape = (car_num, 8)
actions = [[1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1]]
obs, reward, done, _ = game.step(actions)
```

### 3、使用键盘控制

如手动用键盘控制，则调用下面这个函数，注意：只有`render`为`True`时才可以调用，用鼠标点击窗口的关闭图标可以正常停止游戏

```python
game.play()
```

### 4、保存记忆

这里的记忆指的是`kernal`的记忆，记忆将被保存为[npy](https://stackoverflow.com/questions/4090080/what-is-the-way-data-is-stored-in-npy)文件，里面存储着用来复现游戏的所需信息，如何播放请参考[record_player](./record_player.md)，保存方式如下

```python
game.save_record(file='./records/record.npy')
```