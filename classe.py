import pygame

from map import create_one_solution_map

class Objet:
    def __init__(self, nom, type, soin=0, degat=0, resistance=0):
        self.nom = nom
        self.type = type
        self.soin = soin
        self.degat = degat
        self.resistance = resistance

class Inventaire:
    def __init__ (self):
        self.equipements = {} 
        self.consommables = {}

    def add(self, obj: Objet):
        if obj.type.lower() == "potion":
            self.consommables[obj.nom] = obj
        else:
            self.equipements[obj.nom] = obj
            
    def equip(self, perso):
        for objet in self.equipements.values():
            perso.use(objet)
            

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

        self.exp = 0
        self.level = 0

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
        # Ajouter différence de niveau en exp par exemple

        # Regarder si exp % 20 par exemple est plus grand que 0
        # Si c'est le cas appeler self.level_up et enlever exp // 20 à exp

    def level_up(self):
        """Prend les attributs du personnage de base et ajoute un nombre * level"""
        # Augmente self.level de 1
        # Modifie les attributs par attributs de base + 20 par exemple * self.level (Stocker les attributs de base dans __init__)
        # (Use tous les objets de l'inventaire non consommable)

class Monstre(Personnage):
    pass

class Joueur(Personnage):
    def __init__(self, nom, pv, degats, resistance, position:tuple, inventaire:Inventaire = Inventaire() ):
        super().__init__(nom, pv, degats, resistance)
        self.position = position
        self.inventaire = inventaire

    def equipe_obj(self, obj:Objet):
        self.obj = obj
    
    def move(self, direction:tuple):
        self.position = (self.position[0] + direction[0], self.position[1] + direction[1])

class Game:
    def __init__(self):
        height, width = 15, 15
        self.map = create_one_solution_map(height, width, 4)
        self.personnage = Joueur("Nom",50,50,1, (0, height // 2))

    def main(self):
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_RIGHT:
                        self.move((1, 0))
                    elif event.key == pygame.K_UP:
                        self.move((0, -1))
                    elif event.key == pygame.K_DOWN:
                        self.move((0, 1))
                    elif event.key == pygame.K_LEFT:
                        self.move((-1, 0))
            
            self.map.draw(surface=screen, player_pos = self.personnage.position)

            pygame.display.flip()

        pygame.quit()

    def move(self, direction:tuple):
        if self.map.can_move(self.personnage.position, direction):
            self.personnage.move(direction)

        cur_room = self.map.grid[self.personnage.position[1]][self.personnage.position[0]]
        if cur_room.type == "key":
            self.map.open()
            cur_room.type = "path"

if __name__ == "__main__":
    g = Game()
    g.main()
