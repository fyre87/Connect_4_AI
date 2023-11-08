import numpy as np
import pygame
import sys
import math
import time
 
BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)
 
ROW_COUNT = 6
COLUMN_COUNT = 7
SQUARESIZE = 100
RADIUS = int(SQUARESIZE/2 - 5)


class Connect_Four():
    def __init__(self, rows = ROW_COUNT, cols = COLUMN_COUNT):
        self.board = np.zeros((rows, cols))
        self.width = COLUMN_COUNT * SQUARESIZE
        self.height = (ROW_COUNT+1) * SQUARESIZE
        self.size = (self.width, self.height)
        pygame.init()
        self.myfont = pygame.font.SysFont("monospace", 75)
        self.screen = pygame.display.set_mode(self.size)
    
    '''
    def create_board():
        board = np.zeros((ROW_COUNT,COLUMN_COUNT))
        return board
    '''
    
    def drop_piece(self, row, col, piece):
        self.board[row][col] = piece
    
    def is_valid_location(self, col):
        return self.board[ROW_COUNT-1][col] == 0
    
    # Use this one for the human game
    def get_next_open_row(self, col):
        for r in range(ROW_COUNT):
            if self.board[r][col] == 0:
                return r
    
    def print_board(self):
        print(np.flip(self.board, 0))

    def play_step(self, action, player):
        # Action should be an array ex: np.array([0, 0, 1, 0, 0, 0, 0])
        # Player should be "1" or "2"
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # np.where(action == 1)[0][0] gets the first index of 1 in numpy the array
        col = np.where(np.array(action) == 1)[0][0]
        row = self.get_next_open_row(col)
        self.drop_piece(row, col, player)
        

        reward = 0
        game_over = False
        if self.winning_move(player):
            #label = self.myfont.render("Player " + str(player) +  " wins!!", player, RED)
            #self.screen.blit(label, (40,10))
            print("Player", player, "wins!")
            reward = 10
            game_over = True
            return reward, game_over
        
        if self.game_is_draw():
            #label = self.myfont.render("Tie Game", 1, BLUE)
            #self.screen.blit(label, (40,10))
            print("Tie Game!")

            # Drawing is good for the second player, bad for the first player
            if player == 1:
                reward = -1
            elif player == 2:
                reward = 1
            else:
                print("Player: ", player)
                raise ValueError("Invalid Player number")
            game_over = True
            return reward, game_over
        
        return reward, game_over

    def winning_move(self, piece):
        # Check horizontal locations for win
        for c in range(COLUMN_COUNT-3):
            for r in range(ROW_COUNT):
                if self.board[r][c] == piece and self.board[r][c+1] == piece and self.board[r][c+2] == piece and self.board[r][c+3] == piece:
                    return True
    
        # Check vertical locations for win
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT-3):
                if self.board[r][c] == piece and self.board[r+1][c] == piece and self.board[r+2][c] == piece and self.board[r+3][c] == piece:
                    return True
    
        # Check positively sloped diaganols
        for c in range(COLUMN_COUNT-3):
            for r in range(ROW_COUNT-3):
                if self.board[r][c] == piece and self.board[r+1][c+1] == piece and self.board[r+2][c+2] == piece and self.board[r+3][c+3] == piece:
                    return True
    
        # Check negatively sloped diaganols
        for c in range(COLUMN_COUNT-3):
            for r in range(3, ROW_COUNT):
                if self.board[r][c] == piece and self.board[r-1][c+1] == piece and self.board[r-2][c+2] == piece and self.board[r-3][c+3] == piece:
                    return True
    
    def draw_board(self):
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT):
                pygame.draw.rect(self.screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
                pygame.draw.circle(self.screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
        
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT):      
                if self.board[r][c] == 1:
                    pygame.draw.circle(self.screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), self.height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
                elif self.board[r][c] == 2: 
                    pygame.draw.circle(self.screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), self.height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
        pygame.display.update()
    
    def reset(self, rows = ROW_COUNT, cols = COLUMN_COUNT):
        self.board = np.zeros((rows, cols))
    
    def game_is_draw(self):
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT):
                if self.board[r][c] == 0:
                    return False
        return True



# Play one on one vs human
if __name__ == "__main__":
    game = Connect_Four()

    #board = self.create_board()
    game.print_board()
    game_over = False
    turn = 0
    
    #initalize pygame
    pygame.init()
    
    #define our screen size
    SQUARESIZE = 100
    
    #define width and height of board
    width = COLUMN_COUNT * SQUARESIZE
    height = (ROW_COUNT+1) * SQUARESIZE
    
    size = (width, height)
    
    RADIUS = int(SQUARESIZE/2 - 5)
    
    #screen = pygame.display.set_mode(size)
    #Calling function draw_board again
    game.draw_board()
    
    myfont = pygame.font.SysFont("monospace", 75)
    
    while not game_over:
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
    
            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(game.screen, BLACK, (0,0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn == 0:
                    pygame.draw.circle(game.screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
                else: 
                    pygame.draw.circle(game.screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)
            pygame.display.update()
    
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(game.screen, BLACK, (0,0, width, SQUARESIZE))
                
                # Ask for Player 1 Input
                if turn == 0:
                    posx = event.pos[0]
                    col = int(math.floor(posx/SQUARESIZE))
    
                    if game.is_valid_location(col):
                        row = game.get_next_open_row(col)
                        game.drop_piece(row, col, 1)
                        turn += 1
                        turn = turn % 2
    
                        if game.winning_move(1):
                            label = myfont.render("Player 1 wins!!", 1, RED)
                            game.screen.blit(label, (40,10))
                            game_over = True

    
    
                # # Ask for Player 2 Input
                else:               
                    posx = event.pos[0]
                    col = int(math.floor(posx/SQUARESIZE))
    
                    if game.is_valid_location(col):
                        row = game.get_next_open_row(col)
                        game.drop_piece(row, col, 2)
                        turn += 1
                        turn = turn % 2

    
                        if game.winning_move(2):
                            label = myfont.render("Player 2 wins!!", 1, YELLOW)
                            game.screen.blit(label, (40,10))
                            game_over = True

                # Check for tie game
                if game.game_is_draw():
                    label = myfont.render("Tie Game", 1, BLUE)
                    game.screen.blit(label, (40,10))
                    game_over = True

                game.print_board()
                game.draw_board()
        
                if game_over:
                    pygame.time.wait(3000)