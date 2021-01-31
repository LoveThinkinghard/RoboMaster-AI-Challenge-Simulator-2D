import numpy as np

BULLET_IDX = 10

class Actor:
    def __init__(self, car_num):
        self.car_num = car_num
        self.team = 1 if car_num % 2 == 0 else 0 # Red = 0, Blue = 1
        self.prev_action = None
        self.destination = None
    
    def action_from_state(self, state, g_map):
        # action = [x, y, rotate, barrel_yaw, shoot, supply, shoot_mode, autoaim]
        x = y = rotate = yaw = shoot = supply = shoot_mode = 0
        autoaim = 1

        if state.agents[self.car_num][BULLET_IDX] == 0:
            supply_zone = g_map.areas[self.team][1]
            supply_zone_x = np.mean(supply_zone[:2])
            supply_zone_y = np.mean(supply_zone[2:])
            self.set_destination((supply_zone_x, supply_zone_y))
        elif np.sum(state.vision[self.car_num]) > 0:
            #TODO: Change this condition so it ignores friendly robots
            shoot = 1
            x,y,rotate = self.attack_enemy()

        action = [x, y, rotate, yaw, shoot, supply, shoot_mode, autoaim]
        
        self.prev_action = action
        return action

    def attack_enemy(self):
        return 0, 0, 0
    
    def set_destination(self, dest):
        '''Update the robots (x,y) destination co-ordinates'''
        self.destination = dest
    
    def navigate(self):
        '''Pathfind to the destination. Returns the x,y,rotation values'''
        return 0, 0, 0
