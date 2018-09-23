import unittest
from sudoku import *


class CellTests(unittest.TestCase):
    def set_up(self):
        pass

    def test_cell_not_editable_and_value_0(self):
        with self.assertRaises(AttributeError) as cm:
            cell = Cell(0, 0, 9, editable=False, value=0)

        self.assertTrue("Cell not editable and without value" in str(cm.exception))

    def test_cell_value_below_0(self):
        max_value = 9
        with self.assertRaises(AttributeError) as cm:
            cell = Cell(0, 0, max_value, value=-1)

        self.assertTrue("Incorrect value (-1 not in <0,{}>)".format(max_value) in str(cm.exception))

    def test_cell_value_over_MAX(self):
        max_value = 9
        with self.assertRaises(AttributeError) as cm:
            cell = Cell(0, 0, max_value, value=max_value+1)

        self.assertTrue("Incorrect value ({} not in <0,{}>)".format(max_value+1, max_value) in str(cm.exception))

    def test_cell_not_editable_and_correct_value(self):
        cell = Cell(0, 0, 9, editable=False, value=1)
        self.assertFalse(cell.editable)
        self.assertEqual(cell.value, 1)
        self.assertTrue(cell.possible_values == set())

    def test_cell_editable_and_correct_value(self):
        max_value = 9
        cell = Cell(0, 0, max_value, editable=True, value=1)
        self.assertTrue(cell.editable)
        self.assertEqual(cell.value, 1)
        self.assertTrue(cell.possible_values == set(range(1, max_value + 1)))

    def test_cell_set_value(self):
        cell = Cell(0, 0, 9, editable=True, value=0)
        cell.value = 1
        self.assertEqual(cell.value, 1)

    def test_cell_not_editable_set_value(self):
        cell = Cell(0, 0, 9, editable=False, value=1)
        with self.assertRaises(AttributeError) as cm:
            cell.value = 2
        self.assertTrue("Cell not editable" in str(cm.exception))

    def test_cell_set_incorrect_value(self):
        max_value = 9
        incorrect_values = [-1]

        for v in incorrect_values:
            cell = Cell(0, 0, max_value, editable=True, value=1)
            with self.assertRaises(AttributeError) as cm:
                cell.value = v

            msg = "Value below 0"
            self.assertTrue(msg in str(cm.exception))

    def test_clear_value(self):
        cell = Cell(0, 0, 9, editable=True, value=1)
        self.assertEqual(cell.value, 1)
        cell.clear()
        self.assertEqual(cell.value, 0)

    def test_cell_not_editable_clear_value(self):
        cell = Cell(0, 0, 9, editable=False, value=1)
        self.assertEqual(cell.value, 1)
        cell.clear()
        self.assertEqual(cell.value, 1)

    def test_cell_possible_values(self):
        max_value = 9
        cell = Cell(0, 0, max_value, editable=True, value=0)
        possible_values = set(range(1, max_value + 1))
        self.assertEqual(cell.possible_values, possible_values)
        cell.value = 1
        self.assertEqual(cell.possible_values, set())
        cell.value = 0
        cell.init_possible_values(max_value)
        self.assertEqual(cell.possible_values, possible_values)

    def test_intersect_possible_values(self):
        max_value = 9
        cell = Cell(0, 0, max_value, True, 0)
        intersect_values = set(range(1, max_value + 1))
        self.assertEqual(cell.possible_values, intersect_values)

        intersect_values.remove(1)
        cell.intersect_possible_values(intersect_values)
        self.assertEqual(cell.possible_values, intersect_values)

        intersect_values.remove(2)
        cell.intersect_possible_values(intersect_values)
        self.assertEqual(cell.possible_values, intersect_values)

        intersect_values.remove(3)
        cell.intersect_possible_values(intersect_values)
        self.assertEqual(cell.possible_values, intersect_values)

        cell.init_possible_values(max_value)
        self.assertEqual(cell.possible_values, set(range(1, max_value + 1)))

    def test_remove_possible_value(self):
        max_value = 9
        cell = Cell(0, 0, max_value, True, 0)
        self.assertEqual(cell.possible_values, set(range(1, max_value + 1)))
        cell.remove_possible_value(1)
        self.assertEqual(cell.possible_values, set(range(2, max_value + 1)))


class RegionTest(unittest.TestCase):
    def SetUp(self):
        pass

    def test_init(self):
        region = Region()
        self.assertEqual(region.cells, [])

    def test_add_cell(self):
        region = Region()
        cell_1 = Cell(0, 0, True, 0)
        cell_2 = Cell(0, 0, True, 0)
        region.add(cell_1)
        self.assertEqual(region.cells, [cell_1])
        self.assertNotEqual(region.cells, [cell_2])

    def test_remove_possible_values_if_cell_is_in_region(self):
        max_value = 9
        region = Region()
        cell_1 = Cell(0, 0, max_value, True, 0)
        cell_2 = Cell(0, 0, max_value, True, 0)
        region.add(cell_1)

        possible_values = set(range(1, max_value + 1))
        possible_values_without_1 = set(range(2, max_value + 1))

        self.assertEqual(cell_1.possible_values, possible_values)
        self.assertEqual(cell_1.possible_values, possible_values)

        region.remove_possible_value_if_cell_is_in_region(cell_1, 1)
        self.assertNotEqual(cell_1, possible_values)
        self.assertEqual(cell_1.possible_values, possible_values_without_1)

        region.remove_possible_value_if_cell_is_in_region(cell_2, 1)
        self.assertEqual(cell_2.possible_values, possible_values)
        region.remove_possible_value_if_cell_is_in_region(cell_2, 2)
        self.assertEqual(cell_2.possible_values, possible_values)
        self.assertEqual(cell_1.possible_values, possible_values_without_1)

    def test_update_possible_values(self):
        max_value = 9
        region = Region()
        cells = [Cell(0, 0, max_value, True, 0), Cell(0, 1, max_value, True, 0),
                 Cell(0, 2, max_value, True, 0), Cell(0, 3, max_value, False, 1)]
        count = len(cells)
        for cell in cells:
            region.add(cell)

        region.update_possible_values()
        for cell in region.cells:
            if cell.value == 0:
                self.assertEqual(cell.possible_values, set(range(2, count+1)))
            else:
                self.assertEqual(cell.possible_values, set())

    def test_is_not_solved(self):
        max_value = 9
        region = Region()
        cells = [Cell(0, 0, max_value, True, 0), Cell(0, 1, max_value, True, 2),
                 Cell(0, 2, max_value, True, 3), Cell(0, 3, max_value, False, 4)]
        for cell in cells:
            region.add(cell)
        self.assertFalse(region.is_solved())

    def test_is_solved(self):
        max_value = 9
        region = Region()
        cells = [Cell(0, 0, max_value, True, 1), Cell(0, 1, max_value, True, 2),
                 Cell(0, 2, max_value, True, 3), Cell(0, 3, max_value, False, 4)]
        for cell in cells:
            region.add(cell)
        self.assertTrue(region.is_solved())

    def test_is_wrong(self):
        max_value = 9
        region = Region()
        cells = [Cell(0, 0, max_value, True, 2), Cell(0, 1, max_value, True, 2),
                 Cell(0, 2, max_value, True, 3), Cell(0, 3, max_value, False, 4)]
        for cell in cells:
            region.add(cell)
        self.assertFalse(region.is_solved())

    def test_is_not_possible_to_solve(self):
        max_value = 9
        region = Region()
        cells = [Cell(0, 0, max_value, True, 0), Cell(0, 1, max_value, True, 2),
                 Cell(0, 2, max_value, True, 3), Cell(0, 3, max_value, False, 4)]
        for cell in cells:
            region.add(cell)
        cell = region.cells[0]
        cell.intersect_possible_values(set())
        self.assertTrue(region.is_not_possible_to_solve())


class UndoRedoTest(unittest.TestCase):

    def test_action_added(self):
        row = 1
        column = 2
        old_value = 0
        value = 3
        method = 'manual'
        undo_redo = UndoRedo()

        undo_redo.add_action(row, column, old_value, value, method)
        self.assertTrue(undo_redo.undo_length() == 1)

        action = (1, 3, 0, 4, 'manual')
        undo_redo.add_action(*action)
        self.assertTrue(undo_redo.undo_length() == 2)

    def test_undo_redo(self):
        undo_redo = UndoRedo()
        action_1 = (1, 2, 3, 4, 'manual')
        action_2 = (2, 3, 4, 5, 'manually')
        undo_redo.add_action(*action_1)
        undo_redo.add_action(*action_2)

        self.assertTrue(undo_redo.undo_length() == 2)
        self.assertTrue(undo_redo.redo_length() == 0)

        row, column, old_value, value, method, undo_length, redo_length = undo_redo.undo()
        self.assertEqual(row, 2)
        self.assertEqual(column, 3)
        self.assertEqual(old_value, 4)
        self.assertEqual(value, 5)
        self.assertEqual(method, 'manually')
        self.assertEqual(undo_length, 1)
        self.assertEqual(redo_length, 1)

        row, column, old_value, value, method, undo_length, redo_length = undo_redo.undo()
        self.assertEqual(row, 1)
        self.assertEqual(column, 2)
        self.assertEqual(old_value, 3)
        self.assertEqual(value, 4)
        self.assertEqual(method, 'manual')
        self.assertEqual(undo_length, 0)
        self.assertEqual(redo_length, 2)

        row, column, old_value, value, method, undo_length, redo_length = undo_redo.redo()
        self.assertEqual(row, 1)
        self.assertEqual(column, 2)
        self.assertEqual(old_value, 3)
        self.assertEqual(value, 4)
        self.assertEqual(method, 'manual')
        self.assertEqual(undo_length, 1)
        self.assertEqual(redo_length, 1)

        row, column, old_value, value, method, undo_length, redo_length = undo_redo.redo()
        self.assertEqual(row, 2)
        self.assertEqual(column, 3)
        self.assertEqual(old_value, 4)
        self.assertEqual(value, 5)
        self.assertEqual(method, 'manually')
        self.assertEqual(undo_length, 2)
        self.assertEqual(redo_length, 0)


class SudokuTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_empty_sudoku(self):
        sudoku = Sudoku()
        for row in sudoku.cells:
            for cell in row:
                self.assertTrue(cell.editable)
                self.assertEqual(cell.value, 0)

    def test_creation_of_sudoku_from_cells(self):
        max_value = 9
        cells = [[Cell(x, y, max_value, editable=False, value=x+1) if x == y
                  else Cell(x, y, max_value) for x in range(9)] for y in range(9)]
        sudoku = Sudoku(cells=cells)

        for r in range(len(sudoku.cells)):
            for c in range(len(sudoku.cells[0])):
                if r == c:
                    self.assertFalse(sudoku.cells[r][c].editable)
                    self.assertEqual(sudoku.cells[r][c].value, r + 1)
                else:
                    self.assertTrue(sudoku.cells[r][c].editable)
                    self.assertEqual(sudoku.cells[r][c].value, 0)

    def test_get_cell_value(self):
        max_value = 9
        cells = [[Cell(x, y, max_value, editable=False, value=x+1) if x == y
                  else Cell(x, y, max_value) for x in range(9)] for y in range(9)]
        sudoku = Sudoku(cells=cells)

        self.assertEqual(sudoku.get_cell_value(3, 3), 4)
        self.assertEqual(sudoku.get_cell_value(3, 4), 0)

    def test_get_cell_value_index_out_of_range(self):
        sudoku = Sudoku()
        with self.assertRaises(AttributeError) as cm:
            sudoku.get_cell_value(0, -1)

        self.assertTrue("Row or column out of range: <0,{}>".format(sudoku.size - 1) in str(cm.exception))

    def test_editable(self):
        max_value = 9
        cells = [[Cell(x, y, max_value, editable=False, value=x+1) if x == y
                  else Cell(x, y, max_value) for x in range(9)] for y in range(9)]
        sudoku = Sudoku(cells=cells)

        rang = range(len(cells))
        for row in rang:
            for col in rang:
                if row == col:
                    self.assertFalse(sudoku.is_editable(row, col))
                else:
                    self.assertTrue(sudoku.is_editable(row, col))

    def test_set_cell_value(self):
        sudoku = Sudoku()
        size = sudoku.size
        with self.assertRaises(AttributeError) as cm:
            sudoku.set_cell_value(0, 0, size+1)
        msg = "Incorrect value: {}, max: {}".format(size+1, size)
        self.assertTrue(msg in str(cm.exception))

        with self.assertRaises(AttributeError) as cm:
            sudoku.set_cell_value(0, 0, -1)
        msg = "Incorrect value: {}, max: {}".format(-1, size)
        self.assertTrue(msg in str(cm.exception))

    def test_solve(self):
        sudoku = Sudoku()

        sudoku.set_cell_value(0, 0, 1)
        sudoku.set_cell_value(0, 5, 8)
        sudoku.set_cell_value(0, 6, 4)

        sudoku.set_cell_value(1, 1, 2)
        sudoku.set_cell_value(1, 5, 4)
        sudoku.set_cell_value(1, 6, 9)

        sudoku.set_cell_value(2, 0, 9)
        sudoku.set_cell_value(2, 2, 3)
        sudoku.set_cell_value(2, 3, 2)
        sudoku.set_cell_value(2, 4, 5)
        sudoku.set_cell_value(2, 5, 6)

        sudoku.set_cell_value(3, 0, 6)
        sudoku.set_cell_value(3, 6, 5)
        sudoku.set_cell_value(3, 7, 7)
        sudoku.set_cell_value(3, 8, 1)

        sudoku.set_cell_value(4, 0, 4)
        sudoku.set_cell_value(4, 1, 1)
        sudoku.set_cell_value(4, 3, 8)
        sudoku.set_cell_value(4, 5, 5)
        sudoku.set_cell_value(4, 7, 6)
        sudoku.set_cell_value(4, 8, 2)

        sudoku.set_cell_value(5, 0, 5)
        sudoku.set_cell_value(5, 1, 3)
        sudoku.set_cell_value(5, 2, 2)
        sudoku.set_cell_value(5, 8, 4)

        sudoku.set_cell_value(6, 3, 5)
        sudoku.set_cell_value(6, 4, 8)
        sudoku.set_cell_value(6, 5, 2)
        sudoku.set_cell_value(6, 6, 7)
        sudoku.set_cell_value(6, 8, 9)

        sudoku.set_cell_value(7, 2, 1)
        sudoku.set_cell_value(7, 3, 3)
        sudoku.set_cell_value(7, 7, 4)

        sudoku.set_cell_value(8, 2, 8)
        sudoku.set_cell_value(8, 3, 1)
        sudoku.set_cell_value(8, 8, 5)

        puzzle = """100008400
        020004900
        903256000
        600000571
        410805062
        532000004
        000582709
        001300040
        008100005       
        """.replace(' ', '')
        self.assertEqual(sudoku.to_string(), puzzle)

        solver = SudokuSolver(sudoku)
        solver.solve()

        solution = """175938426
        826714953
        943256187
        689423571
        417895362
        532671894
        364582719
        751369248
        298147635
        """.replace(' ', '')

        self.assertEqual(solver.sudoku.to_string(), solution)

    def test_solve2(self):
        sudoku = Sudoku()

        sudoku.set_cell_value(0, 0, 1)
        sudoku.set_cell_value(0, 5, 8)
        sudoku.set_cell_value(0, 6, 4)

        sudoku.set_cell_value(1, 1, 2)
        sudoku.set_cell_value(1, 5, 4)
        sudoku.set_cell_value(1, 6, 9)

        sudoku.set_cell_value(2, 0, 9)
        sudoku.set_cell_value(2, 2, 3)
        sudoku.set_cell_value(2, 3, 2)
        sudoku.set_cell_value(2, 4, 5)
        sudoku.set_cell_value(2, 5, 6)

        sudoku.set_cell_value(3, 0, 6)
        sudoku.set_cell_value(3, 6, 5)
        sudoku.set_cell_value(3, 7, 7)
        sudoku.set_cell_value(3, 8, 1)

        sudoku.set_cell_value(4, 0, 4)
        sudoku.set_cell_value(4, 1, 1)
        sudoku.set_cell_value(4, 3, 8)
        sudoku.set_cell_value(4, 5, 5)
        sudoku.set_cell_value(4, 7, 6)
        sudoku.set_cell_value(4, 8, 2)

        sudoku.set_cell_value(5, 0, 5)
        sudoku.set_cell_value(5, 1, 3)
        sudoku.set_cell_value(5, 2, 2)
        sudoku.set_cell_value(5, 8, 4)

        sudoku.set_cell_value(6, 3, 5)
        sudoku.set_cell_value(6, 4, 8)
        sudoku.set_cell_value(6, 5, 2)
        sudoku.set_cell_value(6, 6, 7)
        sudoku.set_cell_value(6, 8, 9)

        sudoku.set_cell_value(7, 2, 1)
        sudoku.set_cell_value(7, 3, 3)
        sudoku.set_cell_value(7, 7, 4)

        sudoku.set_cell_value(8, 2, 8)
        sudoku.set_cell_value(8, 3, 1)
        sudoku.set_cell_value(8, 8, 5)

        puzzle = """100008400
        020004900
        903256000
        600000571
        410805062
        532000004
        000582709
        001300040
        008100005
        """.replace(' ', '')
        self.assertEqual(sudoku.to_string(), puzzle)

        solver = SudokuSolver(sudoku)
        solver.solve()

        solution = """175938426
        826714953
        943256187
        689423571
        417895362
        532671894
        364582719
        751369248
        298147635
        """.replace(' ', '')
        self.assertEqual(solver.sudoku.to_string(), solution)

    def test_solve3(self):
        puzzle = """
        293040100
        516230740
        847156000
        354002690
        600415000
        000900000
        000394802
        000600005
        000521000
        """.replace(' ', '').replace('\n', '', 1)

        sudoku = SudokuFactory.create_from_string(puzzle)
        self.assertEqual(sudoku.to_string(), puzzle)

        solver = SudokuSolver(sudoku)
        solver.solve()
        solution = """
        293847156
        516239748
        847156923
        354782691
        689415237
        721963584
        165394872
        932678415
        478521369
        """.replace(' ', '').replace('\n', '', 1)
        self.assertEqual(solver.sudoku.to_string(), solution)

    def test_solve_6x6(self):
        puzzle = """
        100000
        020000
        003000
        000400
        000050
        000000
        """.replace(' ', '').replace('\n', '', 1)
        sudoku = SudokuFactory.create_from_string(puzzle)
        self.assertEqual(sudoku.to_string(), puzzle)

        solver = SudokuSolver(sudoku)
        solver.solve()
        solution = """
        134265
        526134
        243516
        615423
        461352
        352641
        """.replace(' ', '').replace('\n', '', 1)
        self.assertEqual(solver.sudoku.to_string(), solution)

    def test_solve_4x4(self):
        puzzle = """
        1000
        0200
        0030
        0004
        """.replace(' ', '').replace('\n', '', 1)
        sudoku = SudokuFactory.create_from_string(puzzle)
        self.assertEqual(sudoku.to_string(), puzzle)

        solver = SudokuSolver(sudoku)
        solver.solve()
        solution = """
        1342
        4213
        2431
        3124
        """.replace(' ', '').replace('\n', '', 1)
        self.assertEqual(solver.sudoku.to_string(), solution)


if __name__ == '__main__':
    unittest.main()
