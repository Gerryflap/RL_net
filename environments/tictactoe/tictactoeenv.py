import math

from agents.q_agent import QAgent
from agents.random_agent import RandomAgent
from agents.softmax_q_agent import SMaxQAgent
from environment.action import Action
from environment.environment import Environment
from environment.serverside.game import Game, DisconnectException
from environment.state import State


class TTTState(State):
    def __init__(self, board):
        # Board contains player index or -1 for empty squares
        self.board = board[:]

    def __repr__(self):
        s = ""
        for row in range(3):
            for col in range(3):
                s += "%2d "%self.board[row*3 + col]
            s += "\n"
        return s


class TTTAction(Action):
    def __init__(self, index):
        self.i = index


action_space = list([TTTAction(i) for i in range(9)])


class TTTEnvironment(Environment):
    def get_possible_actions(self, state: TTTState):
        return list([a for a in action_space if state.board[a.i] == -1])

    def get_action_space(self):
        return action_space

    def start_new_game(self, players: list, server):
        return TTTGame(players, server)


class TTTGame(Game):
    def __init__(self, players: list, server):
        super().__init__(players, server)
        self.board = [-1]*9

    def play_game(self):
        player = 0
        other_player = 1

        #print("Playing TTT with", self.players)

        while True:
            self.request_action(player, TTTState(self.board))
            try:
                A = self.get_requested_actions()
            except DisconnectException:
                print("Disconnect happened!")
                self.report_draw()
                return
            action = A[player]
            if self.board[action.i] != -1:
                self.report_winners([other_player], [player])
                break
            self.board[action.i] = player

            if self.is_full():
                self.report_draw()
                break

            if self.get_winner() != -1:
                winner = self.get_winner()
                loser = (winner + 1)%2
                self.report_winners([winner], [loser])
                #print("Reported winners: ", self.players[winner], self.players[loser])
                break
            player, other_player = other_player, player

    def is_full(self):
        for i in range(9):
            if self.board[i] == -1:
                return False
        return True

    def get_winner(self):
        # Returns player index of winner or -1 if no winner
        for row in range(3):
            i = row*3
            if self.board[i] != -1 and self.board[i] == self.board[i+1] and self.board[i+1] == self.board[i+2]:
                return self.board[i]

        for col in range(3):
            i = col
            if self.board[i] != -1 and self.board[i] == self.board[i+3] and self.board[i+3] == self.board[i+6]:
                return self.board[i]

        if self.board[0] != -1 and self.board[0] == self.board[4] and self.board[4] == self.board[8]:
            return self.board[0]

        if self.board[2] != -1 and self.board[2] == self.board[4] and self.board[4] == self.board[6]:
            return self.board[2]
        return -1


if __name__ == "__main__":
    from server import Server
    import threading

    server_name = ('localhost', 1337)

    s = Server(server_name, "ttt_rankings", TTTEnvironment())
    clients = [
        RandomAgent(server_name, "Random1", TTTEnvironment()),
        RandomAgent(server_name, "Random2", TTTEnvironment()),
        #QAgent(server_name, "QAgent2", TTTEnvironment(), 0.9, 0.1),
        QAgent(server_name, "ShortSightedQAgent", TTTEnvironment(), 0.1, 0.1),
        QAgent(server_name, "HighGammaQAgent", TTTEnvironment(), 0.999, 0.1),
        QAgent(server_name, "SlowQAgent", TTTEnvironment(), 0.9, 0.01),
        QAgent(server_name, "FastQAgent", TTTEnvironment(), 0.9, 0.3),
    ] + list([QAgent(server_name, "QAgent%d"%i, TTTEnvironment(), 0.9, 0.1) for i in range(10)]) \
        + list([SMaxQAgent(server_name, "SMaxQAgent%d" % i, TTTEnvironment(), 0.9, 0.1, temp=math.exp((i-5))) for i in range(10)])

    for c in clients:
        threading.Thread(target=c.run).start()

    s.run()