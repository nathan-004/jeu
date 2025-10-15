from typing import Optional
import pygame
import random

from utils import Stack
from classe import Objet

class Room:
    def __init__(self, type = "none"):
        self.type = type
        self.walls = {
            "left": True,
            "right": True,
            "top": True,
            "bottom": True,
        }
        self.items = []

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[Room() for x in range(width)] for y in range(height)]

    def random_map(self, start_pos:Optional[tuple] = None, end_pos:Optional[tuple] = None):
        if start_pos is None:
            start_pos = (0, self.height//2)
        if end_pos is None:
            end_pos = (self.width-1, self.height//2)

        self.grid = [[Room() for x in range(self.width)] for y in range(self.height)]
        self.grid[start_pos[1]][start_pos[0]].type = "start"
        self.grid[end_pos[1]][end_pos[0]].type = "end"

        self.random_path(start_pos, end_pos)
        self.create_maze(start_pos)
        self.create_locked_rooms()

    def random_path(self, start_pos:tuple, end_pos:tuple):
        diff_x, diff_y = end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]
        variations = [0 for _ in range(diff_x // 3 - 1)] + [1 for _ in range(diff_x // 3)] + [-1 for _ in range(diff_x // 3)]
        random.shuffle(variations)
        variations += [0]

        cur_y = start_pos[1]
        for x, y_variation in zip(range(start_pos[0] + 1, end_pos[0]), variations):
            cell_base = self.grid[cur_y][x]
            cell_base.type = "path_original"
            cell_base.walls["left"] = False

            if y_variation == 0:
                continue

            cur_y += y_variation
            var_cell = self.grid[cur_y][x]
            var_cell.type = "path_original"
            var_cell.walls["bottom" if y_variation == -1 else "top"] = False
            cell_base.walls["top" if y_variation == -1 else "bottom"] = False
        
        self.grid[end_pos[1]][end_pos[0]].walls["left"] = False

    def create_maze(self, start_pos:tuple):
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
        
    def create_locked_rooms(self, n:int = 4):
        for idx in range(1, n + 1):
            for row in self.grid:
                row[idx * (self.width // (n+1))].type = "locked"

        # Ajouter clés
        for idx in range(1, n+1):
            sigma = (self.height // 2) // 4 # Plus petit -> moins de dispersion
            diff_y = int(random.normalvariate(self.height // 4, sigma))
            diff_y = min(max(2, diff_y), self.height // 2)
            diff_y *= random.choice([-1, 1])
            self.grid[self.height//2 + diff_y][idx * (self.width // (n+1)) - random.randint(1, self.width // (n+1) - 1) ].type = 'key'

    def _is_complete(self):
        return all([cell.type != "none" for row in self.grid for cell in row])

    def _random_path_cell(self, visited:Optional[set] = set()):
        valid_cells = []
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell.type != "none" and (x,y) not in visited:
                    valid_cells.append((x, y))
        return random.choice(valid_cells)

    def draw(self):
        cell_size = 30
        screen = pygame.display.set_mode((cell_size * self.width, cell_size * self.height))
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            for y in range(self.height):
                for x in range(self.width):
                    self.draw_cell(x, y, cell_size, screen)
            pygame.display.flip()
        pygame.quit()

    def draw_cell(self, x, y, cell_size, surface):
        room = self.grid[y][x]
        room_type = room.type

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
        elif room_type == "locked":
            color = (125, 125, 0)
        elif room_type == "key":
            color = (165, 42, 42)
        else:
            color = (128, 128, 128)

        px = x * cell_size
        py = y * cell_size

        pygame.draw.rect(surface, color, (px, py, cell_size, cell_size))

        wall_thickness = 2
        wall_color = (255, 255, 255)

        if room.walls["top"]:
            pygame.draw.line(surface, wall_color, (px, py), (px + cell_size, py), wall_thickness)
        if room.walls["bottom"]:
            pygame.draw.line(surface, wall_color, (px, py + cell_size), (px + cell_size, py + cell_size), wall_thickness)
        if room.walls["left"]:
            pygame.draw.line(surface, wall_color, (px, py), (px, py + cell_size), wall_thickness)
        if room.walls["right"]:
            pygame.draw.line(surface, wall_color, (px + cell_size, py), (px + cell_size, py + cell_size), wall_thickness)

if __name__ == "__main__":
    a = Map(25, 25)
    a.random_map()
    a.draw()