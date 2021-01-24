# -*- coding: utf-8 -*-
from rmaics import rmaics
from kernal import record_player

#%%
game = rmaics(agent_num=4, render=True)
game.reset()
# only when render = True
game.play()

#%%
game.save_record('./records/record0.npy')

#%%
'''
player = record_player()
player.play('./records/record_test.npy')
'''
