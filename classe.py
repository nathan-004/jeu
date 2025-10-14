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
        print("test")
        self.nom = nom
        self.pv = pv
        self.degats = degats
        self.resistance = resistance



class Monstre(Personnage):
    pass


class Objet:
    def __init__(self, nom,):
        self.nom = nom


class Inventaire:
    def __init__ (self, objet:Objet):
        self.objet = objet


class Arme(Objet):
    def __init__(self, nom):
        super().__init__(nom)
        self.degat = degat


class Potion(Objet):
    def __init__(self, nom, soin):
        super().__init__(nom)
        self.soin = soin


class Joueur(Personnage):
    def __init__(self, nom, pv, degats, resistance, position, inventaire:Inventaire):
        super().__init__(nom, pv, degats, resistance)
        self.position = (0, 0)
        self.inventaire = inventaire