import pygame
from os.path import join
import random
#os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()
windowWidth = 1280
windowHeight = 720

pygame.display.set_caption('Test Game')
display_surface = pygame.display.set_mode((windowWidth, windowHeight))
running = True

#Surface not used
surf = pygame.Surface((100,200))
surf.fill('orange')
x = 100

#importing spaceship ------------------------------------
player_surface = pygame.image.load(join('images', 'spaceship.png')).convert_alpha() #for non-transparent - convert()
player_rect = player_surface.get_frect(center = (windowWidth/2 , windowHeight/2))
player_direction = 1

#importing stars ---------------------------------------------
star_surface = pygame.image.load(join('images', 'star.png')).convert_alpha()
star_position = [(random.randint(0, windowWidth), random.randint(0, windowHeight)) for i in range(20)]

#importing laser----------------------------------------------
laser_surface = pygame.image.load(join('images', 'laser.png')).convert_alpha()
laser_rect = laser_surface.get_frect(bottomleft = (20, windowHeight-20))

#importing meteor ---------------------------------------------
meteor_surface = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
meteor_rect = meteor_surface.get_frect(center = (windowWidth/2 , windowHeight/2))



#Closing window event loop -------------------------------------------
while running:
    #Event Loop    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #Drawing the game 
    display_surface.fill('darkgray')

    for pos in star_position: #star
        display_surface.blit(star_surface, pos)
    
    display_surface.blit(laser_surface, laser_rect) #laser
    display_surface.blit(meteor_surface, meteor_rect) #meteor

    #player movement
    player_rect.x += player_direction * 0.4
    if player_rect.right > windowWidth or player_rect.left < 0:
        player_direction *= -1 
    display_surface.blit(player_surface, player_rect)
        
    

    pygame.display.update()


pygame.quit()