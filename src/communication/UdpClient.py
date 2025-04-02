import socket

class UdpClient:
    def __init__(self, serverIP = "127.0.0.1", serverPort = 8888, bufferSize = 1024, protocol = socket.AF_INET, tiemout = 0.2):
        """
        Funkcja wykonuje operacje związane z komunikacją z serwerem.\n
        Parametry:\n
        serverIP    (str) : Adres IP serwera, z którym ma się komunikować klient.\n
        serverPort  (int) : Port serwera.\n
        bufferSize  (int) : Maksymalny rozmiar wiadomości przychodzących (w bajtach).\n
        protocol    (socket.AF_INET lub socket.AF_INET6) : Protokół komunikacji (np. 'ipv4' lub 'ipv6').\n
        timeout     (float) : czas oczekiwania na odbiór danych

        Zwraca:
        None
        """
        self.__serverIP = serverIP
        self.__serverPort = serverPort
        self.__bufferSize = bufferSize
        self.__protocol = protocol
        self.__timeout = tiemout

        self.__socket : socket.socket = self.__createSocket()
        self.__socket.settimeout(tiemout)
    
    def __createSocket(self):
        udpSocket = socket.socket(self.__protocol, socket.SOCK_DGRAM)
        return udpSocket
    
    def __createMessage(self, message):
        return message.encode()

    def createAndSendMessage(self, message):
        encodedMessage = self.__createMessage(message= message)
        self.__socket.sendto(encodedMessage,(self.__serverIP,self.__serverPort))
    
    def receiveMessage(self):
        try:
            data, server = self.__socket.recvfrom(self.__bufferSize)
        except (OSError, socket.timeout):
            return None, None
        return data.decode(), server

    def closeSocket(self):
        self.__socket.close()
    
    @property
    def bufferSize(self):
        return self.__bufferSize
    
    @bufferSize.setter
    def bufferSize(self, newSize):
        self.__bufferSize = newSize

    @property
    def timeout(self):
        return self.__timeout
    
    @timeout.setter
    def timeout(self, newTime):
        self.__timeout = newTime
        self.__socket.settimeout(newTime)




if __name__ == "__main__":
    clientUdp = UdpClient()
    clientUdp.createAndSendMessage("Left: 100")
    