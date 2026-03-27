import os
import pygame
from os.path import join
import random
os.environ['SDL_VIDEO_CENTERED'] = '1'

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join("images", "player.png")).convert_alpha()
        self.rect = self.image.get_frect(center = (windowWidth/2, windowHeight/2))
        self.direction = pygame.Vector2()
        self.speed = 500
        
        #laser cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400


    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt

        recent_keys = pygame.key.get_just_released()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
        
        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, star_surf):
        super().__init__(groups)
        self.image = star_surf
        self.rect = self.image.get_frect(center = (random.randint(0, windowWidth), random.randint(0, windowHeight)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)

    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill() 
        
class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(random.uniform(-0.5, 0.5), 1)
        self.speed = random.randint(400, 500)
        self.rotation_speed = random.randint(40, 80)
        self.rotation = 0
        base_speed = random.randint(400, 500)
        self.speed = base_speed * meteor_speed_multiplier

    def update(self, dt):
        self.rect.center += self.direction * self.speed *  dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()

        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
        explosion_sound.play()
    
    def update(self, dt):
        self.frame_index += 30 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

def collision():
    global running, score, level, meteor_speed_multiplier, level_up_text, level_up_start_time
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        running = False

    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)

            score += 1

            if score == 3:
                level = 2
                meteor_speed_multiplier = 1.3
                pygame.time.set_timer(meteor_event, 350)
                level_up_text = f"LEVEL {level}!"
                level_up_start_time = pygame.time.get_ticks()
                levelup_sound.play()
            elif score == 6:
                level = 3
                meteor_speed_multiplier = 1.6
                pygame.time.set_timer(meteor_event, 200)
                level_up_text = f"LEVEL {level}!"
                level_up_start_time = pygame.time.get_ticks()
                levelup_sound.play()
            
def display_score():
    current_time_ms = pygame.time.get_ticks()
    current_time = current_time_ms // 100
    text_surf = font.render(str(current_time), True, (240, 240, 240))
    text_rect = text_surf.get_frect(midbottom = (windowWidth/2, windowHeight -50))
    pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(20,10).move(0, -8),5, 10)

    stats_text = f'Lvl: {level} | Hits: {score}'
    stats_surf = font_stats.render(stats_text, True, (240, 240, 240))
    stats_rect = stats_surf.get_frect(topright = (windowWidth - 20, 20))
    
    #levelup message showw
    if level_up_text and current_time_ms - level_up_start_time < level_up_duration:
        msg_surf = font_message.render(level_up_text, True, 'yellow')
        msg_rect = msg_surf.get_frect(center = (windowWidth / 2, windowHeight / 2))
        
        display_surface.blit(msg_surf, msg_rect)

    display_surface.blit(stats_surf, stats_rect)
    display_surface.blit(text_surf, text_rect)

    


pygame.init()
windowWidth = 1280
windowHeight = 720
display_surface = pygame.display.set_mode((windowWidth, windowHeight))
pygame.display.set_caption('Space Blaster')
running = True
clock = pygame.Clock()

#score
score = 0
level = 1
meteor_speed_multiplier = 1.0

#levelup message
level_up_text = ""
level_up_start_time = 0
level_up_duration = 2000

#imports -------------------------------------------
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()

font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 35)
font_stats = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 25)
font_message = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 45)

explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]

laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
explosion_sound.set_volume(0.5)
damage_sound = pygame.mixer.Sound(join('audio', 'damage.ogg'))
damage_sound.set_volume(0.5)
levelup_sound = pygame.mixer.Sound(join('audio', 'levelup.mp3'))
levelup_sound.set_volume(1)
gameover_sound = pygame.mixer.Sound(join('audio', 'gameover.mp3'))
gameover_sound.set_volume(1)
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.2)
game_music.play(loops = -1)

#sprites -------------------------------------------
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

for i in range(20):
    Star(all_sprites, star_surf)
player = Player(all_sprites)


#Custom Meteor Event 
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)


#Closing window event loop -------------------------------------------
while running:
    dt = clock.tick() / 1000

    #Closing Loop    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == meteor_event:
            x = random.randint(0, windowWidth)
            y = random.randint(-200, -100)
            Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))
    
    # updates
    all_sprites.update(dt) 
    collision()

    #Drawing the game 
    display_surface.fill('#3a2e3f')
    all_sprites.draw(display_surface)
    display_score()

    pygame.display.update()


pygame.quit()