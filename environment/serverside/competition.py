import json
import os


class Competition(object):
    def __init__(self, fpath):
        self.fpath = fpath
        if fpath is not None and os.path.isfile(fpath):
            print("Loading previous ranked scores")
            with open(fpath, "r") as f:
                config = json.load(f)

            self.ranks = config
        else:
            self.ranks = dict()

    def register_player(self, id):
        if id not in self.ranks:
            self.ranks[id] = 0

    def get_leaderboard(self):
        return sorted(self.ranks.items(), reverse=True, key=lambda t: t[1])

    def register_win(self, winner_ids, loser_ids):
        avg_winner_score = sum([self.ranks[id] for id in winner_ids]) / len(winner_ids)
        avg_loser_score = sum([self.ranks[id] for id in loser_ids]) / len(loser_ids)
        #print("Competition recieved winners and losers: ", winner_ids, loser_ids)

        # This function has been determined by trail and error
        try:
            elo_diff = min(10, 1.05 ** (avg_loser_score - avg_winner_score))
        except OverflowError:
            return min(10, abs(avg_loser_score - avg_winner_score))

        for winner in winner_ids:
            self.ranks[winner] += elo_diff

        for loser in loser_ids:
            self.ranks[loser] -= elo_diff

        return elo_diff

    def find_best_match(self, id, online_players):
        p, diff = min([(player, abs(self.ranks[id] - self.ranks[player])) for player in online_players if player != id],
                      key=lambda t: t[1])
        return p

    def exit(self):
        if self.fpath is not None:
            print("Saving competition...")
            with open(self.fpath, "w") as f:
                json.dump(self.ranks, f)
            print("Saved competition successfully!")


if __name__ == "__main__":

    import random
    import matplotlib.pyplot as plt

    steps = 100000
    test_player_skills = {"legend": 40, "master": 4, "pro": 2, "amateur": 1, "amateur2": 1.3, "noob": 0.5, "useless": 0.01}
    test_player_score_graph = {id: list() for id in test_player_skills.keys()}
    exclude_till_half = {"legend"}

    comp = Competition(None)
    for player in test_player_skills.keys():
        comp.register_player(player)

    for i in range(steps):
        p = random.choice(list(test_player_skills.keys() - exclude_till_half))
        opponent = comp.find_best_match(p, test_player_skills.keys() - exclude_till_half)
        p1_win_prob = test_player_skills[p]/(test_player_skills[p] + test_player_skills[opponent])
        if random.random() < p1_win_prob:
            comp.register_win([p], [opponent])
        else:
            comp.register_win([opponent], [p])

        for player in test_player_score_graph:
            test_player_score_graph[player].append(comp.ranks[player])

        if steps/2 == i:
            exclude_till_half = {}

    print(comp.get_leaderboard())

    for player in test_player_score_graph:
        plt.plot(test_player_score_graph[player])
    plt.show()