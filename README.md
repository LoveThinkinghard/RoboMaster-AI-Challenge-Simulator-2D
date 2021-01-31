# RoboMaster AI Challenge Simulator 2D

RoboMaster AI Challenge Simulator 2D，abbreviated as`RMAICS`，is a simulator designed for participating 
in the [ICRA 2019 RoboMaster AI Challenge](https://www.robomaster.com/zh-CN/resource/pages/980?type=announcementSub).
 Its main function is to provide a simulation environment for intelligent decision-making groups to train neural networks.

![demo](./demo.gif)

The frame rate of the game is around 200fps, but the frame rate for gifs are capped at 60fps

## 1. Dependencies

numpy

[pygame](https://www.pygame.org/)（only for visualisation）

## 2. User Guide

### 1. Basic Information

The simulation consists of two levels:

> The high-level package class: `rmaics`  
> The low-level implementation: `kernal`

The user needs to define in `rmaisc` the `get_observation` and `get_reward` function in the class to define the observation 
value and reward value; 
the `kernal` class is only responsible for the simulation of the physical environment and the referee system.
Therefore, when training the network, the ones that directly deal with users are `rmaisc` classified as

### 2. Content Citation

Please find the content you need according to the following references

High-level training interface in `rmaics.py`：[rmaics_manual.md](./docs/rmaics_manual.md)

Low level simulation implementation in `kernel.py`：[kernal_manual.md](docs/kernel_manual.md)

Instructions for `record player`：[record_player.md](./docs/record_player.md)

Instructions for controls：[operation.md](./docs/operation.md)

Parameter format：[params.md](./docs/params.md)

`kernel` development guide：[develop.md](./docs/develop.md)


