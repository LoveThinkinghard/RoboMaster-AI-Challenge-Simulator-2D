from kernel import Kernel


class Rmaics(object):
    def __init__(self, agent_num, render=True):
        self.game = Kernel(robot_count=agent_num, render=render)
        # self.g_map = self.game.get_map()
        self.memory = []

    def reset(self):
        self.state = self.game.reset()
        self.obs = self.get_observation(self.state)
        return self.obs

    def step(self, actions):
        state = self.game.step(actions)
        obs = self.get_observation(state)
        rewards = self.get_reward(state)

        self.memory.append([self.obs, actions, rewards])
        self.state = state
        return obs, rewards, state.done, None
    
    def get_observation(self, state):
        # personalize your observation here
        obs = state
        return obs
    
    def get_reward(self, state):
        # personalize your reward here
        rewards = None
        return rewards

    def play(self):
        self.game.play()

    def save_record(self, file):
        self.game.save_record(file)