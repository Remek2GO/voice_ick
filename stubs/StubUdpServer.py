import socket
import sys

class StubServerUDP:
    def __init__(self, host, port, buffsize):
        self.host = host
        self.port = port
        self.buffsize = buffsize
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.start()

    def start(self):
        while True:
            data, addr = self.sock.recvfrom(self.buffsize)
            self.sock.sendto(data, addr)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(1)
    host = sys.argv[1]
    port = int(sys.argv[2])
    buffSize = int(sys.argv[3])

    port = 8888
    StubServerUDP(host,port, buffSize)
    