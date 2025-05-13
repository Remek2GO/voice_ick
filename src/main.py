import multiprocessing as mp
import sys
import socket
import os
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.communication.UdpClient import UdpClient
from src.detection.VoiceCommandRecognizer import VoiceCommandRecognizer

logging.basicConfig(level=logging.DEBUG,  # Ustawiamy minimalny poziom logowania
                    format='%(asctime)s - %(levelname)s - %(message)s')  # Format logów

def communication(queue : mp.Queue, serverIP = "127.0.0.1", serverPort = 8888, bufferSize = 1024, protocol = socket.AF_INET, tiemout = 0.2):
    udpClient = UdpClient(serverIP=serverIP, serverPort=serverPort,bufferSize=bufferSize,protocol=protocol,tiemout=tiemout)
    try:
        while True:
            message = queue.get()
            udpClient.createAndSendMessage(message)
            logging.info(f"Message was send - MSG: {message}")

    finally:
        udpClient.closeSocket()



def main(command_file, model_path, serverIP = "127.0.0.1", serverPort = 8888, bufferSize = 1024, protocol = socket.AF_INET, tiemout = 0.2):
    voskQueue = mp.Queue(20)
    voiceCommandRecognizer = VoiceCommandRecognizer(model_path=model_path,commands_file=command_file)
    udpClientProcess = mp.Process(target=communication, args=(voskQueue,serverIP,serverPort,bufferSize,protocol,tiemout))
    udpClientProcess.start()
    logging.info("Application was setuped")
    try:
        while True:
            recognitedText =voiceCommandRecognizer.process_audio()
            if recognitedText is not None:
                voskQueue.put(recognitedText)
    finally:
        udpClientProcess.terminate()



if __name__ == "__main__":
    commands_file = os.path.join("commands.json")
    model_path = os.path.join("models", "vosk-model-small-en-us-0.15")
    serverIP = "127.0.0.1"
    serverPort = 8888
    bufferSize = 1024
    protocol = socket.AF_INET
    tiemout = 0.2
    main(command_file= commands_file, model_path= model_path,serverIP=serverIP,
            serverPort=serverPort,bufferSize=bufferSize,protocol=protocol,tiemout=tiemout)
