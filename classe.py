import pygame

from display import bloc_txt
from map import create_one_solution_map

class Objet:
    def __init__(self, nom, type_, soin=0, degat=0, resistance=0):
        self.nom = nom
        self.type = type_
        self.soin = soin
        self.degat = degat
        self.resistance = resistance

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

        # self.TEXTS = {
        #     (0, height//2): ["Test1", "Test2"],
        #     (width//2, height//2): ["Test3", "Test4"]
        # }

        self.visited = set()

    def main(self):
        # pygame.font.init()

        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.combat = False
        # clock = pygame.time.Clock()

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

            # if self.personnage.position in self.TEXTS and self.personnage.position not in self.visited:
            #     for text in self.TEXTS[self.personnage.position]:
            #         text_bloc = bloc_txt(text, screen, clock)
            #         text_bloc.annim_txt()
            
            self.visited.add(self.personnage.position)

            pygame.display.flip()

        pygame.quit()

    def move(self, direction:tuple):
        if self.map.can_move(self.personnage.position, direction):
            if not self.combat:
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
        if self.tour % 2 == 0: # Vérifier si c'est au tour du joueur sinon return
            self.joueur.use(objet) # Utiliser ici
        else:
            return
        self.tour += 1

    def joueur_attaque(self):
        """Attaque du joueur sur l'ennemi"""
        if self.tour % 2 == 0: # Vérifier si c'est au tour du joueur sinon return
            self.joueur.attaque() # Attaquer ici
        else:
            return
        self.tour += 1

    def ennemi_turn(self):
        """Tour de l'ennemi choisir action ennemi"""
        if self.tour % 2 != 0: # Vérifier que c'est bien le tour de l'ennemi
            if self.ennemi.pv <= 10: # Jouer ici
                self.ennemi.use(objet)
            else:
                self.ennemi.attaque()
        else:
            return
        self.tour += 1

if __name__ == "__main__":
    g = Game()
    g.main()
