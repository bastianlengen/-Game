from settings import *
from sprites import Sprite, AnimatedSprite, MovingSprite, Spike, Item, ParticleEffectSprite
from player import Player
from groups import AllSprites
from enemies import Tooth, Shell, Pearl, Canon, Boulet

from random import uniform


class Level():
    def __init__(self, tmx_map, level_frames, data, switch_stage):
        self.display_surface = pygame.display.get_surface()
        self.data = data
        self.switch_stage = switch_stage

        # Level data
        self.level_width = tmx_map.width * TILE_SIZE
        self.level_bottom = tmx_map.height * TILE_SIZE
        tmx_level_properties = tmx_map.get_layer_by_name('Data')[0].properties
        self.level_unlock = tmx_level_properties['level_unlock']
        if tmx_level_properties['bg']:
            bg_tile = level_frames['bg_tiles'][tmx_level_properties['bg']]
        else:
            bg_tile = None

        # Groups
        self.all_sprites = AllSprites(
            width = tmx_map.width,
            height = tmx_map.height,
            bg_tile = bg_tile,
            top_limit = tmx_level_properties['top_limit'],
            clouds = {'large': level_frames['cloud_large'], 'small': level_frames['cloud_small']},
            horizon_line = tmx_level_properties['horizon_line']
        )
        self.collision_sprites = pygame.sprite.Group()
        self.semi_collision_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.tooth_sprites = pygame.sprite.Group()
        self.pearl_sprites = pygame.sprite.Group()
        self.boulet_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()

        # Set up the level
        self.setup(tmx_map, level_frames)

        # Frames
        self.pearl_surf = level_frames['pearl']
        self.particle_frames = level_frames['particle']

    def setup(self, tmx_map, level_frames):
        # Get the tiles/terrain
        for layer in ['BG', 'Terrain', 'FG', 'Platforms']:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                # Assign each tile to its corresponding groups
                groups = [self.all_sprites]
                if layer == 'Terrain': groups.append(self.collision_sprites)
                if layer == 'Platforms': groups.append(self.semi_collision_sprites)
                # Assign their correct z-value
                match layer:
                    case 'BG':
                        z = Z_LAYERS['bg tiles']
                    case 'FG':
                        z = Z_LAYERS['bg tiles']
                    case _:
                        z = Z_LAYERS['main']
                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, groups, z)

        # Get the bg details
        for obj in tmx_map.get_layer_by_name('BG details'):
            if obj.name == 'static':
                Sprite((obj.x, obj.y), obj.image, self.all_sprites, Z_LAYERS['bg details'])
            else:
                AnimatedSprite((obj.x, obj.y), level_frames[obj.name], self.all_sprites, Z_LAYERS['bg details'])
                if obj.name == 'candle':
                    AnimatedSprite((obj.x, obj.y) + vector(-20, -20), level_frames['candle_light'], self.all_sprites,
                                   Z_LAYERS['bg details'])

        # Get the objects (and the player)
        for obj in tmx_map.get_layer_by_name('Objects'):
            if obj.name == 'player':
                self.player = Player(
                    pos=(obj.x, obj.y),
                    groups=self.all_sprites,
                    collision_sprites=self.collision_sprites,
                    semi_collision_sprites=self.semi_collision_sprites,
                    frames=level_frames['player'],
                    data = self.data
                )
            else:
                if obj.name in ('barrel', 'crate'):  # Not animated
                    Sprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
                else:
                    # frames
                    frames = level_frames[obj.name] if 'palm' not in obj.name else level_frames['palms'][obj.name]
                    if obj.name == 'floor_spike' and obj.properties['inverted']:
                        frames = [pygame.transform.flip(frame, False, True) for frame in frames]

                    # groups
                    groups = [self.all_sprites]
                    if obj.name in ('palm_small', 'palm_large'):
                        groups.append(self.semi_collision_sprites)
                    if obj.name in ('floor_spike', 'saw'):
                        groups.append(self.damage_sprites)

                    # z-index
                    z = Z_LAYERS['main'] if not 'bg' in obj.name else Z_LAYERS['bg details']

                    # animation speed
                    animation_speed = ANIMATION_SPEED if 'palm' not in obj.name else ANIMATION_SPEED + uniform(-2, 2)

                    AnimatedSprite((obj.x, obj.y), frames, groups, z, animation_speed)
            if obj.name == 'flag':
                self.level_finish_rect = pygame.FRect((obj.x, obj.y), (obj.width, obj.height))

        # Get the moving objects
        for obj in tmx_map.get_layer_by_name('Moving Objects'):
            if obj.name == 'spike':
                Spike(
                    pos = (obj.x + obj.width / 2, obj.y, obj.height / 2),
                    surf = level_frames['spike'],
                    groups = (self.all_sprites, self.damage_sprites),
                    radius = obj.properties['radius'],
                    speed = obj.properties['speed'],
                    start_angle = obj.properties['start_angle'],
                    end_angle = obj.properties['end_angle']
                )
                # Chain
                for radius in range(0, obj.properties['radius'], 20):
                    Spike(
                        pos = (obj.x + obj.width / 2, obj.y, obj.height / 2),
                        surf = level_frames['spike_chain'],
                        groups = self.all_sprites,
                        radius = radius,
                        speed = obj.properties['speed'],
                        start_angle = obj.properties['start_angle'],
                        end_angle = obj.properties['end_angle'],
                        z = Z_LAYERS['bg details']
                    )

            else:
                frames = level_frames[obj.name]
                groups = (self.all_sprites, self.semi_collision_sprites) if obj.properties['platform'] else (
                self.all_sprites, self.damage_sprites)
                # Check if moving horizontal or vertical
                if obj.width > obj.height:  # Horizontal
                    move_dir = 'x'
                    start_pos = (obj.x, obj.y + obj.height / 2)  # Cause (x,y) gives the top corner
                    end_pos = (obj.x + obj.width, obj.y + obj.height / 2)
                else:  # Vertical
                    move_dir = 'y'
                    start_pos = (obj.x + obj.width / 2, obj.y)  # Cause (x,y) gives the top corner
                    end_pos = (obj.x + obj.width / 2, obj.y + obj.height)
                speed = obj.properties['speed']
                MovingSprite(frames, groups, start_pos, end_pos, move_dir, speed, obj.properties['flip'])

                # Saw's path
                if obj.name == 'saw':
                    if move_dir == 'x':
                        y = start_pos[1] - level_frames['saw_chain'].get_height() / 2
                        left, right = int(start_pos[0]), int(end_pos[0])
                        for x in range(left, right, 20):
                            Sprite((x, y), level_frames['saw_chain'], self.all_sprites, z=Z_LAYERS['bg details'])
                    else:
                        x = start_pos[0] - level_frames['saw_chain'].get_width() / 2
                        top, bottom = int(start_pos[1]), int(end_pos[1])
                        for y in range(top, bottom, 20):
                            Sprite((x, y), level_frames['saw_chain'], self.all_sprites, z=Z_LAYERS['bg details'])

        # Get the enemies
        for obj in tmx_map.get_layer_by_name('Enemies'):
            if obj.name == 'tooth':
                Tooth(
                    pos = (obj.x, obj.y),
                    frames = level_frames['tooth'],
                    groups = (self.all_sprites, self.damage_sprites, self.tooth_sprites),
                    collision_sprites = self.collision_sprites
                )
            if obj.name == 'shell':
                Shell(
                    pos = (obj.x, obj.y),
                    frames = level_frames['shell'],
                    groups = (self.all_sprites, self.collision_sprites),
                    reverse = obj.properties['reverse'],
                    player = self.player,
                    create_pearl = self.create_pearl
                )

        # Get the items
        for obj in tmx_map.get_layer_by_name('Items'):
            Item(
                item_type = obj.name,
                pos = (obj.x+TILE_SIZE/2, obj.y+TILE_SIZE/2),
                frames = level_frames['items'][obj.name],
                groups = (self.all_sprites, self.item_sprites),
                data = self.data
            )

        # water
        for obj in tmx_map.get_layer_by_name('Water'):
            # Get the number of tiles that are water
            rows = int(obj.height / TILE_SIZE)
            cols = int(obj.width / TILE_SIZE)
            for row in range(rows):
                for col in range(cols):
                    x = obj.x + col * TILE_SIZE
                    y = obj.y + row * TILE_SIZE
                    # Animated spire for the surface
                    if row == 0:
                        AnimatedSprite((x,y), level_frames['water_top'], self.all_sprites, Z_LAYERS['water'])
                    else:
                        Sprite((x,y), level_frames['water_body'], self.all_sprites, Z_LAYERS['water'])

    def create_pearl(self, pos, direction):
        Pearl(pos = pos,
              groups = (self.all_sprites, self.damage_sprites, self.pearl_sprites),
              surf = self.pearl_surf,
              direction = direction,
              speed = 150
        )

    def create_boulet(self, pos, direction):
        Boulet(pos = pos,
              groups = (self.all_sprites, self.damage_sprites, self.boulet_sprites),
              surf = self.boulet_surf,
              direction = direction,
              speed = 150
        )

    def pearl_collision(self):
        # Check collisions with walls to destroy the pearls
        for sprite in self.collision_sprites:
            sprite_colliding = pygame.sprite.spritecollide(sprite, self.pearl_sprites, dokill=True)
            if sprite_colliding:
                ParticleEffectSprite((sprite_colliding[0].rect.center), self.particle_frames, self.all_sprites)

    def boulet_collision(self):
        # Check collisions with walls to destroy the boulets
        for sprite in self.collision_sprites:
            sprite_colliding = pygame.sprite.spritecollide(sprite, self.boulet_sprites, dokill=True)
            if sprite_colliding:
                ParticleEffectSprite((sprite_colliding[0].rect.center), self.particle_frames, self.all_sprites)

    def hit_collision(self):
        # Check any dmg to the player (and destroy bullets)
        for sprite in self.damage_sprites:
            if sprite.rect.colliderect(self.player.hitbox_rect):
                self.player.get_damage()
                if hasattr(sprite, 'pearl'):
                    ParticleEffectSprite((sprite.rect.center), self.particle_frames, self.all_sprites)
                    sprite.kill()
                if hasattr(sprite, 'boulet'):
                    ParticleEffectSprite((sprite.rect.center), self.particle_frames, self.all_sprites)
                    sprite.kill()

    def item_collision(self):
        for sprite in self.item_sprites:
            if sprite.rect.colliderect(self.player.hitbox_rect):
                ParticleEffectSprite((sprite.rect.center), self.particle_frames, self.all_sprites)
                sprite.activate()
                sprite.kill()

    def attack_collision(self):
        for target in self.pearl_sprites.sprites() + self.tooth_sprites.sprites() + self.boulet_sprites.sprites():
            # Here use full rect not hitbox and checking that we're facing the enemy
            facing_target = self.player.rect.centerx < target.rect.centerx and self.player.facing_right or\
                            self.player.rect.centerx > target.rect.centerx and not self.player.facing_right
            if target.rect.colliderect(self.player.rect) and self.player.attacking and facing_target:
                target.reverse()

    def check_constraint(self):
        # Left and right
        if self.player.hitbox_rect.left <= 0:
            self.player.hitbox_rect.left = 0
        if self.player.hitbox_rect.right >= self.level_width:
            self.player.hitbox_rect.right = self.level_width

        # Bottom border
        if self.player.hitbox_rect.bottom >= self.level_bottom:
            self.switch_stage('overworld', -1)

        # Success state, i.e. reached the flag
        if self.player.hitbox_rect.colliderect(self.level_finish_rect):
            self.switch_stage('overworld', self.level_unlock)


    def run(self, dt):
        self.display_surface.fill('black')

        # Update
        self.all_sprites.update(dt)
        self.pearl_collision()
        self.boulet_collision()
        self.hit_collision()
        self.item_collision()
        self.attack_collision()
        self.check_constraint()

        # Draw
        self.all_sprites.draw(self.player.hitbox_rect.center, dt)
