"""Script for Tkinter GUI chat client."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread, Lock
from tkinter import *
import chess


BUFFER_SIZE = 1024
LOCK = Lock()

class Connection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.msg_queue = []
    
    def connect(self, username):
        # Establish socket connection
        self.sock.connect(self.addr)

        # Send username
        self.sock.send(username.encode())

        # Get role and board
        data = []

    def receive(self):
        """ Handles receiving of messages. """
        try:
            data = self.sock.recv(BUFFER_SIZE).decode()
            if data:
                return data
            else:
                return False
        except OSError:
            pass

    def send(self, data):
        """ Handles sending of messages. """
        self.sock.send(data)

    def close(self):
        """ Close connection. """
        self.sock.send("EVENT:LEAVE".encode())
        self.sock.close()