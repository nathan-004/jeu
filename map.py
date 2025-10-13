from typing import Optional
import pygame

class Room:
    def __init__(self, type = "none"):
        self.type = type

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[Room() for x in range(width)] for y in range(height)]

    def random_map(self, start_pos:Optional[tuple[int, int]] = None, end_pos:Optional[tuple[int, int]] = None):
        if start_pos is None:
            start_pos = (0, self.height//2)
        if end_pos is None:
            end_pos = (self.width-1, self.height//2)

        self.grid = [[Room() for x in range(self.width)] for y in range(self.height)]
        self.grid[start_pos[1]][start_pos[0]].type = "start"
        self.grid[end_pos[1]][end_pos[0]].type = "end"

    def draw(self):
        cell_size = 15
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
        room_type = self.grid[y][x].type
        rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
        if room_type == "none":
            color = (0, 0, 0)
        elif room_type == "start":
            color = (0, 255, 0)
        elif room_type == "end":
            color = (255, 0, 0)
        else:
            color = (128, 128, 128)
        pygame.draw.rect(surface, color, rect)
    

a = Map(50, 50)
a.random_map()
a.draw()