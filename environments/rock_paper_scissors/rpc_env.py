import random

from environment.action import Action
from environment.environment import Environment
from environment.serverside.game import Game
from environment.state import State


class RPCAction(Action):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "A(%s)"%(self.name)

class RPCState(State):
    def __init__(self, iteration):
        self.i = iteration

    def __repr__(self):
        return "S(%d)"%self.i

action_space = [RPCAction("Rock"), RPCAction("Paper"), RPCAction("Scissors")]


class RPCEnv(Environment):
    def get_possible_actions(self, state: State):
        return action_space

    def get_action_space(self):
        return action_space

    def start_new_game(self, players: list, server):
        return RPCGame(players, server)


class RPCGame(Game):
    def play_game(self):
        r0, r1 = 0, 0
        for i in range(10):
            i = 0
            self.request_action(0, RPCState(i))
            print("Requested first action")
            self.request_action(1, RPCState(i))
            print("Requested second action")

            A = self.get_requested_actions()

            if A[0].name == "Rock":
                if A[1].name == "Rock":
                    i += 1
                    continue
                elif A[1].name == "Paper":
                    r0, r1 = -1, 1
                    break
                else:
                    r0, r1 = 1, -1
                    break
            elif A[0].name == "Paper":
                if A[1].name == "Paper":
                    i += 1
                    continue
                elif A[1].name == "Scissors":
                    r0, r1 = -1, 1
                    break
                else:
                    r0, r1 = 1, -1
                    break
            else:
                if A[1].name == "Scissors":
                    i += 1
                    continue
                elif A[1].name == "Rock":
                    r0, r1 = -1, 1
                    break
                else:
                    r0, r1 = 1, -1
                    break

        if r0 == 0:
            w = round(random.random())
            l = (w + 1) % 2

        else:
            if r0 == 1:
                w = 1
                l = 0
            else:
                w = 0
                l = 1

        self.report_winners([w], [l])
        return


if __name__ == "__main__":
    from environments.rock_paper_scissors.clients import RandomAgent, OnlyOne
    from server import Server
    import threading

    server_name = ('localhost', 1339)

    s = Server(server_name, "rpc_rankings", RPCEnv())
    clients = [
        RandomAgent(server_name, "random", RPCEnv()),
        OnlyOne(server_name, "OnlyPaper", RPCEnv(), action_space[1]),
        OnlyOne(server_name, "OnlyRock", RPCEnv(), action_space[0]),
    ]

    for c in clients:
        threading.Thread(target=c.run).start()

    s.run()