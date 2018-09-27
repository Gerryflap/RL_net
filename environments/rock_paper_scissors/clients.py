import random

from environment.action import Action
from environment.client.player import Player
from environment.environment import Environment
from environment.state import State


class RandomAgent(Player):
    def request_action(self, state: State):
        return random.choice(self.env.get_action_space())

    def game_start(self):
        pass

    def game_end(self, winners, losers):
        print("Game Ended on client")


class OnlyOne(Player):
    def request_action(self, state: State):
        return self.a

    def game_start(self):
        pass

    def game_end(self, winners, losers):
        print("Game Ended on client")

    def __init__(self, server_addr, name: str, env: Environment, a: Action):
        super().__init__(server_addr, name, env)
        self.a = a
