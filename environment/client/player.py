"""
    Clientside player
    An interface to communicate with the competition server
"""
import socket
import pickle
import time

from environment.environment import Environment
from environment.state import State
from util.message_socket import MessageSocket


class Player(object):
    def __init__(self, server_addr, name: str, env: Environment):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message_sock = MessageSocket(self.socket)
        self.env = env
        self.server_addr = server_addr
        self.name = name

    def run(self):
        while True:
            try:
                self.socket.connect(self.server_addr)
                break
            except ConnectionRefusedError:
                print("Connection refused, attempting to reconnect in 1 second...")
                time.sleep(1)
        self.socket.send(("CONNECT "+self.name + "\n").encode('UTF-8'))

        # Main loop
        while True:
            packet = self.message_sock.recv()
            print(packet)

            packet = packet.decode("UTF-8")


            if not packet.startswith("START"):
                continue

            self.game_start()
            # We're playing the game now

            playing = True
            while playing:
                packet = self.message_sock.recv()
                try:
                    packet = packet.decode("UTF-8")
                except UnicodeDecodeError:
                    print(packet)
                    print(pickle.loads(packet))

                if packet.startswith("ACTION_REQUEST"):
                    n_packets = int(packet.split(" ")[1])
                    print("Receiving ", n_packets, " state packets")
                    state_packet = self.message_sock.recv()
                    state = pickle.loads(state_packet)
                    print("State: ", state)
                    action = self.request_action(state)
                    self.message_sock.send(pickle.dumps(action))
                else:
                    splitted = packet.split(" ")
                    winstr = splitted[1]
                    lossstr = splitted[2]
                    winners = winstr.split(",")
                    losers = lossstr.split(",")
                    self.game_end(winners, losers)
                    playing = False

    def request_action(self, state: State):
        raise NotImplementedError

    def game_start(self):
        raise NotImplementedError

    def game_end(self, winners, losers):
        raise NotImplementedError


