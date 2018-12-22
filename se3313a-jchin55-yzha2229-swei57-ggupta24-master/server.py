import json
import chess
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread, Lock

from constants import *

HOST = input("HOST: ")
PORT = int(input("PORT: "))

class User:
    def __init__(self, sock, addr, uid, name, role=ROLE.SPECTATOR):
        self.sock = sock
        self.addr = addr
        self.uid = uid
        self.name = name
        self.role = role

    def send(self, data):
        self.sock.send(data)

    def close(self):
        self.sock.close()

    def get_role(self):
        if self.role == ROLE.BLACK:
            return "black player"
        elif self.role == ROLE.WHITE:
            return "white player"
        elif self.role == ROLE.SPECTATOR:
            return "spectator"         

class Server:
    def __init__(self, host=HOST, port=PORT, buffer_size=BUFFER_SIZE, v=False):
        # Verbose
        self.v = v
       
        self.addr = (host, port)
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.board = chess.Board()

        self.users = []
        self.running = False
        self.client_threads = []

    def start(self):
        """ Start the server and listen for connections. """
        self.running = True

        self.sock.bind(self.addr)
        self.sock.listen(4)

        self.accept_thread = Thread(target=self.accept)
        self.accept_thread.start()

    def close(self):
        self.running = False
        for cthread in client_threads:
            cthread.join()
        self.accept_thread.join()
        self.sock.close()

    def accept(self):
        """ Take incoming connections off the queue and establish a connection. """
        while self.running:
            # Accept connection
            client_sock, client_addr = self.sock.accept()
            print("New connection {}.".format(client_addr))
            
            # Get name from first send
            name = client_sock.recv(BUFFER_SIZE).decode()
            
            # Add user to users list
            uid = len(self.users)
            user = User(client_sock, client_addr, uid, name, self.next_role())
            self.users.append(user)

            # Start handle thread for user
            cthread = Thread(target=self.handle_user, args=(user,))
            self.client_threads.append(cthread)
            cthread.start()

    def handle_user(self, user):
        """ Handles each user connection. """

        # Send the user's assigned role and current board state
        user.send(("ROLE:" + user.role).encode())
        res = user.sock.recv(BUFFER_SIZE).decode()
        
        user.send(("CHESS:" + self.board.fen()).encode())
        res = user.sock.recv(BUFFER_SIZE).decode()

        # Start main user handler loop
        while self.running:
            msg_data = user.sock.recv(BUFFER_SIZE).decode()
            if not msg_data:
                continue

            msg = msg_data.split(":")

            # Parse type and message
            try:
                m_type = msg[0]
                contents = msg[1]

                if m_type == M_TYPE.CHESS:
                    move = chess.Move.from_uci(contents)
                    self.play(move)
                elif m_type == M_TYPE.EVENT:
                    self.event(user, contents)
            except IndexError:
                print(msg)

        user.close()

    def broadcast(self, m_type, msg):
        """ 
        Broadcast message to all users. 
        
        Examples:
            CHAT:hello
            CHESS:rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
            EVENT:LEAVE
        """
        data = "{}:{}".format(m_type, msg).encode()
        for user in self.users:
            user.send(data)

    def event(self, sender, event):
        if event == EVENT.LEAVE:
            print("{} has left.".format(sender.name))
            del self.users[sender.uid]

    def play(self, move):
        self.board.push(move)
        self.broadcast(M_TYPE.CHESS, self.board.fen())

    def next_role(self):
        n_users = len(self.users)
        if n_users == 0:
            return ROLE.WHITE
        elif n_users == 1:
            return ROLE.BLACK
        else:
            return ROLE.SPECTATOR
            

if __name__ == "__main__":
    server = Server(v=True)

    try:
        server.start()
    except KeyboardInterrupt:
        server.close()