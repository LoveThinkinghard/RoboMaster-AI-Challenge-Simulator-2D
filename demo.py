from rmaics import Rmaics
from record_player import record_player

if __name__ == '__main__':
    game = Rmaics(agent_num=4, render=True)
    game.play()

# game.save_record('./records/record0.npy')
# player = record_player()
# player.play('./records/record_test.npy')
