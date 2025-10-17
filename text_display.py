import pygame
from pygame.locals import *

pygame.init()
pygame.font.init()

running=True
fenetre = pygame.display.set_mode((300,300))
my_font = pygame.font.SysFont('Comic Sans MS', 30)
clock = pygame.time.Clock()

texte='une petite prairie jolie'

w,h = pygame.display.get_window_size()
class bloc_txt:
    def __init__(self,txt):
        self.txt=f'*{txt}*'
        self.bloc=pygame.Rect((10,h/1.7), (w-20, 1/3*h))		#img.get_rect()
        
    def display_bloc(self,txt=''):
        txt = self.txt if txt=='' else txt
        pygame.draw.rect(fenetre,(255,0,0),self.bloc)
        fenetre.blit(my_font.render(txt, True, (0,0,0)), self.bloc)
    def annim_txt(self):
        aff=''
        for val in self.txt:
            aff+=val
            print(aff)
            self.display_bloc(aff)
            clock.tick(10)
            pygame.display.update()
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    test=bloc_txt(texte)
    #test.display_bloc('txt')
    test.annim_txt()
    pygame.display.update()
    clock.tick(10)
pygame.quit()