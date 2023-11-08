import torch
import random
import numpy as np
from collections import deque
from game import Connect_Four
from model import Linear_QNet, QTrainer
from helper import plot
import time
import pickle


MAX_MEMORY = 100_000
#BATCH_SIZE = 1000
BATCH_SIZE = 2000
LR = 0.001

class Agent:

    def __init__(self, path = None):
        self.n_games = 0
        self.epsilon = 0 # Randomness
        self.gamma = 0.9 # Discount Rate of how you discount future rewards
        self.memory = deque(maxlen = MAX_MEMORY) # popleft()
        if path == None:
            self.model = Linear_QNet(42, 256, 7) # Has 42 inputs, 256 hidden layer, 7 outputs
        else:
            self.model = Linear_QNet(42, 256, 7)
            self.model.load_state_dict(torch.load(path))
            self.n_games = int(path[12:(path.index(".pth"))])
            self.model.eval()

        self.trainer = QTrainer(self.model, lr = LR, gamma = self.gamma)
        # TODO: model, trainer

    def set_model(self, model):
        self.model = model

    def get_state(self, game, player):
        # State is dependent on which player the AI is controlling
        state = []
        for r in range(len(game.board)):
            for c in range(len(game.board[0])):
                cell_value = game.board[r][c]
                if cell_value == player:
                    state.append(1)
                elif (cell_value == 1 and player == 2) or (cell_value == 2 and player == 1):
                    state.append(-1)
                elif cell_value == 0:
                    state.append(0)
                else:
                    print("Cell Value: ", cell_value)
                    raise ValueError("Invalid cell value") 
        return np.array(state, dtype=int)


    def get_random_legal_move(self, board):
        legal_columns = []
        # Check top row (which is last row) if its filled
        row_num = len(board)-1
        for c in range(0, len(board[row_num])):
            if board[row_num][c] == 0:
                legal_columns.append(c)
        randy = random.randint(0, len(legal_columns)-1)
        return legal_columns[randy]
    
    def get_best_legal_move(self, prediction, board):
        legal_columns = []
        row_num = len(board)-1
        for c in range(0, len(board[row_num])):
            if board[row_num][c] == 0:
                legal_columns.append(True)
            else:
                legal_columns.append(False)
        true_indices = np.where(legal_columns)[0]
        if len(true_indices) == 0:
            raise ValueError("No legal moves but game didn't end!")
        max_index = true_indices[np.argmax(prediction[true_indices])]
        return max_index
        

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) #popleft if MAX_MEMORY is reached
        

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            print("Hit batch size")
            mini_sample = random.sample(self.memory, BATCH_SIZE) # List of tuples
        else:
            # Don't have BATCH_SIZE memory yet, so just look at it all
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state, board):
        # Random moves: Tradeoff between exploration and exploitation
        #self.epsilon = max(150 - self.n_games
        self.epsilon = 20 # always keep at 10% epsilon
        final_move = [0, 0, 0, 0, 0, 0, 0]
        # So at the first game have an 80/200 chance of making a random move
        # That chance diminishes and by the 80th game have a 0% of chance of random move
        if random.randint(0, 200) < self.epsilon:
            # Select a random index from final_move to be 1
            move = self.get_random_legal_move(board)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype = torch.float)
            prediction = self.model(state0) #prediction is a tensor
            prediction = prediction.detach().numpy() #Get prediction to be in numpy form
            move = self.get_best_legal_move(prediction, board)
            final_move[move] = 1
        
        return final_move

def get_other_player_reward(reward):
    if reward == 10:
        # If reward for current player is 10, other player loses 10
        other_reward = -10
    elif reward == -1:
        # Then it was a draw
        other_reward = 1
    elif reward == 1:
        # Also a draw
        other_reward = 1
    else:
        other_reward = 0
    return other_reward

def train():
    agent = Agent()
    game = Connect_Four()
    game.draw_board()
    
    player = 1

    # First get move
    # Second get move, get first players "new_state" and train
    # First get move, get second players "new_state" and train
    # ...

    old_states = [None, None]
    new_states = [None, None]
    # Player1 move: pre move in old_states[player1], post move in new_states[player2]
    # Player2 move: pre move in old_states[player2], post move in new_states[player1], then remember (old_states[player1], new_states[player1])
    # Player1 move: pre move in old_states[player1], post move in new_states[player2], then remember (old_states[player2], new_states[player2])
    # ...

    while True: #Runs forever until we quit the scipt
        # Get old (current) state for that player
        old_states[player-1] = agent.get_state(game, player)

        # get move, execute move, get reward
        final_move = agent.get_action(old_states[player-1], game.board)
        reward, done = game.play_step(final_move, player)

        # Save new state for other player
        other_player = 3 - player
        new_states[other_player-1] = agent.get_state(game, other_player)

        if old_states[other_player-1] is not None:
            # Now remember and train on (old_states[other_player], new_states[other_player])
            # Give the other model the other reward
            other_reward = get_other_player_reward(reward)
            agent.train_short_memory(old_states[other_player-1], final_move, other_reward, new_states[other_player-1], done)
            agent.remember(old_states[other_player-1], final_move, other_reward, new_states[other_player-1], done) 

        # Switch players and play from other side
        player = player + 1
        if player > 2:
            player = 1

        # Draw the board
        #game.draw_board()
        #game.print_board()
        
        if done:
            # Then train the winning players batch cuz yay they won!
            # Give the current model the reward
            new_state = agent.get_state(game, player)
            agent.train_short_memory(old_states[player-1], final_move, reward, new_state, done)
            agent.remember(old_states[player-1], final_move, reward, new_state, done) 


            game.reset()

            old_states = [None, None]
            new_states = [None, None]

            agent.n_games += 1

            # train long memory (on all previous games)
            agent.train_long_memory()
            if agent.n_games % 500 == 0:
                # Save model and memory
                torch.save(agent.model.state_dict(), "epsilon_10/saved_model " + str(agent.n_games) + ".pth")
                f = open("epsilon_10/saved_memory " + str(agent.n_games) + ".pkl","wb")
                pickle.dump(agent.memory,f)
                f.close()


            # Load model with: "model_to_load.eval()""
            # model_to_load = SAME ARCITECHTURE MODEL 
            # model_to_load.load_state_dict(torch.load(model_path))
            player = 1
            print('Game', agent.n_games)



    

if __name__ == '__main__':
    train()