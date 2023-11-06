import torch
import random
import numpy as np
from collections import deque
from game import SnakeGameAI, Direction, Point
from model import Linear_QNet, QTrainer
from helper import plot


MAX_MEMORY = 100_000
#BATCH_SIZE = 1000
BATCH_SIZE = 10000
LR = 0.001

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # Randomness
        self.gamma = 0.95 # Discount Rate of how you discount future rewards
        self.memory = deque(maxlen = MAX_MEMORY) # popleft()
        #self.model = Linear_QNet(11, 256, 3) # Has 11 inputs, 256 hidden layer, 3 outputs
        self.model = Linear_QNet(13, 256, 3) # Has 13 inputs now, 256 hidden layer, 3 outputs

        self.trainer = QTrainer(self.model, lr = LR, gamma = self.gamma)
        # TODO: model, trainer


    def get_state(self, game):
        head = game.snake[0]
        # 20 is the block size. So point_l is the point directly to the left of the snake
        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y - 20)
        point_d = Point(head.x, head.y + 20)

        point_ul = Point(head.x - 20, head.y - 20)
        point_ur = Point(head.x + 20, head.y - 20)
        point_dl = Point(head.x - 20, head.y + 20)
        point_dr = Point(head.x + 20, head.y + 20)

        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and game.is_collision(point_r)) or 
            (dir_l and game.is_collision(point_l)) or 
            (dir_u and game.is_collision(point_u)) or 
            (dir_d and game.is_collision(point_d)),

            # Danger right
            (dir_u and game.is_collision(point_r)) or 
            (dir_d and game.is_collision(point_l)) or 
            (dir_l and game.is_collision(point_u)) or 
            (dir_r and game.is_collision(point_d)),

            # Danger left
            (dir_d and game.is_collision(point_r)) or 
            (dir_u and game.is_collision(point_l)) or 
            (dir_r and game.is_collision(point_u)) or 
            (dir_l and game.is_collision(point_d)),

            # Danger straight and left
            (dir_r and game.is_collision(point_ur)) or 
            (dir_l and game.is_collision(point_dl)) or 
            (dir_u and game.is_collision(point_ul)) or 
            (dir_d and game.is_collision(point_dr)),

            # Danger straight and right
            (dir_r and game.is_collision(point_dr)) or 
            (dir_l and game.is_collision(point_ul)) or 
            (dir_u and game.is_collision(point_ur)) or 
            (dir_d and game.is_collision(point_dl)),
            
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # Food location 
            game.food.x < game.head.x,  # food left
            game.food.x > game.head.x,  # food right
            game.food.y < game.head.y,  # food up
            game.food.y > game.head.y  # food down
            ]

        return np.array(state, dtype=int)


        

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) #popleft if MAX_MEMORY is reached
        

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # List of tuples
        else:
            # Don't have BATCH_SIZE memory yet, so just look at it all
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # Random moves: Tradeoff between exploration and exploitation
        self.epsilon = 150 - self.n_games
        final_move = [0, 0, 0]
        # So at the first game have an 80/200 chance of making a random move
        # That chance diminishes and by the 80th game have a 0% of chance of random move
        if random.randint(0, 200) < self.epsilon:
            # Select a random index from final_move to be 1
            move = random.randint(0, 2) # 0 1 or 2
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype = torch.float)
            prediction = self.model(state0) #prediction is a tensor
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        
        return final_move

            

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()
    while True: #Runs forever until we quit the scipt
        # Get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember parameters
        agent.remember(state_old, final_move, reward, state_new, done) 

        if done:
            # train long memory (on all previous games)
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                # agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)






    

if __name__ == '__main__':
    train()