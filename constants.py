NEW_LINE_CHARACTER = "&"
MAX_LEVEL = 10

PLAYER_BASE_PV = 10
PLAYER_BASE_ATTACK = 5 # Dégâts émis
PLAYER_BASE_RESISTANCE = 0 # Dêgats réduits de 0% de l'attaque de base
PLAYER_LEVEL_AUGMENTATION_PV = 7
PLAYER_LEVEL_AUGMENTATION_ATTACK = 3
PLAYER_LEVEL_AUGMENTATION_RESISTANCE = 0.015
MAX_PLAYER_RESISTANCE = 0.40

MONSTER_BASE_PV = 10
MONSTER_BASE_PV_RANGE = 10 # Choix aléatoire avec distance maximale MONSTER_BASE_PV_RANGE/2
MONSTER_BASE_ATTACK = 2
MONSTER_BASE_ATTACK_RANGE = 6
MONSTER_BASE_RESISTANCE = 0.15
MONSTER_BASE_RESISTANCE_RANGE = 0.1
MONSTER_LEVEL_AUGMENTATION_PV = 10
MONSTER_LEVEL_AUGMENTATION_ATTACK = 4
MONSTER_LEVEL_AUGMENTATION_RESISTANCE = 0.025
MAX_MONSTER_RESISTANCE = 0.55

BASE_EXP_REWARD = 10
BASE_EXP_REWARD_RANGE = 10 # Choix aléatoire entre BASE_EXP_REWARD - BASE_EXP_REWARD/2 et BASE_EXP_REWARD + BASE_EXP_REWARD/2
EXP_REWARD_LEVEL_AUGMENTATION_COEFF = 1.3 # Exp = BASE_EXP_REWARD * (EXP_REWARD_LEVEL_AUGMNTATION_COEFF ** Level)

BASE_EXP_LEVEL_UP = 15 # Exp nécéssaire pour augmenter de niveau
BASE_EXP_LEVEL_UP_AUGMENTATION_COEFF = 1.1

# Items
PLAYER_BASE_ITEM_SOIN = 3
PLAYER_BASE_ITEM_DEGATS = 3
PLAYER_BASE_ITEM_RES = 0.05
PLAYER_ITEM_LEVEL_AUGMENTATION_SOIN = 1          # soin ajouté par niveau
PLAYER_ITEM_LEVEL_AUGMENTATION_DEGATS = 1        # dégats ajoutés par niveau
PLAYER_ITEM_LEVEL_AUGMENTATION_RES = 0.01        # résistance ajoutée par niveau (fraction)
MONSTER_BASE_ITEM_SOIN = 3

# Monstres
va_texts = [("Tu es un humain comme moi", "Tu es passé par les mêmes épreuves"), ("Combattre sans arrêt", "Ca n'en finit jamais"), ("On en oublie qui on est", "Et notre objectif", "Mais tu sembles différent"), ("Je vois dans tes yeux l'espoir", "Ce qui nous est enlevé dans cet endroit")]
va_generator = (el for el in va_texts)
MONSTERS = {
    "Chevalier" : {
        "image": "assets/images/monster/Perso_2.png",
        "dialogues": {
            "start": ["Je ne pensais pas te revoir un jour", "... Essaye de passer derrière moi !", "Je vais pouvoir émousser ma lame", "Qui aurait cru que tu arriverais jusqu'à là"],
            "receive_damage": ["Ouch !", "Tu ne rigoles pas", "Tu ne penses quand même pas gagner ?", "Je ne tomberai pas si facilement"],
            "monster_death": ["Pourquoi ce sourire niarquois ?", "Si facilement ...", "Cette douleur ... Il te fera comprendre un jour ..."],
            "miss_attack": ["Concentre toi, je n'aimes pas quand c'est trop facile.", "Regarde où tu vises"],
            "player_death": ["Je te l'avais dit ...", "Ne reviens plus jamais !", "C'était vraiment très simple ..."]
        }
    },
    "Ventre d'Acier" : {
        "image": "assets/images/monster/ventre_acier.png",
        "dialogues": {
            "start": ["Je t'attendais", "Ca a du être dur tout seul ...", "dans le noir ...", "entouré par l'inconnu ...", "Mais ne t'inquiète pas", "Tout ira mieux", "lorsque JE TE TUERAIS"],
            "receive_damage": va_generator,
            "miss_attack": ["Test de miss", "test de miiss2"],
            "monster_death": ["Je l'ai vu en toi", "cette détermination à toute épreuve", "elle m'habitait moi aussi", "Et elle t'a permis de me battre", "Et j'ai voulu t'éliminer ..."],
            "player_death": ["Maintenant tu comprends", "Que l'espoir est vain", "Il est préférable de mourir.", "Peut être que moi aussi un jour je pourrais y accéder ..."]
        }
    },
}

MONSTERS_LIST = ["Chevalier"]