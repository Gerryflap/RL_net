import random
import threading
import time

from environment.environment import Environment
from environment.serverside.competition import Competition
import socket

from environment.serverside.player import NetworkPlayer


class Server(object):
    def __init__(self, listen_addr, competition_config_path, env: Environment):
        print("Starting server")
        self.comp = Competition(competition_config_path)
        self.ip, self.port = listen_addr
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(listen_addr)
        self.socket.listen(1)
        self.connected_players = dict()
        self.connected_lock = threading.Lock()
        self.searching = list()
        self.searching_lock = threading.Lock()
        self.comp_lock = threading.Lock()
        self.active_games = dict()
        self.env = env
        self.queue_manager = threading.Thread(target=self.game_queue_manager)
        self.running = True

    def run(self):
        self.queue_manager.start()
        try:
            print("Waiting for connections")
            while True:
                connection, client_address = self.socket.accept()

                command = connection.recv(4096)
                command = command.decode("utf-8")

                if command.startswith('GET'):
                    self.handle_http(connection)
                elif command.startswith("CONNECT"):
                    self.handle_connect(connection, command)
                else:
                    print("Received invalid command: ", command)
                    connection.close()

        except KeyboardInterrupt:
            print("Closing Server!")
            self.running = False
            self.comp.exit()
            self.socket.close()
            exit()

    def handle_http(self, conn):
        s = ""
        for id, score in self.comp.get_leaderboard():
            s += "%s: %.2f <br>\n"%(id, score)
        html = "<html><body><h1>Players and scores: </h1>%s</body></html>"%(s,)
        conn.sendall(("HTTP/1.1 200 OK\nContent-Type: text/html\ncontent-length: %d\n\n"%(len(html,)) + html).encode('utf-8'))
        conn.close()

    def handle_connect(self, conn, message):
        message = message.split("\n")[0]
        split = message.split(" ")
        id = split[1]
        print("Player ", id, " connected")
        with self.connected_lock:
            self.comp.register_player(id)
            self.connected_players[id] = NetworkPlayer(id, conn, self)
            with self.searching_lock:
                self.searching.append(id)

    def game_queue_manager(self):
        while self.running:
            with self.searching_lock:
                with self.comp_lock:
                    while len(self.searching) >= 2:
                        p1 = random.choice(self.searching)
                        #print("Matchmaking with ", p1)

                        p2 = self.comp.find_best_match(p1, self.searching)
                        if p1 not in self.connected_players:
                            print("Removing disconnected player from queue: ", p1)
                            self.searching.remove(p1)
                            break
                        if p2 not in self.connected_players:
                            print("Removing disconnected player from queue: ", p2)
                            self.searching.remove(p2)
                            break
                        #print(self.searching, p1, p2)
                        self.searching.remove(p1)
                        self.searching.remove(p2)

                        for p in [self.connected_players[p1], self.connected_players[p2]]:
                            p.game_start()

                        #print(self.connected_players)
                        game = self.env.start_new_game([self.connected_players[p1], self.connected_players[p2]], self)
                        self.active_games[game] = threading.Thread(target=game.play_game)
                        self.active_games[game].start()
            time.sleep(0.001)

    def end_game(self, winners, losers, game):
        winner_ids, loser_ids = list([p.id for p in winners]), list([p.id for p in losers])
        #print("Game end in server: ", winner_ids, loser_ids)
        for p in winners + losers:
            p.game_end(winner_ids, loser_ids)

        with self.comp_lock:
            self.comp.register_win(winner_ids, loser_ids)
            del self.active_games[game]
            del game

        with self.searching_lock:
            self.searching += list([p.id for p in winners]) + list([p.id for p in losers])
        #print("Game closed on Server")

    def end_game_draw(self, players, game):

        pids = list([p.id for p in players])
        for p in players:
            p.game_end([], pids)

        with self.comp_lock:
            self.comp.register_draw(pids)
            if game in self.active_games:
                del self.active_games[game]
            del game

        with self.searching_lock:
            self.searching += pids
        #print("Game closed on Server")

    def deregister_player(self, p: NetworkPlayer):
        print("Player %s disconnected" % p.id)
        with self.connected_lock and self.comp_lock and self.searching_lock:
            del self.connected_players[p.id]
            if p in self.searching:
                self.searching.remove(p)








if __name__ == "__main__":
    s = Server(('localhost', 1338), "leaderboard.json", Environment())
    s.run()