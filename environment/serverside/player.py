"""
    Models a player over the network
"""
import math
import pickle
import socket
import threading

from environment.state import State
from util.message_socket import MessageSocket


class NetworkPlayer(object):
    def __init__(self, id, socket, server):
        self.socket = socket
        self.message_sock = MessageSocket(socket)
        self.id = id
        self.server = server
        self.last_action = None
        self.socket.settimeout(60.0)

    def request_action(self, state: State):
        s = pickle.dumps(state)
        packs = math.ceil(len(s)/4096)
        self.message_sock.send(("ACTION_REQUEST "+str(packs)+"\n").encode('utf-8'))
        self.message_sock.send(s)

        wait_thread = threading.Thread(target=self.wait)
        wait_thread.start()

        return wait_thread

    def game_start(self):
        self.message_sock.send("START\n".encode('utf-8'))

    def game_end(self, winners, losers):
        self.message_sock.send(("END %s %s\n"%(','.join(winners), ','.join(losers))).encode('utf-8'))

    def wait(self):
        try:
            a = self.message_sock.recv()
        except socket.timeout:
            self.handle_timeout(True)
            return
        action = pickle.loads(a)
        print("Received action ", action)
        self.last_action = action

    def handle_timeout(self, in_game):
        if in_game:
            pass
        self.server.deregister_player(self)
