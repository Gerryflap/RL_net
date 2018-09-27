"""
    The RandomAgent plays a random (possible) move when requested
"""

import random

from environment.client.player import Player
from environment.state import State


class RandomAgent(Player):
    def request_action(self, state: State):
        return random.choice(self.env.get_possible_actions(state))

    def game_start(self):
        pass

    def game_end(self, winners, losers):
        pass