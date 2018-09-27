


class MessageSocket(object):
    def __init__(self, sock):
        self.socket = sock
        self.remaining_bytes = None

    def send(self, message: bytes):
        message = (len(message)).to_bytes(4, 'big') + message
        self.socket.sendall(message)


    def recv(self):
        # Receives the next full message
        if self.remaining_bytes is not None:
            packet = self.remaining_bytes
            self.remaining_bytes = None
        else:
            packet = self.socket.recv(4096)

        message_length = int.from_bytes(packet[:4], 'big')
        packet = packet[4:]
        if message_length < len(packet):
            self.remaining_bytes = packet[message_length:]
            return packet[:message_length]
        elif message_length == len(packet):
            return packet
        else:
            packet += self.socket.recv(message_length - len(packet))
            return packet
