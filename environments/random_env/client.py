from environment.client.player import Player
from environment.state import State


class RandomClient(Player):
    def request_action(self, state: State):
        print("Got action request with state ", state, " this should not happen in RandomEnv!!!!")
        return None

    def game_start(self):
        print("Game has started")

    def game_end(self, winners, losers):
        print("Game ended")
        print("We (%s) have %s"%(self.name, "won" if winners[0] == self.name else "lost"))
