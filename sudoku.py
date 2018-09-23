import copy
from typing import List, Set, Tuple


class Cell(object):
    """Basic class to store data of one cell.

    Attributes:
        _row (int): Row parameter of a cell.
        _column (int): Column parameter of a cell.
        _editable (bool): Defines if object's value can be edited or is permanent.
        _value (int): Value of the cell between 0 (empty) and MAX_VALUE.
        _possible_values (set[int]): A set of values that are possible to write to the cell.
    """

    MAX_VALUE = 9  # TODO rethink if it should be class static

    def __init__(self, row: int, column: int, editable=True, value=0):
        """Initiate a cell. Write arguments to instance attributes and create a set of possible values. Populate the set
        with values from range <1, MAX_VALUE> if the cell is editable.

        Args:
            row (int): Row parameter of a cell.
            column (int): Column parameter of a cell.
            editable (bool): Defines if object's value can be edited or is permanent. Defaults to True.
            value (int): Value of the cell between 0 (empty) and MAX_VALUE. Defaults to 0.

        Raises:
            AttributeError: Raise if:
            - editable is False and value is 0, or
            - value is not in a range <0, MAX_VALUE>, or
            - row or column is not in a range <0, MAX_VALUE).
        """
        if editable is False and value == 0:
            raise AttributeError("Cell not editable and without value")
        elif value < 0 or value > self.MAX_VALUE:
            raise AttributeError("Incorrect value ({} not in <0,{}>)".format(value, self.MAX_VALUE))
        elif not(0 <= row < self.MAX_VALUE) or not(0 <= column < self.MAX_VALUE):
            raise AttributeError("Incorrect row or column ({},{} not in <0,{}>".format(row, column, self.MAX_VALUE))

        self._editable = editable
        self._value = value
        self._row = row
        self._column = column

        if editable:
            self._possible_values = set(range(1, self.MAX_VALUE + 1))
        else:
            self._possible_values = set()

    @property
    def row(self) -> int:
        """Return row as integer. Row should be in a range <0, MAX_VALUE-1>."""
        return self._row

    @property
    def column(self) -> int:
        """Return column as integer. Column should be in a range <0, MAX_VALUE-1>."""
        return self._column

    @property
    def editable(self) -> bool:
        """Return bool value if cell is editable."""
        return self._editable

    @property
    def possible_values(self) -> Set[int]:
        """Return a set of cell's possible values."""
        return self._possible_values

    @property
    def value(self) -> int:
        """Cell's value as integer.

        Write value if a cell is editable and the value is in a correct range (<0, MAX_VALUE>).
        Clear a set of possible values if value is not 0.

        Raises:
            Attribute Error: Raise if:
            - editable attribute is False
            - value is not in a range <0, MAX_VALUE>
        """
        return self._value

    @value.setter
    def value(self, value: int):
        if self._editable is False:
            raise AttributeError("Cell not editable")
        elif value < 0 or value > self.MAX_VALUE:
            raise AttributeError("Incorrect value ({} not in <0,{}>)".format(value, self.MAX_VALUE))
        elif value == 0:
            self._value = value
        else:
            self._value = value
            self._possible_values.clear()

    def init_possible_values(self):
        """Fill the set of possible values with full range <1, MAX_VALUE>."""
        self._possible_values = set(range(1, 1+self.MAX_VALUE))

    def intersect_possible_values(self, values: set):
        """Intersect cell's possible values with given set (i.e. set of possible values from region)

        Args:
            values (set[int]): Set to intersect with instance's possible values.
        """
        self._possible_values = self._possible_values.intersection(values)

    def clear(self):
        """Clear the cell's value if the cell is editable"""
        if self.editable:
            self.value = 0

    def remove_possible_value(self, value: int):
        """Remove possible value from a set (if present)

        Args:
            value (int): Remove value from possible values set.
        """
        if value in self._possible_values:
            self._possible_values.remove(value)

    def to_string(self) -> str:
        """Print cell's attributes for diagnostic purpose.

        Returns:
            str: Diagnostic string.
        """
        return "[{0._row},{0._column}]: editable: {0._editable}: {0._value} / {0._possible_values}".format(self)


class Region(object):
    """Class holding a list of cells that have to have unique values. It might be:
    - row,
    - column,
    - rectangle.

     Attributes:
        _cells[Cell]: A list of objects of type Cell.
    """

    def __init__(self):
        self._cells = []

    @property
    def cells(self):
        """List of cells in a region"""
        return self._cells

    def add(self, cell: Cell):
        """Add a cell to a list of cells if the list does not contain it.

        Args:
            cell (Cell): Cell to be added to the list.
        """
        if cell not in self._cells:
            self._cells.append(cell)

    def remove_possible_value_if_cell_is_in_region(self, cell: Cell, value: int):
        """Remove value from cell's possible values if the cell is in region.

        Args:
            cell (Cell): Cell instance to check if it is in a region and to remove possible value from.
            value (int): Possible value.
        """
        if cell in self._cells:
            for cell in self._cells:
                cell.remove_possible_value(value)

    def update_possible_values(self):
        """Update possible values in all cells that the region contains.

        Create a set of possible values in a range <1, number of cells in a region>. Go through all cells and read their
        values. Remove read values from prepared set. Go through each cell and intersect cell's possible values with
        the set.

        Each cell belongs to 3 regions (row, column, rectangle), so its possible values should be intersected 3 times
        (by calling 'update_possible_values' method for all regions.
        """
        values = set(range(1, 1+len(self._cells)))
        for cell in self._cells:
            v = cell.value
            if v in values:
                values.remove(v)

        for cell in self._cells:
            if cell.value == 0:
                cell.intersect_possible_values(values)

    def is_solved(self) -> bool:
        """Check if the region is solved.

        The region is solved if all cells have non-zero value, and all possible values from range
        <1, number of cells in a region> are used.

        Returns:
             bool: True if the region is solved. False otherwise.
        """
        values = set()
        for cell in self._cells:
            values.add(cell.value)

        expected_values = set(range(1, len(self._cells)+1))
        return values == expected_values

    def is_not_possible_to_solve(self):
        """Check if a region is not possible to solve in a current configuration.

        Returns:
            bool: True if there is a cell with no value (zero) and it has zero possible values or if there are at least
            two cells with the same value.
        """
        a_set = set()
        for cell in self._cells:
            if cell.value == 0 and len(cell.possible_values) == 0:
                return True
            elif cell.value in a_set:
                return True
            elif cell.value != 0:
                a_set.add(cell.value)
        return False


class UndoRedo(object):
    """
    Class storing actions of setting values to Sudoku's cells in order to perform 'undo' and 'redo' actions.

    Attributes:
        _undo (List[ Tuple[int, int, int, str] ]): Performed actions as list of tuples with row, column, value
        and method.
        _redo (List[ Tuple[int, int, int, str] ]): Actions after 'undo' operation are moved to 'redo' list.
    """

    def __init__(self):
        self._undo = []
        self._redo = []

    def add_action(self, row: int, column: int, old_value: int, value: int, method: str = ''):
        """Store data of action performed on a cell. When new data is inserted, 'redo' list is cleared.

        Args:
        row (int):  Cell's row parameter.
        column (int): Cell's column parameter.
        old_value (int): Cell's value before writing a new value.
        value (int): Value written to the cell.
        method (str): Name of the method writing value (optional). Defaults to ''.
        """
        self._undo.append((row, column, old_value, value, method))
        self._redo.clear()

    def undo_length(self):
        """Return length of undo list."""
        return len(self._undo)

    def redo_length(self):
        """Return length of redo list."""
        return len(self._redo)

    def undo(self) -> Tuple[int, int, int, int, str, int, int]:
        """Get last action performed on Sudoku as: row, column, value before writing, value written, method, number of
        remaining actions in undo list and number of actions in redo list. Returned action is also written to redo list.
        It means that updating Cell's value with returned data should be performed without calling add_action function,
        because it clears redo list.

        Returns:
            Tuple[int, int, int, int, str, int, int]: row, column, old_value, value, method, length_of_undo_list,
            length_of_redo_list.
        """
        last_action = self._undo.pop()
        self._redo.append(last_action)
        return (*last_action), len(self._undo), len(self._redo)

    def redo(self):
        """Get undone action. Returned action is also written to undo list. If you want to write value to a cell, do not
        call add_action function, because it clears redo list and adds action to undo list (you would get two the same
        actions in a row).

        Returns:
            Tuple[int, int, int, int, str, int, int]: row, column, old_value, value, method, length_of_undo_list,
            length_of_redo_list.
        """
        redo_action = self._redo.pop()
        self._undo.append(redo_action)
        return (*redo_action), len(self._undo), len(self._redo)


class Sudoku(object):
    """Class that contains Sudoku board - two dimensional array of cells.

    Attributes:
        cells (List[List[Cell]]):
        _size (int)
        _rect_width (int)
        _rect_height (int)
        _undo_redo
    """

    def __init__(self, size=9, cells=None, rect_width=3, rect_height=3):
        if cells is None:
            self.cells = [[Cell(r, c) for c in range(size)] for r in range(size)]
            self._size = size
        else:
            self.cells = cells
            self._size = len(cells)

        self._undo_redo = UndoRedo()

        self._rect_width = rect_width
        self._rect_height = rect_height

        rows = columns = self._size
        rectangles = (self._size ** 2) // (self._rect_width * self._rect_height)  # number of rectangles = board size / rect_size
        self._regions = [Region() for x in range(rows + columns + rectangles)]  # generate regions for rows, cols, rects

        for row in range(self._size):
            for col in range(self._size):
                self._regions[row].add(self.cells[row][col])        # populate row regions
                self._regions[rows+col].add(self.cells[row][col])   # populate column regions

        # populate rectangle regions
        width_size = self._size // self._rect_width
        height_size = self._size // self._rect_height
        reg = self._size * 2 - 1
        for x_start in range(height_size):
            for y_start in range(width_size):
                reg += 1
                for x in range(x_start * width_size, (x_start+1) * width_size):
                    for y in range((y_start * height_size), (y_start+1) * height_size):
                        self._regions[reg].add(self.cells[x][y])

        self.update_possible_values_in_all_regions()

    @property
    def size(self) -> int:
        """Sudoku board size (number of cells per row / column / rectangle)."""
        return self._size

    @property
    def regions(self) -> List[Region]:
        """List of regions."""
        return self._regions

    def _is_row_and_column_in_range(self, row: int, column: int) -> bool:
        """Check if row and integer are in range <0, size-1>.

        Args:
            row (int): A row number (<0, size-1>).
            column (int): A column number (<0, size-1>).

        Returns:
            True if a row and column are in the correct range.

        Raises:
            AttributeError: Raise if row or column is outside <0, size-1> range.
        """
        if (0 <= row < self.size) and (0 <= column < self.size):
            return True
        else:
            raise AttributeError("Row or column out of range: <0,{}>, ({},{})".format(self.size - 1, row, column))

    def get_cell_value(self, row: int, column: int) -> int:
        """Return a value of a cell.

        Args:
            row (int): A row number.
            column (int): A column number.

        Returns:
            Value of a cell placed in [row, column].
        """
        if self._is_row_and_column_in_range(row, column):
            return self.cells[row][column].value

    def set_cell_value(self, row: int, column: int, value: int, method: str = ''):
        """Set a value of a cell. Remove the value from possible values of ranges that the cell belongs to (row, column,
        rectangle). Add action to _undo_redo.

        Args:
            row (int): A row number (<0, size-1>).
            column (int): A column number (<0, size-1>).
            value (int): Value to write to a cell.
            method (str): Optional method identifier. Defaults to ''.

        Raises:
            Attribute Error: Raise if:
            - editable attribute is False
            - value is not in a range <0, MAX_VALUE>
        """
        if self._is_row_and_column_in_range(row, column):
            cell = self.cells[row][column]
            old_value = cell.value
            cell.value = value
            self._remove_possible_value(cell, value)
            self._undo_redo.add_action(row, column, old_value, value, method)

    def _remove_possible_value(self, cell: Cell, value: int):
        """Remove value from cells' possible values in the same region as given cell (row, column, rectangle).

        Args:
            cell (Cell): Cell object.
            value (int): Value to remove from possible values.
        """
        for region in self._regions:
            region.remove_possible_value_if_cell_is_in_region(cell, value)

    def get_cell_possibilities(self, row: int, column: int) -> Set[int]:
        """Return a set of possible values that can be written to the cell from given row and column.

        Args:
            row (int): A row number (<0, size-1>).
            column (int):  A column number (<0, size-1>).

        Returns:
            Set[int]: Possible values that can be written to the cell.
        """
        if self._is_row_and_column_in_range(row, column):
            return self.cells[row][column].possible_values

    def is_editable(self, row: int, column: int) -> bool:
        """Check if a cell from given row and column is editable.

        Args:
            row: A row number (<0, size-1>).
            column: A column number (<0, size-1>).

        Returns:
             bool: True if the cell is editable.
        """
        if self._is_row_and_column_in_range:
            return self.cells[row][column].editable

    def update_possible_values_in_all_regions(self):
        """Update (refresh) possible values in all regions (meaning all cells).

        Use the function after modifying cell's value, clearing its value or undoing action.
        """
        for region in self._regions:
            region.update_possible_values()

    def is_solved(self) -> bool:
        """Check if Sudoku is solved.

        Returns:
            True if Sudoku is solved correctly. False otherwise.
        """
        for region in self._regions:
            if not region.is_solved():
                return False
        return True

    def is_wrong(self) -> bool:
        """Check if Sudoku is not possible to solve.

        Sudoku is not possible to solve if there is a region (row, column, rectangle) containing a cell with no value
        (zero) and zero possible values to write or if there are at least two cells with the same value.

        Returns:
             True if there is a region with no solution.
        """
        for region in self._regions:
            if region.is_not_possible_to_solve():
                return True
        return False

    def to_string(self) -> str:
        """Print Sudoku for diagnostic purpose.

        Returns:
            str: Diagnostic string.
        """
        sudoku = ""
        for row in self.cells:
            for cell in row:
                sudoku += str(cell.value)
            sudoku += "\n"
        return sudoku

    def copy_from(self, sudoku: 'Sudoku'):
        """Copy data from given argument 'sudoku' to current instance by repeating actions of sudoku's undo list.

        Args:
            sudoku (Sudoku): Sudoku instance to copy actions from.
        """
        for i in range(self._undo_redo.undo_length(), sudoku._undo_redo.undo_length()):
            row, column, old_value, value, method = sudoku._undo_redo._undo[i]
            self.set_cell_value(row, column, value, method)


class SudokuSolver(object):
    """Class holding sudoku board and solving it.

    Attributes:
        sudoku (Sudoku): Sudoku board.
        patterns (Pattern): List of patterns for solving sudoku board.
    """

    def __init__(self, sudoku: Sudoku = None):
        """Initiate a SudokuSolver with sudoku.

        Args:
            sudoku (Sudoku): Initiated sudoku object.
        """
        self.sudoku = sudoku
        self.patterns = Pattern.get_patterns_without_brute_force()

    def solve(self) -> bool:
        """Solve sudoku using patterns. If typical patterns do not solve sudoku, use Brute Force.

        Returns:
            bool: True if sudoku is solved. Otherwise sudoku is wrong.
        """
        restart = True
        while restart:
            restart = False
            for pattern in self.patterns:
                solve_again = pattern.solve(self.sudoku, False)
                if self.sudoku.is_solved():
                    restart = False
                    break
                elif solve_again:
                    restart = True

        # If not solved by means of typical patterns - use Brute Force.
        if not self.sudoku.is_solved():
            pattern = BruteForce()
            pattern.solve(self.sudoku, False)

        return self.sudoku.is_solved()

    def to_string(self) -> str:
        """Print Sudoku for diagnostic purpose.

        Returns:
            str: Diagnostic string.
        """
        return self.sudoku.to_string()


class Pattern(object):

    def solve(self, sudoku: Sudoku, solve_one: bool = False) -> bool:
        """Solve sudoku with a implemented pattern and return True if any Cell was changed. If not, return false.

        Args:
            sudoku (Sudoku): Sudoku class to which apply solution algorithm.
            solve_one (bool): If True, finish solving after modifying one Cell. Defaults to False.

        Returns:
            bool: Value determining if any Cell was modified. False means that algorithm is no longer able to find
            solution to any Cell.
        """
        return False

    def name(self) -> str:
        """Return a name of the pattern.

        Returns:
            str: Name of the pattern.
        """
        return self.__class__.__name__

    @staticmethod
    def get_patterns_without_brute_force() -> List['Pattern']:
        """Get a list of all patterns except Brute Force.

        Returns:
            List[Pattern]: A list of Pattern objects.
        """
        return [OnePossibility(), Exclusion()]

    @staticmethod
    def get_patterns_with_brute_force() -> List['Pattern']:
        """Get a list off all patterns (including Brute Force).

        Returns:
            List[Pattern]: A list of Pattern objects.
        """
        return [*Pattern.get_patterns_without_brute_force(), BruteForce()]


class OnePossibility(Pattern):
    """A class solving sudoku by One Possibility pattern. Extends Pattern class.

    The pattern looks for cells with only one possible value and writes it to the cell.
    """

    def solve(self, sudoku: Sudoku, solve_one: bool = False) -> bool:
        """Solve sudoku with OnePossibility pattern.

        The pattern goes through all the cells in sudoku and checks if there is only one possible value to write. If it
        is True then function writes that value to a cell. It checks following cells until the end unless argument
        solve_one is True. In this situation it finishes operating on sudoku after first write.

        Args:
            sudoku (Sudoku): Sudoku object to solve.
            solve_one (bool): Parameter to enable finishing function after writing one value to a cell.

        Returns:
            bool: True if functions wrote value to at least one cell.
        """
        size = sudoku.size
        was_changed = False
        for row in range(0, size):
            for column in range(0, size):
                possibilities = sudoku.get_cell_possibilities(row, column)
                if len(possibilities) == 1:
                    sudoku.set_cell_value(row, column, list(possibilities)[0], self.name())
                    was_changed = True
                    if solve_one:
                        return True
        return was_changed


class Exclusion(Pattern):
    """A class solving sudoku by Exclusion pattern. Extends Pattern class.

    The pattern checks cells in Region of sudoku and excludes possible values that exists in multiple cells. If there is
    remaining possible value it is written to the cell.
    """

    def solve(self, sudoku: Sudoku, solve_one=False) -> bool:
        """Solve sudoku with Exclusion pattern.

        The pattern checks cells in Region of sudoku. If there is a cell that has multiple possibilities but one of them
        does not exist in other cells then the function writes the possible value to the cell.

        Algorithm:
        Go through each region of the sudoku. Then go though each cell of the region. Check possible values of each
        cell. Update dictionary where a key is possible value and item is a tuple consisting of:
        - number of times each possible value exists in cells of the region,
        - a list of cells that have the possible value.

        After the region is checked and possible values are counted, go though the dictionary and check if there is
        the possible value that exists only in one cell. If it is present, write the value to the cell.

        Args:
            sudoku (Sudoku): Sudoku object to solve.
            solve_one (bool): Parameter to enable finishing function after writing one value to a cell.

        Returns:
            bool: True if functions wrote value to at least one cell.
        """
        count_possibilities_dict = dict()
        was_changed = False

        for region in sudoku.regions:
            count_possibilities_dict.clear()
            for cell in region.cells:
                for possible_value in cell.possible_values:
                    count, cells_list = count_possibilities_dict.get(possible_value, (0, []))
                    cells_list.append(cell)
                    count_possibilities_dict[possible_value] = ((count+1), cells_list)

            for value, (count, cells_list) in count_possibilities_dict.items():
                if count == 1:
                    sudoku.set_cell_value(cells_list[0].row, cells_list[0].column, value, self.name())
                    was_changed = True

        return was_changed


class BruteForce(Pattern):
    """A class solving sudoku by Brute Force (recursively). Extends Pattern class.

    Attributes:
        _root (SudokuNode): Object of internal class SudokuNode.
    """

    def __init__(self):
        self._root = None

    def solve(self, sudoku: Sudoku, solve_one=False) -> bool:
        """Solve sudoku by Brute Force (recursively).

        Algorithm:
        Create object of internal class SudokuNode as a root of recursive method. If the sudoku is not wrong call
        'solve' method the root object.

        Args:
            sudoku (Sudoku): Sudoku object to solve.
            solve_one (bool): Parameter to enable finishing function after writing one value to a cell.

        Returns:
            bool: True if sudoku was solved. Otherwise False.
        """
        self._root = self.SudokuNode(sudoku)
        self.SudokuNode.sudoku_solved = None
        if not sudoku.is_wrong():
            self._root.solve()
            if self.SudokuNode.sudoku_solved is not None:
                sudoku.copy_from(self.SudokuNode.sudoku_solved)
                return True
        return False

    class SudokuNode(object):
        """Class representing variation of sudoku as a node of the tree in a recursive method of solving sudoku.

        Class static attributes:
            sudoku_solved (Sudoku): Static object of Sudoku to which solved sudoku is written.
            patterns (List[Pattern]): Static list of patterns for solving sudoku.
            METHOD (str): Static string with the name of the method ('BruteForce')

        Attributes:
            _sudoku (Sudoku): Sudoku in a current node.
            _children (List[SudokuNode]): List of children SudokuNode objects for BruteForce.
        """

        sudoku_solved = None
        patterns = Pattern.get_patterns_without_brute_force()
        METHOD = 'BruteForce'

        def __init__(self, sudoku: Sudoku, row=-1, column=-1, value=-1):
            """Initiate the SudokuNode with sudoku and optional arguments for writing value to a cell.

            Write the value to a cell of row and column if the arguments are specified and different than -1.

            Args:
                  sudoku (Sudoku): Sudoku variation.
                  row (int): A row number of a cell to which value should be written. Defaults to -1.
                  column (int): A column number of a cell to which value should be written. Defaults to -1.
                  value (int): Value to write to a cell. Defaults to -1.
            """
            self._sudoku = copy.deepcopy(sudoku)
            self._children = []
            if row != -1 and column != -1 and value > 0:
                self._sudoku.set_cell_value(row, column, value, self.METHOD)

        def solve(self) -> bool:
            """Solve sudoku with BruteForce.

            Algorithm:
            First use typical patterns like OnePossibility and Exclusion in order to minimize recursion.

            If sudoku is solved - finish. If it is unsolvable return False.

            Go through each row and column and if there is a cell with no value (zero), create children, each with one
            of the possible values written to the cell.

            Go through children and call solve method.

            Returns:
                bool: True if sudoku is solved. Otherwise False.
            """
            for pattern in self.patterns:
                solve_again = True
                while solve_again:
                    solve_again = pattern.solve(self._sudoku, False)

            if self._sudoku.is_solved():
                BruteForce.SudokuNode.sudoku_solved = self._sudoku
                return True
            elif self._sudoku.is_wrong():
                return False

            is_done = False
            for row in range(self._sudoku.size):
                for column in range(self._sudoku.size):
                    if self._sudoku.get_cell_value(row, column) == 0:
                        for possibility in self._sudoku.get_cell_possibilities(row, column):
                            sudoku_node = BruteForce.SudokuNode(self._sudoku, row, column, possibility)
                            self._children.append(sudoku_node)
                        is_done = True
                        break
                if is_done:
                    break

            for child in self._children:
                return child.solve()
                # result = child.solve()
                # if result:
                #     return True


class SudokuFactory(object):
    """Sudoku factory class.

    Static attributes:
        POSSIBLE_SIZES (dict(int: Tuple(int, int))): dictionary holding possible sizes of Sudoku as keys and size of
        rectangle as values.
    """
    POSSIBLE_SIZES = {4: (2, 2), 6: (3, 2), 9: (3, 3)}

    @staticmethod
    def create_from_string(sudoku: str):
        """Create sudoku instance from multiline string.

        Correct format of sudoku is:
        '293040100
        516230740
        847156000
        354002690
        600415000
        000900000
        000394802
        000600005
        000521000'

        or:
        '134265
        526134
        243516
        615423
        461352
        352641'

        Args:
            sudoku (str): Sudoku written as a string.

        Raises:
            ValueError: raise if string is in incorrect format or size of sudoku is not included in POSSIBLE_SIZES.
        """
        lines = []
        for line in sudoku.splitlines():
            line = line.strip()
            if line.isdigit():
                lines.append(line)

        size = len(lines)
        for line in lines:
            if len(line) != size or size not in SudokuFactory.POSSIBLE_SIZES:
                raise ValueError("Incorrect input string")

        Cell.MAX_VALUE = size
        cells = [[None for _ in range(0, size)] for _ in range(0, size)]
        for row in range(0, size):
            for col in range(0, size):
                value = int(lines[row][col])
                cells[row][col] = Cell(row, col, False, value) if value else Cell(row, col)

        # is it ok to shorten it to:
        # cells = [[Cell(row, col, False, int(lines[row][col])) if int(lines[row][col])
        #           else Cell(row, col) for col in range(0, 9)] for row in range(0, 9)]
        return Sudoku(size=size, cells=cells, rect_width=SudokuFactory.POSSIBLE_SIZES[size][0],
                      rect_height=SudokuFactory.POSSIBLE_SIZES[size][1])


if __name__ == '__main__':
    sud = """
        293040100
        516230740
        847156000
        354002690
        600415000
        000900000
        000394802
        000600005
        000521000
        """
    sudoku = SudokuFactory.create_from_string(sud)
    sudoku_solver = SudokuSolver(sudoku)
    sudoku_solver.solve()
    print(sudoku_solver.to_string())
