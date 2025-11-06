import pygame
from pygame.locals import *
"""
Module gérant les sons et la musique de fond du jeu.
"""
def monster_damage():
    try:
        sound = pygame.mixer.Sound("assets/sound/degats.ogg")
        sound.play()
    except pygame.error as e:   # Affiche l'erreur si le fichier son est introuvable ou que la lecture échoue
        print(e)

def open_door():
    try:
        sound = pygame.mixer.Sound("assets/sound/porte.ogg")
        sound.play()
    except pygame.error:
        pass

def attack_sword():
    try:
        sound = pygame.mixer.Sound("assets/sound/attaque.ogg")
        sound.play()
    except pygame.error:
        pass

def heavy_attack():
    try:
        sound = pygame.mixer.Sound("assets/sound/attaque_forte.ogg")
        sound.play()
    except pygame.error:
        pass

def key_open():
    try:
        sound = pygame.mixer.Sound("assets/sound/key_open.ogg")
        sound.play()
    except pygame.error:
        pass

def miss_attack():
    try:
        sound = pygame.mixer.Sound("assets/sound/rate.ogg")
        sound.play()
    except pygame.error:
        pass

def potion_use():
    try:
        sound = pygame.mixer.Sound("assets/sound/heal.ogg")
        sound.play()
    except pygame.error:
        pass


class Musique:
    """
    Classe gérant la musique de fond du jeu.
    Attributes:
        path (str): Le chemin du fichier de musique.
        pause (bool): Indique si la musique est en pause.
        load (bool): Indique si la musique a été chargée.
    """
    def __init__(self,path):
        self.path=path
        self.pause=False
        self.load = False

    def play_music(self,rpt=False): #lance la musique, rpt indique si elle doit être en boucle, load indique si elle a déjà été chargée
        if not self.load:
            pygame.mixer.music.load(self.path)
            pygame.mixer.music.play(-1 if rpt else 0)
            self.load = True
        elif not self.pause:
            pygame.mixer.music.unpause()

    def pause_music(self):  #met en pause la musique
        pygame.mixer.music.pause()
        self.pause=True if not self.pause else False

    def reset_music(self):  #remet la musique au début
        pygame.mixer.music.rewind()

    def music_change(self,path):    #change la musique de fond tout en gardant l'état de pause
        self.path=path
        self.load = False
        self.play_music()
        if self.pause :
            self.pause_music()
            self.pause=True

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
            elif event.type == KEYDOWN:
                if event.key == pygame.K_a:
                    miss_attack()
                elif event.key == pygame.K_z:
                    monster_damage()
                elif event.key == pygame.K_e:
                    open_door()
                elif event.key == pygame.K_r:
                    heavy_attack()
                elif event.key == pygame.K_t:
                    key_open()
                elif event.key == pygame.K_y:
                    sound.music_change("assets/sound/musique_boss.mp3")
                elif event.key == pygame.K_SPACE:
                    sound.pause_music()
        sound.play_music(True)
        clock.tick(10)
    pygame.quit()