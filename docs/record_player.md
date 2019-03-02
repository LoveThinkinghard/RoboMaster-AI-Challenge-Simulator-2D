# Record Player Manual

`Record Player`可以用来复现之前的游戏

## 一、保存游戏记忆

```python
from rmaics import rmaics
game = rmaics(agent_num=4, render=True)
game.reset()
# only when render = True
game.play()

game.save_record('./records/record0.npy')
```

注意：用鼠标点击游戏窗口的关闭图标，`Windows`下为右上角的红色`×`，能够正常结束游戏，且内存里的游戏记忆不会被清空

## 二、复现游戏

```python
from kernal import record_player
player = record_player()
player.play('./records/record0.npy')
```

可使用`←`，`→`键控制播放进度，用`space`暂停，具体请参见[operation.md](./operation.md)