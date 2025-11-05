from typing import Optional, Union
import pygame
import random
from copy import deepcopy
import json
from collections import deque

from display import ChestDisplay

class Stack(deque):
    def empty(self):
        return len(self) == 0
    
    def empiler(self, el):
        super().append(el)
    
    def depiler(self):
        return super().popleft()

class Room:
    DIRECTIONS = {
        (0, -1): "top",
        (0, 1): "bottom",
        (1, 0): "right",
        (-1, 0): "left"
    }
    INVERTED_DIRECTION = {str_dir: tuple_dir for tuple_dir, str_dir in DIRECTIONS.items()}

    def __init__(self, type = "none"):
        self.type = type
        self.walls = {
            "left": True,
            "right": True,
            "top": True,
            "bottom": True,
        }
        self.locked = False
        self.chest = False
        self.monster = False

    def get_content(self) -> dict:
        """Renvoie un dictionnaire contenant les informations de la salle"""
        return {
            "type": self.type,
            "walls": self.walls,
            "chest": self.chest.closed if type(self.chest) is ChestDisplay else self.chest,
            "monster": self.monster,
            "locked": self.locked
        }

    def load_content(self, content:dict):
        """Modifie Room pour avoir les mêmes attributs que `content` -> même format que self.get_content"""
        for attr, value in content.items():
            setattr(self, attr, value)

class Map:
    """Objet représentant la carte sous forme de matrice de Salles"""

    def __init__(self, width:int, height:int):
        """Initie la matrice de salle totalement vide"""
        self.width = width
        self.height = height
        self.grid = [[Room() for x in range(width)] for y in range(height)]
        self.name = None

    # --------------------------------------------------------------------------------------------
    # Génération aléatoire du labyrinthe --------------------------------------------------------|
    # --------------------------------------------------------------------------------------------

    def random_map(self, start_pos:Optional[tuple] = None, end_pos:Optional[tuple] = None):
        """
        Modifie `grid` pour générer le labyrinthe, les portes verrouillées et les clés

        Warnings
        --------
        Faire en sorte que l'on puisse passer au travers d'une salle verrouillée mais pas passer la porte

        Parameters
        ----------
        start_pos:tuple
            Position (x, y) de la salle de départ par défaut (0, self.height // 2)
        end_pos:tuple
            Position (x, y) de la salle de fin par défaut (self.width, self.height // 2)
        """
        if start_pos is None:
            start_pos = (0, self.height//2)
        if end_pos is None:
            end_pos = (self.width-1, self.height//2)

        self.grid = [[Room() for x in range(self.width)] for y in range(self.height)]
        self.grid[end_pos[1]][end_pos[0]].locked = "right"
        self.grid[end_pos[1]][end_pos[0]].walls["right"] = False
        self.grid[start_pos[1]][start_pos[0]].walls["left"] = False

        self.random_path(start_pos, end_pos)
        self.create_maze(start_pos)
        self.create_chest()

    def random_path(self, start_pos:tuple, end_pos:tuple):
        """
        Modifie `grid` pour créer un chemin aléatoire de la salle de départ vers la salle de fin

        Notes
        -----
        Conserve une direction globale vers la droite
        """
        diff_x, diff_y = end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]
        variations = [0 for _ in range(diff_x // 3 - 1)] + [1 for _ in range(diff_x // 3)] + [-1 for _ in range(diff_x // 3)]
        random.shuffle(variations)
        variations += [0]
        self.grid[start_pos[1]][start_pos[0]].walls["right"] = False

        cur_y = start_pos[1]
        for x, y_variation in zip(range(start_pos[0]+1, end_pos[0]), variations):
            cell_base = self.grid[cur_y][x]
            cell_base.type = "path"
            cell_base.walls["left"] = False

            if y_variation == 0:
                cell_base.walls["right"] = False
                continue

            cur_y += y_variation
            var_cell = self.grid[cur_y][x]
            var_cell.type = "path"
            var_cell.walls["bottom" if y_variation == -1 else "top"] = False
            cell_base.walls["top" if y_variation == -1 else "bottom"] = False
            var_cell.walls["right"] = False

        self.grid[end_pos[1]][end_pos[0]].walls["left"] = False

    def create_maze(self, start_pos:tuple):
        """
        Créé le labyrinthe autour du chemin principale (`random_path`)

        Algorithme :
        1. Initier une Pile des cellules à observer
        2. Tant que toutes les cellules n'ont pas été visitées
        3.     Prendre la dernière cellule de la Pile ou une cellule active aléatoire
        4.     Sélectionner une direction aléatoire puis ajouter à la Pile si visitable
        """
        visited = set()
        stack = Stack([start_pos])

        while not self._is_complete():
            if stack.empty():
                stack.empiler(self._random_path_cell())
            current_pos = stack.depiler()
            x, y = current_pos
            visited.add(current_pos)
            current_cell = self.grid[y][x]
            if current_cell.type == "none":
                current_cell.type = "path"

            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            random.shuffle(directions)

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and (nx, ny) not in visited:
                    if dx == 1:
                        self.grid[y][x].walls["right"] = False
                        self.grid[ny][nx].walls["left"] = False
                    elif dx == -1:
                        self.grid[y][x].walls["left"] = False
                        self.grid[ny][nx].walls["right"] = False
                    elif dy == 1:
                        self.grid[y][x].walls["bottom"] = False
                        self.grid[ny][nx].walls["top"] = False
                    elif dy == -1:
                        self.grid[y][x].walls["top"] = False
                        self.grid[ny][nx].walls["bottom"] = False

                    stack.empiler((nx, ny))
                    break
        
    def generate_keys(self, n:int = 1):
        """
        Place les clés dans les salles pour pouvoir dévérouiller les portes
        """
        for idx in range(1, n+1):
            sigma = (self.height // 2) // 4 # Plus petit -> moins de dispersion
            diff_y = int(random.normalvariate(self.height // 4, sigma))
            diff_y = min(max(2, diff_y), self.height // 2)
            diff_y *= random.choice([-1, 1])
            self.grid[self.height//2 + diff_y][idx * (self.width // (n)) - random.randint(1, self.width // n) ].type = 'key'

    def create_chest(self, p:float = 0.1):
        """
        Crée plusieurs coffres en respectant le rapport p/1
        """
        n = int(p * self.width * self.height)
        for _ in range(n):
            x = int(random.uniform(0, self.width)) # Avoir la même chance de tomber au début ou à la fin
            sigma = (self.height // 2) // 2 # Plus petit -> moins de dispersion
            diff_y = int(random.normalvariate(self.height // 4, sigma)) # Plus de chances de tomber à 1/4 de distance du centre
            diff_y = min(max(2, diff_y), self.height // 2)
            diff_y *= random.choice([-1, 1])
            self.grid[self.height // 2 + diff_y][x].chest = True

    def _is_complete(self):
        """Retourne `True` si toutes les cellules de la Grille ont été initiées"""
        return all([cell.type != "none" for row in self.grid for cell in row])

    def _random_path_cell(self, visited:Optional[set] = set()):
        """Renvoie une cellule aléatoire parmi les cellules qui sont <actives> (!= none)"""
        valid_cells = []
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell.type != "none" and (x,y) not in visited:
                    valid_cells.append((x, y))
        return random.choice(valid_cells)
    
    def generate_monsters(self, prob:float, center:float = 0.5):
        """
        Créé prob * total de monstres aléatoirement dans la map

        Parameters
        ----------
        prob:float
            Fraction des salles devant contenir un monstre sur le total
        center:float
            Pic de la distribution normale sur la hauteur
        """
        n = int(prob * self.width * self.height)
        for _ in range(n):
            x = int(random.uniform(0, self.width))
            sigma = (self.height // 2) // 2
            diff_y = int(random.normalvariate(self.height * center, sigma))
            diff_y = min(max(0, diff_y), self.height // 2)
            diff_y *= random.choice([-1, 1])
            self.grid[self.height // 2 + diff_y][x].monster = True

    # --------------------------------------------------------------------------------------------
    # Utilitaires -------------------------------------------------------------------------------|
    # --------------------------------------------------------------------------------------------

    def can_move(self, initial_pos:tuple, direction:Union[tuple, str]):
        """
        Renvoie True si le joueur peut se déplacer de la position initial à la position + direction
        
        Parameters
        ----------
        initial_pos:tuple
            Position (x,y) du joueur
        direction:tuple ou string
            Direction (x,y)
            Si string, transformé en tuple (x,y)
        """
        if type(direction) is str:
            direction = Room.INVERTED_DIRECTION[direction]

        if direction not in Room.DIRECTIONS:
            return False
        if not (0 <= initial_pos[0] + direction[0] < self.width and 0 <= initial_pos[1] + direction[1] < self.height):
            return False

        initial_cell = self.grid[initial_pos[1]][initial_pos[0]]
        if initial_cell.locked:
            if Room.DIRECTIONS[direction] == initial_cell.locked:
                return False
        if not initial_cell.walls[Room.DIRECTIONS[direction]]:
            return True
        
        return False
    
    def open(self):
        """Ouvre la prochaine porte verrouillée à height // 2"""
        for x in range(self.width):
            cell = self.grid[self.height // 2][x]
            if cell.locked:
                cell.locked = False
                break

    def get_start_position(self) -> tuple:
        for y, row in enumerate(self.grid):
            for x, room in enumerate(row):
                if room.type == "start":
                    return (x, y)

    # --------------------------------------------------------------------------------------------
    # Affichage de débogage du labyrinthe -------------------------------------------------------|
    # --------------------------------------------------------------------------------------------

    def draw(self, surface:pygame.Surface, player = None):
        """
        Affichage de la map pour le débogage sur la Surface donnée
        player:Joueur
            Contient la position et la direction du personnage
        """
        w, h = surface.get_size()
        cell_size_x, cell_size_y = w // self.width, h // self.height

        self.key_img = pygame.image.load("assets/images/key.png").convert_alpha()
        self.key_img = pygame.transform.smoothscale(self.key_img, (cell_size_x, cell_size_y))

        self.chest_image = pygame.image.load("assets/images/chest/chest1.png").convert_alpha()
        self.chest_image = pygame.transform.scale(self.chest_image, (cell_size_x, cell_size_y))

        for y in range(self.height):
            for x in range(self.width): 
                self.draw_cell(x, y, (cell_size_x, cell_size_y), surface)
                if (x, y) == player.position:
                    px = x * cell_size_x + cell_size_x // 2
                    py = y * cell_size_y + cell_size_y // 2
                    dir_x, dir_y = player.direction
                    end_pos = (px + dir_x * cell_size_x // 3, py + dir_y * cell_size_y // 3)
                    pygame.draw.circle(surface, (0, 0, 255), (px, py), cell_size_x // 4)
                    pygame.draw.line(surface, (0, 0, 255), (px, py), end_pos, 2)

    def draw_cell(self, x, y, cell_size:Union[int, tuple], surface, forced_color:tuple=None):
        """Affiche la salle correspondante | Composant de `draw`"""
        if type(cell_size) is int:
            cell_size_x, cell_size_y = cell_size, cell_size
        else:
            cell_size_x, cell_size_y = cell_size
        room = self.grid[y][x]
        room_type = room.type
        color = (0, 0, 0)

        if room_type == "none":
            return
        elif room_type == "start":
            color = (0, 255, 0)
        elif room_type == "end":
            color = (255, 0, 0)
        elif room_type == "path":
            color = (0, 0, 0)
        elif room_type == "path_original":
            color = (0, 125, 125)
        elif room_type == "player":
            color = (0, 0, 255)

        if room.monster:
            cx, cy = self.width, self.height / 2
            dist = ((x)**2 + (y - cy)**2)**0.5
            max_dist = ((cx)**2 + (cy)**2)**0.5
            intensity = int(dist * 255 / max_dist)
            color = (intensity, 0, 0)

        if room.locked:
            color = (125, 125, 0)

        px = x * cell_size_x
        py = y * cell_size_y

        pygame.draw.rect(surface, color, (px, py, cell_size_x, cell_size_y))

        if room_type == "key":
            surface.blit(self.key_img, (px, py))
        if room.chest:
            if not type(room.chest) is ChestDisplay:
                room.chest = ChestDisplay(surface, (px, py), (cell_size_x, cell_size_y))
            room.chest.display(surface, (px, py), (cell_size_x, cell_size_y))

        wall_thickness = 2
        wall_color = (255, 255, 255)

        if room.walls["top"]:
            pygame.draw.line(surface, wall_color, (px, py), (px + cell_size_x, py), wall_thickness)
        if room.walls["bottom"]:
            pygame.draw.line(surface, wall_color, (px, py + cell_size_y), (px + cell_size_x, py + cell_size_y), wall_thickness)
        if room.walls["left"]:
            pygame.draw.line(surface, wall_color, (px, py), (px, py + cell_size_y), wall_thickness)
        if room.walls["right"]:
            pygame.draw.line(surface, wall_color, (px + cell_size_x, py), (px + cell_size_x, py + cell_size_y), wall_thickness)

    def create_image(self, filename: str = "map.png", cell_size: int = 30):
        """
        Crée une image PNG de la map sans ouvrir de fenêtre.

        Parameters
        ----------
        filename:str
            chemin de sortie
        cell_size: int
            taille en pixels d'une cellule
        """
        pygame.init()
        width_px = cell_size * self.width
        height_px = cell_size * self.height
        surface = pygame.Surface((width_px, height_px), pygame.SRCALPHA)

        self.key_img = pygame.image.load("assets/images/key.png")
        self.chest_image = pygame.image.load("assets/images/chest/chest1.png")
        self.chest_image = pygame.transform.scale(self.chest_image, (cell_size, cell_size))

        for y in range(self.height):
            for x in range(self.width):
                self.draw_cell(x, y, cell_size, surface)

        try:
            pygame.image.save(surface, filename)
        except Exception as e:
            pygame.quit()
            print(e)
            raise

        pygame.quit()

    # --------------------------------------------------------------------------------------------
    # Fonction spéciales de la map --------------------------------------------------------------|
    # --------------------------------------------------------------------------------------------

    def __add__(self, other):
        if isinstance(other, Map):
            result = Map(self.width + other.width, other.height)
            if self.grid == []:
                result.grid = deepcopy(other.grid)
                return result
            for idx, (cur_row, other_row) in enumerate(zip(self.grid, other.grid)):
                result.grid[idx] = cur_row + other_row

            return result
        else:
            raise NotImplementedError
    
    # --------------------------------------------------------------------------------------------
    # Export + Import d'objet Map ---------------------------------------------------------------|
    # --------------------------------------------------------------------------------------------

    def load(self, filename:str):
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        grid = json.loads(content)["grid"]

        if type(grid) is dict:
            self.load_dict_format(grid)
        elif type(grid) is list:
            self.load_matrice_format(grid)
        else:
            raise NotImplementedError
        self.name = filename.split("/")[-1] if "/" in filename else filename

    def get_content(self) -> dict:
        """
        Renvoie le contenu de la map sous forme de dictionnaire

        Renvoie
        -------
        {
            "grid": [
            ],
        }
        """
        content = {
            "grid": [[room.get_content() for room in row] for row in self.grid],
            "name": self.name
        }

        return content
    
    def load_dict_format(self, grid):
        """
        Crée une nouvelle map à partir d'un dictionnaire de salles

        Formats
        -------
        grid:dict -> {
            '0,0': Room.get_content(),
            ...
            "size": 'width,height'
        }
        """
        self.width, self.height = self._decode_tuple(grid["size"])
        self.grid = []
        for y in range(self.height):
            self.grid.append([])
            for _ in range(self.width):
                empty_room = Room()
                empty_room.chest, empty_room.monster = False, False
                self.grid[y].append(empty_room)
        del grid["size"]

        for room_pos, room_info in grid.items():
            room_pos = self._decode_tuple(room_pos)
            cur_room = self.grid[room_pos[1]][room_pos[0]]
            
            for attr, value in room_info.items():
                if type(value) is bool or type(value) is str:
                    setattr(cur_room, attr, value)
                elif type(value) is dict:
                    if len(value) == 4:
                        cur_room.walls = value
                    else:
                        for dir, val in value.items():
                            cur_room.walls[dir] = val
                else:
                    raise NotImplementedError(f"{type(value)} n'est pas implémenté.")
            
            if cur_room.type == "none":
                cur_room.type = "path"

    def load_matrice_format(self, grid:list):
        """
        Modifie Map pour correspondre au fichier
        Format d'export de map (self.get_content)

        Format
        ------
        [[Room.get_content, Room.get_content], [Room.get_content, Room.get_content]],
        """
        self.width, self.height = len(grid[0]), len(grid)
        self.grid = []

        for y, row in enumerate(grid):
            self.grid.append([])
            for room_content in row:
                cur_room = Room()
                cur_room.load_content(room_content)
                self.grid[y].append(cur_room)

    def _decode_tuple(self, s:str) -> tuple:
        els = s.split(",")
        return tuple(int(el) for el in els)

def create_one_solution_map(width, height, n = 3) -> Map:
    """
    Créé `n` instance de Map pour garantir qu'il n'y a qu'une solution possible au labyrinthe
    !!Ne pas mettre une width trop petite pour un `n` trop grand!!
    !!Peut diminuer la taille longueur si n ne divise pas width!! 

    Returns
    -------
    Assemblage des `n` instances de Map
    """
    w = width // n
    result = Map(0,0)
    max_prob = 0.5
    min_center_distance, max_center_distance = 0, 0.3
    var = (max_center_distance - min_center_distance) / n
    centers = [max_center_distance - i * var for i in range(n)]

    for idx in range(n):
        part_map = Map(w, height)
        part_map.random_map()
        part_map.generate_monsters(0.3 + idx * (max_prob / n), centers[idx])
        result += part_map

    result.grid[result.height // 2][0].type = "start"
    result.grid[result.height // 2][0].walls["right"] = False
    result.grid[result.height // 2][width - 1].type = "end"
    result.generate_keys(n)
    
    return result

def get_absolute_direction(initial_direction: tuple, relative_direction: tuple):
    """
    Renvoie la direction absolue (dans la map) à partir de la direction initiale
    et de la direction relative à l'initiale.

    Paramètres
    ----------
    initial_direction : tuple[int, int]
    relative_direction : tuple[int, int]
        direction relative à l'orientation initiale

    Retourne
    --------
    tuple[int, int]
        La direction absolue dans la map
    """
    rotations = {
        (0, -1): lambda x, y: (x, y),
        (1, 0): lambda x, y: (-y, x), # rotation 90° horaire
        (0, 1): lambda x, y: (-x, -y), # rotation 180°
        (-1, 0): lambda x, y: (y, -x), # rotation 90° antihoraire
    }

    assert initial_direction in rotations, "Direction initiale non valide" + str(initial_direction) 

    return rotations[initial_direction](*relative_direction)

if __name__ == "__main__":
    a = Map(0, 0)
    a.load("assets/maps/demo")
    a.create_image()