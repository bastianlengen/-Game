from pytmx.util_pygame import load_pygame
from os.path import join

from settings import *
from level import Level

class Game():
    def __init__(self):
        pygame.init()
        # Create the screen
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('??? World')
        # Import the levels
        self.tmx_maps = {0: load_pygame(join('..','data','levels','omni.tmx'))}
        self.current_stage = Level(self.tmx_maps[0])

    def run(self):
        while True:
            # Go through the events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Run the current stage
            self.current_stage.run()

            # Update what's on screen
            pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()