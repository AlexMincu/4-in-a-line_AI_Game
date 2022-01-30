from enum import Enum
import numpy as np
import pygame


NO_ROWS = 7
NO_COLUMNS = 8
CELL_DIM = 75
LINE_WIDTH = int(CELL_DIM * 0.10)

SCREEN_WIDTH = (NO_COLUMNS * CELL_DIM) + ((NO_COLUMNS - 1) * LINE_WIDTH)
SCREEN_HEIGHT = (NO_ROWS * CELL_DIM) + ((NO_ROWS - 1) * LINE_WIDTH)

game_matrix = np.zeros([NO_ROWS, NO_COLUMNS], dtype=int)


class NeighborPos(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP_LEFT = (-1, -1)
    UP_RIGHT = (1, -1)
    DOWN_LEFT = (-1, 1)
    DOWN_RIGHT = (1, 1)


class State(Enum):
    CLOSING = 0
    RUNNING = 1
    TURN_ZERO = 2
    TURN_X = 3


class Symbol(Enum):
    Nothing = 0
    Zero = 1
    X = 2
    Zero_possible = 3
    X_possible = 4


class Colors(Enum):
    Background = pygame.Color(35, 35, 35)
    GridLine = pygame.Color(60, 60, 60)
    Symbol = pygame.Color(255, 255, 255)
    PossibleSymbol = pygame.Color(100, 100, 100)


class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('four-in-a-line but not really')
        pygame.display.set_icon(pygame.image.load('resources/icon.png'))

        # The game always starts with the player X
        self.game_state = State.TURN_X

        # Variables used for the moving methods
        self.showing_possible_moves = False
        self.moving_cell_index = None

    # ------ Drawing Methods ------ #
    def draw(self):
        """
        Draw everything on the window
        """
        # Creates a background
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background.fill(Colors.Background.value)

        self.window.blit(background, (0, 0))
        self.draw_grid()
        self.draw_symbols()

    def draw_grid(self):
        # Draw vertical lines of the grid
        x = CELL_DIM + LINE_WIDTH / 2
        for i in range(NO_COLUMNS):
            pygame.draw.line(self.window, Colors.GridLine.value, (x, 0), (x, SCREEN_HEIGHT), width=LINE_WIDTH)
            x += CELL_DIM + LINE_WIDTH

        # Draw horizontal lines of the grid
        y = CELL_DIM + LINE_WIDTH / 2
        for i in range(NO_ROWS):
            pygame.draw.line(self.window, Colors.GridLine.value, (0, y), (SCREEN_WIDTH, y), width=LINE_WIDTH)
            y += CELL_DIM + LINE_WIDTH

    def draw_symbols(self):
        """
        Iterates through the matrix and it draws the symbols
        """
        cell_dim_offset = CELL_DIM + LINE_WIDTH

        for row_index in range(len(game_matrix)):
            for (column_index, cell_value) in enumerate(game_matrix[row_index]):
                cell_value = int(cell_value)    # From numpy.int32 to int

                # Draw the Zero Symbols
                if (cell_value is Symbol.Zero.value) or (cell_value is Symbol.Zero_possible.value):
                    # Get the center position of the cell
                    cell_pos = (column_index * cell_dim_offset + CELL_DIM / 2, row_index * cell_dim_offset + CELL_DIM / 2)

                    pygame.draw.circle(self.window, (Colors.Symbol.value if (cell_value is Symbol.Zero.value) else Colors.PossibleSymbol.value), cell_pos, (CELL_DIM * 0.8) / 2, width=int(CELL_DIM * 0.1))

                # Draw the X Symbols
                elif (cell_value is Symbol.X.value) or (cell_value is Symbol.X_possible.value):
                    # Get the top-left position of the cell
                    cell_pos = (column_index * cell_dim_offset, row_index * cell_dim_offset)
                    offset = CELL_DIM * 0.2

                    pygame.draw.line(self.window, (Colors.Symbol.value if (cell_value is Symbol.X.value) else Colors.PossibleSymbol.value), (cell_pos[0] + offset, cell_pos[1] + offset), (cell_pos[0] + CELL_DIM - offset, cell_pos[1] + CELL_DIM - offset), width=LINE_WIDTH)
                    pygame.draw.line(self.window, (Colors.Symbol.value if (cell_value is Symbol.X.value) else Colors.PossibleSymbol.value), (cell_pos[0] + CELL_DIM - offset, cell_pos[1] + offset), (cell_pos[0] + offset, cell_pos[1] + CELL_DIM - offset), width=LINE_WIDTH)

    # ------ Game Functionality Methods ------ #
    def put_symbol(self, symbol_type, cursor_pos):
        """
        This function handles the placement/movement of the symbols inside the matrix

        :param symbol_type: The symbol that needs to be placed Symbol.X.value / Symbol.Zero.value
        :param cursor_pos: A tuple of the position where the symbol needs to be placed
        :return: True if the symbol was placed, False otherwise
        """

        # Find the cell to put the symbol
        cell_dim_offset = CELL_DIM + LINE_WIDTH

        cell_index = (int(cursor_pos[1] / cell_dim_offset),
                      int(cursor_pos[0] / cell_dim_offset))

        # If a move needs to be done it has priority over the placement
        if self.showing_possible_moves:
            # Clears the possible moves, and it moves the symbol by having the positions' mem, where:
            #       moving_cell_index   - Indexes of the cell that needs to be moved
            #       cell_index          - Indexes of the cell where the symbol is moved
            if (self.game_state is State.TURN_ZERO) and (game_matrix[cell_index[0], cell_index[1]] == Symbol.Zero_possible.value):
                self.clear_possible_moves()
                game_matrix[self.moving_cell_index[0], self.moving_cell_index[1]] = Symbol.Nothing.value
                game_matrix[cell_index[0], cell_index[1]] = Symbol.Zero.value
                return True

            elif (self.game_state is State.TURN_X) and (game_matrix[cell_index[0], cell_index[1]] == Symbol.X_possible.value):
                self.clear_possible_moves()
                game_matrix[self.moving_cell_index[0], self.moving_cell_index[1]] = Symbol.Nothing.value
                game_matrix[cell_index[0], cell_index[1]] = Symbol.X.value
                return True

        # Put symbol on an empty cell
        if game_matrix[cell_index[0], cell_index[1]] == Symbol.Nothing.value:
            # TODO - Conditions of placements
            game_matrix[cell_index[0], cell_index[1]] = symbol_type
            self.clear_possible_moves()
            return True

        # Move a symbol
        elif game_matrix[cell_index[0], cell_index[1]] == symbol_type:

            # If the possible moves are already rendered, by clicking on the same type of symbol it clears them
            if self.showing_possible_moves is True:
                self.clear_possible_moves()
                return False

            else:
                for possible_cell in NeighborPos:  # Iterate through all possible neighbors
                    possible_cell_counter = 0
                    neighbor_index = (cell_index[0] + possible_cell.value[0], cell_index[1] + possible_cell.value[1])

                    # Checking if the neighbor cell is In-Bounds + Empty (No symbol is placed there)
                    if (0 <= neighbor_index[0] < NO_ROWS) and (0 <= neighbor_index[1] < NO_COLUMNS) and (game_matrix[neighbor_index[0], neighbor_index[1]] == Symbol.Nothing.value):
                        if symbol_type is Symbol.Zero.value:
                            game_matrix[neighbor_index[0], neighbor_index[1]] = Symbol.Zero_possible.value
                        elif symbol_type is Symbol.X.value:
                            game_matrix[neighbor_index[0], neighbor_index[1]] = Symbol.X_possible.value

                    possible_cell_counter = possible_cell_counter + 1

                    # If there are possible cells where to move the symbol, initiate the moving process by
                    #   assigning True to showing_possible_moves and
                    #   keeping the indexes of the symbol that needs to be moved
                    if possible_cell_counter:
                        self.showing_possible_moves = True
                        self.moving_cell_index = (cell_index[0], cell_index[1])

                return False

        return False

    def clear_possible_moves(self):
        """
        Clears the symbols of the possible moves and
            sets the showing_possible_moves to False
        """
        for row_index in range(len(game_matrix)):
            for (column_index, cell_value) in enumerate(game_matrix[row_index]):
                if (game_matrix[row_index][column_index] == Symbol.Zero_possible.value) or (
                        game_matrix[row_index][column_index] == Symbol.X_possible.value):
                    game_matrix[row_index][column_index] = Symbol.Nothing.value

        self.showing_possible_moves = False


if __name__ == '__main__':
    g = Game()

    # Game loop
    while g.game_state is not State.CLOSING:
        # --- Events ---
        for event in pygame.event.get():

            # Closing event
            if event.type == pygame.QUIT:
                g.game_state = State.CLOSING

            # Mouse press down event
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 1 == left button
                    if g.game_state is State.TURN_ZERO:
                        if g.put_symbol(Symbol.Zero.value, pygame.mouse.get_pos()):
                            g.game_state = State.TURN_X

                    elif g.game_state is State.TURN_X:
                        if g.put_symbol(Symbol.X.value, pygame.mouse.get_pos()):
                            g.game_state = State.TURN_ZERO

        # Drawing
        g.draw()

        # Rendering
        pygame.display.update()
