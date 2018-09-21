import random

from environment.environment import Environment
from environment.serverside.game import Game
from environment.state import State


class RandomEnv(Environment):
    def get_possible_actions(self, state: State):
        return []

    def get_action_space(self):
        return []

    def start_new_game(self, players: list, server):
        return RandomGame(players, server)


class RandomGame(Game):
    def play_game(self):
        if random.random() > 0.5:
            self.report_winners([0], [1])
        else:
            self.report_winners([1], [0])


if __name__ == "__main__":
    import server
    s = server.Server(('localhost', 1336), "randomcomp", RandomEnv())
    s.run()
