"""
    This Q-Agent will not explore the environment, but will learn due to random opponents
"""
from collections import defaultdict

from environment.action import Action
from environment.client.player import Player
from environment.environment import Environment
from environment.state import State


class QAgent(Player):
    def __init__(self, server_addr, name: str, env: Environment, gamma, learning_rate, state_converter=lambda s: str(s)):
        super().__init__(server_addr, name, env)
        self.qsa = defaultdict(lambda: 0)
        self.prev_sa = None
        self.gamma = gamma
        self.learning_rate = learning_rate
        self.sc = state_converter

    def request_action(self, state: State):

        max_qsa, best_action = max([(self.Qsa(state, a), a) for a in self.env.get_possible_actions(state)], key=lambda t: t[0])

        if self.prev_sa is not None:
            s,a = self.prev_sa
            self.update_Qsa(s, a, self.learning_rate * (self.gamma * max_qsa - self.Qsa(s,a)))
        self.prev_sa = state, best_action
        return best_action

    def game_start(self):
        self.prev_sa = None

    def game_end(self, winners, losers):
        pass

    def Qsa(self, s: State, a: Action):
        return self.qsa[(self.sc(s), a)]

    def update_Qsa(self, s: State, a: Action, grad):
        s = self.sc(s)
        self.qsa[(s,a)] += grad
