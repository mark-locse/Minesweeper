import random
import pygame
from enum import Enum, auto

class GameState(Enum):
    READY = auto()
    RUNNING = auto()
    WON = auto()
    LOST = auto()
    
class Game:
    def __init__(self, difficulty):
        match difficulty:
            case "beginner":
                self.grid = Grid(9,9,10)
            case "intermediate":
                self.grid = Grid(16,16,40)
            case "expert":
                self.grid = Grid(30,16,99)
            case "impossible":
                self.grid = Grid(30,30,450)
        self.state = GameState.READY

class Grid:
    def __init__(self, width, height, mines):
        #basic variables
        self.width = width
        self.height = height
        self.mines = mines
        self.cells = [[Cell() for i in range(width)] for i in range(height)]

        #counters and checks
        self.total_cells = width*height
        self.non_mine_cells = self.total_cells - self.mines
        self.revealed_safe_cells = 0
        self.first_click = True

    def reset_grid(self):
        self.revealed_safe_cells = 0
        self.first_click = True
        for row in self.cells:
            for cell in row:
                cell.is_mine = False
                cell.revealed = False
                cell.flagged = False
                cell.adjacent = 0
    
    def mine_placement(self, forbidden):
        positions = [
            (x,y)
            for y in range(self.height)
            for x in range(self.width)
            if (x,y) not in forbidden
            ]
        mine_positions = random.sample(positions, self.mines)
        for x,y in mine_positions:
            self.cells[y][x].is_mine = True

    def neighbours(self, x, y):
        for difference_y in (-1,0,1):
            for difference_x in (-1,0,1):
                neighbour_x = x + difference_x
                neighbour_y = y + difference_y
                if difference_x == 0 and difference_y == 0:
                    continue
                if 0 <= neighbour_x < self.width and 0 <= neighbour_y < self.height:
                    yield neighbour_x, neighbour_y

    def adjacency_calculator(self):
        #Go through every cell
        for y in range(self.height):
            for x in range(self.width):
                cell = self.cells[y][x]
                if cell.is_mine:
                    continue
                
                #Go through every neighbour of each cell
                count = 0
                for neighbour_x, neighbour_y in self.neighbours(x,y):
                    if self.cells[neighbour_y][neighbour_x].is_mine:
                        count += 1
                cell.adjacent = count

    def reveal(self, x,y):
        #Validation Checks
    
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        
        if self.first_click:
            while True:
                self.reset_grid()
                self.mine_placement(forbidden = {
                    (x + difference_x, y + difference_y)
                    for difference_x in (-1, 0, 1)
                    for difference_y in (-1, 0, 1)
                    if 0 <= x + difference_x < self.width and 0 <= y + difference_y < self.height
                    })
                self.adjacency_calculator()
                if self.cells[y][x].adjacent == 0:
                    break
            self.first_click = False
        
        cell = self.cells[y][x]
        if cell.revealed or cell.flagged:
            return
        
        cell.revealed = True
        if cell.is_mine:
            return "Lost"

        self.revealed_safe_cells += 1
        if self.revealed_safe_cells == self.non_mine_cells:
            return "Won"
        
        #Flood-Fill Algorithm
        if cell.adjacent == 0:
            for neighbour_x, neighbour_y in self.neighbours(x,y):
                self.reveal(neighbour_x,neighbour_y)

    def toggle_flag(self, x, y):
        #Validation Checks

        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        
        cell = self.cells[y][x]
        if cell.revealed:
            return

        cell.flagged = not cell.flagged

    def chord(self, x, y):
        cell = self.cells[y][x]
        won = False

        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        
        if not cell.revealed:
            return
        if cell.adjacent == 0:
            return

        flags = 0
        for neighbour_x, neighbour_y in self.neighbours(x,y):
            if self.cells[neighbour_y][neighbour_x].flagged:
                flags += 1

        if flags != cell.adjacent:
                return
            
        for neighbour_x, neighbour_y in self.neighbours(x,y):
            neighbour = self.cells[neighbour_y][neighbour_x]

            if neighbour.flagged or neighbour.revealed:
                continue

            result = self.reveal(neighbour_x, neighbour_y)
            if result == "Lost":
                return result

        if self.revealed_safe_cells == self.non_mine_cells:
            return "Won"
        
class Cell:
    def __init__ (self):
        self.is_mine = False
        self.revealed = False
        self.flagged = False
        self.adjacent = 0
