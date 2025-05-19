import pygame
import random
from gameconfig import *

# --- Maze Generation (Recursive Backtracker) ---
def generate_maze_grid(rows, cols):
    grid = [[{'walls': [True, True, True, True], 'visited': False} for _ in range(cols)] for _ in range(rows)]

    def get_neighbors(r, c):
        """Gets unvisited neighbors of a cell."""
        # directions: (dr, dc, wall_to_break_current, wall_to_break_neighbor)
        directions = [(-1, 0, 0, 2), (0, 1, 1, 3), (1, 0, 2, 0), (0, -1, 3, 1)]
        neighbors = []
        for dr, dc, w1, w2 in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not grid[nr][nc]['visited']:
                neighbors.append((nr, nc, w1, w2))
        return neighbors

    def remove_walls(r, c, nr, nc, w1, w2):
        """Removes the wall between two adjacent cells."""
        grid[r][c]['walls'][w1] = False
        grid[nr][nc]['walls'][w2] = False

    stack = []
    # Start from a random cell
    sr, sc = random.randint(0, rows - 1), random.randint(0, cols - 1)
    grid[sr][sc]['visited'] = True
    stack.append((sr, sc))

    while stack:
        r, c = stack[-1]
        neighbors = get_neighbors(r, c)
        if neighbors:
            # Choose a random unvisited neighbor
            nr, nc, w1, w2 = random.choice(neighbors)
            grid[nr][nc]['visited'] = True
            remove_walls(r, c, nr, nc, w1, w2)
            stack.append((nr, nc))
        else:
            # Backtrack if no unvisited neighbors
            stack.pop()

    return grid


# --- Wall Rectangles for Drawing ---
def create_maze_wall_rects(grid):
    walls = []
    rows, cols = len(grid), len(grid[0])
    offset_y = GAMEBAR_HEIGHT
    half_thickness = WALL_THICKNESS // 2

    # Draw internal walls
    for r in range(rows):
        for c in range(cols):
            cell = grid[r][c]

            # Right wall of cell (r, c)
            # Draw if the wall exists in the current cell's definition
            if cell['walls'][1]:
                # Calculate position centered on the boundary between cells
                x = (c + 1) * CELL_SIZE - half_thickness
                y = r * CELL_SIZE + offset_y - half_thickness
                # Extend the wall vertically by half_thickness at top and bottom
                walls.append(pygame.Rect(x, y, WALL_THICKNESS, CELL_SIZE + WALL_THICKNESS))

            # Bottom wall of cell (r, c)
            # Draw if the wall exists in the current cell's definition
            if cell['walls'][2]:
                # Calculate position centered on the boundary between cells
                x = c * CELL_SIZE - half_thickness
                y = (r + 1) * CELL_SIZE + offset_y - half_thickness
                # Extend the wall horizontally by half_thickness at left and right
                walls.append(pygame.Rect(x, y, CELL_SIZE + WALL_THICKNESS, WALL_THICKNESS))

    # Draw outer walls to ensure a complete border
    # Top outer wall
    walls.append(
        pygame.Rect(0 - half_thickness, offset_y - half_thickness, cols * CELL_SIZE + WALL_THICKNESS, WALL_THICKNESS))
    # Bottom outer wall
    walls.append(
        pygame.Rect(0 - half_thickness, rows * CELL_SIZE + offset_y - half_thickness, cols * CELL_SIZE + WALL_THICKNESS,
                    WALL_THICKNESS))
    # Left outer wall
    walls.append(
        pygame.Rect(0 - half_thickness, offset_y - half_thickness, WALL_THICKNESS, rows * CELL_SIZE + WALL_THICKNESS))
    # Right outer wall
    walls.append(pygame.Rect(cols * CELL_SIZE - half_thickness, offset_y - half_thickness, WALL_THICKNESS,
                             rows * CELL_SIZE + WALL_THICKNESS))

    return walls


# --- Yardımcılar ---
def get_cell_center(row, col):
    """Calculates the center coordinates of a cell."""
    x = (col * CELL_SIZE) + (CELL_SIZE // 2)
    y = ((row * CELL_SIZE) + CELL_SIZE // 2) + GAMEBAR_HEIGHT
    return x, y


def find_start_positions(grid, count=2):
    """Finds random starting positions for players."""
    rows, cols = len(grid), len(grid[0])
    cells = [(r, c) for r in range(rows) for c in range(cols)]
    # Ensure enough cells are available for the requested count
    if count > len(cells):
        count = len(cells)  # Or raise an error
    chosen = random.sample(cells, count)
    return [get_cell_center(r, c) for r, c in chosen]


def is_dead_end(cell):
    """Sadece bir yönü açık olan hücre çıkmaz sokaktır."""
    return cell['walls'].count(False) == 1


def find_dead_end_cells(grid):
    """Harita üzerindeki tüm çıkmaz sokakları bulur ve [(row, col)] listesi döner."""
    dead_ends = []
    rows = len(grid)
    cols = len(grid[0])

    for r in range(rows):
        for c in range(cols):
            if is_dead_end(grid[r][c]):
                dead_ends.append((r, c))
    print(dead_ends)
    return dead_ends
