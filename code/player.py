from math import sin
from settings import *
from timer import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, semi_collision_sprites, frames, data):
        # General setup
        super().__init__(groups)
        self.z = Z_LAYERS['main']
        self.data = data

        # Images
        self.frames, self.frames_index = frames, 0
        self.state, self.facing_right = 'idle', True
        self.image = self.frames[self.state][self.frames_index]

        # Rectangles
        self.rect = self.image.get_frect(center = pos)
        self.hitbox_rect = self.rect.inflate(-76, -36)  # Shrinks x-axis by -76/2 and yaxis by -36/2
        self.old_rect = self.hitbox_rect.copy()

        # Movement
        self.direction = vector()
        self.speed = 300
        self.gravity = 900
        self.jump = False
        self.jump_height = 800
        self.attacking = False

        # Collision
        self.collision_sprites = collision_sprites
        self.semi_collision_sprites = semi_collision_sprites
        self.on_surface = {'floor': False, 'left': False, 'right': False}
        self.platform = None

        # Timer
        self.timers = {
            'wall jump': Timer(200),
            'wall slide block': Timer(250),
            'platform skip': Timer(100),
            'attack block': Timer(500),
            'hit': Timer(750)
        }


    def input(self):
        keys = pygame.key.get_pressed()
        input_vector = vector(0,0)

        # Movement and attacks
        if not self.timers['wall jump'].active:

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                input_vector.x += 1
                self.facing_right = True

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                input_vector.x += -1
                self.facing_right = False

            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.timers['platform skip'].activate()

            if keys[pygame.K_f]:
                self.attack()

            self.direction.x = input_vector.normalize().x if input_vector else 0

        # Jump
        if keys[pygame.K_SPACE]:
            self.jump = True


    def attack(self):
        if not self.timers['attack block'].active:
            self.attacking = True
            self.frames_index = 0
            self.timers['attack block'].activate()


    def move(self, dt):
        # Horizontal move
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        # Vertical fall
        if not self.on_surface['floor'] and any((self.on_surface['left'], self.on_surface['right'])) and not self.timers['wall slide block'].active:
            self.direction.y = 0 # Stop any fall
            self.hitbox_rect.y += self.gravity / 10 * dt
        else:
            self.direction.y += self.gravity / 2 * dt
            self.hitbox_rect.y += self.direction.y * dt
            self.direction.y += self.gravity / 2 * dt
        # Jumps
        if self.jump:
            if self.on_surface['floor']:
                self.direction.y = -self.jump_height
                self.timers['wall slide block'].activate()
                self.hitbox_rect.bottom -= 1  # To make sure you can jump on a moving platform moving downward
            elif any((self.on_surface['left'], self.on_surface['right'])) and not self.timers['wall slide block'].active:
                self.timers['wall jump'].activate()
                self.direction.y = -self.jump_height
                self.direction.x = 1 if self.on_surface['left'] else -1
            self.jump = False
        self.collision('vertical')
        self.semi_collision()
        # Align the image rectangle with the hitbox rectangle
        self.rect.center = self.hitbox_rect.center


    def platform_move(self, dt):
        if self.platform:
            self.hitbox_rect.topleft += self.platform.direction * self.platform.speed * dt


    def check_contact(self):
        # Generate floor left and right rectangles to check for floor/wall contact (only half height for walls)
        floor_rect = pygame.Rect(self.hitbox_rect.bottomleft,(self.hitbox_rect.width,2)) # (left, top), (width, height)
        left_rect = pygame.Rect((self.hitbox_rect.topleft + vector(0, self.hitbox_rect.height / 4)), (-2, self.hitbox_rect.height / 2))
        right_rect = pygame.Rect((self.hitbox_rect.topright + vector(0, self.hitbox_rect.height / 4)), (2, self.hitbox_rect.height / 2))
        collide_rects = [sprite.rect for sprite in self.collision_sprites]
        semi_collide_rect = [sprite.rect for sprite in self.semi_collision_sprites]
        # Collisions
        self.on_surface['floor'] = True if floor_rect.collidelist(collide_rects) >= 0 or floor_rect.collidelist(semi_collide_rect) >= 0 and self.direction.y >= 0 else False
        self.on_surface['left'] = True if left_rect.collidelist(collide_rects) >= 0 else False
        self.on_surface['right'] = True if right_rect.collidelist(collide_rects) >= 0 else False
        # Check at each iteration if we are on a platform
        self.platform = None
        sprites = self.collision_sprites.sprites() + self.semi_collision_sprites.sprites() # .sprites() makes a list
        for sprite in [sprite for sprite in sprites if hasattr(sprite, 'moving')]:
            if sprite.rect.colliderect(floor_rect):
                self.platform = sprite


    def collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if axis == 'horizontal':
                    # Left collision
                    if self.hitbox_rect.left <= sprite.rect.right and int(self.old_rect.left) >= int(sprite.old_rect.right):
                        self.hitbox_rect.left = sprite.rect.right
                    # Right collision
                    if self.hitbox_rect.right >= sprite.rect.left and int(self.old_rect.right) <= int(sprite.old_rect.left):
                        self.hitbox_rect.right = sprite.rect.left
                else:
                    # Top collision
                    if self.hitbox_rect.top <= sprite.rect.bottom and int(self.old_rect.top) >= int(sprite.old_rect.bottom):
                        self.hitbox_rect.top = sprite.rect.bottom
                        if hasattr(sprite, 'moving'): # Avoid being stuck with platform moving
                            self.hitbox_rect.top += 6
                    # Bottom collision
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= int(sprite.old_rect.top):
                        self.hitbox_rect.bottom = sprite.rect.top
                    self.direction.y = 0


    def semi_collision(self):
        if not self.timers['platform skip'].active:
            for sprite in self.semi_collision_sprites:
                if sprite.rect.colliderect(self.hitbox_rect):
                    # Bottom collision
                    if (self.hitbox_rect.bottom >= sprite.rect.top) and (int(self.old_rect.bottom) <= sprite.old_rect.top):
                        self.hitbox_rect.bottom = sprite.rect.top
                        if self.direction.y > 0:
                            self.direction.y = 0


    def update_timers(self):
        for timer in self.timers.values():
            timer.update()


    def animate(self, dt):
        self.frames_index += ANIMATION_SPEED * dt
        # Attack reset after 1 cycle
        if self.state == 'attack' and self.frames_index >= len(self.frames[self.state]):
            self.state == 'idle'
        if self.attacking and self.frames_index > len(self.frames[self.state]):
            self.attacking = False

        # Other
        self.image = self.frames[self.state][int(self.frames_index) % len(self.frames[self.state])]
        self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)


    def get_state(self):
        if self.on_surface['floor']:
            if self.attacking:
                self.state = 'attack'
            else:
                self.state = 'idle' if self.direction.x == 0 else 'run'
        else:
            if self.attacking:
                self.state = 'air_attack'
            else:
                if any((self.on_surface['left'], self.on_surface['right'])):
                    self.state = 'wall'
                else:
                    self.state = 'jump' if self.direction.y <0 else 'fall'


    def get_damage(self):
        if not self.timers['hit'].active:
            self.data.health -= 1
            self.timers['hit'].activate()


    def flicker(self):
        if self.timers['hit'].active and sin(pygame.time.get_ticks() * 200) >= 0:
            white_mask = pygame.mask.from_surface(self.image)
            white_surf = white_mask.to_surface()
            white_surf.set_colorkey('black')
            self.image = white_surf

    def update(self, dt):
        # General update
        self.old_rect = self.hitbox_rect.copy()
        self.update_timers()

        # Input and movement
        self.input()
        self.move(dt)
        self.platform_move(dt)
        self.check_contact()

        # Animation
        self.get_state()
        self.animate(dt)
        self.flicker()
