import pygame
import time
from random import shuffle, randint, choice, uniform
import json
from typing import Optional

from display import TextDisplay, get_size, RoomDisplay, MouseButton, HealthBar, EnnemiDisplay, ChestDisplay, get_dialogue_text, ItemDisplay, Credits
from map import create_one_solution_map, get_absolute_direction, Map
from constants import *
from son import *

BUTTONS = []


def make_buttons(surface: pygame.Surface, actions: list, space_percent: int = 20, button_bloc_pos: tuple = (0, 0)) -> list:
    """
    Crée et renvoie une liste de MouseButton pour la surface donnée.

    Parameters
    ----------
    surface: pygame.Surface
        Surface sur laquelle les boutons seront dessinés (utilisée pour calculs de taille).
    actions: list
        Liste de tuples (label: str, callback: Callable).
    space_percent: int
        Pourcentage d'espace réservé autour des boutons (voir implémentation originale).
    button_bloc_pos: tuple
        Position (offset) en coordonnées fenêtre où la surface contenant les boutons est blittée.
    """
    if not actions:
        return []

    nb = len(actions)
    space = int(get_size(surface, space_percent) / (nb + 1))
    size = (int(get_size(surface, 100 - space_percent) / nb), int(get_size(surface, 100, "height")))

    buttons = []
    for idx, (button_txt, button_callable) in enumerate(actions, start=1):
        pos = (space * idx + size[0] * (idx - 1), 0)
        buttons.append(MouseButton(button_txt, pos, size, button_callable, surface, button_bloc_pos))

    return buttons

def make_vertical_buttons(surface: pygame.Surface, actions: list, space_percent: int = 20, button_bloc_pos: tuple = (0, 0)) -> list:
    """
    Crée et renvoie une liste de MouseButton pour la surface donnée.

    Parameters
    ----------
    surface: pygame.Surface
        Surface sur laquelle les boutons seront dessinés (utilisée pour calculs de taille).
    actions: list
        Liste de tuples (label: str, callback: Callable).
    space_percent: int
        Pourcentage d'espace réservé autour des boutons (voir implémentation originale).
    button_bloc_pos: tuple
        Position (offset) en coordonnées fenêtre où la surface contenant les boutons est blittée.
    """
    if not actions:
        return []

    nb = len(actions)
    space = int(get_size(surface, space_percent, "height") / (nb + 1))
    size = (int(get_size(surface, 100)), int(get_size(surface, 100 - space_percent, "height") / nb))

    buttons = []
    for idx, (button_txt, button_callable) in enumerate(actions, start=1):
        pos = (0, space * idx + size[1] * (idx - 1))
        buttons.append(MouseButton(button_txt, pos, size, button_callable, surface, button_bloc_pos))

    return buttons

def add_random_dialogue(monster_type:str, event:str, game):
    if monster_type == "Ventre d'Acier":
        if event == "start" or event == "monster_death" or event == "player_death":
            for el in MONSTERS[monster_type]["dialogues"][event]:
                game.current_texts.append(get_dialogue_text(el, None, game.screen, game.clock))
            return
        elif event == "receive_damage":
            gen = MONSTERS[monster_type]["dialogues"][event]
            txts = next(gen, ("..."))
            for el in txts:
                game.current_texts.append(get_dialogue_text(el, None, game.screen, game.clock))
            return
        else:
            pass

    txt = get_random_dialogue(monster_type, event)

    if txt is not None:
        game.current_texts.append(get_dialogue_text(txt, None, game.screen, game.clock))

def get_random_dialogue(monster_type:str, event:str) -> Optional[str]:
    # Sur 10, seulement 5 fois où il y a du texte
    max_ = 10
    prob = 5
    try:
        texts = MONSTERS[monster_type]["dialogues"][event]
    except:
        return "..."

    if randint(1, max_) <= prob:
        return choice(texts)
    return None

def get_random_monster(game):
    """Renvoie un monstre"""
    if game.map.name == "start":
        return Monstre("Chevalier", 30, 1, 0)
    elif game.map.name == "end":
        return Monstre("Ventre d'Acier", 100, 10, 0.6)

    monster_type = choice(MONSTERS_LIST)
    monster = Monstre(monster_type)
    monster.level_up(get_level(game))
    return monster

def get_random_item_stats(game, type_:str) -> tuple:
    """Renvoie un tuple (soin, degats, resistance) basé sur l'avancement du joueur et son niveau"""
    if game.map.name == "start":
        level = 0
    elif game.map.name == "end":
        level = 50
    else:
        level = get_level(game)

    soin, degats, resistance = 0,0,0

    if type_ == "potion":
        soin = PLAYER_BASE_ITEM_SOIN + level * PLAYER_ITEM_LEVEL_AUGMENTATION_SOIN
    elif type_ == "arme":
        degats = PLAYER_BASE_ATTACK + level * PLAYER_ITEM_LEVEL_AUGMENTATION_DEGATS
    elif type_ == "armure":
        resistance = PLAYER_BASE_ITEM_RES + level * PLAYER_ITEM_LEVEL_AUGMENTATION_RES

    return tuple([val * (1 + uniform(-0.3, 0.3)) for val in [soin, degats, resistance]])

def is_better(obj1, obj2) -> int:
    """
    Renvoi si l'objet 1 est meilleur que l'objet 2
    < 0 si obj2 est meilleur
    > 1 si obj1 est meilleur
    0 s'ils sont équivalents
    """
    parameters = ["soin", "degat", "resistance"]
    obj1_n = 0
    obj2_n = 0

    for obj1_val, obj2_val in zip([getattr(obj1, par) for par in parameters], [getattr(obj2, par) for par in parameters]):
        obj1_n += int(obj1_val > obj2_val)
        obj2_n += int(obj2_val > obj1_val)

    return obj1_n - obj2_n

class Objet:
    current_room = (0, 0)

    def __init__(self, nom, type_, soin=0, degat=0, resistance=0):
        self.nom = nom
        self.type = type_
        self.soin = soin
        self.degat = degat
        self.resistance = resistance
        self.last_used = None

    def use(self, personnage):
        """
        - Vérifie que l'objet n'a pas été utilisé dans la même salle
        - Ajoute les attributs de l'objet au personnage
        - Met à jour last_used
        """

        if self.last_used == self.current_room:
            return False

        personnage.pv += self.soin
        personnage.degat += self.degat
        personnage.resistance += self.resistance

        self.last_used = self.current_room

        return True

    def get_message(self) -> str:
        """
        Renvoie les stats de l'objet sous forme de texte.
        """
        message = f"{self.nom}, {self.type} {NEW_LINE_CHARACTER} "

        # Ajouter seulement les valeurs différentes de 0
        if self.soin != 0:
            message += f"Soin : +{self.soin:.1f} {NEW_LINE_CHARACTER} "
        if self.degat != 0:
            message += f"Dégâts : +{self.degat:.1f} {NEW_LINE_CHARACTER} "
        if self.resistance != 0:
            message += f"Résistance : +{self.resistance:2f} {NEW_LINE_CHARACTER} "

        return message

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

    def get(self, type_) -> Objet:
        if type_ in self.consommables:
            return self.consommables[type_]
        elif type_ in self.equipements:
            return self.equipements[type_]
        return Objet(None, None)

    def get_content(self) -> dict:
        """Renvoie les informations à sauvegarder"""
        content = {
            "equipements": {
                obj.type: {"nom": obj.nom, "soin": obj.soin, "degat": obj.degat, "resistance": obj.resistance} for obj in self.equipements.values()
            },
            "consommables": {
                obj.type: {"nom": obj.nom, "soin": obj.soin, "degat": obj.degat, "resistance": obj.resistance} for obj in self.consommables.values()
            }
        }

        return content

    def load(self, content:dict):
        for obj_type, obj in content["equipements"].items():
            self.equipements[obj_type] = Objet(obj["nom"], obj_type, obj["soin"], obj["degat"], obj["resistance"])
        for obj_type, obj in content["consommables"].items():
            self.consommables[obj_type] = Objet(obj["nom"], obj_type, obj["soin"], obj["degat"], obj["resistance"])

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
        self.item = None

        self.chest_display = None
        self.item_display = None
        self.text_display = None
        self.end = False
        self.buttons = None

        self.actions_end = False

    def get(self):
        """Retourne un type d'objet aléatoire"""
        if not self.objets:
            self.objets = self.types * self.n
            shuffle(self.objets)

        return self.objets.pop(0)

    def display(self, game, pos:tuple, size:tuple):
        if self.chest_display is None:
            self.open_animation(game.screen, pos, size)
        elif not self.chest_display.ended:
            self.open_animation(game.screen, pos, size)
        elif not self.actions_end:
            self.display_item_choice(game, pos, size)
        else:
            self.end = True

    def open_animation(self, surface:pygame.Surface, pos:tuple, size:tuple):
        # La taille et la position correspondent à une bande au milieu de l'écran
        if self.chest_display is None:
            self.chest_display = ChestDisplay(surface, pos, size) # Initier un objet ChestDisplay dans self.chest_display
            self.chest_display.closed = False # L'ouvrir
        self.chest_display.display()

    def display_item_choice(self, game, pos: tuple, size: tuple):
        """
        Affiche un objet aléatoire dans une carte, propose au joueur de l'accepter ou de le refuser.
        """
        self.game = game
        # Création d'un objet aléatoire
        if self.item is None:
            type_objet = self.get()
            nom = type_objet.capitalize()

            if type_objet == "arme":
                nom = choice(["Lance", "Epée"])

            soin, degat, resistance = get_random_item_stats(game, type_objet)

            self.item = Objet(nom, type_objet, soin=soin, degat=degat, resistance=resistance)

        if self.item_display is None:
            self.item_display = ItemDisplay(game.screen, pos, (size[0], size[1]/2), self.item)
        if self.text_display is None:
            val = is_better(self.item, game.personnage.inventaire.get(self.item.type))
            if val < 0:
                color = (255, 0, 0)
            elif val > 0:
                color = (0, 255, 0)
            else:
                color = (0, 0, 0)
            self.text_display = TextDisplay(self.item.get_message(), game.screen, game.clock, size = (size[0], size[1]/2), pos=(pos[0], pos[1] + size[1]/2), background_color=(50, 50, 50), color=color)

        self.item_display.display()
        self.text_display.display()

        actions = [
            ("Accepter", self.accept_item),
            ("Refuser", self.decline_item)
        ]
        buttons_surface = pygame.Surface((size[0], 80), pygame.SRCALPHA)
        buttons_surface.fill((0, 0, 0, 150))
        buttons_pos = (pos[0], pos[1] + size[1] + 10)

        self.buttons = make_buttons(buttons_surface, actions, space_percent=20, button_bloc_pos=buttons_pos)

        # Affichage des boutons
        for b in self.buttons:
            b.display()

        game.screen.blit(buttons_surface, buttons_pos)

    def buttons_event(self, event):
        if self.buttons is None:
            return

        for button in self.buttons:
            button.handle_event(event)

    def accept_item(self):
        """
        Ajoute l'item au joueur, puis marque la fin de l'action.
        """
        if hasattr(self, "item") and self.item:
            self.game.personnage.inventaire.add(self.item)
            self.game.personnage.reset()
            self.game.current_texts.append(
                TextDisplay(f"Vous obtenez : {self.item.get_message()}", self.game.screen, self.game.clock)
            )

        self.actions_end = True
        self.end = True

    def decline_item(self):
        """
        Le joueur refuse l’objet, simplement fermer l’interface du coffre.
        """
        self.actions_end = True
        self.end = True

    def reset(self):
        self.chest_display = None
        self.end = False
        self.actions_end = False
        self.item = None
        self.item_display = None
        self.text_display = None

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
        potion_use() if obj.soin > 0 else None
        return obj.use(self)

    def degat_subit(self, degats):
        degat_restant = degats - (degats * self.resistance)
        self.pv = self.pv - degat_restant

        if self.pv < 0:
            self.pv = 0

        return degat_restant

    def attaque(self, ennemi):
        a = randint(1, 10)
        if a >= 1:
            if self.nom=="Ventre d'Acier":
                heavy_attack()
            else:
                attack_sword()
            return ennemi.degat_subit(self.degat)
        else:
            miss_attack()
            return None

    def attaque_lourde(self, ennemi):
        a = randint(1, 10)
        if a >= 7:
            heavy_attack()
            return ennemi.degat_subit(self.degat*2)
        else:
            miss_attack()
            return None

    def level_up(self):
        """Prend les attributs du personnage de base et ajoute un nombre * level"""
        if self.level >= MAX_LEVEL:
            self.level = MAX_LEVEL - 1
        self.level = self.level + 1

    def get_max_pv(self):
        return self.pv_base + PLAYER_LEVEL_AUGMENTATION_PV * self.level

    def get_stats_message(self) -> str:
        content = f"{self.nom} & PV : {self.pv}/{self.get_max_pv()} & Degats : {self.degat} & Resistance : {self.resistance} & Exp : {self.exp}/{ BASE_EXP_LEVEL_UP * (BASE_EXP_LEVEL_UP_AUGMENTATION_COEFF**self.level)} & Level : {self.level}"
        return content

class Monstre(Personnage):
    def __init__(self, nom, pv=uniform(-MONSTER_BASE_PV_RANGE/2, MONSTER_BASE_PV_RANGE/2) + MONSTER_BASE_PV, degats=uniform(-MONSTER_BASE_ATTACK_RANGE/2, MONSTER_BASE_ATTACK_RANGE/2) + MONSTER_BASE_ATTACK, resistance=uniform(-MONSTER_BASE_RESISTANCE_RANGE/2, MONSTER_BASE_RESISTANCE_RANGE/2) + MONSTER_BASE_RESISTANCE):
        super().__init__(nom, pv, degats, resistance)
        self.ennemi_display = None
        self.health_bar = None
        self.damage = False

    def level_up(self, level:int = None):
        if level is None:
            super().level_up()
        else:
            self.level = level

        self.pv = self.pv_base + MONSTER_LEVEL_AUGMENTATION_PV * self.level
        self.degat = self.degat_base + MONSTER_LEVEL_AUGMENTATION_ATTACK * self.level
        self.resistance = min(self.resistance_base + MONSTER_LEVEL_AUGMENTATION_RESISTANCE * self.level, MAX_MONSTER_RESISTANCE)

    def degat_subit(self, degats):
        self.damage = True
        monster_damage()
        return super().degat_subit(degats)

    def display(self, surface:pygame.Surface):
        if self.ennemi_display is None:
            self.ennemi_display = EnnemiDisplay(surface, (get_size(surface, 40), 125), 0.5, MONSTERS[self.nom]["image"])
            self.health_bar = HealthBar(self, (get_size(surface, 40), get_size(surface, 5, "height")), (get_size(surface, 20), 50), surface)
        if self.damage:
            self.ennemi_display.display_damage()
        else:
            self.ennemi_display.display()
        self.health_bar.display()
        self.damage = False

    def use(self, obj:Objet):
        self.pv += obj.soin
        potion_use() if obj.soin > 0 else None
        self.degat += obj.degat
        self.resistance += obj.resistance

class Joueur(Personnage):
    def __init__(self, nom, pv, degats, resistance, position:tuple, inventaire:Inventaire = Inventaire(), game = None):
        super().__init__(nom, pv, degats, resistance)
        self.position = position
        self.direction = (1, 0) # Direction de base vers la droite
        self.inventaire = inventaire
        self.game = game

    def equipe_obj(self, obj:Objet):
        self.obj = obj

    def move(self, direction:tuple):
        open_door()
        self.position = (self.position[0] + direction[0], self.position[1] + direction[1])
        self.direction = direction

    def victoire(self, ennemi:Personnage):
        """Ajoute de l'exp au personnage en fonction du niveau de l'ennemi"""
        new_exp = BASE_EXP_REWARD * (BASE_EXP_LEVEL_UP_AUGMENTATION_COEFF ** ennemi.level) + randint(-BASE_EXP_REWARD_RANGE//2, BASE_EXP_REWARD_RANGE//2)
        self.exp += new_exp
        self.game.current_texts.append(TextDisplay(f"Vous avez battu {ennemi.nom} vous gagnez {new_exp} exp", self.game.screen, self.game.clock))

        val = BASE_EXP_LEVEL_UP * (BASE_EXP_LEVEL_UP_AUGMENTATION_COEFF**self.level)
        while self.exp >= val:
            if self.exp >= val:
                self.level_up()
                self.exp -= val
                val *= BASE_EXP_LEVEL_UP_AUGMENTATION_COEFF

    def level_up(self):
        super().level_up()
        self.reset()
        self.game.current_texts.append(TextDisplay(f"Vous passez au niveau {self.level}", self.game.screen, self.game.clock))

    def reset(self):
        self.pv = self.pv_base + PLAYER_LEVEL_AUGMENTATION_PV * self.level
        self.degat = self.degat_base + PLAYER_LEVEL_AUGMENTATION_ATTACK * self.level
        self.resistance = self.resistance_base + PLAYER_LEVEL_AUGMENTATION_RESISTANCE * self.level
        self.inventaire.equip(self)
        self.resistance = min(self.resistance, MAX_PLAYER_RESISTANCE)
        self.pv, self.degat, self.resistance = round(self.pv, 1), round(self.degat, 1), round(self.resistance, 3)

    def get_content(self) -> dict:
        """Renvoie les informations sous forme de dictionnaire qui pourront être transcrite au format json"""
        content = {
            "position": self.position,
            "inventaire": self.inventaire.get_content(),
            "level": self.level,
            "exp": self.exp
        }

        return content

    def load(self, content:dict):
        """Modifie self.personnage pour correspondre aux valeurs de content"""
        self.position = tuple(content["position"])
        self.level = content["level"]
        self.exp = content["exp"]
        self.inventaire.load(content["inventaire"])
        self.reset()

class Game:
    def __init__(self):
        self.height, self.width = 15, 16
        self.elements = self.get_maps()
        self.map, self.texts = next(self.elements)
        self.personnage = Joueur("Nom", PLAYER_BASE_PV, PLAYER_BASE_ATTACK, PLAYER_BASE_RESISTANCE, self.map.get_start_position(), game = self)

        self.visited = set()
        self.last_moved = False
        self.end = False

    def display_room(self,screen:pygame.Surface, percentage=70):
        if self.room is None:
            self.room = RoomDisplay(screen, percentage)
        if self.last_moved:
            self.room.start_enter()
            self.last_moved = False
        doorL =  pygame.image.load('assets\\images\\doors\\Porte_cote.png')#.transform.flip(img, True, False)
        doorC =  pygame.image.load('assets\\images\\doors\\Porte_Face.png')
        doorR =  pygame.image.load('assets\\images\\doors\\Porte_cote.png')
        doors = [doorR, doorL, doorC]
        dir_ = [(-1, 0), (1, 0), (0, -1)]
        self.room.display_bg()
        for  i in range(3):
            direction = get_absolute_direction(self.personnage.direction, dir_[i])
            if self.map.can_move(self.personnage.position, direction):
                doors[i] = pygame.transform.scale(doors[i], (get_size(screen, 13*(percentage/100)), get_size(screen, 71*(percentage/100), "height"))) if i != 2 else pygame.transform.scale(doors[i], (get_size(screen,(300*100/get_size(screen,100))*(percentage/100)), get_size(screen, 49*(percentage/100), "height")))
                doors[i] = pygame.transform.flip(doors[i], True, False) if i == 0 else doors[i]
                screen.blit(doors[i],(get_size(screen, ((99.7-percentage)/2)+((85/(100/percentage))if i == 1 else (4/(100/percentage))) ),get_size(screen, 26*(percentage/99.7), "height"))) if i != 2 else screen.blit(doors[i],(get_size(screen, ((100-percentage)/2)+((36.3-(10/(100/percentage)))) ),get_size(screen, 32*(percentage/99.7), "height")))
        self.room.display_shade()
        self.room.display_enter()

    def start_menu(self):
        pygame.font.init()
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        buttons = [("Charger", self._start_loaded_game), ("Nouvelle", self._start_new_game), ("Demo", self._start_demo_game), ("Quitter", self._quit_start_menu)] # A modifier pour stopper l'erreur
        buttons_size = (get_size(screen, 50), get_size(screen, 75, "height"))
        buttons_pos = (get_size(screen, 25), get_size(screen, 12.5, "height"))
        buttons_surface = pygame.Surface(buttons_size, pygame.SRCALPHA)
        buttons = make_vertical_buttons(buttons_surface, buttons, 10, buttons_pos)

        self.start_running = True

        while self.start_running: # Créer la boucle de fonctionnement
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.start_running = False

                for button in buttons:
                    button.handle_event(event)

            for button in buttons:
                button.display()

            screen.fill((0,0,0))
            screen.blit(buttons_surface, buttons_pos)
            pygame.display.flip()

        pygame.quit()

    def main(self):
        pygame.font.init()
        MUSIQUE = True
        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(RED, "Erreur lors de l'initialisation du son (vérifier si sortie audio connectée) :", e, RESET)
            MUSIQUE = False

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

        item_choice_size = (get_size(self.screen, 40), get_size(self.screen, 40, "height"))
        item_choice_pos = (get_size(self.screen, 30), get_size(self.screen, 30, "height"))
        self.coffre = Coffre(1)

        self.combat = False
        self.clock = pygame.time.Clock()
        self.room = None

        debug_text_size = (75, 50)
        debug_text_pos = (get_size(self.screen, (100 - debug_text_size[0])/2), get_size(self.screen, (100 - debug_text_size[1])/2, "height"))
        debug_text_size = (get_size(self.screen, debug_text_size[0]), get_size(self.screen, debug_text_size[1], "height"))
        debug_text = TextDisplay(self.personnage.get_stats_message(), self.screen, self.clock, background_color=(0,0,0), color=(255,255,255), pos=debug_text_pos, size=debug_text_size)

        if MUSIQUE:
            self.musique = Musique("assets/sound/musique_boucle1.mp3")

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

                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.move((1, 0))
                    elif event.key == pygame.K_UP or event.key == INPUT_LIST[0]:
                        self.move((0, -1))
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.move((0, 1))
                    elif event.key == pygame.K_LEFT or event.key == INPUT_LIST[1]:
                        self.move((-1, 0))
                    elif any(pygame.key.get_pressed()):
                        if self.current_texts != []:
                            if self.current_texts[0].end:
                                self.current_texts.pop(0)
                            else:
                                self.current_texts[0].frames = len(self.current_texts[0].txt)

                if self.combat:
                    self.combat.buttons_event(event)
                if self.coffre:
                    self.coffre.buttons_event(event)

            if MUSIQUE:
                self.musique.play_music(True)

            if self.end:
                self.end.display()
                if self.end.end:
                    self.end = False
                    running = False
                pygame.display.flip()
                self.clock.tick(60)
                continue

            if self.personnage.position in self.texts and self.personnage.position not in self.visited:
                for text in self.texts[self.personnage.position]:
                    self.current_texts.append(TextDisplay(f"V.A. - {text}", self.screen, self.clock))
            if self.personnage.position in self.texts:
                self.save()

            cur_room = self.map.grid[self.personnage.position[1]][self.personnage.position[0]]

            if cur_room.type == "end" and not cur_room.locked:
                try:
                    self.map, self.texts = next(self.elements)
                    self.personnage.position = self.map.get_start_position()
                    self.visited = set()
                    continue
                except StopIteration:
                    if self.current_texts == []:
                        self.end = Credits(CREDITS_TEXT, self.screen, self.clock)

            self.display_room(self.screen)
            self.map.draw(surface=map_surface, player = self.personnage)
            self.screen.blit(map_surface, map_position)

            if self.combat:
                if self.combat.ennemi.nom == "Ventre d'Acier":
                    if MUSIQUE:
                        self.musique.music_change("assets/sound/musique_boss.mp3") if self.musique.path != "assets/sound/musique_boss.mp3" else None
                if self.combat.is_ended() and self.current_texts == []:
                    if type(self.combat.winner) is Joueur:
                        self.combat = False
                        cur_room.monster = False
                        if MUSIQUE:
                            self.musique.music_change("assets/sound/musique_boucle1.mp3") if self.musique.path != "assets/sound/musique_boucle1.mp3" else None
                        continue
                    else:
                        running = False
                if self.combat.tour % 2 != 0:
                    self.combat.ennemi_turn()
                self.combat.display_buttons(buttons_surface, button_bloc_pos=buttons_position)
                self.screen.blit(buttons_surface, buttons_position)
                self.combat.ennemi.display(self.screen)
            elif cur_room.type == "key":
                self.map.open()
                cur_room.type = "path"
                key_open()
                self.current_texts.append(TextDisplay("Vous avez trouvé une clé", self.screen, self.clock))
                self.current_texts.append(TextDisplay("Une porte s'est ouverte ...", self.screen, self.clock))
            elif cur_room.chest:
                if not self.combat and not self.room.enter_animation:
                    if self.coffre.chest_display is None and not self.coffre.end:
                        self.current_texts.append(TextDisplay("Vous trouvez un coffre. Vous l'ouvrez.", self.screen, self.clock))
                    if self.current_texts != [] and (self.coffre.chest_display is None or not self.coffre.chest_display.ended):
                        self.coffre.reset()
                    self.coffre.display(self, item_choice_pos, item_choice_size)
                    if self.coffre.end:
                        cur_room.chest = False
                        self.coffre.reset()

            if cur_room.monster:
                if not self.combat and not self.room.enter_animation:
                    self.combat = Combat(self.personnage, get_random_monster(self), self)
                    self.current_texts.append(TextDisplay(f"Vous tombez nez à nez avec {self.combat.ennemi.nom} LV{self.combat.ennemi.level}", self.screen, self.clock))
                    add_random_dialogue(self.combat.ennemi.nom, "start", self)

            player_health_bar.display()

            if self.current_texts != []:
                self.current_texts[0].display()

            self.visited.add(self.personnage.position)

            keys = pygame.key.get_pressed()

            if keys[pygame.K_e]:
                stats = self.personnage.get_stats_message()
                if f"*{stats}*" != debug_text.txt:
                    debug_text = TextDisplay(stats, self.screen, self.clock, background_color=(0, 0, 0), color=(255,255,255), pos=debug_text_pos, size=debug_text_size)
                borders = pygame.Rect(debug_text_pos, debug_text_size)
                debug_text.display(20)
                pygame.draw.rect(self.screen, (255,255,255) , borders, 2)

            pygame.display.flip()
            self.clock.tick(100)

    def move(self, direction:tuple):
        direction = get_absolute_direction(self.personnage.direction, direction)
        if self.map.can_move(self.personnage.position, direction):
            if not self.combat:
                self.personnage.move(direction)
                self.last_moved = True
            else:
                self.current_texts.append(TextDisplay("Ne vous en allez pas si vite !", self.screen, self.clock))
        Objet.current_room = self.personnage.position

    def get_maps(self, demo=False):
        """Renvoie un générateur contenant un tuple map, text"""
        yield (self._load_map("assets/maps/start"), self._load_text("assets/maps/start"))
        if not demo:
            base_text = {
                (0, self.height//2): ["Vous y êtes arrivé !", "Il ne vous reste plus qu'à trouver le chemin dans ce donjon, à battre tous les ennemis sur votre chemin, à acquérir les meilleurs statistiques.", "On ne sait jamais, ce qui semble être la fin peut parfois n'être que le début d'une plus grande aventure."],
                (self.width//4, self.height//2): ["Vous avez l'air de bien vous en sortir", "En espérant que vous ne mourriez pas dans d'atroces souffrances.", "Un homme comme vous a déjà fait son apparition auparavant ..."],
                (self.width//4 + 1, self.height // 2): ["Il était rempli d'espoir, il s'en est sorti pendant bien longtemps.", "Trop longtemps", "Si longtemps qu'il en a perdu la raison."],
                (self.width//2, self.height // 2): ["Chaque monstre connaît son armure iconique. & Ils ont tous appris à la fuir", "Car lassé de cet endroit, il n'a laissé aucun témoin de son passage."],
                (self.width//2 + 1, self.height // 2): ["Seulement un nom, une réputation, et les corps qu'il a laissé derrière lui.", "Mais n'importe qui deviendrait fou dans cet endroit. Non ?"],
                (self.width - self.width//4, self.height//2): ["On dit de lui qu'il a finalement réussi à sortir de cet endroit.", "Et qu'il attend patiemment tout survivant pour ...", "On s'est compris & Comme ça il enlève le poids de ce traumatisme de leurs épaules, littéralement ..."],
                (self.width - 1, self.height//2): ["Tu as finalement réussi à franchir tous ces obstacles.", "Tu y es ! La sortie est devant tes yeux !", "Ta détermination a payé.", "Mais à quel prix ................."]
            }
            yield (create_one_solution_map(self.width, self.height, 4), base_text)
        else:
            yield (self._load_map("assets/maps/demo"), self._load_text("assets/maps/demo"))
        yield (self._load_map("assets/maps/end"), self._load_text("assets/maps/end"))

    def _load_map(self, filename:str) -> Map:
        """Renvoie la Map à partir du fichier donné"""
        map = Map(0,0)
        map.load(filename)
        map.name = filename.split("/")[-1] if "/" in filename else filename
        return map

    def _load_text(self, filename:str) -> dict:
        """Renvoie le dictionnaire sous la forme {pos: ['text1']}"""
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        text = json.loads(content)["texts"]

        def decode_tuple(s) -> tuple:
            return tuple(int(el) for el in s.split(","))

        res = {}
        for key, value in text.items():
            res[decode_tuple(key)] = value
        return res

    def save(self, filename:str = "assets/saves/save1"):
        # Sauvegarder la map
        map_content = self.map.get_content()
        personnage_content = self.personnage.get_content()
        result = {
            "map": map_content,
            "player": personnage_content,
            "visited": list(self.visited)
        }

        with open(filename, "w") as f:
            json.dump(result, f, indent=4)

    def load(self, filename:str = "assets/saves/save1"):
        with open(filename, "r") as f:
            content = json.load(f)

        self.elements = self.get_maps()
        self.map, self.texts = next(self.elements)
        self.visited = set([tuple(pos_list) for pos_list in content["visited"]])
        map_name = content["map"].get("name", None)
        if map_name is None or map_name == "end" or map_name == "demo":
            self.map, self.texts = next(self.elements)
        if map_name == "end":
            self.map, self.texts = next(self.elements)
        self.map.load_matrice_format(content["map"]["grid"])
        self.personnage.load(content["player"])

    def _start_loaded_game(self):
        try:
            self.load()
        except Exception:
            print(f"{RED}Erreur lors du chargement de la map{RESET}")
            print(f"{GREEN}Création d'une nouvelle map ...{RESET}")
            self._start_new_game()
            return
        self.main()

    def _start_new_game(self):
        self.elements = self.get_maps()
        self.map, self.texts = next(self.elements)
        self.personnage.__init__('nom', PLAYER_BASE_PV, PLAYER_BASE_ATTACK, PLAYER_BASE_RESISTANCE, self.map.get_start_position(), game = self)
        self.main()

    def _start_demo_game(self):
        self.elements = self.get_maps(True)
        self.map, self.texts = next(self.elements)
        self.personnage.__init__('nom', PLAYER_BASE_PV, PLAYER_BASE_ATTACK, PLAYER_BASE_RESISTANCE, self.map.get_start_position(), game = self)
        self.main()

    def _quit_start_menu(self):
        self.start_running = False

class Combat:
    def __init__(self, joueur:Joueur, ennemi:Personnage, game: Game):
        self.joueur = joueur
        self.ennemi = ennemi
        self.tour = 0 # Pair quand c'est au tour du joueur
        self.buttons = None
        self.game = game
        self.winner = None

    def joueur_utiliser(self):
        """Fait utiliser le seul consommable de l'inventaire du joueur"""
        if self.tour % 2 == 0:
            try:
                objet = list(self.joueur.inventaire.consommables.values())[0]
                if not self.joueur.use(objet):
                    self.game.current_texts.append(TextDisplay("Cet objet a déjà été utilisé.", self.game.screen, self.game.clock))
                else:
                    self.game.current_texts.append(TextDisplay(f"Vous utilisez l'objet : {objet.get_message()}", self.game.screen, self.game.clock))
            except IndexError:
                self.game.current_texts.append(TextDisplay("Vous ne possédez pas de consommables ...", self.game.screen, self.game.clock))
        else:
            return
        self.tour += 1

    def joueur_attaque(self):
        """Attaque du joueur sur l'ennemi"""
        if self.tour % 2 == 0:
            att = self.joueur.attaque(self.ennemi)
            if att is None:
                self.game.current_texts.append(TextDisplay(f"Vous avez stressé et vous avez manqué votre attaque ...", self.game.screen, self.game.clock))
                add_random_dialogue(self.ennemi.nom, "miss_attack", self.game)
            else:
                self.game.current_texts.append(TextDisplay(f"Vous infligez {att:.1f} dégâts {NEW_LINE_CHARACTER} Il ne lui reste plus que {self.ennemi.pv:.1f} pv", self.game.screen, self.game.clock))
            if self.ennemi.pv > 0 and not att is None:
                add_random_dialogue(self.ennemi.nom, "receive_damage", self.game)
        else:
            return

        self.tour += 1

    def joueur_attaque_lourde(self):
        """Attaque lourde du joueur"""
        if self.tour % 2 == 0:
            att = self.joueur.attaque_lourde(self.ennemi)
            if att is None:
                self.game.current_texts.append(TextDisplay(f"Vous avez tout risqué mais vous êtes loupé ...", self.game.screen, self.game.clock))
                add_random_dialogue(self.ennemi.nom, "miss_attack", self.game)
            else:
                self.game.current_texts.append(TextDisplay(f"Vous infligez {att:.1f} dégâts {NEW_LINE_CHARACTER} Il ne lui reste plus que {self.ennemi.pv:.1f} pv", self.game.screen, self.game.clock))
            if self.ennemi.pv > 0 and not att is None:
                add_random_dialogue(self.ennemi.nom, "receive_damage", self.game)
        else:
            return

        self.tour += 1

    def is_ended(self) -> bool:
        """Renvoie si le combat est terminé et modifie self.winner par le vainqueur"""
        if self.winner != None:
            return True
        if not any([pers.pv <= 0 for pers in [self.ennemi, self.joueur]]):
            return False
        self.winner = self.joueur if self.ennemi.pv <= 0 else self.ennemi
        other = self.ennemi if self.ennemi.pv <= 0 else self.joueur

        if type(self.winner) is Joueur:
            self.winner.victoire(other)
            add_random_dialogue(self.ennemi.nom, "monster_death", self.game)
        else:
            self.game.current_texts.append(TextDisplay(f"Vous êtes morts ...", self.game.screen, self.game.clock))
            add_random_dialogue(self.ennemi.nom, "player_death", self.game)

        return True

    def ennemi_turn(self):
        """Tour de l'ennemi choisir action ennemi"""
        if self.tour % 2 == 0 or self.game.current_texts != []:
            return
        a = randint(1,10)

        if self.ennemi.pv <= self.ennemi.pv_base * 0.5: # Jouer ici
            if self.game.personnage.pv < self.ennemi.damage:
                deg = self.ennemi.attaque(self.joueur)
                self.game.current_texts.append(TextDisplay(f"Il vous inflige {deg:.1f} dégâts {NEW_LINE_CHARACTER} Il ne vous reste plus que {self.joueur.pv:.1f} pv", self.game.screen, self.game.clock))
            elif a <=3:
                obj = Objet("Potion de soin contenant du vice", "potion", soin=MONSTER_BASE_ITEM_SOIN)
                self.ennemi.use(obj)
                self.game.current_texts.append(TextDisplay(f"L'ennemi utilise l'objet : {NEW_LINE_CHARACTER} {obj.get_message()}", self.game.screen, self.game.clock))
            else:
                deg = self.ennemi.attaque(self.joueur)
                self.game.current_texts.append(TextDisplay(f"Il vous inflige {deg:.1f} dégâts {NEW_LINE_CHARACTER} Il ne vous reste plus que {self.joueur.pv:.1f} pv", self.game.screen, self.game.clock))

        elif self.ennemi.pv <= self.ennemi.pv_base * 0.25:
            if self.game.personnage.pv < self.ennemi.damage:
                deg = self.ennemi.attaque(self.joueur)
                self.game.current_texts.append(TextDisplay(f"Il vous inflige {deg:.1f} dégâts {NEW_LINE_CHARACTER} Il ne vous reste plus que {self.joueur.pv:.1f} pv", self.game.screen, self.game.clock))
            elif a <=5:
                obj = Objet("Potion de soin contenant du vice", "potion", soin=MONSTER_BASE_ITEM_SOIN)
                self.ennemi.use(obj)
                self.game.current_texts.append(TextDisplay(f"L'ennemi utilise l'objet : {NEW_LINE_CHARACTER} {obj.get_message()}", self.game.screen, self.game.clock))
            else:
                deg = self.ennemi.attaque(self.joueur)
                self.game.current_texts.append(TextDisplay(f"Il vous inflige {deg:.1f} dégâts {NEW_LINE_CHARACTER} Il ne vous reste plus que {self.joueur.pv:.1f} pv", self.game.screen, self.game.clock))

        else:
            deg = self.ennemi.attaque(self.joueur)
            self.game.current_texts.append(TextDisplay(f"Il vous inflige {deg:.1f} dégâts {NEW_LINE_CHARACTER} Il ne vous reste plus que {self.joueur.pv:.1f} pv", self.game.screen, self.game.clock))
        self.tour += 1

    def display_buttons(self, surface:pygame.Surface, space_percent:int = 20, button_bloc_pos:tuple = (0, 0)):
        """
        Initie les boutons de combat
        """
        surface.fill((0, 0, 0, 180))

        if self.game.current_texts != []:
            return

        if self.buttons is None:
            buttons = [("ATTAQUE", self.joueur_attaque), ("TOUT RISQUER", self.joueur_attaque_lourde), ("UTILISER", self.joueur_utiliser)]
            self.buttons = make_buttons(surface, buttons, space_percent, button_bloc_pos)

        if self.tour % 2 == 0:
            for button in self.buttons:
                button.display()

    def buttons_event(self, event):
        if self.game.current_texts != []:
            return
        if self.buttons is None or self.tour % 2 != 0:
            return

        for button in self.buttons:
            button.handle_event(event)

def get_level(game:Game) -> int:
    """
    Utilise le niveau du joueur et l'anvancée dans le jeu pour déterminer un niveau
    """
    avancee_level = game.personnage.position[0] / game.map.width * MAX_LEVEL
    return max(min(int((avancee_level + game.personnage.level)/2 + randint(-1, 1)), MAX_LEVEL), 0)

if __name__ == "__main__":
    g = Game()
    g.start_menu()