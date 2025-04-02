# Import globalnych bibliotek
import unittest
import sys
import os
import subprocess
from time import sleep, time
from json import dumps, loads

# Import lokalnych modułów
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..', '..')))
from src.communication.UdpClient import UdpClient

class TestUdpClientWithActiveServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server_process = subprocess.Popen(['python', os.path.join(".","stubs","StubUdpServer.py"),'127.0.0.1', '8888', '1024'])
        sleep(1)
        

    @classmethod
    def tearDownClass(cls):
        cls.server_process.terminate()

    def createSocketClient(self):
        self.__UdpSocketClient = UdpClient()

    def test_SendGoodData(self):
        message = {'LEFT' : 100}
        self.createSocketClient()
        self.__UdpSocketClient.createAndSendMessage(dumps(message))
        data, _ = self.__UdpSocketClient.receiveMessage()
        print(data)
        self.__UdpSocketClient.closeSocket()
        self.assertEqual(loads(data), message)

    def test_SendNoGoodData(self):
        message = "LEFT: 100000000000000000"
        exceptData = None
        self.createSocketClient()
        self.__UdpSocketClient.createAndSendMessage(message)
        self.__UdpSocketClient.bufferSize = 5
        data, _ = self.__UdpSocketClient.receiveMessage()
        self.__UdpSocketClient.closeSocket()
        self.assertEqual(data, exceptData)
    
    def test_changeSize(self):
        message = "LEFT: 100000000000000000"
        exceptData = message
        self.createSocketClient()
        self.__UdpSocketClient.createAndSendMessage(message)
        self.__UdpSocketClient.bufferSize = 200
        data, _ = self.__UdpSocketClient.receiveMessage()
        self.__UdpSocketClient.closeSocket()

        self.assertEqual(self.__UdpSocketClient.bufferSize, 200)
        self.assertEqual(data, exceptData)
    
    def test_SendTenPackageGoodDataWithCloseConnection(self):
        for _ in range(10):
            message = "LEFT: 100"
            self.createSocketClient()
            self.__UdpSocketClient.createAndSendMessage(message)
            data, _ = self.__UdpSocketClient.receiveMessage()
            self.__UdpSocketClient.closeSocket()
            self.assertEqual(data, message)
    
    def test_SendTenPackageGoodDataWithOutCloseConnection(self):
        self.createSocketClient()
        for _ in range(10):
            message = "LEFT: 100"
            self.__UdpSocketClient.createAndSendMessage(message)
            data, _ = self.__UdpSocketClient.receiveMessage()
            self.assertEqual(data, message)
        self.__UdpSocketClient.closeSocket()
    
    def test_SendDataWhenServerIsNotDisabled(self):
        self.createSocketClient()
        for _ in range(10):
            message = "LEFT: 100"
            self.__UdpSocketClient.createAndSendMessage(message)
            data, _ = self.__UdpSocketClient.receiveMessage()
            self.assertEqual(data, message)
        self.__UdpSocketClient.closeSocket()

    __UdpSocketClient = None

class TestUdpClientWithOutActiveServer(unittest.TestCase):

    def createSocketClient(self):
        self.__UdpSocketClient = UdpClient()

    def test_SendGoodData(self):
        message = "LEFT: 100"
        exceptData = None
        self.createSocketClient()
        self.__UdpSocketClient.createAndSendMessage(message)
        data, _ = self.__UdpSocketClient.receiveMessage()
        self.__UdpSocketClient.closeSocket()
        self.assertEqual(data, exceptData)

    def test_SendTenGoodData(self):
        for _ in range(10):
            message = "LEFT: 100"
            exceptData = None
            self.createSocketClient()
            self.__UdpSocketClient.createAndSendMessage(message)
            data, _ = self.__UdpSocketClient.receiveMessage()
            self.__UdpSocketClient.closeSocket()
            self.assertEqual(data, exceptData)

    def test_CheckTimeoutAndTimeOfLast(self):
        message = "LEFT: 100"
        exceptData = None
        timeout = 0.2
        self.createSocketClient()
        self.__UdpSocketClient.createAndSendMessage(message)

        # Dla czasu 0.2
        self.__UdpSocketClient.timeout = timeout
        timeStart = time()
        data, _ = self.__UdpSocketClient.receiveMessage()
        timeEnd = time() - timeStart

        self.assertLessEqual(abs(timeout - timeEnd), 0.005)
        self.assertEqual(self.__UdpSocketClient.timeout, timeout)
        self.assertEqual(data, exceptData)


        timeout = 0.5
        # Dla czasu 0.5
        self.__UdpSocketClient.timeout = timeout
        timeStart = time()
        data, _ = self.__UdpSocketClient.receiveMessage()
        timeEnd = time() - timeStart

        self.assertLessEqual(abs(timeout - timeEnd), 0.002)
        self.assertEqual(self.__UdpSocketClient.timeout, timeout)
        self.assertEqual(data, exceptData)


        self.__UdpSocketClient.closeSocket()

        


if __name__ == "__main__":
    unittest.main()