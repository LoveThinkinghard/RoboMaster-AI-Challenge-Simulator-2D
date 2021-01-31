import numpy as np

BULLET_IDX = 10

class Actor:
    def __init__(self, car_num):
        self.car_num = car_num
        self.team = 1 if car_num % 2 == 0 else 0
        self.prev_action = None
    
    def action_from_state(self, state, g_map):
        # action = [x, y, rotate, yaw, shoot, supply, shoot_mode, autoaim]
        x = y = rotate = yaw = shoot = supply = shoot_mode = 0
        autoaim = 1

        if state.agents[self.car_num][BULLET_IDX] == 0:
            x,y,rotate = self.find_ammo(g_map)

        #TODO: change this condition so it ignores friendly robots
        elif np.sum(state.vision[self.car_num]) > 0:
            shoot = 1
            x,y,rotate = self.attack_enemy()

        action = [x, y, rotate, yaw, shoot, supply, shoot_mode, autoaim]
        
        self.prev_action = action
        return action
    
    def find_ammo(self, g_map):
        # borders is the location of the borders of the supply zone
        borders = g_map.areas[self.team][1] # Index 1 represents the supply zone
        
        # TODO: Tell the robot to move towards the supply zone

        return 0, 0, 0

    def attack_emeny(self):
        return 0, 0, 0
