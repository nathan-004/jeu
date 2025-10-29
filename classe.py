import pygame
import time
from random import shuffle
import json

from display import TextDisplay, get_size, RoomDisplay, MouseButton, HealthBar, EnnemiDisplay
from map import create_one_solution_map, get_absolute_direction
from constants import *

class Objet:
    current_room = (0, 0)
    def __init__(self, nom, type_, soin=0, degat=0, resistance=0):
        self.nom = nom
        self.type = type_
        self.soin = soin
        self.degat = degat
        self.resistance = resistance
        # initier l'attribut last_used qui correspond à la dernière salle dans laquel un 

    def use(self, personnage):
        # Vérifier que l'objet n'a pas été utilisé si c'est un consommable -> que la salle dans lequel le dernier item a été utilisé est différente de self.current_room
        # Rajouter les attributs de l'objet au personnage (modifie Personnage.use pour appeler cette méthode à la place)
        # Modifier self.last_used par self.current_room
        pass

    def get_message(self) -> str:
        """Renvoie les stats de l'objet sous forme de texte"""
        # Si tu renvoie f"test {NEW_LINE_CHARACTER} test" -> ça sautera une ligne entre les deux tests

        return ""

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

    def __init__(self, n: int = 1, types: list = ["potion", "arme", "armure"]):
        """
        n: Nombre de tirages où l'on est sûr d'avoir le même nombre d'objets
        types: Nom des types d'objet à retourner
        """
        self.types = types
        self.n = n
        self.objets = []  # Contient la liste de types d'objet aléatoires

    def get(self):
        """Retourne un type d'objet aléatoire"""

        if not self.objets:                 # Si la liste est vide, on la recrée

            self.objets = self.types * self.n   # Crée une nouvelle liste contenant self.n fois tous les éléments de self.types
            shuffle(self.objets)         # Mélange la liste aléatoirement

        return self.objets.pop(0)           # Retourne le premier élément et le supprime

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
        degat_restant = degats - (degats * self.resistance)
        self.pv = self.pv - degat_restant
        return degat_restant

    def attaque(self, ennemi):
        return ennemi.degat_subit(self.degat)

    def victoire(self, ennemi):
        """Ajoute de l'exp au personnage en fonction du niveau de l'ennemi"""
        self.exp = ennemi.level - self.level # Ajouter différence de niveau en exp par exemple

        if self.exp // BASE_EXP_LEVEL_UP > 0: # Regarder si exp // 20 par exemple est plus grand que 0
            self.level_up()
            self.exp = self.exp % BASE_EXP_LEVEL_UP # Si c'est le cas appeler self.level_up et mettre exp à exp % 20

    def level_up(self):
        """Prend les attributs du personnage de base et ajoute un nombre * level"""
        self.level = self.level + 1

    def get_max_pv(self):
        return self.pv_base + PLAYER_LEVEL_AUGMENTATION_PV * self.level

class Monstre(Personnage):
    def __init__(self, nom, pv, degats, resistance):
        super().__init__(nom, pv, degats, resistance)
        self.ennemi_display = None
        self.health_bar = None

    def level_up(self):
        super().level_up()

        self.pv = self.pv_base + MONSTER_LEVEL_AUGMENTATION_PV * self.level
        self.degat = self.degat_base + MONSTER_LEVEL_AUGMENTATION_ATTACK * self.level
        self.resistance = min(self.resistance_base + MONSTER_LEVEL_AUGMENTATION_RESISTANCE * self.level, MAX_MONSTER_RESISTANCE)
        self.inventaire.use(self)

    def display(self, surface:pygame.Surface):
        if self.ennemi_display is None:
            self.ennemi_display = EnnemiDisplay(surface, (get_size(surface, 40), 125), 0.5, MONSTERS[self.nom]["image"])
            self.health_bar = HealthBar(self, (get_size(surface, 40), get_size(surface, 70, "height")), (get_size(surface, 20), 50), surface)
        self.ennemi_display.display()
        self.health_bar.display()

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
    
    def level_up(self):
        super().level_up()

        self.pv = self.pv_base + PLAYER_LEVEL_AUGMENTATION_PV * self.level
        self.degat = self.degat_base + PLAYER_LEVEL_AUGMENTATION_ATTACK * self.level
        self.resistance = min(self.resistance_base + PLAYER_LEVEL_AUGMENTATION_RESISTANCE * self.level, MAX_PLAYER_RESISTANCE)
        self.inventaire.use(self)

class Game:
    def __init__(self):
        height, width = 15, 16
        self.map = create_one_solution_map(width, height, 4)
        self.personnage = Joueur("Nom", PLAYER_BASE_PV, PLAYER_BASE_ATTACK, PLAYER_BASE_RESISTANCE, (0, height // 2))

        self.TEXTS = {
            (0, height//2): ["Ceci est un texte plutôt long pour tester le test vicieusement fait", "Ceci est un autre texte qui permet de décrire ce qui se passe dans ce jeu de manière plutôt exhaustive même si le jeu n'est pas fini car c'est le destin. Il y a du texte alors qu'on n'a pas de jeu mais c'est pas si grave. On se demande comment le jeu peut il être joué lorsque les utilisateurs ne connaîssent pas les règles donc on doit bien lui expliquer correctement en développant bien toutes les options"],
            (width//2 - 1, height//2): ["Test3", "Test4"],
            (width-1, height // 2): ["Félicitation, vous êtes arrivés à la fin.", "Mais ne vous méprenez pas.", "L'aventure n'est jamais ..."]
        }

        self.visited = set()
    
    def display_room(self,screen:pygame.Surface, percentage=70):
        room = RoomDisplay(screen, percentage)
        doorL =  pygame.image.load('assets\\images\\doors\\Porte_cote.png')#.transform.flip(img, True, False)
        doorC =  pygame.image.load('assets\\images\\doors\\Porte_Face.png')
        doorR =  pygame.image.load('assets\\images\\doors\\Porte_cote.png')
        doors = [doorR, doorL, doorC]
        dir_ = [(-1, 0), (1, 0), (0, -1)]
        room.display_bg()
        for  i in range(3):
            direction = get_absolute_direction(self.personnage.direction, dir_[i])
            if self.map.can_move(self.personnage.position, direction):
                doors[i] = pygame.transform.scale(doors[i], (get_size(screen, 13*(percentage/100)), get_size(screen, 71*(percentage/100), "height"))) if i != 2 else pygame.transform.scale(doors[i], (get_size(screen,(300*100/get_size(screen,100))*(percentage/100)), get_size(screen, 49*(percentage/100), "height")))
                doors[i] = pygame.transform.flip(doors[i], True, False) if i == 0 else doors[i]
                screen.blit(doors[i],(get_size(screen, ((99.7-percentage)/2)+((85/(100/percentage))if i == 1 else (4/(100/percentage))) ),get_size(screen, 26*(percentage/99.7), "height"))) if i != 2 else screen.blit(doors[i],(get_size(screen, ((100-percentage)/2)+((41-(10/(100/percentage)))) ),get_size(screen, 32*(percentage/99.7), "height")))
        room.display_shade()
        print( self.map.can_move(self.personnage.position, direction) )

    def main(self):
        pygame.font.init()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        map_size = (get_size(self.screen, 30, "height"), get_size(self.screen, 30, "height"))
        map_surface = pygame.Surface(map_size, pygame.SRCALPHA)
        map_surface.fill((0, 0, 0, 180))
        map_position = (get_size(self.screen, 100) - map_size[0], get_size(self.screen, 100, "height") - map_size[1])

        buttons_size = (get_size(self.screen, 100), 50)
        buttons_surface = pygame.Surface(buttons_size, pygame.SRCALPHA)
        buttons_surface.fill((0, 0, 0, 180))
        buttons_position = (0, get_size(self.screen, 100, "height") - buttons_size[1])

        player_health_bar = HealthBar(self.personnage, (0, 0), (150, 50), self.screen)

        self.combat = False
        self.clock = pygame.time.Clock()

        self.current_texts = []

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    if self.current_texts != []:
                        if any(pygame.key.get_pressed()):
                            if self.current_texts != []:
                                if self.current_texts[0].end:
                                    self.current_texts.pop(0)
                                else:
                                    self.current_texts[0].frames = len(self.current_texts[0].txt)
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
                        if self.current_texts != []:
                            if self.current_texts[0].end:
                                self.current_texts.pop(0)
                            else:
                                self.current_texts[0].frames = len(self.current_texts[0].txt)
                if self.combat:
                    self.combat.buttons_event(event)

            cur_room = self.map.grid[self.personnage.position[1]][self.personnage.position[0]]
            if cur_room.monster:
                if not self.combat:
                    self.combat = Combat(self.personnage, Monstre("Knight", MONSTER_BASE_PV, MONSTER_BASE_ATTACK, MONSTER_BASE_RESISTANCE), self)
                    self.current_texts.append(TextDisplay(f"Vous tombez nez à nez avec {self.combat.ennemi.nom}", self.screen, self.clock))

            self.display_room(self.screen)
            self.map.draw(surface=map_surface, player = self.personnage)
            self.screen.blit(map_surface, map_position)

            if self.combat:
                if self.combat.tour % 2 != 0:
                    self.combat.ennemi_turn()
                self.combat.display_buttons(buttons_surface, button_bloc_pos=buttons_position)
                self.screen.blit(buttons_surface, buttons_position)
                self.combat.ennemi.display(self.screen)
            elif cur_room.type == "key":
                self.map.open()
                cur_room.type = "path"
                self.current_texts.append(TextDisplay("Vous avez trouvé une clé", self.screen, self.clock))
                self.current_texts.append(TextDisplay("Une porte s'est ouverte ...", self.screen, self.clock))
            elif cur_room.chest:
                cur_room.chest.closed = False

            player_health_bar.display()
            
            if self.personnage.position in self.TEXTS and self.personnage.position not in self.visited:
                for text in self.TEXTS[self.personnage.position]:
                    self.current_texts.append(TextDisplay(text, self.screen, self.clock))
            
            if self.current_texts != []:
                self.current_texts[0].display()
            
            self.visited.add(self.personnage.position)

            pygame.display.flip()
            self.clock.tick(100)

        pygame.quit()

    def move(self, direction:tuple):
        direction = get_absolute_direction(self.personnage.direction, direction)
        if self.map.can_move(self.personnage.position, direction):
            if not self.combat:
                self.personnage.move(direction)
            else:
                self.current_texts.append(TextDisplay("Ne vous en allez pas si vite !", self.screen, self.clock))
        Objet.current_room = self.personnage.position
    
    def save(self):
        # Sauvegarder la map
        map_content = self.map.get_content()

class Combat:
    def __init__(self, joueur:Joueur, ennemi:Personnage, game: Game):
        self.joueur = joueur
        self.ennemi = ennemi
        self.tour = 0 # Pair quand c'est au tour du joueur
        self.buttons = None
        self.game = game

    def joueur_utiliser(self):
        """Fait utiliser le seul consommable de l'inventaire du joueur"""
        print("Utilise un item")
        if self.tour % 2 == 0:
            self.game.current_texts.append(TextDisplay("Vous utilisez un objet.", self.game.screen, self.game.clock))
            try:
                objet = list(self.joueur.inventaire.consommables.values())[0]
                self.joueur.use(objet)
                self.game.current_texts.append(TextDisplay(objet.get_message(), self.game.screen, self.game.clock))
            except IndexError:
                self.game.current_texts.append(TextDisplay("Vous ne possédez pas de consommables ...", self.game.screen, self.game.clock))
        else:
            return
        self.tour += 1

    def joueur_attaque(self):
        """Attaque du joueur sur l'ennemi"""
        print("Attaque du joueur")
        if self.tour % 2 == 0:
            att = self.joueur.attaque(self.ennemi)
            self.game.current_texts.append(TextDisplay(f"Vous infligez {att} dégâts {NEW_LINE_CHARACTER} Il ne lui reste plus que {self.ennemi.pv} pv", self.game.screen, self.game.clock))
        else:
            return

        self.tour += 1

    def ennemi_turn(self):
        """Tour de l'ennemi choisir action ennemi"""
        if self.tour % 2 == 0:
            return
        
        if self.ennemi.pv <= self.ennemi.pv_base * 0.5: # Jouer ici
            obj = Objet("Soin", "potion", soin=MONSTER_BASE_ITEM_SOIN)
            self.ennemi.use(obj)
            self.game.current_texts.append(TextDisplay(f"L'ennemi utilise un objet {NEW_LINE_CHARACTER} {obj.get_message()}", self.game.screen, self.game.clock))
        else:
            deg = self.ennemi.attaque(self.joueur)
            self.game.current_texts.append(TextDisplay(f"Il vous inflige {deg} dégâts {NEW_LINE_CHARACTER} Il ne vous reste plus que {self.joueur.pv} pv", self.game.screen, self.game.clock))
        self.tour += 1

    def display_buttons(self, surface:pygame.Surface, space_percent:int = 20, button_bloc_pos:tuple = (0, 0)):
        """
        Initie les boutons de combat
        """
        surface.fill((0, 0, 0, 180))

        if self.buttons is None:
            buttons = [("COMBAT", self.joueur_attaque), ("UTILISER", self.joueur_utiliser)]

            space = int(get_size(surface, space_percent) / (len(buttons) + 1))
            size = (int(get_size(surface, 100 - space_percent) / len(buttons)), int(get_size(surface, 100, "height")))

            self.buttons = []
            for idx, (button_txt, button_callable) in enumerate(buttons, start=1):
                pos = (space * idx + size[0] * (idx - 1), 0)
                self.buttons.append(MouseButton(button_txt, pos, size, button_callable, surface, button_bloc_pos))
        
        if self.tour % 2 == 0:
            for button in self.buttons:
                button.display()
    
    def buttons_event(self, event):
        if self.buttons is None or self.tour % 2 != 0:
            return
        
        for button in self.buttons:
            button.handle_event(event)

if __name__ == "__main__":
    g = Game()
    g.main()
    print(g.save())