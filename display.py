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

class TextDisplay:
    def __init__(self,txt, fenetre, clock):
        self.txt = f'*{txt}*'
        self.mot = self.txt.split(' ')[0]
        self.frames = 0	#len(self.txt*pygame.time.get_ticks())
        self.end = False
        self.time = 0
        w,h = pygame.display.get_window_size()
        self.bloc = pygame.Rect((10,h/1.7), (w-20, 1/3*h))

        self.my_font = pygame.font.SysFont('Comic Sans MS', 20)
        self.fenetre = fenetre
        self.clock = clock
        self.blocliste = [pygame.Rect((15,h/1.7+5), (w-20, self.my_font.get_height()))]
        
        cur_w = 0
        cur_l = 0
        self.txts = [""]

        for mot in self.txt.split(' '):
            if (len(mot) + cur_w ) * self.my_font.size("a")[0] >= w - 20:
                cur_l += 1
                self.txts.append("")
                self.blocliste.append(pygame.Rect((15,h/1.7+cur_l*(self.my_font.get_height()+5)), (w-20, self.my_font.get_height())))
                cur_w = 0
            self.txts[cur_l] += mot + " "
            cur_w += len(mot) + 1

        print(self.blocliste, self.txts)
        
    def display(self,delay=100):	#delay est en milliseconde
        pygame.draw.rect(self.fenetre,(255,0,0),self.bloc)
        cur_txt_prog = 0
        for txt, bloc in zip(self.txts, self.blocliste):
            self.fenetre.blit(self.my_font.render(txt[:max(0, min(self.frames - cur_txt_prog, len(txt) - 1))], True, (0,0,0)), bloc)
            cur_txt_prog += len(txt)
        if self.time>=delay and not self.end:
            self.frames = self.frames+self.time//delay
            self.time = 0
        self.time += self.clock.get_time()
        self.end = self.frames>=len(self.txt)
        print(self.txt[0:self.frames],self.end)
        
    def reset(self):
        self.frames = 0
        self.time = 0
        self.end = False
        
    def reset(self):
        self.frames = 0
        self.time = 0
        self.end = False

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
    fenetre = pygame.display.set_mode((500,300))
    clock = pygame.time.Clock()

    texte= 'une petite prairie jolie, et des petites fleurs y poussait. En frolant cette pelouse, vous remarquez un arbre'

    w,h = pygame.display.get_window_size()
    test=TextDisplay(texte, fenetre, clock)
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
        test.display()
        #test.reset() if test.end and test.time >= 1000 else None
        pygame.display.update()
        clock.tick(10)
    pygame.quit()
