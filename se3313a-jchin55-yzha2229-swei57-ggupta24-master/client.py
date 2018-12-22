# imports 
import chess
import os
from threading import Thread
import pygame
from pygame.locals import*
pygame.init()
FONT = pygame.font.SysFont("monospace", 15)
BIG_FONT = pygame.font.SysFont("monospace", 40)

from connection import Connection

from constants import *

HOST = input("HOST: ")
PORT = int(input("PORT: "))

# Set dictionary to the images file paths
PIECES = {
    "b": "img/blackb.png",
    "k": "img/blackk.png",
    "n": "img/blackn.png",
    "p": "img/blackp.png",
    "q": "img/blackq.png",
    "r": "img/blackr.png",
    "B": "img/whiteb.png",
    "K": "img/whitek.png",
    "N": "img/whiten.png",
    "P": "img/whitep.png",
    "Q": "img/whiteq.png",
    "R": "img/whiter.png",
}

class Client:
    def __init__(self, connection):
        self.running = True
        self.turn = ROLE.WHITE
        self.error_text = ""

        # Get role
        data = connection.receive().split(":")
        role = data[1]
        if role == ROLE.BLACK:
            self.role = "Black"
        elif role == ROLE.WHITE:
            self.role = "White"
        elif role == ROLE.SPECTATOR:
            self.role = "Spectator"
        connection.send("RESULT:SUCCESS".encode())

        # Get initial board
        self.get_board(loop=False)

        # Start update thread
        update_thread = Thread(target=self.main_loop)
        update_thread.start()

        receive_thread = Thread(target=self.get_board)
        receive_thread.start()

        # Start input thread
        # if role != ROLE.SPECTATOR:
        #     input_thread = Thread(target=self.input_loop)
        #     input_thread.start()

    def close(self):
        self.running = False
        update_thread.join()
        receive_thread.join()
        # input_thread.join()
    
    def parse_board(self, board):
        return board.__str__().replace("\n"," ").split(" ")

    def draw_piece(self, piece, x, y):
        pie = pygame.image.load(PIECES[piece])
        self.game_display.blit(pie, (x,y))

    def get_board(self, loop=True):
        while self.running:
            data = connection.receive()
            if data:
                data = data.split(":")
                self.board = chess.Board(data[1])
                self.turn = data[1].split(" ")[1]
                if self.turn == "w":
                    self.turn_str = "White's move"
                elif self.turn == "b":
                    self.turn_str = "Black's move"
                self.board_pieces = self.parse_board(self.board)
                connection.send("RESULT:SUCCESS".encode())
            if loop != True:
                break

    def is_users_turn(self):
        pass

    def make_move(self, input_str):
        try:
            move = chess.Move.from_uci(input_str)
            if move in self.board.legal_moves:
                self.error_text = ""
                connection.send("CHESS:{}".format(move).encode())
            else:
                self.error_text = "That move is invalid."
        except ValueError:
            self.error_text = "That move is invalid."

    def main_loop(self):
        white, gray, red, purple = (255,255,255),(241,241,241),(255,0,0),(79,38,131)
        sq_size = 62 # Square size
        slength = 8 # Side length of the chess board

        # Initialize game display
        board_size = slength * sq_size
        self.game_display = pygame.display.set_mode((board_size, board_size + 200))
        pygame.display.set_caption("WeChess")

        # Initialize input string
        move_str = ""

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == 8:
                        move_str = move_str[:-1]
                    elif event.key == 13:
                        self.make_move(move_str)
                        move_str = ""
                    else:
                        move_str += event.unicode
        
            # Background
            self.game_display.fill(gray)

            """
            DRAW BOARD
            """
            piececnt = 0 # keeping track of pieces
            cnt = 0 # keeping track of the squares
            for i in range(slength):
                for z in range(slength):

                    if cnt % 2 == 0: # even and odd for black and white squares
                        pygame.draw.rect(self.game_display, white, [sq_size*z, sq_size*i, sq_size, sq_size])
                    else:
                        pygame.draw.rect(self.game_display, purple, [sq_size*z, sq_size*i, sq_size, sq_size])
                    
                    piece = self.board_pieces[piececnt]
                    if piece != ".":
                        self.draw_piece(piece, sq_size*z, sq_size*i)

                    piececnt+=1
                    cnt +=1
                cnt-=1

            """
            DRAW INFO AND INPUT
            """
            role_label = FONT.render("You: {}".format(self.role), 3, (0,0,0))
            self.game_display.blit(role_label, (20, board_size + 20))

            turn_label = FONT.render(self.turn_str, 3, (0,0,0))
            self.game_display.blit(turn_label, (20, board_size + 40))

            input_label = FONT.render(move_str, 3, (0,0,0))
            self.game_display.blit(input_label, (20, board_size + 60))

            error_label = FONT.render(self.error_text, 3, (0,0,0))
            self.game_display.blit(error_label, (20, board_size + 80))

            """
            CHECK FOR END CONDITIONS
            """
            if self.board.is_checkmate():
                game_over_label = BIG_FONT.render("CHECKMATE", 10, (255,0,0))
                self.game_display.blit(game_over_label, (board_size//2-100, board_size//2-20))

            # Border
            pygame.draw.rect(self.game_display,gray,[sq_size,sq_size,slength*sq_size,slength*sq_size],1)

            # Update display
            pygame.display.update()

        pygame.quit()

if __name__ == "__main__":
    try:
        # Prompt user for username
        username = input("Enter a username: ")

        # Establish connection with the server
        connection = Connection(HOST, PORT)
        connection.connect(username)
        connection.sock.settimeout(0.3)

        client = Client(connection)

    except KeyboardInterrupt:
        connection.close()