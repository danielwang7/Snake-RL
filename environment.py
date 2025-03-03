import pygame
import sys
from enum import Enum
from collections import namedtuple, deque
import random
import numpy as np 

pygame.init()

# ================ BASIC INITS ================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
CELL_SIZE = 50
SPEED = 10
FONT = pygame.font.SysFont("arial.ttf", CELL_SIZE * 2)

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
PURPLE = (190, 0, 250)
DARK_PURPLE = (130, 20, 195)
BLUE = (0, 100, 255)
DARK_BLUE = (0, 0, 255)
BLACK = (0,0,0)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

# ================ ============ ================

scoreVal = 0
scoreText = FONT.render("0", True, "white")
scoreRect = scoreText.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/20))

# NOTE: this is an original copy of the snake game without the AI model, playable via keyboard
class SnakeGameAI:
    def __init__(self):

        # INIT PYGAME DISPLAY
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("SNAKE!")
        self.clock = pygame.time.Clock()

        self.reset_game()

    def reset_game(self):

        # INIT SNAKE INFO
        self.direction = Direction.RIGHT

        self.head = Point(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        self.snake =  deque([self.head, 
                      Point(self.head.x - CELL_SIZE, self.head.y),
                      Point(self.head.x - (2 * CELL_SIZE), self.head.y)])

        # INIT FOOD INFO
        self.score = 0
        self.food = None
        self._place_food()
        self.game_iteration = 0
    

    def play_step(self, action=None):
        """
        RETURNS:
        reward(int), game_over(bool), score(int)
        """
        self.game_iteration += 1

        # COLLECT USER INPUT
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_LEFT:
            #         self.direction = Direction.LEFT
            #     elif event.key == pygame.K_RIGHT:
            #         self.direction = Direction.RIGHT
            #     elif event.key == pygame.K_UP:
            #         self.direction = Direction.UP
            #     elif event.key == pygame.K_DOWN:
            #         self.direction = Direction.DOWN
        
        self._move(action)
        self.snake.appendleft(self.head) # APPEND HEAD IN THE NEXT DIRECTION (REMEMBER HEAD IS JUST COORDS)

        # CHECK GAME OVER 
        # CALCULTE THE REWARD FROM TAKING THE ACTION
        reward = 0
        game_over = False
        if self.is_collision() or self.game_iteration > 100 * len(self.snake):
            game_over = True

            # NOTE: REWARD IS ADJUSTED HERE
            reward -= 10
            return reward, game_over, self.score

        # HITS FOOD - IF NO FOOD, POP FROM TAIL TO KEEP LENGTH SAME
        if self.head == self.food:
            self.score += 1
            self.reward = 10
            self._place_food()
        else:
            self.snake.pop()
        
        # UPDATE UI AND CLOCK SPEED
        self._update_ui()
        self.clock.tick(SPEED) 


        return reward, game_over, self.score
    
    def is_collision(self, pt=None):
        """
        Checks for collision with the boundaries and body only
        """

        if pt is None:
            pt = self.head

        # hits boundary
        if (
            pt.x > SCREEN_HEIGHT - CELL_SIZE or 
            pt.y > SCREEN_WIDTH - CELL_SIZE or 
            pt.x < 0 or
            pt.y < 0
            ):
            return True
        # hits itself
        if pt in list(self.snake)[1:]:
            return True

    def _place_food(self):
        x = random.randint(0, SCREEN_WIDTH) // CELL_SIZE * CELL_SIZE
        y = random.randint(0, SCREEN_HEIGHT) // CELL_SIZE * CELL_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()
    
    def _update_ui(self):
        self.screen.fill(BLACK)

        # DRAW GRID
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, "#3c3c3b", rect, 1)

        # DRAW SNAKE
        for i, pt in enumerate(self.snake):
            if i == 0:
                pygame.draw.rect(self.screen, PURPLE, pygame.Rect(pt.x, pt.y, CELL_SIZE , CELL_SIZE))
            else:
                pygame.draw.rect(self.screen, DARK_PURPLE, pygame.Rect(pt.x, pt.y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(self.screen, PURPLE, pygame.Rect(pt.x, pt.y, CELL_SIZE / 1.1, CELL_SIZE / 1.1))
        
        # DRAW FOOD
        pygame.draw.rect(self.screen, RED, pygame.Rect(self.food.x, self.food.y, CELL_SIZE, CELL_SIZE))
        
        # DRAW SCORE
        text = FONT.render("Score: " + str(self.score), True, WHITE)
        self.screen.blit(text, [0, 0])
        pygame.display.flip()
        
    def _move(self, action):
        """
        move based on the action [straight, right, left]
        """

        # STORES THE DIRECTIONS IN A CLOCKWISE MANNER
        clockwise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clockwise.index(self.direction) # GET INDEX OF THE CURRENT DIRECTION

        new_dir = None
        if np.array_equal(action, [1, 0, 0]): # STRAIGHT
            new_dir = clockwise[idx]
        elif np.array_equal(action, [0, 1, 0]): # RIGHT
            next_idx = (idx + 1) % 4
            new_dir = clockwise[next_idx]
        else: # LEFT
            next_idx = (idx - 1) % 4
            new_dir = clockwise[next_idx]

        self.direction = new_dir

        x = self.head.x
        y = self.head.y

        if self.direction == Direction.RIGHT:
            x += CELL_SIZE
        elif self.direction == Direction.LEFT:
            x -= CELL_SIZE
        elif self.direction == Direction.DOWN:
            y += CELL_SIZE
        elif self.direction == Direction.UP:
            y -= CELL_SIZE
            
        self.head = Point(x, y)


# if __name__ == "__main__":
#     game = SnakeGameAI()

#     while True:

#         game_over, score = game.play_step()

#         if game_over == True:
#             break
            
#     print('Final Score', score)
#     pygame.quit()
#     sys.exit("Game completed successfully!")

            

