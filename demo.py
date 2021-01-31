# -*- coding: utf-8 -*-
from rmaics import rmaics
from kernal import record_player
from actor import Actor
import numpy as np

#%%
game = rmaics(agent_num=4, render=True)
game.reset()

actor0 = Actor(0)
action0 = [1, 0, 0, 0, 0, 0, 0, 0]
# only when render = True
for _ in range(1000):
    obs, reward, done, info = game.step(np.array([action0,
       [0, 0, 0, 0, 0, 0, 0, 1],
       [0, 0, 0, 0, 0, 0, 0, 1],
       [0, 0, 0, 0, 0, 0, 0, 1]]))
    action0 = actor0.action_from_state(obs, game.g_map)
# game.play()

#%%
game.save_record('./records/record0.npy')

#%%
player = record_player()
player.play('./records/record_test.npy')

