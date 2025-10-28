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
        self.img_f = 1
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
    def __init__(self,txt, fenetre, clock, police=20):
        self.txt = f'*{txt}*'
        self.mot = self.txt.split(' ')[0]
        self.frames = 0	#len(self.txt*pygame.time.get_ticks())
        self.end = False
        self.time = 0
        w,h = pygame.display.get_window_size()
        self.bloc = pygame.Rect((10,h/1.7), (w-20, 1/3*h))

        self.my_font = pygame.font.SysFont('Comic Sans MS', police)
        self.fenetre = fenetre
        self.clock = clock
        self.blocliste = [pygame.Rect((15,h/1.7+5), (w-20, self.my_font.get_height()))]
        
        cur_w = 0
        cur_l = 0
        self.txts = [""]

        for mot in self.txt.split(' '):
            if (len(mot) + cur_w ) * self.my_font.size("a")[0] >= w - 20 or mot == "&":
                cur_l += 1
                self.txts.append("")
                self.blocliste.append(pygame.Rect((15,h/1.7+cur_l*(self.my_font.get_height()+5)), (w-20, self.my_font.get_height())))
                cur_w = 0

            if mot == "&":
                continue
            
            self.txts[cur_l] += mot + " "
            cur_w += len(mot) + 1

        print(self.blocliste, self.txts)
        
    def display(self,delay=20):	#delay est en milliseconde
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
        #print(self.txt[0:self.frames],self.end)
        
    def reset(self):
        self.frames = 0
        self.time = 0
        self.end = False

class MouseButton:
    def __init__(self, text, pos, size, action:Callable, screen:pygame.Surface, position:tuple = (0, 0)):
        """
        Stocker le text, la pos, la taille, l'action et la fenêtre
        action correspond à la fonction qui doit être lancée à l'appui -> on peut l'appeler comme ça : action()
        """
        self.text = text
        self.pos = pos
        self.size = size
        self.action = action
        self.screen = screen
        self.background = pygame.Rect(pos, size)
        self.position = position
    
    def display(self):
        """Affiche le rectangle, ses contours et le texte d'une couleur ou d'une autre si la souris passe dessus"""
        mouse_pos = pygame.mouse.get_pos()
        local_mouse_pos = (mouse_pos[0] - self.position[0], mouse_pos[1] - self.position[1])
        hovered = self.background.collidepoint(local_mouse_pos)
        color = (255, 120, 87) if not hovered else (239, 255, 94)

        pygame.draw.rect(self.screen, "black", self.background)

        pygame.draw.rect(self.screen, color, self.background, 2)

        font = pygame.font.SysFont(None, int(self.size[1] * 0.6))
        text_surf = font.render(self.text, True, color)
        text_rect = text_surf.get_rect(center=self.background.center)
        self.screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            print("Clic intercepté")
            local_pos = (event.pos[0] - self.position[0], event.pos[1] - self.position[1])
            if self.background.collidepoint(local_pos):
                print("action réalisée")
                self.action()

class RoomDisplay:
    def __init__(self,screen,taille=70):
        self.taille=taille/100
        self.screen = screen
        self.bg = pygame.image.load('assets\\images\\background\\Salle_fond.png')
        self.shade = pygame.image.load('assets\\images\\background\\Shade.png')
        self.w,self.h =pygame.display.get_window_size()
        self.bg = pygame.transform.scale(self.bg, (self.w*self.taille,self.h*self.taille))
        self.shade = pygame.transform.scale(self.shade, (self.w*self.taille,self.h*self.taille))

        
    def display_bg(self):
        self.screen.fill(('black'))
        self.screen.blit(self.bg,(self.w*(1-self.taille)/2,0))
    def display_shade(self):
        self.screen.blit(self.shade,(self.w*(1-self.taille)/2,0))
        
class EnnemiDisplay:
    def __init__(self, surface:pygame.Surface, pos:tuple, size:tuple, ennemi):
        self.surface = surface
        self.pos = pos
        self.size = size
        self.ennemi = ennemi
        self._last_loaded = None
        self.load(self.ennemi.image)

    def display(self):
        self.load(self.ennemi.image)
        self.surface.blit(self.ennemi_image, (self.pos[0], self.pos[1]))

    def load(self, image_path):
        if image_path == self._last_loaded:
            return
        self.ennemi_image = pygame.image.load(image_path)
        self.ennemi_image = pygame.transform.scale(self.ennemi_image, (self.size[0], self.size[1]))
        self._last_loaded = image_path
        
class HealthBar:
    """Barre de vie à afficher"""

    def __init__(self, personnage, pos:tuple, size:tuple, surface:pygame.Surface):
        """
        personnage:Personnage -> barre de vie reliée au personnage
        pos -> position (x, y)
        """
        self.personnage = personnage
        self.pos = pos
        self.size = size# Initier variables
        self.surface = surface

        self.fond_color = (50, 50, 50)
        self.pv_color = (0, 255, 0)  # Initier le bloc de fond à taille size

    def display(self):
        pygame.draw.rect(self.surface, self.fond_color,(self.pos[0], self.pos[1], self.size[0], self.size[1]))# Afficher le rectangle du fond

        rectangle_pv = self.size[0] * self.personnage.pv / self.personnage.get_max_pv()
        pygame.draw.rect(self.surface, self.pv_color, (self.pos[0], self.pos[1], rectangle_pv, self.size[1]))
        
def get_size(surface:pygame.Surface, pourcentage:float, size:str = "width") -> float:
    """Renvoie la valeur en pixel qui correspond au pourcentage de la dimension de la surface"""
    assert size == "width" or size == "height", f"Dimension {size} non disponible"
    val = surface.get_size()[0 if size == "width" else 1]

    return pourcentage * val / 100

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()

    running=True
    fenetre = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    texte= 'une petite prairie jolie, et des petites fleurs y poussait. En frolant cette pelouse, vous remarquez un arbre'

    test=TextDisplay(texte, fenetre, clock, 15)
    background = RoomDisplay(fenetre)
    button = MouseButton("Test", (0,0), (100, 50), lambda : print("test"), fenetre)
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    if test.end:
                        running = False
                    else:
                        test.frames = len(test.txt)
                if event.key == K_ESCAPE:
                    running = False
            button.handle_event(event)
        background.display_bg()
        #test.display()
        background.display_shade()
        button.display()
        #test.reset() if test.end and test.time >= 1000 else None
        pygame.display.update()
        clock.tick(10)
    pygame.quit()

