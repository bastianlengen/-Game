from settings import *
from random import choice
from timer import Timer

class Tooth(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, collision_sprites):
        super().__init__(groups)

        # Animation
        self.frames, self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(topleft=pos)
        self.z = Z_LAYERS['main']

        # Movement
        self.speed = 200
        self.direction = choice((-1,1))
        self.collision_rects = [sprite.rect for sprite in collision_sprites] # Only keep the rect not the whole sprites

        # Timers
        self.hit_timer = Timer(500)

    def reverse(self):
        if not self.hit_timer.active:
            self.direction *= -1
            self.hit_timer.activate()

    def update(self, dt):
        self.hit_timer.update()

        # Animate
        self.frame_index += ANIMATION_SPEED * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        self.image = pygame.transform.flip(self.image, True, False) if self.direction < 0 else self.image

        # Movement
        self.rect.x += self.direction * self.speed * dt

        # Reverse direction
        floor_rect_right = pygame.FRect(self.rect.bottomright, (1,1))
        floor_rect_left = pygame.FRect(self.rect.bottomleft, (-1, 1))
        wall_rect = pygame.FRect(self.rect.topleft + vector(-1,0), (self.rect.width + 2, 2))
        if floor_rect_right.collidelist(self.collision_rects) == -1 and self.direction > 0 or\
            floor_rect_left.collidelist(self.collision_rects) == -1 and self.direction < 0 or\
            wall_rect.collidelist(self.collision_rects) != -1:
            self.direction *= -1


class Shell(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, reverse, player, create_pearl):
        super().__init__(groups)

        # Animation
        if reverse:
            self.frames = {}
            for key, surf_list in frames.items():
                self.frames[key] = [pygame.transform.flip(surf, True, False) for surf in surf_list]
                self.bullet_direction = -1
        else:
            self.frames = frames
            self.bullet_direction = 1
        self.frame_index = 0
        self.state = 'idle'
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_frect(topleft = pos)
        self.old_rect = self.rect.copy()
        self.z = Z_LAYERS['main']
        self.player = player

        # Shoot
        self.shoot_timer = Timer(3000)
        self.has_fired = False
        self.create_pearl = create_pearl  # Shooting function


    def state_management(self):
        player_pos, shell_pos = vector(self.player.hitbox_rect.center), vector(self.rect.center)
        # First check if the player is close
        player_near = shell_pos.distance_to(player_pos) < 500
        # If it's in front of the shell
        player_front = shell_pos.x < player_pos.x if self.bullet_direction > 0 else shell_pos.x > player_pos.x
        # And on the same level (ex +/- 15 pxl
        player_level = abs(shell_pos.y - player_pos.y) < 30

        if player_near and player_front and player_level and not self.shoot_timer.active:
            self.state = 'fire'
            self.frame_index = 0
            self.shoot_timer.activate()


    def update(self, dt):
        self.shoot_timer.update()
        self.state_management()

        # Animation/attack
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index < len(self.frames[self.state]): # No modulo cuz we want to finish shooting
            self.image = self.frames[self.state][int(self.frame_index)]
            # Fire a bullet every 3rd image
            if self.state == 'fire' and int(self.frame_index) == 3 and not self.has_fired:
                self.create_pearl((self.rect.center), self.bullet_direction)
                self.has_fired = True
        else:
            self.frame_index = 0
            if self.state == 'fire':
                self.state = 'idle'
                self.has_fired = False


class Pearl(pygame.sprite.Sprite):
    def __init__(self, pos, groups, surf, direction, speed):
        super().__init__(groups)
        self.pearl = True  # To recognize from outside the class

        # Animation
        self.image = surf
        self.rect = self.image.get_frect(center = pos + vector(45*direction,7))
        self.direction = direction
        self.speed = speed
        self.z = Z_LAYERS['main']

        # Timers
        self.timers = {'lifetime': Timer(5000), 'reverse': Timer(500)}
        self.timers['lifetime'].activate()

    def reverse(self):
        if not self.timers['reverse'].active:
            self.direction *= -1
            self.timers['reverse'].activate()
    def update(self, dt):
        for timer in self.timers.values():
            timer.update()

        self.rect.x += self.direction * self.speed * dt
        if not self.timers['lifetime'].active:
            self.kill()



''' MY STUFF '''
class Canon(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, reverse, player, create_boulet):
        super().__init__(groups)

        # Animation
        if reverse:
            self.frames = {}
            for key, surf_list in frames.items():
                self.frames[key] = [pygame.transform.flip(surf, True, False) for surf in surf_list]
                self.bullet_direction = -1
        else:
            self.frames = frames
            self.bullet_direction = 1
        self.frame_index = 0
        self.state = 'idle'
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_frect(topleft=pos)
        self.old_rect = self.rect.copy()
        self.z = Z_LAYERS['main']
        self.player = player

        # Shoot
        self.shoot_timer = Timer(3000)
        self.has_fired = False
        self.create_boulet = create_boulet  # Shooting function

    def state_management(self):
        player_pos, boulet_pos = vector(self.player.hitbox_rect.center), vector(self.rect.center)
        # First check if the player is close
        player_near = boulet_pos.distance_to(player_pos) < 500
        # If it's in front of the shell
        player_front = boulet_pos.x < player_pos.x if self.bullet_direction > 0 else boulet_pos.x > player_pos.x
        # And on the same level (ex +/- 15 pxl
        player_level = abs(boulet_pos.y - player_pos.y) < 30

        if player_near and player_front and player_level and not self.shoot_timer.active:
            self.state = 'fire'
            self.frame_index = 0
            self.shoot_timer.activate()

    def update(self, dt):
        self.shoot_timer.update()
        self.state_management()

        # Animation/attack
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index < len(self.frames[self.state]): # No modulo cuz we want to finish shooting
            self.image = self.frames[self.state][int(self.frame_index)]
            # Fire a bullet every 3rd image
            if self.state == 'fire' and int(self.frame_index) == 5 and not self.has_fired:
                self.create_boulet((self.rect.center), self.bullet_direction)
                self.has_fired = True
        else:
            self.frame_index = 0
            if self.state == 'fire':
                self.state = 'idle'
                self.has_fired = False

class Boulet(pygame.sprite.Sprite):
    def __init__(self, pos, groups, surf, direction, speed):
        super().__init__(groups)
        self.boulet = True  # To recognize from outside the class

        # Animation
        self.image = surf
        self.rect = self.image.get_frect(center=pos + vector(49 * direction, -5))
        self.direction = direction
        self.speed = speed
        self.z = Z_LAYERS['main']

        # Timers
        self.timers = {'lifetime': Timer(5000), 'reverse': Timer(500)}
        self.timers['lifetime'].activate()

    def reverse(self):
        if not self.timers['reverse'].active:
            self.direction *= -1
            self.timers['reverse'].activate()

    def update(self, dt):
        for timer in self.timers.values():
            timer.update()

        self.rect.x += self.direction * self.speed * dt
        if not self.timers['lifetime'].active:
            self.kill()
