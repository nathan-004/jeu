import pygame
from pygame.locals import *

def monster_damage():
    sound = pygame.mixer.Sound("assets/sound/degats.mp3")
    sound.play()

class Musique:
    def __init__(self,path):
        self.path=path
        self.pause=False
        self.load = False

    def play_music(self,rpt=False):
        if not self.load:
            pygame.mixer.music.load(self.path)
            pygame.mixer.music.play(-1 if rpt else 0)  
            self.load = True
        elif not self.pause:
            pygame.mixer.music.unpause()
    
    def pause_music(self):
        pygame.mixer.music.pause()
        self.pause=True if not self.pause else False
    
    def reset_music(self):
        pygame.mixer.music.rewind()

if __name__ == "__main__":
    sound=Musique("assets/sound/sound.mp3")

    pygame.mixer.init()
    clock = pygame.time.Clock()
    fenetre = pygame.display.set_mode((300,300))
    continuer = True
    while continuer:
        for event in pygame.event.get():
            if event.type == QUIT:
                continuer = False
            if event.type == KEYDOWN:
                monster_damage()
        sound.play_music(True)
        clock.tick(10)
    pygame.quit()