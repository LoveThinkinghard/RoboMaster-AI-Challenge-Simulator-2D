# RMAICS Manual

## 1. Design observations and reward functions

First complete the `get_observation` and `get_reward` 
parts in the package class `rmaics` according to your needs, namely the following two parts

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

If you need to use map information, you can call the `get_map` function of `kernal`,
and the map information will be returned. For the format of the returned data, see [params.md]

```python
game = kernal(car_num=1, render=True)
g_map = game.get_map()
```

## Two, start using

The usage of `rmaics` is similar to [gym](https://github.com/openai/gym) of [openai](https://openai.com/)

### 1. Initialization

Import, declare and initialize. When `render` is `True`,
the screen will be displayed, and keyboard operations can be used, but not vice versa

```python
from rmaics import rmaics
car_num = 4
game = rmaics(agent_num=car_num, render=True)
game.reset()
```

### 2. Perform one step

Incoming decision, get observations, rewards, whether to end, and other information,
please refer to the specific format of the parameters: [params.md](./params.md)

```python
# action format (int, np.array): [['x', 'y', 'rotate', 'yaw', 'shoot', 'supply', 'shoot_mode', 'auto_aim'], ...]
# action.shape = (car_num, 8)
actions = [[1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1]]
obs, reward, done, _ = game.step(actions)
```

### 3. Use keyboard control

If you use the keyboard to control manually, call the following function. Note: It can be called only 
when `render` is `True`. Click the close icon of the window with the mouse to stop the game normally

```python
game.play()
```

### 4. Save memory

The memory here refers to the memory of `kernal`, the memory will be saved as 
[npy](https://stackoverflow.com/questions/4090080/what-is-the-way-data-is-stored-in-npy ) File, which 
stores the information needed to reproduce the game. For how to play, 
please refer to [record_player](./record_player.md), save as follows

```python
game.save_record(file='./records/record.npy')
```