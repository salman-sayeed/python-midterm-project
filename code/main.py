import pygame
from os.path import join


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
player_x = 100
player_y = 150


#Closing window event loop -------------------------------------------
while running:
    #Event Loop    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #Drawing the game ------------------------------------------------ 
    display_surface.fill('darkgray')
    player_x += 0.2
    display_surface.blit(player_surface, (player_x, player_y))
    pygame.display.update()


pygame.quit()