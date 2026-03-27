import os
import pygame
from os.path import join
import random
import json

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

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > windowWidth:
            self.rect.right = windowWidth
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > windowHeight:
            self.rect.bottom = windowHeight

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
        self.speed = random.randint(400, 500) * meteor_speed_multiplier

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
    global start_time, game_state, running, score, level, meteor_speed_multiplier, level_up_text, level_up_start_time

    if pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask):
        game_state = 'gameover'
        gameover_sound.play()
        game_music.stop()
        
        session_time = (pygame.time.get_ticks() - start_time) // 1000
        save_stats(score, level, session_time)

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
    current_time_ms = pygame.time.get_ticks() - start_time 
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

def draw_home_screen():
    display_surface.blit(home_bg_surf, (0, 0))

    hint_surf = font_home.render("P to Start | F to Fire | L for Leaderboard | Q to Quit", True, 'white')
    hint_rect = hint_surf.get_frect(center = (windowWidth/2, 600))

    bg_rect = hint_rect.inflate(40, 20) 
    bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    bg_surf.fill((0, 0, 0, 150)) 
    
    display_surface.blit(bg_surf, bg_rect)
    display_surface.blit(hint_surf, hint_rect)

def draw_game_over():
    overlay = pygame.Surface((windowWidth, windowHeight))
    overlay.set_alpha(150)
    overlay.fill('black')
    display_surface.blit(overlay, (0,0))
    
    go_surf = font_message.render("GAME OVER", True, 'red')
    go_rect = go_surf.get_frect(center = (windowWidth/2, 200))
    
    stats_text = f"Score: {score} | Level: {level}"
    stats_surf = font.render(stats_text, True, 'white')
    stats_rect = stats_surf.get_frect(center = (windowWidth/2, 350))
    
    retry_surf = font.render("Press R to Play Again or H for Home", True, 'gray')
    retry_rect = retry_surf.get_frect(center = (windowWidth/2, 500))
    
    display_surface.blit(go_surf, go_rect)
    display_surface.blit(stats_surf, stats_rect)
    display_surface.blit(retry_surf, retry_rect)
    
def save_stats(final_score, final_level, final_time):
    filename = 'highscore.json'
    
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                leaderboard = json.load(f)
            except:
                leaderboard = []
    else:
        leaderboard = []

    new_entry = {'score': final_score, 'level': final_level, 'time': final_time}
    leaderboard.append(new_entry)

    leaderboard = sorted(leaderboard, key=lambda x: x['score'], reverse=True)[:5]

    with open(filename, 'w') as f:
        json.dump(leaderboard, f)

def draw_leaderboard():
    display_surface.blit(home_bg_surf, (0, 0))
    overlay = pygame.Surface((windowWidth, windowHeight))
    overlay.set_alpha(200)
    overlay.fill('black')
    display_surface.blit(overlay, (0,0))

    title_surf = font_message.render("TOP 5 BLASTERS", True, 'gold')
    display_surface.blit(title_surf, title_surf.get_frect(center = (windowWidth/2, 100)))

    try:
        with open('highscore.json', 'r') as f:
            leaderboard = json.load(f)
    except:
        leaderboard = []

    for i, entry in enumerate(leaderboard):
        y_pos = 200 + (i * 70)
        txt = f"{i+1}. Score: {entry['score']} | Lvl: {entry['level']} | {entry['time']}s"
        score_surf = font.render(txt, True, 'white')
        display_surface.blit(score_surf, score_surf.get_frect(center = (windowWidth/2, y_pos)))

    back_surf = font.render("Press H for Home", True, 'gray')
    display_surface.blit(back_surf, back_surf.get_frect(center = (windowWidth/2, 650)))

def reset_game():
    global score, level, start_time, meteor_speed_multiplier, level_up_text
    score = 0
    level = 1
    start_time = pygame.time.get_ticks()
    meteor_speed_multiplier = 1.0
    level_up_text = ""
    
    #Clear sprites
    all_sprites.empty()
    meteor_sprites.empty()
    laser_sprites.empty()
    pygame.time.set_timer(meteor_event, 500)
    
    # new env creted
    for i in range(20): 
        Star(all_sprites, star_surf)
    global player
    player = Player(all_sprites)

    game_music.play(loops=-1)

def handle_home_state(events):
    global game_state, running
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                reset_game()
                game_state = 'game'
            elif event.key == pygame.K_l:
                game_state = 'leaderboard'
            elif event.key == pygame.K_q:
                running = False
    draw_home_screen()

def handle_game_state(events, dt):
    global game_state
    for event in events:
        if event.type == meteor_event:
            x = random.randint(0, windowWidth)
            y = random.randint(-200, -100)
            Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))

    # Update andd draw
    all_sprites.update(dt)
    collision()
    display_surface.fill('#3a2e3f')
    all_sprites.draw(display_surface)
    display_score()

def handle_leaderboard_state(events):
    global game_state
    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
            game_state = 'home'
    draw_leaderboard()

def handle_gameover_state(events):
    global game_state
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
                game_state = 'game'
            elif event.key == pygame.K_h:
                game_state = 'home'
    
    display_surface.fill('#3a2e3f')
    all_sprites.draw(display_surface)
    draw_game_over()

pygame.init()
windowWidth = 1280
windowHeight = 720
display_surface = pygame.display.set_mode((windowWidth, windowHeight))
pygame.display.set_caption('Space Blaster 2099')
game_state = 'home'
#running = True
clock = pygame.Clock()

#score
start_time = 0
score = 0
level = 1
meteor_speed_multiplier = 1.0

#levelup message
level_up_text = ""
level_up_start_time = 0
level_up_duration = 2000

#imports -------------------------------------------
home_bg_surf = pygame.image.load(join('images', 'bg.png')).convert() 
home_bg_surf = pygame.transform.scale(home_bg_surf, (windowWidth, windowHeight))

laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()

font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 35)
font_stats = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 25)
font_message = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 45)
font_home = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 45)

explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]

laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
explosion_sound.set_volume(0.5)
levelup_sound = pygame.mixer.Sound(join('audio', 'levelup.mp3'))
levelup_sound.set_volume(1)
gameover_sound = pygame.mixer.Sound(join('audio', 'gameover.mp3'))
gameover_sound.set_volume(1)
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.2)


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


#Main loop -------------------------------------------
running = True

while running:
    dt = clock.tick() / 1000
    events = pygame.event.get()

    # Quit Check
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # State Manager
    if game_state == 'home':
        handle_home_state(events)
    elif game_state == 'game':
        handle_game_state(events, dt)
    elif game_state == 'leaderboard':
        handle_leaderboard_state(events)
    elif game_state == 'gameover':
        handle_gameover_state(events)

    pygame.display.update()

pygame.quit()