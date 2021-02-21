import numpy as np
import pickle

# Indices of important robot properties in state.agents[car_num]
from modules.robot import Robot
from modules.waypoints.nav_graph import NavigationGraph

OWNER = 0
POS_X = 1
POS_Y = 2
ANGLE = 3
YAW = 4
BULLET_COUNT = 10

with open('waypoints.pk', 'rb') as f:
    data = pickle.load(f)
    waypoints = data[0]
    adjacency_matrix = data[1]

class Actor:
    def __init__(self, car_num):
        self.car_num = car_num
        self.team = 1 if car_num % 2 == 0 else 0 # Red = 0, Blue = 1
        self.prev_action = None
        self.next_waypoint = None
        self.destination = None
        self.nav = NavigationGraph()
        self.current_robot: Robot = Robot()
    
    def action_from_state(self, state, g_map):
        '''Given the current state of the arena, determine what this robot should do next
        using a simple rule-based algorithm. This action is represented as an array of numbers,
        which are interpreted by game.step()'''
        # action = [x, y, rotate, barrel_yaw, shoot, supply, shoot_mode, autoaim]
        x = y = rotate = yaw = shoot = supply = shoot_mode = 0
        autoaim = 1

        if self.get_property(state, BULLET_COUNT) == 0:
            supply_zone = g_map.areas[self.team][1]
            supply_zone_x = np.mean(supply_zone[:2])
            supply_zone_y = np.mean(supply_zone[2:])
            self.set_destination((supply_zone_x, supply_zone_y))
        elif np.sum(state.vision[self.car_num]) > 0:
            #TODO: Change this condition so it ignores friendly robots
            enemy_coords = g_map.areas[self.team][1]
            enemy_x = np.mean(enemy_coords[:2])
            enemy_y = np.mean(enemy_coords[2:])
            self.set_destination((enemy_x, enemy_y))
            
            shoot = 1
        
        x,y,rotate = self.navigate()

        action = [x, y, rotate, yaw, shoot, supply, shoot_mode, autoaim]
        
        self.prev_action = action
        return action

    @property
    def current_waypoint(self):
        return self.nav.get_nearest_waypoint(self.current_robot.center)

    def get_path(self, target_pos):
        return self.nav.calculate_path(self.current_waypoint, self.nav.get_nearest_waypoint(target_pos))

    
    def set_destination(self, dest):
        '''Update the robots (x,y) destination co-ordinates'''
        nav_path = self.get_path(dest)
    
    def navigate(self):
        '''Pathfind to the destination. Returns the x,y,rotation values'''
        # TODO: Implement this using the waypoint system to hop in the
        #       direction of the destination
        return 1, 0, 0

    def get_property(self, state, property):
        # TODO: Update this method to use the new standard for accessing robot properties
        return state.agents[self.car_num][property]
