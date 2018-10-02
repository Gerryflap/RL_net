"""
    This Q-Agent will explore the environment by picking a move based on SoftMax probabilities of the values
"""
import math
import random
from collections import defaultdict

from environment.action import Action
from environment.client.player import Player
from environment.environment import Environment
from environment.state import State


class SMaxQAgent(Player):
    def __init__(self, server_addr, name: str, env: Environment, gamma, learning_rate, state_converter=lambda s: str(s), temp=1):
        super().__init__(server_addr, name, env)
        self.qsa = defaultdict(lambda: 0)
        self.prev_sa = None
        self.gamma = gamma
        self.learning_rate = learning_rate
        self.sc = state_converter
        self.temp = temp

    def request_action(self, state: State):

        softmax_sum = sum([math.exp(self.Qsa(state, a)/self.temp) for a in self.env.get_possible_actions(state)])
        softmaxed_actions = [(math.exp(self.Qsa(state, a)/self.temp)/softmax_sum, a) for a in self.env.get_possible_actions(state)]

        p_mass = 0
        p_val = random.random()
        chosen_action = None

        for p, a in softmaxed_actions:
            p_mass += p
            if p_val <= p_mass:
                chosen_action = a
        assert chosen_action is not None
        max_qsa, _ = max([(self.Qsa(state, a), a) for a in self.env.get_possible_actions(state)], key=lambda t: t[0])

        if self.prev_sa is not None:
            s,a = self.prev_sa
            self.update_Qsa(s, a, self.learning_rate * (self.gamma * max_qsa - self.Qsa(s,a)))
        self.prev_sa = state, chosen_action
        return chosen_action

    def game_start(self):
        self.prev_sa = None

    def game_end(self, winners, losers):
        if self.prev_sa is None:
            return
        s,a = self.prev_sa
        if self.name in winners:
            r = 1
        elif len(winners) == 0:
            r = 0
        else:
            r = -1
        self.update_Qsa(s, a, self.learning_rate * (self.gamma * r - self.Qsa(s, a)))


    def Qsa(self, s: State, a: Action):
        return self.qsa[(self.sc(s), a)]

    def update_Qsa(self, s: State, a: Action, grad):
        s = self.sc(s)
        self.qsa[(s,a)] += grad
