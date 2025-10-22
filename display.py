from typing import Optional, Callable

import pygame
from pygame.locals import *

class ChestDisplay:
    def __init__(self, surface:pygame.Surface, pos:tuple, size:tuple, closed:bool = True):
        self.surface = surface
        self.pos = pos
        self.size = size
        self.frame = 0
        self.image = 1 if closed else 15
        self._last_loaded = None
        self.img_f = 10
        self.closed = closed
        self.load(self.image)

    def display(self, surface:Optional[pygame.Surface] = None, pos:Optional[tuple] = None, size:Optional[tuple] = None):
        surface = surface or self.surface
        pos = pos or self.default_pos
        size = size or self.size
        assert not (surface is None or pos is None or size is None), "Arguments non fournis"

        if self.closed and self.image > 1:
            self.frame += 1
            if self.frame // self.img_f > 0:
                self.image -= self.frame // self.img_f
                self.frame = self.frame % self.img_f
        if not self.closed and self.image < 15:
            self.frame += 1
            if self.frame // self.img_f > 0:
                self.image += self.frame // self.img_f
                self.frame = self.frame % self.img_f
        
        self.load(self.image)
        self.surface.blit(self.chest_image, (self.pos[0], self.pos[1]))

    def load(self, n):
        if n == self._last_loaded:
            return
        self.chest_image = pygame.image.load(f"assets/images/chest/chest{str(self.image)}.png")
        self.chest_image = pygame.transform.scale(self.chest_image, (self.size[0], self.size[1]))
        self._last_loaded = n

class bloc_txt:
    def __init__(self,txt, fenetre, clock):
        self.txt=f'*{txt}*'
        w,h = pygame.display.get_window_size()
        self.bloc=pygame.Rect((10,h/1.7), (w-20, 1/3*h))

        self.my_font = pygame.font.SysFont('Comic Sans MS', 30)
        self.fenetre = fenetre
        self.clock = clock
        
    def display_bloc(self,txt=''):
        txt = self.txt if txt=='' else txt
        pygame.draw.rect(self.fenetre,(255,0,0),self.bloc)
        self.fenetre.blit(self.my_font.render(txt, True, (0,0,0)), self.bloc)
    def annim_txt(self):
        aff=''
        for val in self.txt:
            aff+=val
            print(aff)
            self.display_bloc(aff)
            self.clock.tick(10)
            pygame.display.update()

class MouseButton:
    def __init__(self, text, pos, size, action:Callable, screen:pygame.Surface):
        """
        Stocker le text, la pos, la taille, l'action et la fenêtre
        action correspond à la fonction qui doit être lancée à l'appui -> on peut l'appeler comme ça : action()
        """
        # Initier les attributs

        # Créer un attribut qui contient un bloc pygame
    
    def display(self):
        """Affiche le rectangle, ses contours et le texte d'une couleur ou d'une autre si la souris passe dessus"""
        # Déterminer la couleur en fonction de la position de la souris
        
        # Ajoute le rectangle dans l'écran

        # Ajoute les bordures

        # Affiche le texte

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()

    running=True
    fenetre = pygame.display.set_mode((300,300))
    clock = pygame.time.Clock()

    texte='une petite prairie jolie'

    w,h = pygame.display.get_window_size()

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
        test=bloc_txt(texte, fenetre, clock)
        #test.display_bloc('txt')
        test.annim_txt()
        pygame.display.update()
        clock.tick(10)
    pygame.quit()
