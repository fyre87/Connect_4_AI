from game import Connect_Four
from agent import Agent
from model import Linear_QNet, QTrainer
import pygame
import torch
import math
import time
import random
import sys
import matplotlib.pyplot as plt
from IPython import display

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)
 
ROW_COUNT = 6
COLUMN_COUNT = 7
SQUARESIZE = 100
RADIUS = int(SQUARESIZE/2 - 5)

class Tester:
    def __init__(self):
        pass

    def test_vs_human(self, model_path):
        model = Linear_QNet(42, 256, 7)
        model.load_state_dict(torch.load(model_path))
        model.eval()
        agent = Agent()
        agent.set_model(model)

        game = Connect_Four()
        

        human_player = random.randint(1, 2)
        if human_player == 2:
            AI_player = 1
            # Now AI should move
            final_move = [0, 0, 0, 0, 0, 0, 0]
            current_state = agent.get_state(game, AI_player)
            state0 = torch.tensor(current_state, dtype = torch.float)
            prediction = agent.model(state0) #prediction is a tensor
            prediction = prediction.detach().numpy() #Get prediction to be in numpy form
            move = agent.get_best_legal_move(prediction, game.board)
            final_move[move] = 1
            reward, done = game.play_step(final_move, AI_player)
        else:
            AI_player = 2

        game.print_board()
        game.draw_board()
        game_over = False
        pygame.init()

        

        while not game_over:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    pygame.draw.rect(game.screen, BLACK, (0,0, game.width, SQUARESIZE))
                    posx = event.pos[0]
                    if human_player == 1:
                        pygame.draw.circle(game.screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
                    else:
                        pygame.draw.circle(game.screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)
                pygame.display.update()
        
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.draw.rect(game.screen, BLACK, (0,0, game.width, SQUARESIZE))
                    # Ask for human input
                    posx = event.pos[0]
                    col = int(math.floor(posx/SQUARESIZE))
    
                    # If valid move, then move and let AI move after
                    if game.is_valid_location(col):
                        row = game.get_next_open_row(col)
                        game.drop_piece(row, col, human_player)
    
                        if game.winning_move(1):
                            label = game.myfont.render("You win!", human_player, RED)
                            game.screen.blit(label, (40,10))
                            game_over = True
                        elif game.game_is_draw():
                            label = game.myfont.render("Tie Game", human_player, BLUE)
                            game.screen.blit(label, (40,10))
                            game_over = True

                    # If game is still going, then ask for AI input
                    if game_over == False:
                        final_move = [0, 0, 0, 0, 0, 0, 0]
                        current_state = agent.get_state(game, AI_player)
                        state0 = torch.tensor(current_state, dtype = torch.float)
                        prediction = agent.model(state0) #prediction is a tensor
                        prediction = prediction.detach().numpy() #Get prediction to be in numpy form
                        move = agent.get_best_legal_move(prediction, game.board)
                        final_move[move] = 1
                        reward, done = game.play_step(final_move, AI_player)
                        if game.winning_move(AI_player):
                            label = game.myfont.render("AI wins!", 1, YELLOW)
                            game.screen.blit(label, (40,10))
                            game_over = True
                
                # Check for tie game
                if game.game_is_draw():
                    label = game.myfont.render("Tie Game", 1, BLUE)
                    game.screen.blit(label, (40,10))
                    game_over = True

                #game.print_board()
                game.draw_board()

                if game_over:
                    pygame.time.wait(3000)



            

    def test_vs_random_bot(self, model_path):
        model = Linear_QNet(42, 256, 7)
        model.load_state_dict(torch.load(model_path))
        model.eval()

        model_wins = 0
        draws = 0
        TOTAL_GAMES = 200
        game = Connect_Four()
        for n in range(1, TOTAL_GAMES+1):
            outcome = self.play_game_vs_random(model, game)
            if outcome == 1:
                model_wins += 1
            elif outcome == 0:
                draws += 1
            #print(model_wins/n)
        print("Win %: ", 100*(model_wins/TOTAL_GAMES))
        print("Draw %: ", 100*(draws/TOTAL_GAMES))
        return 100*(model_wins/TOTAL_GAMES) + 50*(draws/TOTAL_GAMES)

    def play_game_vs_random(self, model, game):
        # Returns 1 if the model wins
        # Returns 0 if the model ties
        # Returns -1 if the model loses
        game.reset()
        game.draw_board()
        agent = Agent()
        agent.set_model(model)
        
        player = 1 # To randomize, just randomize who is player 1 and 2??? NO CANT DO THAT!
        while True: #Runs forever until we quit the scipt
            #game.print_board()
            final_move = [0, 0, 0, 0, 0, 0, 0]
            if player == 1:
                current_state = agent.get_state(game, player)
                state0 = torch.tensor(current_state, dtype = torch.float)
                prediction = agent.model(state0) #prediction is a tensor
                prediction = prediction.detach().numpy() #Get prediction to be in numpy form
                move = agent.get_best_legal_move(prediction, game.board)
                final_move[move] = 1
                reward, done = game.play_step(final_move, player)
            elif player == 2:
                move = agent.get_random_legal_move(game.board)
                final_move[move] = 1
                reward, done = game.play_step(final_move, player)
            #game.draw_board()
            #time.sleep(0.1)
            if done:
                if player == 1 and reward == 10:
                    # Player 1 wins
                    return 1
                elif reward == 1 or reward == -1:
                    # Draw
                    return 0
                elif player == 2 and reward == 10:
                    # Player 2 wins
                    return -1
                else:
                    raise ValueError("Reward unrecognized")
            # Swap players
            player = 2 if player == 1 else 1

    def plot_vs_random_bot(self):
        scores = []
        paths = range(500, 11500, 500)
        for num in paths:
            scores.append(self.test_vs_random_bot("epsilon_10/saved_model " + str(num) + ".pth"))
        plt.ion()
        display.clear_output(wait=True)
        display.display(plt.gcf())
        plt.xlabel('Number of Games (hundreds)')
        plt.ylabel('Avg score (1=win, 0.5=draw) vs random bot')
        plt.plot(scores)
        plt.show(block = True)

if __name__ == '__main__':
    test = Tester()
    #test.plot_vs_random_bot()
    test.test_vs_human("epsilon_10/saved_model 11000.pth")