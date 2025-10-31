import pygame
from pygame.locals import *

class musique:
    def __init__(self,path):
        self.path=path

    def play_music(self,rpt=False):

        if pygame.mixer.music.get_busy():
            pygame.event.poll()
        elif rpt!=0:
            pygame.mixer.music.load(self.path)
            pygame.mixer.music.play(1) # repeat rpt times
            pygame.mixer.music.queue(self.path)
            
sound=musique("assets/sound/sound.mp3")

pygame.mixer.init()
clock = pygame.time.Clock()
fenetre = pygame.display.set_mode((300,300))
continuer = True
while continuer:
    for event in pygame.event.get():
        if event.type == QUIT:
            continuer = False
    sound.play_music(True)
    clock.tick(10)
pygame.quit()
