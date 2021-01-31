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
actor1 = Actor(1)
action1 = [1, 0, 0, 0, 0, 0, 0, 0]
actor2 = Actor(2)
action2 = [1, 0, 0, 0, 0, 0, 0, 0]
actor3 = Actor(3)
action3 = [1, 0, 0, 0, 0, 0, 0, 0]
# only when render = True
for _ in range(1000):
    obs, reward, done, info = game.step(np.array([action0,action1,action2,action3]))
    action0 = actor0.action_from_state(obs, game.g_map)
    action1 = actor1.action_from_state(obs, game.g_map)
    action2 = actor2.action_from_state(obs, game.g_map)
    action3 = actor3.action_from_state(obs, game.g_map)
# game.play()

#%%
game.save_record('./records/record0.npy')

#%%
player = record_player()
player.play('./records/record_test.npy')

