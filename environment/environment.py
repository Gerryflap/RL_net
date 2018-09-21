"""
    Models an environment
"""
from environment.state import State


class Environment(object):

    def get_possible_actions(self, state: State):
        raise NotImplementedError

    def get_action_space(self):
        raise NotImplementedError

    def start_new_game(self, players: list, server):
        # Returns a new game
        raise NotImplementedError