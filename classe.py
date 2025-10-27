import pygame
import time
from random import shuffle

from display import TextDisplay, get_size, RoomDisplay
from map import create_one_solution_map, get_absolute_direction

class Objet:
    def __init__(self, nom, type_, soin=0, degat=0, resistance=0):
        self.nom = nom
        self.type = type_
        self.soin = soin
        self.degat = degat
        self.resistance = resistance
        # initier la valeur d'utilisation de l'objet

    def use(self, personnage):
        # Vérifier que l'objet n'a pas été utilisé si c'est un consommable 
        # Rajouter les attributs de l'objet au personnage (remplace Personnage.use)
        # Midifier joueur.move pour qu'à chaque appel, reanitialise l'utilisation de l'objet consommable
        pass

class Inventaire:
    def __init__ (self):
        self.equipements = {} 
        self.consommables = {}

    def add(self, obj: Objet):
        if obj.type.lower() == "potion":
            self.consommables[obj.type] = obj
        else:
            self.equipements[obj.type] = obj
            
    def equip(self, perso):
        for objet in self.equipements.values():
            perso.use(objet)

class Coffre:
    """Permet de renvoyer un type d'objet aléatoire en fonction de ceux déjà renvoyés"""

    def __init__(self, n:int=1, types:list=["potion", "arme", "armure"]):
        """
        n: Nombre de tirages où l'on est sûr d'avoir le même nombre d'objets
        types: Nom des types d'objet à retourner
        """
        self.types = types
        self.n = n
        self.objets = [] # Contient la liste de types d'objet aléatoires

    def get(self):
        """Retourne un type d'objet aléatoire"""
        # Regarder si self.objets est vide
        # Si vide : créer une nouvelle liste qui contient self.n fois tous les éléments de self.types et la rendre aléatoire avec shuffle !! Attention aux références !!

        # Retourner le premier élément de self.objets et le supprimer (liste.pop(0) ?)

class Personnage:
    def __init__(self, nom, pv, degats, resistance):
        """
        Constructeur de la classe Personnage
        Attributs :
            - nom : chaine de caractères qui sert de prénom au personnage
            - pv : entier positif ou nul qui représente les point de vie du personnage
            - degats : entier positif qui agit comme quantité de degats qu'inflige le personnage
            - resistance : entier soustrayant les degats subit pour connaitre le nombre de point de vie retirée
        """
        self.nom = nom
        self.pv = pv
        self.degat = degats
        self.resistance = resistance

        self.pv_base = self.pv
        self.degat_base = self.degat
        self.resistance_base = self.resistance

        self.exp = 0
        self.level = 0
        self.inventaire = Inventaire()

    def use(self, obj:Objet):
        self.pv += obj.soin
        self.degat += obj.degat
        self.resistance += obj.resistance

    def degat_subit(self, degats):
        degat_restant = self.degat // self.resistance
        self.pv = self.pv - degat_restant

    def attaque(self, ennemi):
        ennemi.degat_subit(self.degat)

    def victoire(self, ennemi):
        """Ajoute de l'exp au personnage en fonction du niveau de l'ennemi"""
        self.exp = ennemi.level - self.level # Ajouter différence de niveau en exp par exemple

        if self.exp // 20 > 0: # Regarder si exp // 20 par exemple est plus grand que 0
            self.level_up()
            self.exp = self.exp % 20 # Si c'est le cas appeler self.level_up et mettre exp à exp % 20

    def level_up(self):
        """Prend les attributs du personnage de base et ajoute un nombre * level"""
        self.level = self.level + 1 # Augmente self.level de 1

        self.pv = self.pv_base + 20 * self.level
        self.degat = self.degat_base + 20 * self.level
        self.resistance = self.resistance_base + 20 * self.level # Modifie les attributs par attributs de base + 20 par exemple * self.level (Stocker les attributs de base dans __init__)
        self.inventaire.use(self) # (Use tous les objets de l'inventaire non consommable)

class Monstre(Personnage):
    pass

class Joueur(Personnage):
    def __init__(self, nom, pv, degats, resistance, position:tuple, inventaire:Inventaire = Inventaire() ):
        super().__init__(nom, pv, degats, resistance)
        self.position = position
        self.direction = (1, 0) # Direction de base vers la droite
        self.inventaire = inventaire

    def equipe_obj(self, obj:Objet):
        self.obj = obj
    
    def move(self, direction:tuple):
        self.position = (self.position[0] + direction[0], self.position[1] + direction[1])
        self.direction = direction

class Game:
    def __init__(self):
        height, width = 15, 16
        self.map = create_one_solution_map(width, height, 4)
        self.personnage = Joueur("Nom",50,50,1, (0, height // 2))

        self.TEXTS = {
            (0, height//2): ["Ceci est un texte plutôt long pour tester le test vicieusement fait", "Ceci est un autre texte qui permet de décrire ce qui se passe dans ce jeu de manière plutôt exhaustive même si le jeu n'est pas fini car c'est le destin. Il y a du texte alors qu'on n'a pas de jeu mais c'est pas si grave. On se demande comment le jeu peut il être joué lorsque les utilisateurs ne connaîssent pas les règles donc on doit bien lui expliquer correctement en développant bien toutes les options"],
            (width//2 - 1, height//2): ["Test3", "Test4"],
            (width-1, height // 2): ["Félicitation, vous êtes arrivés à la fin.", "Mais ne vous méprenez pas.", "L'aventure n'est jamais ..."]
        }

        self.visited = set()
    
    def display_room(self,screen :pygame.Surface, direction:tuple,percentage=70):
        room = RoomDisplay(screen, percentage)
        direction = get_absolute_direction(self.personnage.direction, direction)
        doorL =  pygame.image.load('assets\\images\\doors\\Porte_cote.png')#.transform.flip(img, True, False)
        doorC =  pygame.image.load('assets\\images\\doors\\Porte_Face.png')
        doorR =  pygame.image.load('assets\\images\\doors\\Porte_cote.png')
        doors = [doorR, doorL, doorC]
        dir = ['left', 'right', 'top', 'bottom']
        room.display_bg()
        for  i in range(3):
            if self.map.can_move(self.personnage.position, direction):
                doors[i] = pygame.transform.scale(doors[i], (get_size(screen, 13*(percentage/100)), get_size(screen, 71*(percentage/100), "height"))) if i != 2 else pygame.transform.scale(doors[i], (get_size(screen,(300*100/get_size(screen,100))*(percentage/100)), get_size(screen, 49*(percentage/100), "height")))
                doors[i] = pygame.transform.flip(doors[i], True, False) if i == 0 else doors[i]
                screen.blit(doors[i],(get_size(screen, ((99.7-percentage)/2)+((85/(100/percentage))if i == 1 else (4/(100/percentage))) ),get_size(screen, 26*(percentage/99.7), "height"))) if i != 2 else screen.blit(doors[i],(get_size(screen, ((100-percentage)/2)+((41-(10/(100/percentage)))) ),get_size(screen, 32*(percentage/99.7), "height")))
        room.display_shade()
        print( get_absolute_direction(self.personnage.direction, (0, 0)) )

    def main(self):
        pygame.font.init()

        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        map_size = (get_size(screen, 30, "height"), get_size(screen, 30, "height"))
        map_surface = pygame.Surface(map_size, pygame.SRCALPHA)
        map_surface.fill((0, 0, 0, 180))
        map_position = (get_size(screen, 100) - map_size[0], get_size(screen, 100, "height") - map_size[1])

        self.combat = False
        clock = pygame.time.Clock()

        current_texts = []

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    if current_texts != []:
                        if any(pygame.key.get_pressed()):
                            if current_texts != []:
                                if current_texts[0].end:
                                    current_texts.pop(0)
                                else:
                                    current_texts[0].frames = len(current_texts[0].txt)
                        continue
                    
                    if event.key == pygame.K_RIGHT:
                        self.move((1, 0))
                    elif event.key == pygame.K_UP:
                        self.move((0, -1))
                    elif event.key == pygame.K_DOWN:
                        self.move((0, 1))
                    elif event.key == pygame.K_LEFT:
                        self.move((-1, 0))
                    elif any(pygame.key.get_pressed()):
                        if current_texts != []:
                            if current_texts[0].end:
                                current_texts.pop(0)
                            else:
                                current_texts[0].frames = len(current_texts[0].txt)

            self.display_room(screen, self.personnage.position)
            self.map.draw(surface=map_surface, player = self.personnage)
            screen.blit(map_surface, map_position)

            if self.personnage.position in self.TEXTS and self.personnage.position not in self.visited:
                for text in self.TEXTS[self.personnage.position]:
                    current_texts.append(TextDisplay(text, screen, clock))
            
            if current_texts != []:
                current_texts[0].display()
            
            self.visited.add(self.personnage.position)

            pygame.display.flip()
            clock.tick(100)

        pygame.quit()

    def move(self, direction:tuple):
        direction = get_absolute_direction(self.personnage.direction, direction)
        if self.map.can_move(self.personnage.position, direction):
            if not self.combat:
                self.personnage.move(direction)
            else:
                self.personnage.move(direction)

        cur_room = self.map.grid[self.personnage.position[1]][self.personnage.position[0]]
        if cur_room.monster:
            self.combat = Combat(self.personnage, Monstre("Test", 10, 10, 10))
        if cur_room.type == "key":
            self.map.open()
            cur_room.type = "path"
        if cur_room.chest:
            cur_room.chest.closed = False
        
        

class Combat:
    def __init__(self, joueur:Joueur, ennemi:Personnage):
        self.joueur = joueur
        self.ennemi = ennemi
        self.tour = 0 # Pair quand c'est au tour du joueur

    def joueur_utiliser(self, objet:Objet):
        """Fait utiliser un objet de l'inventaire du joueur"""
        if self.tour % 2 == 0:
            self.joueur.use(objet)
        else:
            return
        self.tour += 1

    def joueur_attaque(self):
        """Attaque du joueur sur l'ennemi"""
        if self.tour % 2 == 0:
            self.joueur.attaque(self.ennemi)
        else:
            return

        self.tour += 1

    def ennemi_turn(self):
        """Tour de l'ennemi choisir action ennemi"""
        if self.tour % 2 == 0:
            return
        
        if self.ennemi.pv <= 10: # Jouer ici
            self.ennemi.use(Objet("Soin", "potion", soin=10))
        else:
            self.ennemi.attaque(self.joueur)
        self.tour += 1   

if __name__ == "__main__":
    g = Game()
    g.main()