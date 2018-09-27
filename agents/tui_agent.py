from environment.client.player import Player
from environment.environment import Environment
from environment.state import State


class TUIAgent(Player):
    def __init__(self, server_addr, name: str, env: Environment, action_builder):
        super().__init__(server_addr, name, env)
        self.action_builder = action_builder

    def request_action(self, state: State):
        print("New Action Requested")
        print("Current State:")
        print(state)
        a = input("Please input action: ")
        action = self.action_builder(a)
        return action

    def game_start(self):
        print("You've joined a new game!")

    def game_end(self, winners, losers):
        print("Game has ended")
        if self.name in winners:
            print("You've won the game!")
        elif len(winners) == 0:
            print("It's a draw!")
        else:
            print("You've lost the game :(")
