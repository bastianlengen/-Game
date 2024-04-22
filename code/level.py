from settings import *
from sprites import Sprite

class Level():
    def __init__(self, tmx_map):
        self.display_surface = pygame.display.get_surface()
        # Group
        self.all_sprites = pygame.sprite.Group()
        # Setup the level
        self.setup(tmx_map)

    def setup(self, tmx_map):
        # Get the terrain
        for x,y,surf in tmx_map.get_layer_by_name('Terrain').tiles():
            Sprite((x*TILE_SIZE,y*TILE_SIZE), surf, self.all_sprites)

    def run(self):
        self.display_surface.fill('black')
        self.all_sprites.draw(self.display_surface)
