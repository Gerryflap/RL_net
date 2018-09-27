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
    from environments.random_env.client import RandomClient
    import threading

    server_addr = ('localhost', 1337)

    c1 = RandomClient(server_addr, "Player1", RandomEnv())
    c2 = RandomClient(server_addr, "Player2", RandomEnv())
    s = server.Server(server_addr, "randomcomp", RandomEnv())

    s_thread = threading.Thread(target=s.run)
    s_thread.start()
    #s.run()

    for c in [c1, c2]:
        threading.Thread(target=c.run).start()

    s_thread.join()
