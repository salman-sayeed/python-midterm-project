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

#Surface
surf = pygame.Surface((100,200))
surf.fill('orange')
x = 100
y = 150

#importing spaceship ------------------------------------
player_surface = pygame.image.load(join('images', 'spaceship.png')).convert_alpha() #for non-transparent - convert()
player_rect = player_surface.get_frect(center = (windowWidth/2 , windowHeight/2))
player_x = 100
player_y = 500

#importing stars ---------------------------------------------
star_surface = pygame.image.load(join('images', 'star.png')).convert_alpha()
star_position = [(random.randint(0, windowWidth), random.randint(0, windowHeight)) for i in range(20)]

#importing meteor ---------------------------------------------



#Closing window event loop -------------------------------------------
while running:
    #Event Loop    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #Drawing the game ------------------------------------------------ 
    display_surface.fill('darkgray')

    for pos in star_position:
        display_surface.blit(star_surface, pos)

    if player_rect.right < windowWidth:
        player_rect.left += 0.2
    display_surface.blit(player_surface, player_rect)
    pygame.display.update()


pygame.quit()