import copy
from enum import Enum
import numpy as np
import pygame


class NeighborPos(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP_LEFT = (-1, -1)
    UP_RIGHT = (1, -1)
    DOWN_LEFT = (-1, 1)
    DOWN_RIGHT = (1, 1)


class GameState(Enum):
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


class Board:
    def __init__(self, game_matrix=None, impossible_moves_matrix=None):
        if game_matrix is not None:
            self.game_matrix = game_matrix
        else:
            self.game_matrix = np.zeros([Game.NO_ROWS, Game.NO_COLUMNS], dtype=int)

        if impossible_moves_matrix is not None:
            self.impossible_moves_matrix = impossible_moves_matrix
        else:
            self.impossible_moves_matrix = np.zeros([Game.NO_ROWS, Game.NO_COLUMNS], dtype=int)

    def get_game_matrix(self):
        return self.game_matrix

    def get_impossible_moves_matrix(self):
        return self.impossible_moves_matrix

    def is_board_final(self):
        print("Board to test if final:")
        print(self.game_matrix)
        for row_index in range(Game.NO_ROWS):
            for column_index in range(Game.NO_COLUMNS):
                if (self.game_matrix[row_index, column_index] == Symbol.X.value) or (
                        self.game_matrix[row_index, column_index] == Symbol.Zero.value):
                    if g.is_final(cell_index=(row_index, column_index), game_matrix=self.game_matrix):
                        return self.game_matrix[row_index, column_index]
        return False


class Game:
    NO_ROWS = 4
    NO_COLUMNS = 4
    CELL_DIM = 75
    LINE_WIDTH = int(CELL_DIM * 0.10)

    SCREEN_WIDTH = (NO_COLUMNS * CELL_DIM) + ((NO_COLUMNS - 1) * LINE_WIDTH)
    SCREEN_HEIGHT = (NO_ROWS * CELL_DIM) + ((NO_ROWS - 1) * LINE_WIDTH)

    DEPTH = 3
    P_MIN = None
    P_MAX = None

    def __init__(self, board):
        pygame.init()
        self.window = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption('four-in-a-line but not really')
        # pygame.display.set_icon(pygame.image.load('resources/icon.png'))

        # The game always starts with the player X
        self.game_state = GameState.TURN_X

        # Current Board used
        self.board = board
        self.game_matrix = board.get_game_matrix()
        self.impossible_moves_matrix = board.get_impossible_moves_matrix()
        self.P_MIN = Symbol.X.value
        self.P_MAX = Symbol.Zero.value

        # Variables used for the moving methods
        self.showing_possible_moves = False
        self.moving_cell_index = None

    # ------ Setters ------ #
    def set_board(self, board: Board):
        self.board = board
        self.game_matrix = board.get_game_matrix()
        self.impossible_moves_matrix = board.get_impossible_moves_matrix()

    # ------ Drawing Methods ------ #
    def draw(self):
        """
        Draw everything on the window
        """
        # Creates a background
        background = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        background.fill(Colors.Background.value)

        self.window.blit(background, (0, 0))
        self.draw_grid()
        self.draw_symbols()

    def draw_grid(self):
        # Draw vertical lines of the grid
        x = self.CELL_DIM + self.LINE_WIDTH / 2
        for i in range(self.NO_COLUMNS):
            pygame.draw.line(self.window, Colors.GridLine.value, (x, 0), (x, self.SCREEN_HEIGHT), width=self.LINE_WIDTH)
            x += self.CELL_DIM + self.LINE_WIDTH

        # Draw horizontal lines of the grid
        y = self.CELL_DIM + self.LINE_WIDTH / 2
        for i in range(self.NO_ROWS):
            pygame.draw.line(self.window, Colors.GridLine.value, (0, y), (self.SCREEN_WIDTH, y), width=self.LINE_WIDTH)
            y += self.CELL_DIM + self.LINE_WIDTH

    def draw_symbols(self):
        """
        Iterates through the matrix and it draws the symbols
        """
        cell_dim_offset = self.CELL_DIM + self.LINE_WIDTH

        for row_index in range(len(self.game_matrix)):
            for (column_index, cell_value) in enumerate(self.game_matrix[row_index]):
                cell_value = int(cell_value)  # From numpy.int32 to int

                # Draw the Zero Symbols
                if (cell_value is Symbol.Zero.value) or (cell_value is Symbol.Zero_possible.value):
                    # Get the center position of the cell
                    cell_pos = (column_index * cell_dim_offset + self.CELL_DIM / 2, row_index * cell_dim_offset + self.CELL_DIM / 2)

                    pygame.draw.circle(self.window, (
                        Colors.Symbol.value if (cell_value is Symbol.Zero.value) else Colors.PossibleSymbol.value),
                                       cell_pos, (self.CELL_DIM * 0.8) / 2, width=int(self.CELL_DIM * 0.1))

                # Draw the X Symbols
                elif (cell_value is Symbol.X.value) or (cell_value is Symbol.X_possible.value):
                    # Get the top-left position of the cell
                    cell_pos = (column_index * cell_dim_offset, row_index * cell_dim_offset)
                    offset = self.CELL_DIM * 0.2

                    pygame.draw.line(self.window, (
                        Colors.Symbol.value if (cell_value is Symbol.X.value) else Colors.PossibleSymbol.value),
                                     (cell_pos[0] + offset, cell_pos[1] + offset),
                                     (cell_pos[0] + self.CELL_DIM - offset, cell_pos[1] + self.CELL_DIM - offset),
                                     width=self.LINE_WIDTH)
                    pygame.draw.line(self.window, (
                        Colors.Symbol.value if (cell_value is Symbol.X.value) else Colors.PossibleSymbol.value),
                                     (cell_pos[0] + self.CELL_DIM - offset, cell_pos[1] + offset),
                                     (cell_pos[0] + offset, cell_pos[1] + self.CELL_DIM - offset),
                                     width=self.LINE_WIDTH)

                # Draw the cell where you can't place
                elif self.impossible_moves_matrix[row_index][column_index] == Symbol.Impossible.value:
                    # Get the top-left position of the cell
                    cell_pos = (column_index * cell_dim_offset, row_index * cell_dim_offset)

                    pygame.draw.rect(self.window, Colors.ImpossibleSymbol.value,
                                     pygame.Rect(cell_pos[0], cell_pos[1], self.CELL_DIM, self.CELL_DIM))

    # ------ Game Functionality Methods ------ #
    def put_symbol(self, symbol_type, cursor_pos):
        """
        This function handles the placement/movement of the symbols inside the matrix

        :param symbol_type: The symbol that needs to be placed Symbol.X.value / Symbol.Zero.value
        :param cursor_pos: A tuple of the position where the symbol needs to be placed
        :return: True if the symbol was placed, False otherwise
        """

        # Find the cell to put the symbol
        cell_dim_offset = self.CELL_DIM + self.LINE_WIDTH

        cell_index = (int(cursor_pos[1] / cell_dim_offset),
                      int(cursor_pos[0] / cell_dim_offset))

        # If a move needs to be done it has priority over the placement
        if self.showing_possible_moves:
            # Clears the possible moves, and it moves the symbol by having the positions' mem, where:
            #       moving_cell_index   - Indexes of the cell that needs to be moved
            #       cell_index          - Indexes of the cell where the symbol is moved
            if (self.game_state is GameState.TURN_ZERO) and (
                    self.game_matrix[cell_index[0], cell_index[1]] == Symbol.Zero_possible.value):
                self.clear_possible_moves()
                self.game_matrix[self.moving_cell_index[0], self.moving_cell_index[1]] = Symbol.Nothing.value
                self.game_matrix[cell_index[0], cell_index[1]] = Symbol.Zero.value

                self.is_final(cell_index)

                return True

            elif (self.game_state is GameState.TURN_X) and (
                    self.game_matrix[cell_index[0], cell_index[1]] == Symbol.X_possible.value):
                self.clear_possible_moves()
                self.game_matrix[self.moving_cell_index[0], self.moving_cell_index[1]] = Symbol.Nothing.value
                self.game_matrix[cell_index[0], cell_index[1]] = Symbol.X.value

                self.is_final(cell_index)

                return True

        # Put symbol on an empty cell
        if (self.game_matrix[cell_index[0], cell_index[1]] == Symbol.Nothing.value) and (
                self.impossible_moves_matrix[cell_index[0], cell_index[1]] != Symbol.Impossible.value):

            self.game_matrix[cell_index[0], cell_index[1]] = symbol_type
            self.clear_possible_moves()
            self.is_final(cell_index)
            return True

        # Move a symbol
        elif self.game_matrix[cell_index[0], cell_index[1]] == symbol_type:

            # If the possible moves are already rendered, by clicking on the same type of symbol it clears them
            if self.showing_possible_moves is True:
                self.clear_possible_moves()
                return False

            else:
                is_possible_cell = False
                for possible_cell in NeighborPos:  # Iterate through all possible neighbors
                    neighbor_index = (cell_index[0] + possible_cell.value[0], cell_index[1] + possible_cell.value[1])

                    # Checking if the neighbor cell is In-Bounds + Empty (No symbol is placed there)
                    if (0 <= neighbor_index[0] < self.NO_ROWS) and (0 <= neighbor_index[1] < self.NO_COLUMNS) and (
                            self.game_matrix[neighbor_index[0], neighbor_index[1]] == Symbol.Nothing.value):
                        if symbol_type is Symbol.Zero.value:
                            self.game_matrix[neighbor_index[0], neighbor_index[1]] = Symbol.Zero_possible.value
                        elif symbol_type is Symbol.X.value:
                            self.game_matrix[neighbor_index[0], neighbor_index[1]] = Symbol.X_possible.value

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
        for row_index in range(len(self.game_matrix)):
            for (column_index, cell_value) in enumerate(self.game_matrix[row_index]):
                if (self.game_matrix[row_index][column_index] == Symbol.Zero_possible.value) or (
                        self.game_matrix[row_index][column_index] == Symbol.X_possible.value):
                    self.game_matrix[row_index][column_index] = Symbol.Nothing.value

        self.refresh_board()
        self.showing_possible_moves = False

    def is_final(self, cell_index, game_matrix=None):
        if game_matrix is None:
            game_matrix = self.game_matrix

        symbol = game_matrix[cell_index[0], cell_index[1]]

        # Check horizontal line
        symbol_counter = 0

        # Check left
        for i in range(1, 4):
            if (0 <= cell_index[0] < self.NO_ROWS) and (0 <= cell_index[1] - i < self.NO_COLUMNS):
                if game_matrix[cell_index[0], cell_index[1] - i] == symbol:
                    symbol_counter = symbol_counter + 1
                else:
                    break
            else:
                break

        # Check right
        for i in range(1, 4):
            if (0 <= cell_index[0] < self.NO_ROWS) and (0 <= cell_index[1] + i < self.NO_COLUMNS):
                if game_matrix[cell_index[0], cell_index[1] + i] == symbol:
                    symbol_counter = symbol_counter + 1
                else:
                    break
            else:
                break

        if symbol_counter == 3:
            print("A winning position was found on a horizontal line")
            return True

        # Check vertical line
        symbol_counter = 0

        # Check up
        for i in range(1, 4):
            if (0 <= cell_index[0] - i < self.NO_ROWS) and (0 <= cell_index[1] < self.NO_COLUMNS):
                if game_matrix[cell_index[0] - i, cell_index[1]] == symbol:
                    symbol_counter = symbol_counter + 1
                else:
                    break
            else:
                break

        # Check down
        for i in range(1, 4):
            if (0 <= cell_index[0] + i < self.NO_ROWS) and (0 <= cell_index[1] < self.NO_COLUMNS):
                if game_matrix[cell_index[0] + i, cell_index[1]] == symbol:
                    symbol_counter = symbol_counter + 1
                else:
                    break
            else:
                break

        if symbol_counter == 3:
            print("A winning position was found on a vertical line")
            return True

        # Check diagonal 1
        symbol_counter = 0

        # Check top-left half of diagonal
        for i in range(1, 4):
            if (0 <= cell_index[0] - i < self.NO_ROWS) and (0 <= cell_index[1] - i < self.NO_COLUMNS):
                if game_matrix[cell_index[0] - i, cell_index[1] - i] == symbol:
                    symbol_counter = symbol_counter + 1
                else:
                    break
            else:
                break

        # Check bottom-right half of diagonal
        for i in range(1, 4):
            if (0 <= cell_index[0] + i < self.NO_ROWS) and (0 <= cell_index[1] + i < self.NO_COLUMNS):
                if game_matrix[cell_index[0] + i, cell_index[1] + i] == symbol:
                    symbol_counter = symbol_counter + 1
                else:
                    break
            else:
                break

        if symbol_counter == 3:
            print("A winning position was found on diag 1")
            return True

        # Check diagonal 2
        symbol_counter = 0

        # Check bottom-left half of diagonal
        for i in range(1, 4):
            if (0 <= cell_index[0] + i < self.NO_ROWS) and (0 <= cell_index[1] - i < self.NO_COLUMNS):
                if game_matrix[cell_index[0] + i, cell_index[1] - i] == symbol:
                    symbol_counter = symbol_counter + 1
                else:
                    break
            else:
                break

        # Check top-right half of diagonal
        for i in range(1, 4):
            if (0 <= cell_index[0] - i < self.NO_ROWS) and (0 <= cell_index[1] + i < self.NO_COLUMNS):
                if game_matrix[cell_index[0] - i, cell_index[1] + i] == symbol:
                    symbol_counter = symbol_counter + 1
                else:
                    break
            else:
                break

        if symbol_counter == 3:
            print("A winning position was found on diag 2")
            return True

        return False

    def refresh_board(self):
        """
        Mark the positions where the player cannot put a symbol
        """
        symbol = None
        if self.game_state is GameState.TURN_ZERO:
            symbol = Symbol.Zero.value
        elif self.game_state is GameState.TURN_X:
            symbol = Symbol.X.value

        neighbors = list(NeighborPos)[0:4]

        # Iterate through the matrix
        for row_index in range(len(self.game_matrix)):
            for (column_index, cell_value) in enumerate(self.game_matrix[row_index]):

                # Reset the cells so the next turn impossible moves can be refreshed
                if self.impossible_moves_matrix[row_index, column_index] == Symbol.Impossible.value:
                    self.impossible_moves_matrix[row_index, column_index] = Symbol.Nothing.value

                # If the cell is empty check neighbors so the impossible moves can be calculated
                if cell_value == Symbol.Nothing.value:

                    zero_symbol_counter = 0
                    x_symbol_counter = 0

                    for neighbor in neighbors:  # Iterate through the first 4 neighbors (UP, DOWN, LEFT, RIGHT)
                        neighbor_index = (row_index + neighbor.value[0], column_index + neighbor.value[1])

                        # Checking if the neighbor cell is In-Bounds
                        if (0 <= neighbor_index[0] < self.NO_ROWS) and (0 <= neighbor_index[1] < self.NO_COLUMNS):

                            if self.game_matrix[neighbor_index[0], neighbor_index[1]] == Symbol.Zero.value:
                                zero_symbol_counter = zero_symbol_counter + 1
                            elif self.game_matrix[neighbor_index[0], neighbor_index[1]] == Symbol.X.value:
                                x_symbol_counter = x_symbol_counter + 1

                    # Impossible move found
                    if ((symbol is Symbol.Zero.value) and (zero_symbol_counter < x_symbol_counter)) or (
                            (symbol is Symbol.X.value) and (x_symbol_counter < zero_symbol_counter)):
                        self.impossible_moves_matrix[row_index][column_index] = Symbol.Impossible.value

    def is_move_available(self):
        """
        Check if any moves are available for the current player
        """
        symbol = None
        if self.game_state is GameState.TURN_ZERO:
            symbol = Symbol.Zero.value
        elif self.game_state is GameState.TURN_X:
            symbol = Symbol.X.value

        # Look for a valid cell to put a symbol

        # Iterate through the matrix
        for row_index in range(len(self.game_matrix)):
            for column_index in range(len(self.game_matrix[row_index])):
                # The matrix contains an empty cell that is valid for putting a symbol
                if (self.game_matrix[row_index, column_index] == Symbol.Nothing.value) and (
                        self.impossible_moves_matrix[row_index, column_index] != Symbol.Impossible.value):
                    return True

        # If there are no valid cell to put a symbol, look for a move
        # Iterate through the matrix
        for row_index in range(len(self.game_matrix)):
            for column_index in range(len(self.game_matrix[row_index])):
                # The matrix contains an empty cell
                if self.game_matrix[row_index, column_index] == Symbol.Nothing.value:
                    # Check if the empty cell is a possible cell to move a symbol:
                    #   If the neighbor of the empty cell contains a symbol then a move is possible

                    # Iterate through all possible neighbors
                    for neighbor in NeighborPos:
                        neighbor_index = (row_index + neighbor.value[0], column_index + neighbor.value[1])

                        # Checking if the neighbor cell is In-Bounds
                        if (0 <= neighbor_index[0] < self.NO_ROWS) and (0 <= neighbor_index[1] < self.NO_COLUMNS):
                            if self.game_matrix[neighbor_index[0], neighbor_index[1]] == symbol:
                                return True  # Found a possible move

            # Couldn't find any move either -> The player loses turn.
            print("Player doesn't have any moves, skip turn")
            return False

    def get_possible_boards(self, player, current_state_matrix):
        """
        Create the possible boards for the current player - used in the searching algorithms
        :param current_state_matrix: .
        :param player: The value of the player associated with the play: Symbol.Zero.value or Symbol.X.value
        :return:
        """
        print(f"get pos board player value is: {player} and it's type is {type(player)}")
        game_matrix = current_state_matrix
        boards_list = []
        for row_index in range(self.NO_ROWS):
            for column_index in range(self.NO_COLUMNS):

                # Put a piece
                if (game_matrix[row_index, column_index] == Symbol.Nothing.value) and (
                        self.impossible_moves_matrix[row_index, column_index] != Symbol.Impossible.value):
                    matrix_copy = copy.deepcopy(game_matrix)
                    matrix_copy[row_index, column_index] = player
                    boards_list.append(Board(matrix_copy, self.impossible_moves_matrix))

                # Move a piece
                if game_matrix[row_index, column_index] == player:

                    for possible_cell in NeighborPos:  # Iterate through all possible neighbors
                        neighbor_index = (row_index + possible_cell.value[0], column_index + possible_cell.value[1])

                        # Checking if the neighbor cell is In-Bounds + Empty (No symbol is placed there)
                        if (0 <= neighbor_index[0] < self.NO_ROWS) and (0 <= neighbor_index[1] < self.NO_COLUMNS) and (
                                game_matrix[neighbor_index[0], neighbor_index[1]] == Symbol.Nothing.value):
                            matrix_copy = copy.deepcopy(game_matrix)
                            matrix_copy[row_index, column_index] = Symbol.Nothing.value
                            matrix_copy[neighbor_index[0], neighbor_index[1]] = player
                            boards_list.append(Board(matrix_copy, self.impossible_moves_matrix))

        return boards_list

    @classmethod
    def get_opposite_player(cls, current_player: int):
        if current_player == Symbol.Zero.value:
            return Symbol.X.value
        elif current_player == Symbol.X.value:
            return Symbol.Zero.value
        else:
            print("Trying to switch the player, but the current_player param is not a X or Zero")
            return


class State:
    """
    Class used for searching algorithms min-max and alpha-beta;
    - A state represents the node from a tree -

    This class requires that the Game class has
        - the two player: P_MAX, P_MIN
        - a method moves(player) that returns the list of possible moves
    """

    def __init__(self, board: Board, current_player: int, depth, parent=None, estimation=None):
        self.board = board
        self.current_player = current_player
        self.depth = depth
        self.parent = parent  # Parent: Another State -> Parent node from the tree
        self.estimation = estimation
        self.possible_moves = []  # List of the possible moves (ramifications) from this State (node)
        self.chosen_state = None  # Best move computed

    def __str__(self):
        return f"The player {self.current_player} has the board \n{self.board.game_matrix}\n Current Depth is: {self.depth}\nHas the estimation value: {self.estimation}\nIs a chosen state?: {self.chosen_state}\n"

    def get_possible_states(self):
        """
        :return: List of possible states (nodes) of the current player on the subtree
        """
        # Create possible boards of the current player
        possible_boards_list = Game.get_possible_boards(g, player=self.current_player,
                                                        current_state_matrix=self.board.get_game_matrix())

        # Switch players
        print(f"Current player is {self.current_player}")
        opposite_player = Game.get_opposite_player(self.current_player)
        print(f"opposite player is {opposite_player}")

        # If possible, go deeper into the tree and continue the algorithm
        possible_states_list = [State(possible_board, opposite_player, self.depth - 1, parent=self) for possible_board
                                in possible_boards_list]
        print("==================== possible states list: =================")
        for state in possible_states_list:
            print(state)

        return possible_states_list

    def open_line(self, line, current_player_symbol: int):
        opposite_player_symbol = Game.get_opposite_player(current_player_symbol)

        # verific daca pe linia data am simbolul jucatorului opus -> return 0
        if opposite_player_symbol in line:
            return 0
        return 1

    def open_lines(self, current_player_symbol):
        return (self.open_line(g.game_matrix[0, 0:4], current_player_symbol)
                + self.open_line(g.game_matrix[1, 0:4], current_player_symbol)
                + self.open_line(g.game_matrix[2, 0:4], current_player_symbol)
                + self.open_line(g.game_matrix[3, 0:4], current_player_symbol)

                + self.open_line(g.game_matrix[0:4, 0], current_player_symbol)
                + self.open_line(g.game_matrix[0:4, 1], current_player_symbol)
                + self.open_line(g.game_matrix[0:4, 2], current_player_symbol)
                + self.open_line(g.game_matrix[0:4, 3], current_player_symbol)

                + self.open_line([g.game_matrix[0, 0], g.game_matrix[1, 1], g.game_matrix[2, 2], g.game_matrix[3, 3]], current_player_symbol)

                + self.open_line([g.game_matrix[0, 3], g.game_matrix[1, 2], g.game_matrix[2, 1], g.game_matrix[3, 0]], current_player_symbol))

    def estimate_score(self, depth):
        t_final = self.board.is_board_final()
        print(f"T_FINAL = {t_final}")
        if t_final == Symbol.Zero.value:
            print("return 99+depth")
            return 99 + depth
        elif t_final == Symbol.X.value:
            print("return -99+depth")

            return -99 + depth
        else:
            return self.open_lines(Symbol.Zero.value) - self.open_lines(Symbol.X.value)


def min_max(state: State):
    print(f"\n\n\n\n====== Call min_max on state: {state} ======")
    if state.depth == 0 or state.board.is_board_final():
        state.estimation = state.estimate_score(depth=state.depth)
        return state

    # Compute all the possible nodes from the next level of the tree
    state.possible_moves = state.get_possible_states()

    print("Passes the initial get possible states")

    print("Start the recursive part -> estimated_moves = [min_max(move) for move in state.possible_moves]")
    # Apply min-max algorithm on the next level nodes created previously
    estimated_moves = [min_max(move) for move in state.possible_moves]

    print("Passes the estimated moves section")

    # Pick the players best estimation
    if state.current_player == Game.P_MAX:
        # Pick the state with the max estimation if the Player is MAX
        state.chosen_state = max(estimated_moves, key=lambda x: x.estimation)
    else:
        # Pick the state with the min estimation if the Player is MIN
        state.chosen_state = min(estimated_moves, key=lambda x: x.estimation)

    state.estimation = state.chosen_state.estimation
    return state


g = Game(Board())

if __name__ == '__main__':

    # Game loop
    while g.game_state is not GameState.CLOSING:
        # --- Events ---
        for event in pygame.event.get():

            # Closing event
            if event.type == pygame.QUIT:
                g.game_state = GameState.CLOSING

            # Mouse press down event
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 1 == left button

                    if g.game_state is GameState.TURN_X:
                        if g.put_symbol(Symbol.X.value, pygame.mouse.get_pos()):
                            if g.game_state is not GameState.FINAL:
                                g.game_state = GameState.TURN_ZERO
                                g.refresh_board()

                                if not g.is_move_available():
                                    g.game_state = GameState.TURN_X
                                    g.refresh_board()

                            else:
                                print("X is the Winner")

                    elif g.game_state is GameState.TURN_ZERO:
                        # if not g.is_move_available():
                        #     g.game_state = GameState.TURN_ZERO
                        #     g.refresh_board()

                        new_state = min_max(State(board=g.board, current_player=Symbol.Zero.value, depth=Game.DEPTH))
                        print("============================================")

                        print("min_max finished and the current state is:")
                        print(new_state)
                        print("============================================")

                        current_board = new_state.chosen_state.board
                        print("Current board is: ")
                        print(current_board.game_matrix)
                        g.set_board(current_board)
                        if g.game_state is not GameState.FINAL:
                            g.game_state = GameState.TURN_X
                            g.refresh_board()
                        else:
                            print("Zero is the Winner")

        # Drawing
        g.draw()

        # Rendering
        pygame.display.update()
