"""
    Models a player over the network
"""
import math
import pickle
import socket
import threading

from environment.state import State


class NetworkPlayer(object):
    def __init__(self, id, socket, server):
        self.socket = socket
        self.id = id
        self.server = server
        self.last_action = None
        self.socket.settimeout(60.0)

    def request_action(self, state: State):
        s = pickle.dumps(state)
        packs = math.ceil(len(s)/4096)
        self.socket.sendall("ACTION_REQUEST "+str(packs))
        self.socket.sendall(s)

        wait_thread = threading.Thread(target=self.wait)
        wait_thread.start()

        return wait_thread

    def wait(self):
        try:
            a = self.socket.recv(4096)
        except socket.timeout:
            self.handle_timeout(True)
            return
        action = pickle.loads(a)
        self.last_action = action

    def handle_timeout(self, in_game):
        if in_game:
            pass
        self.server.deregister_player(self)
