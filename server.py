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
        self.queue_manager.start()

    def run(self):
        try:
            print("Waiting for connections")
            while True:
                connection, client_address = self.socket.accept()
                print("New connection: ", client_address)

                command = connection.recv(4096)
                command = command.decode("utf-8")

                if command.startswith('GET'):
                    print("Handling GET request")
                    self.handle_http(connection)
                    print("Handled GET request")
                elif command.startswith("CONNECT"):
                    self.handle_connect(connection, command)
                else:
                    print("Received invalid command: ", command)
                    connection.close()


        except KeyboardInterrupt:
            print("Closing Server!")
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
        while True:
            with self.searching_lock:
                if len(self.searching) >= 2:
                    with self.comp_lock:
                        p1 = random.choice(self.searching)
                        p2 = self.comp.find_best_match(random.choice(self.searching), self.searching)

                        game = self.env.start_new_game([self.connected_players[p1], self.connected_players[p2]], self)
                        self.active_games[game] = threading.Thread(target=game.play_game)
                        self.active_games[game].start()
            time.sleep(0.1)

    def end_game(self, winners, losers, game):
        with self.comp_lock:
            self.comp.register_win([p.id for p in winners], [p.id for p in losers])
            del self.active_games[game]
            del game

        with self.searching_lock:
            self.searching += list([p.id for p in winners]) + list([p.id for p in losers])






if __name__ == "__main__":
    s = Server(('localhost', 1337), "leaderboard.json", Environment())
    s.run()