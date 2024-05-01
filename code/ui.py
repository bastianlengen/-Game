from settings import *
from sprites import AnimatedSprite
from random import randint
from timer import Timer

class UI():
    def __init__(self, font, frames):
        self.display_surface = pygame.display.get_surface()
        self.sprites = pygame.sprite.Group()
        self.font = font

        # Health
        self.heart_frames = frames['heart']
        self.heart_surf_width = self.heart_frames[0].get_width()
        self.heart_padding = 5

        # Coins
        self.coin_surf = frames['coin']
        self.coin_amount = 0
        self.coin_timer = Timer(1000)
        pass

    def create_hearts(self, amount):
        # First delete previous hearts:
        for sprite in self.sprites:
            sprite.kill()
        # Then create the new one
        for heart in range(amount):
            Heart(pos =  ( 10+ heart * (self.heart_padding + self.heart_surf_width), 10),
                  frames = self.heart_frames,
                  groups = self.sprites
                  )

    def display_text(self):
        if self.coin_timer.active:
            # Text
            text_surf = self.font.render(str(self.coin_amount), False, 'White')
            text_rect = text_surf.get_frect(topleft = (16, 34))
            self.display_surface.blit(text_surf, text_rect)

            # Coin
            coin_rect = self.coin_surf.get_frect(center = text_rect.midright).move(10,0)
            self.display_surface.blit(self.coin_surf, coin_rect)

    def show_coins(self, amount):
        self.coin_amount = amount
        self.coin_timer.activate()

    def update(self, dt):
        self.coin_timer.update()
        self.sprites.update(dt)
        self.sprites.draw(self.display_surface)
        self.display_text()


class Heart(AnimatedSprite):
    def __init__(self, pos, frames, groups):
        super().__init__(pos, frames, groups)

        # Occasionally animate
        self.active = False

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.active = False
            self.frame_index = 0

    def update(self, dt):
        if self.active:
            self.animate(dt)
        else:
            if randint(0,2000) == 1:
                self.active = True
