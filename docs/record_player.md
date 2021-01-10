# Record Player Manual

`Record Player` can be used to reproduce previous games

## One, save game memory

```python
from rmaics import rmaics
game = rmaics(agent_num=4, render=True)
game.reset()
# only when render = True
game.play()

game.save_record('./records/record0.npy')
```

Note: Use the mouse to click the close icon of the game window, the red `×` in the upper
right corner under `Windows`, the game can be ended normally, and the game memory in the memory will not be cleared

## Second, reproduce the game

```python
from kernal import record_player
player = record_player()
player.play('./records/record0.npy')
```

You can use the `←`, `→` keys to control the playback progress, and use the `space` to pause,
please refer to [operation.md](./operation.md) for details