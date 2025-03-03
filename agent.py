import torch
import random
import numpy as np
from collections import deque
from environment import SnakeGameAI, Direction, Point


MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LEARNING_RATE = 0.001

# GAME RELATED INITS
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
CELL_SIZE = 50
SPEED = 10

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # Controls randomness
        self.gamma = 0 # Bellman discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # Removes exceeding memories

        self.mode = None # TODO
        self.trainer = None # TODO
    
    def predict(self):
        pass

    def get_state(self, game):
        """
        Gets the current state based on the game status
        """
        
        head = game.snake[0]

        # CREATE 4 POINTS ADJACENT TO SNAKE HEAD
        point_l = Point(head.x - CELL_SIZE, head.y)
        point_r = Point(head.x + CELL_SIZE, head.y)
        point_u = Point(head.x, head.y - CELL_SIZE)
        point_d = Point(head.x, head.y + CELL_SIZE)

        # BOOLS REPRESENTING DIRECTION
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


    def get_action(self, state):
        """
        Gets the next action based on the current state
        """
        # GET SOME RANDOM MOVES (Exploration vs Exploitation)


        self.epsilon = 80 - self.n_games # RANDOM CHANCE GETS SMALLER EVERY GAME
        next_move = [0, 0, 0]

        # OUTPUT A RANDOM MOVE BASED ON EPSILON
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            next_move[move] = 1
        else: # IF NOT MAKING RANDOM MOVE, PREDICT  
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model.predict(state0)
            move = torch.argmax(prediction).item() # GET THE ARGMAX FOR NEXT MOVE
            next_move[move] = 1

        return next_move
        

    def store(self, state, action, reward, next_state, game_over):
        """
        Stores everything we have in memory
        """

        self.memory.append((state, action, reward, next_state, game_over))
    
    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # GET LIST OF TUPLES FROM MEMORY
        else:
            mini_sample = self.memory

        # UNPACK THE mini_sample into separate arguments
        states, actions, rewards, next_states, game_statuses = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_statuses)
    
    def train_short_memory(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)

def train():
    plot_scores = []
    plot_mean_scores = []

    total_score = 0
    record = 0

    agent = Agent()
    game = SnakeGameAI()

    while True:
        # GET OLD STATE
        state_old = agent.get_state(game)

        # GET NEXT MOVE
        next_move = agent.get_action(state_old)

        # PERFORM THE MOVE AND GET THE OUTCOME
        reward, game_over, score = game.play_step(next_move)
        state_new = agent.get_state(game)

        # TRAIN SHORT MEMORY & STORE VALUES
        agent.train_short_memory(state_old, next_move, reward, state_new, game_over)
        agent.store(state_old, next_move, reward, state_new, game_over)

        if game_over:
            # TRAIN THE LONG MEMORY
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                # agent.model.save()

            print('Game: ', agent.n_games, 'Score: ', score, 'Record: ', record)


            # TODO: IMPLEMENT PLOTTING


if __name__ == '__main__':
    train()