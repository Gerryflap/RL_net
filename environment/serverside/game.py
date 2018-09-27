from environment.state import State


class Game(object):
    def __init__(self, players: list, server):
        self.server = server
        self.players = players
        self.wait_queue = dict()

    def play_game(self):
        raise NotImplementedError

    def request_action(self, player_index, game_state:State):
        thread = self.players[player_index].request_action(game_state)
        self.wait_queue[player_index] = thread

    def get_requested_actions(self):
        actions = dict()
        for i, t in self.wait_queue.items():
            t.join()
            actions[i] = self.players[i].last_action
        self.wait_queue.clear()
        return actions

    def report_winners(self, winning_ids, losing_ids):
        self.server.end_game([self.players[i] for i in winning_ids], [self.players[i] for i in losing_ids], self)

    def report_draw(self):
        self.server.end_game_draw(self.players, self)