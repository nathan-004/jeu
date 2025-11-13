import pygame

NEW_LINE_CHARACTER = "&"
MAX_LEVEL = 10
RED = "\033[31m"
RESET = "\033[0m"
GREEN = "\033[32m"
YELLOW = '\033[33m'
version = pygame.__version__
if int(version.split(".")[0]) >= 2:
    INPUT_LIST = [pygame.K_z, pygame.K_q]
else:
    INPUT_LIST = [pygame.K_w, pygame.K_a]

PLAYER_BASE_PV = 20
PLAYER_BASE_ATTACK = 5 # Dégâts émis
PLAYER_BASE_RESISTANCE = 0.050 # Dêgats réduits de 0% de l'attaque de base
PLAYER_LEVEL_AUGMENTATION_PV = 7
PLAYER_LEVEL_AUGMENTATION_ATTACK = 3
PLAYER_LEVEL_AUGMENTATION_RESISTANCE = 0.015
MAX_PLAYER_RESISTANCE = 0.40

MONSTER_BASE_PV = 20
MONSTER_BASE_PV_RANGE = 10 # Choix aléatoire avec distance maximale MONSTER_BASE_PV_RANGE/2
MONSTER_BASE_ATTACK = 5
MONSTER_BASE_ATTACK_RANGE = 4
MONSTER_BASE_RESISTANCE = 0.15
MONSTER_BASE_RESISTANCE_RANGE = 0.075
MONSTER_LEVEL_AUGMENTATION_PV = 7
MONSTER_LEVEL_AUGMENTATION_ATTACK = 3
MONSTER_LEVEL_AUGMENTATION_RESISTANCE = 0.025
MAX_MONSTER_RESISTANCE = 0.55

BASE_EXP_REWARD = 7
BASE_EXP_REWARD_RANGE = 8 # Choix aléatoire entre BASE_EXP_REWARD - BASE_EXP_REWARD/2 et BASE_EXP_REWARD + BASE_EXP_REWARD/2
EXP_REWARD_LEVEL_AUGMENTATION_COEFF = 1.05 # Exp = BASE_EXP_REWARD * (EXP_REWARD_LEVEL_AUGMNTATION_COEFF ** Level)

BASE_EXP_LEVEL_UP = 15 # Exp nécéssaire pour augmenter de niveau
BASE_EXP_LEVEL_UP_AUGMENTATION_COEFF = 1.3

# Items
PLAYER_BASE_ITEM_SOIN = 10
PLAYER_BASE_ITEM_DEGATS = 2
PLAYER_BASE_ITEM_RES = 0.05
PLAYER_ITEM_LEVEL_AUGMENTATION_SOIN = 5          # soin ajouté par niveau
PLAYER_ITEM_LEVEL_AUGMENTATION_DEGATS = 1        # dégats ajoutés par niveau
PLAYER_ITEM_LEVEL_AUGMENTATION_RES = 0.01        # résistance ajoutée par niveau (fraction)
MONSTER_BASE_ITEM_SOIN = 3

# Monstres
# Linoooooooooooooooo, quand tu fais les textes dans va_texts dans la liste de tuples, si tu mets juste ("test") qui ne contient qu'un élément, c'est juste une chaîne de caractères au lieu d'être un tuple. Il faut que tu fasses ("test",) pour que ce soit considéré comme un tuple
va_texts = [("Je le sens", "Pour toi aussi cette épreuve a été compliquée",), ("Je ne m'arrèterai jamais de combattre",), ("Ce labyrinthe m'a tout pris", "Mes hommes et mes souvenirs", "Mais on dirait que son pouvoir ne t'affecte pas",)]
va_generator = (el for el in va_texts)
MONSTERS = {
    "Chevalier" : {
        "image": "assets/images/monster/Perso_2.png",
        "dialogues": {
            "start": ["En garde guerrier", "... Essaye de me passer sur le corps !", "Tu n'iras pas plus loin !"],
            "receive_damage": ["Ouch !", "Pas mal pour un débutant ", "Tu ne penses quand même pas gagner aussi facilment ?"],
            "monster_death": ["Pourquoi ce sourire niarquois ?", "Tu te moque de moi?", "Cette douleur ... Il te la fera subir !"],
            "miss_attack": ["Concentre toi, je n'aimes pas quand c'est trop facile.", "Pathétique"],
            "player_death": ["Je te l'avais dit ...", "c'en est fini de toi", "C'était vraiment tout ce que tu pouvais faire ?"]
        }
    },
    "Mannequin d'entraînement": {
        "image": "assets/images/monster/Training_stand.png",
        "dialogues": {
            "start": [".............................", "................................ & (c'est un mannequin)"],
            "receive_damage": [".... & (il ne se passe rien).....", ".... & (pourquoi t'acharnes-tu??)....", ".... & (ça devient long)...."],
            "monster_death": ["... & (ce n'était pas très dur)", "..."],
            "miss_attack": ["... & (Je ne pensais pas ça possible)", "....?"],
            "player_death": ["... & (est-ce le monstre du labyrinthe?)"]
        }
    },
    "Ventre d'Acier" : {
        "image": "assets/images/monster/ventre_acier.png",
        "dialogues": {
            "start": ["Bravo gamin, tu a réussi a passer les épreuves de ce donjon", "Mais maintenant que tu les as tous tués", "JE VAIS LES VENGER"],
            "receive_damage": va_generator,
            "miss_attack": ["Je te croyait plus fort que ça", "Concentre toi, je ne veut pas que ce soit trop facile"],
            "monster_death": ["On dirait bien que j'ai perdu", "Tu t'es battu vaillament", "Tu peux être fière","...Chevalier & ...Je...Te...Félicite"],
            "player_death": ["On dirait bien que tu n'es pas assez fort gamin", "Ton carnage ne t'a donc rien apporté"]
        }
    },
}

MONSTERS_LIST = ["Chevalier"]

CREDITS_TEXT = [
    "Développeurs :",
    "Nathan",
    "Abel",
    "Hugo",
    "Lino",
    "Génération de la map :",
    "Nathan",
    "Barre de vie, Texte(enfin avec des fautes corrigé par Nathan et Abel) :",
    "Lino",
    "Dessin, Son et recherche de musique:",
    "Abel",
    "Items, Crédits :",
    "Hugo",
    "Merci d'avoir joué au jeu.",
    "","","","",
    "Ça vaut bien un 20/20 :)"
]
