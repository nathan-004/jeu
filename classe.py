from map import create_one_solution_map

class Objet:
    def __init__(self, nom, soin=0, degat=0, resistance=0):
        self.nom = nom
        self.soin = soin
        self.degat = degat
        self.resistance = resistance

class Inventaire:
    def __init__ (self):
        self.armure = None
        self.arme = None
        self.potion = None
        self.potion2 = None

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

    def use(self, obj:Objet):
        self.pv += obj.soin
        self.degat += obj.degat
        self.resistance += obj.resistance

    def degat_subit(self, degats):
        degat_restant = self.degat // self.resistance
        self.pv = self.pv - degat_restant

    def attaque(self, ennemi):
        ennemi.degat_subit(self.degat)


class Monstre(Personnage):
    pass

class Joueur(Personnage):
    def __init__(self, nom, pv, degats, resistance, position, inventaire:Inventaire = Inventaire() ):
        super().__init__(nom, pv, degats, resistance)
        self.position = position
        self.inventaire = inventaire

    def equipe_obj(self, obj:Objet):
        self.obj = obj
    
    def move(self, direction:tuple):
        self.position = (self.position[0] + direction[0], self.position[1] + direction[1])

class Game:
    def __init__(self):
        self.map = create_one_solution_map(15, 15, 2)
        self.personnage = Joueur(self,"Nom",50,50,1, (0, 15 // 2))

    def main(self):
        pass

    def move(self, direction:tuple):
        if self.map.can_move(self.personnage.position, direction):
            self.personnage.move(direction)