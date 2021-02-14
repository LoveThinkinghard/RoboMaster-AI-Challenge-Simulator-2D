# Record Player Manual

The `RecordPlayer` class in `kernel.py` can be used to reproduce previous games

## Saving game memory

```python
from modules.rmaics import Rmaics
<<<<<<< HEAD
game = rmaics(agent_num=4, render=True)
=======
game = Rmaics(agent_num=4, render=True)
>>>>>>> master
game.reset()
# only when render = True
game.play()

game.save_record('./records/record0.npy')
```

Note: Use the mouse to click the close icon of the game window, the red `×` in the upper
right corner under `Windows`, the game can be ended normally, and the game memory in the memory will not be cleared

## Loading and replaying the memory

```python
<<<<<<< HEAD
from modules.kernel import record_player
player = record_player()
=======
from modules.kernel import RecordPlayer
player = RecordPlayer()
>>>>>>> master
player.play('./records/record0.npy')
```

You can use the `←`, `→` keys to control the playback progress, and use the `space` to pause,
please refer to [operation.md](./operation.md) for details