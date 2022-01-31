from enum import Enum
import numpy as np
import pygame


NO_ROWS = 5
NO_COLUMNS = 5
CELL_DIM = 75
LINE_WIDTH = int(CELL_DIM * 0.10)

SCREEN_WIDTH = (NO_COLUMNS * CELL_DIM) + ((NO_COLUMNS - 1) * LINE_WIDTH)
SCREEN_HEIGHT = (NO_ROWS * CELL_DIM) + ((NO_ROWS - 1) * LINE_WIDTH)

game_matrix = np.zeros([NO_ROWS, NO_COLUMNS], dtype=int)
impossible_moves_matrix = np.zeros([NO_ROWS, NO_COLUMNS], dtype=int)


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
    FINAL = 4


class Symbol(Enum):
    Nothing = 0
    Zero = 1
    X = 2
    Zero_possible = 3
    X_possible = 4
    Impossible = 5


class Colors(Enum):
    Background = pygame.Color(35, 35, 35)
    GridLine = pygame.Color(60, 60, 60)
    Symbol = pygame.Color(255, 255, 255)
    PossibleSymbol = pygame.Color(100, 100, 100)
    ImpossibleSymbol = pygame.Color(20, 20, 20)


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

                # Draw the cell where you can't place
                elif impossible_moves_matrix[row_index][column_index] == Symbol.Impossible.value:
                    # Get the top-left position of the cell
                    cell_pos = (column_index * cell_dim_offset, row_index * cell_dim_offset)

                    pygame.draw.rect(self.window, Colors.ImpossibleSymbol.value, pygame.Rect(cell_pos[0], cell_pos[1], CELL_DIM, CELL_DIM))

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

                self.is_final(cell_index)

                return True

            elif (self.game_state is State.TURN_X) and (game_matrix[cell_index[0], cell_index[1]] == Symbol.X_possible.value):
                self.clear_possible_moves()
                game_matrix[self.moving_cell_index[0], self.moving_cell_index[1]] = Symbol.Nothing.value
                game_matrix[cell_index[0], cell_index[1]] = Symbol.X.value

                self.is_final(cell_index)

                return True

        # Put symbol on an empty cell
        if (game_matrix[cell_index[0], cell_index[1]] == Symbol.Nothing.value) and (impossible_moves_matrix[cell_index[0], cell_index[1]] != Symbol.Impossible.value):

            game_matrix[cell_index[0], cell_index[1]] = symbol_type
            self.clear_possible_moves()
            self.is_final(cell_index)
            return True

        # Move a symbol
        elif game_matrix[cell_index[0], cell_index[1]] == symbol_type:

            # If the possible moves are already rendered, by clicking on the same type of symbol it clears them
            if self.showing_possible_moves is True:
                self.clear_possible_moves()
                return False

            else:
                is_possible_cell = False
                for possible_cell in NeighborPos:  # Iterate through all possible neighbors
                    neighbor_index = (cell_index[0] + possible_cell.value[0], cell_index[1] + possible_cell.value[1])

                    # Checking if the neighbor cell is In-Bounds + Empty (No symbol is placed there)
                    if (0 <= neighbor_index[0] < NO_ROWS) and (0 <= neighbor_index[1] < NO_COLUMNS) and (game_matrix[neighbor_index[0], neighbor_index[1]] == Symbol.Nothing.value):
                        if symbol_type is Symbol.Zero.value:
                            game_matrix[neighbor_index[0], neighbor_index[1]] = Symbol.Zero_possible.value
                        elif symbol_type is Symbol.X.value:
                            game_matrix[neighbor_index[0], neighbor_index[1]] = Symbol.X_possible.value

                        is_possible_cell = True

                # If there are possible cells where to move the symbol, initiate the moving process by
                #   assigning True to showing_possible_moves and
                #   keeping the indexes of the symbol that needs to be moved
                if is_possible_cell:
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

        self.refresh_board()
        self.showing_possible_moves = False

    def is_final(self, cell_index):
        symbol = game_matrix[cell_index[0], cell_index[1]]

        # Check horizontal line
        symbol_counter = 0

        # Check left
        for i in range(1, 4):
            if (0 <= cell_index[0] < NO_ROWS) and (0 <= cell_index[1] - i < NO_COLUMNS):
                if game_matrix[cell_index[0], cell_index[1] - i] == symbol:
                    symbol_counter = symbol_counter + 1
                else:
                    break
            else:
                break

        # Check right
        for i in range(1, 4):
            if (0 <= cell_index[0] < NO_ROWS) and (0 <= cell_index[1] + i < NO_COLUMNS):
                if game_matrix[cell_index[0], cell_index[1] + i] == symbol:
                    symbol_counter = symbol_counter + 1
                else:
                    break
            else:
                break

        if symbol_counter == 3:
            print("A winning position was found on a horizontal line")
            self.game_state = State.FINAL
            return

        # Check vertical line
        symbol_counter = 0

        # Check up
        for i in range(1, 4):
            if (0 <= cell_index[0] - i < NO_ROWS) and (0 <= cell_index[1] < NO_COLUMNS):
                if game_matrix[cell_index[0] - i, cell_index[1]] == symbol:
                    symbol_counter = symbol_counter + 1
                else:
                    break
            else:
                break

        # Check down
        for i in range(1, 4):
            if (0 <= cell_index[0] + i < NO_ROWS) and (0 <= cell_index[1] < NO_COLUMNS):
                if game_matrix[cell_index[0] + i, cell_index[1]] == symbol:
                    symbol_counter = symbol_counter + 1
                else:
                    break
            else:
                break

        if symbol_counter == 3:
            print("A winning position was found on a vertical line")
            self.game_state = State.FINAL
            return

        # Check diagonal 1
        symbol_counter = 0

        # Check top-left half of diagonal
        for i in range(1, 4):
            if (0 <= cell_index[0] - i < NO_ROWS) and (0 <= cell_index[1] - i < NO_COLUMNS):
                if game_matrix[cell_index[0] - i, cell_index[1] - i] == symbol:
                    symbol_counter = symbol_counter + 1
                else:
                    break
            else:
                break

        # Check bottom-right half of diagonal
        for i in range(1, 4):
            if (0 <= cell_index[0] + i < NO_ROWS) and (0 <= cell_index[1] + i < NO_COLUMNS):
                if game_matrix[cell_index[0] + i, cell_index[1] + i] == symbol:
                    symbol_counter = symbol_counter + 1
                else:
                    break
            else:
                break

        if symbol_counter == 3:
            print("A winning position was found on diag 1")
            self.game_state = State.FINAL
            return

        # Check diagonal 2
        symbol_counter = 0

        # Check bottom-left half of diagonal
        for i in range(1, 4):
            if (0 <= cell_index[0] + i < NO_ROWS) and (0 <= cell_index[1] - i < NO_COLUMNS):
                if game_matrix[cell_index[0] + i, cell_index[1] - i] == symbol:
                    symbol_counter = symbol_counter + 1
                else:
                    break
            else:
                break

        # Check top-right half of diagonal
        for i in range(1, 4):
            if (0 <= cell_index[0] - i < NO_ROWS) and (0 <= cell_index[1] + i < NO_COLUMNS):
                if game_matrix[cell_index[0] - i, cell_index[1] + i] == symbol:
                    symbol_counter = symbol_counter + 1
                else:
                    break
            else:
                break

        if symbol_counter == 3:
            print("A winning position was found on diag 2")
            self.game_state = State.FINAL
            return

        return False

    def refresh_board(self):
        """
        Mark the positions where the player cannot put a symbol
        """
        symbol = None
        if self.game_state is State.TURN_ZERO:
            symbol = Symbol.Zero.value
        elif self.game_state is State.TURN_X:
            symbol = Symbol.X.value

        neighbors = list(NeighborPos)[0:4]

        # Iterate through the matrix
        for row_index in range(len(game_matrix)):
            for (column_index, cell_value) in enumerate(game_matrix[row_index]):

                # Reset the cells so the next turn impossible moves can be refreshed
                if impossible_moves_matrix[row_index, column_index] == Symbol.Impossible.value:
                    impossible_moves_matrix[row_index, column_index] = Symbol.Nothing.value

                # If the cell is empty check neighbors so the impossible moves can be calculated
                if cell_value == Symbol.Nothing.value:

                    zero_symbol_counter = 0
                    x_symbol_counter = 0

                    for neighbor in neighbors:  # Iterate through the first 4 neighbors (UP, DOWN, LEFT, RIGHT)
                        neighbor_index = (row_index + neighbor.value[0], column_index + neighbor.value[1])

                        # Checking if the neighbor cell is In-Bounds
                        if (0 <= neighbor_index[0] < NO_ROWS) and (0 <= neighbor_index[1] < NO_COLUMNS):

                            if game_matrix[neighbor_index[0], neighbor_index[1]] == Symbol.Zero.value:
                                zero_symbol_counter = zero_symbol_counter + 1
                            elif game_matrix[neighbor_index[0], neighbor_index[1]] == Symbol.X.value:
                                x_symbol_counter = x_symbol_counter + 1

                    # Impossible move found
                    if ((symbol is Symbol.Zero.value) and (zero_symbol_counter < x_symbol_counter)) or ((symbol is Symbol.X.value) and (x_symbol_counter < zero_symbol_counter)):
                        impossible_moves_matrix[row_index][column_index] = Symbol.Impossible.value

    def is_move_available(self):
        """
        Check if any moves are available for the current player
        """
        symbol = None
        if self.game_state is State.TURN_ZERO:
            symbol = Symbol.Zero.value
        elif self.game_state is State.TURN_X:
            symbol = Symbol.X.value

        # Look for a valid cell to put a symbol

        # Iterate through the matrix
        for row_index in range(len(game_matrix)):
            for column_index in range(len(game_matrix[row_index])):
                # The matrix contains an empty cell that is valid for putting a symbol
                if (game_matrix[row_index, column_index] == Symbol.Nothing.value) and (impossible_moves_matrix[row_index, column_index] != Symbol.Impossible.value):
                    return True

        # If there are no valid cell to put a symbol, look for a move
        # Iterate through the matrix
        for row_index in range(len(game_matrix)):
            for column_index in range(len(game_matrix[row_index])):
                # The matrix contains an empty cell
                if game_matrix[row_index, column_index] == Symbol.Nothing.value:
                    # Check if the empty cell is a possible cell to move a symbol:
                    #   If the neighbor of the empty cell contains a symbol then a move is possible

                    # Iterate through all possible neighbors
                    for neighbor in NeighborPos:
                        neighbor_index = (row_index + neighbor.value[0], column_index + neighbor.value[1])

                        # Checking if the neighbor cell is In-Bounds
                        if (0 <= neighbor_index[0] < NO_ROWS) and (0 <= neighbor_index[1] < NO_COLUMNS):
                            if game_matrix[neighbor_index[0], neighbor_index[1]] == symbol:
                                return True     # Found a possible move

            # Couldn't find any move either -> The player loses turn.
            print("Player doesn't have any moves, skip turn")
            return False


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
                            if g.game_state is not State.FINAL:
                                g.game_state = State.TURN_X
                                g.refresh_board()

                                if not g.is_move_available():
                                    g.game_state = State.TURN_ZERO
                                    g.refresh_board()
                            else:
                                print("Zero is the Winner")

                    elif g.game_state is State.TURN_X:
                        if g.put_symbol(Symbol.X.value, pygame.mouse.get_pos()):
                            if g.game_state is not State.FINAL:
                                g.game_state = State.TURN_ZERO
                                g.refresh_board()

                                if not g.is_move_available():
                                    g.game_state = State.TURN_X
                                    g.refresh_board()

                            else:
                                print("X is the Winner")

        # Drawing
        g.draw()

        # Rendering
        pygame.display.update()
