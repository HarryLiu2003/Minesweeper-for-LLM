from src.game import MineField


class BoardUnderstandingPrompt:
    def __init__(
        self,
        unchecked_cell: str = "?",
        flag_cell: str = "F",
        empty_cell: str = ".",
        n_rows: int = 9,
        n_cols: int = 9,
        n_mines: int = 10,
        mine_field: MineField = None,
        represent_board_as_coordinates: bool = False,
        with_row_column_ids: bool = True,
    ):
        if mine_field is not None:
            self.unc = mine_field.unc
            self.flg = mine_field.flg
            self.emt = mine_field.emt
            self.n_rows = mine_field.n_rows
            self.n_cols = mine_field.n_cols
            self.n_mines = mine_field.n_mines
        else:
            self.unc: str = unchecked_cell
            self.flg: str = flag_cell
            self.emt: str = empty_cell
            self.n_rows: int = n_rows
            self.n_cols: int = n_cols
            self.n_mines: int = n_mines
        self.represent_board_as_coordinates = represent_board_as_coordinates
        self.with_row_column_ids = with_row_column_ids

    @property
    def desc(self):
        if not self.represent_board_as_coordinates:
            description = f"You will be presented with a {self.n_rows} by {self.n_cols} board for the Minesweeper game."
            if self.with_row_column_ids:
                description += f" The board is wrapped in a {self.n_rows+1} by {self.n_cols+1} table, where the first row and the first column with numbers in double quotation marks are the row and column indices."
            description += f" A coordinate (x,y) represents the cell at the x-th row and y-th column, where x and y, starting from 1, are the row and column indices, respectively."
            description += f""" The state of each cell is represented by the following symbols:
- `{self.emt}' represents a blank cell.
- `1' to `8' represents numbered cells with that number of mines in the adjacent cells.
- `{self.flg}' represents a flagged cell.
- `{self.unc}' represents an unopened cell.
"""
        else:
            description = f"You will be presented with a {self.n_rows} by {self.n_cols} board for the Minesweeper game, which is devided into cells."
            description += f' The cells are presented as "coordinate: state" mappings. A coordinate (x,y) represents the element at the x-th row and y-th column, where x and y, starting from 1, are the row and column indices, respectively.'
            description += f""" The state of each cell is represented by the following symbols:
- \"{self.emt}\" represents a blank cell.
- \"1\" to \"8\" represents numbered cells with that number of mines in the adjacent cells.
- \"{self.flg}\" represents a flagged cell.
- \"{self.unc}\" represents an unopened cell.
"""

        return description

    @property
    def navigation_example1(self):
        if self.with_row_column_ids:
            example = f"""--- PARTIAL BOARD ---
"0","1","2","3","4"
"1",`{self.unc}',`{self.unc}',`1',`{self.emt}'
"2",`{self.unc}',`{self.unc}',`3',`1'
"3",`{self.unc}',`{self.flg}',`2',`{self.flg}'
"4",`{self.unc}',`2',`2',`1'

QUESTION: What is the cell at coordinate (1,3)?
ANSWER: `1'
"""
        else:
            example = f"""--- PARTIAL BOARD ---
`{self.unc}',`{self.unc}',`1',`{self.emt}'
`{self.unc}',`{self.unc}',`3',`1'
`{self.unc}',`{self.flg}',`2',`{self.flg}'
`{self.unc}',`2',`2',`1'

QUESTION: What is the cell at coordinate (1,3)?
ANSWER: `1'
"""
        return example

    @property
    def navigation_dict_example1(self):
        example = f"""--- PARTIAL BOARD ---
(1,1): {self.unc}
(1,2): {self.unc}
(1,3): {self.unc}
(1,4): {self.unc}
(2,1): {self.unc}
(2,2): {self.unc}
(2,3): {self.unc}
(2,4): {self.unc}
(3,1): {self.unc}
(3,2): {self.unc}
(3,3): {self.unc}
(3,4): 1
(4,1): {self.unc}
(4,2): {self.unc}
(4,3): {self.unc}
(4,4): 1

QUESTION: What is the cell at coordinate (3,4)?
ANSWER: \"1\""
"""
        return example

    @property
    def navigation_example2(self):
        return f"""--- PARTIAL BOARD ---
"0","1","2","3","4"
"1",`{self.unc}',`{self.unc}',`1',`{self.emt}'
"2",`{self.unc}',`{self.unc}',`3',`1'
"3",`{self.unc}',`{self.flg}',`2',`{self.flg}'
"4",`{self.unc}',`2',`2',`1'

QUESTION: What is the cell at coordinate (4,1)?
ANSWER: `{self.unc}'
"""

    @property
    def counting_example1(self):
        return f"""--- PARTIAL BOARD ---
"0","1","2","3","4","5"
"1",`{self.unc}',`{self.unc}',`{self.unc}',`{self.unc}',`{self.unc}'
"2",`{self.unc}',`{self.unc}',`{self.unc}',`{self.unc}',`{self.unc}'
"3",`{self.unc}',`{self.unc}',`{self.unc}',`1',`1'
"4",`{self.unc}',`{self.unc}',`{self.unc}',`1',`{self.emt}'
"5",`{self.unc}',`{self.unc}',`{self.unc}',`1',`{self.emt}'

QUESTION: How many cells `{self.flg}' are neighbors (including diagonal) of the cell with coordinate (2,1)?
ANSWER:

To find out how many cells with the value `1' are neighbors of the cell with coordinate (2,1), we need to look at the 8 neighboring cells of (2,1). These coordinates are:
(1,1), (1,2), (3,1), (3,2), (2,2).

Now, we will check the values of these cells on the given Minesweeper board:

(1,1) = `{self.unc}'
(1,2) = `{self.unc}'
(3,1) = `{self.unc}'
(3,2) = `{self.unc}'
(2,2) = `{self.unc}'

All of these neighboring cells are `{self.unc}'. So, the number of cells with `1' that are neighbors of the cell (2,1) is:

ANSWER: 0.
"""

    @property
    def counting_dict_example1(self):
        example = f"""--- PARTIAL BOARD ---
(1,1): {self.flg}
(1,2): {self.unc}
(1,3): {self.unc}
(1,4): {self.flg}
(2,1): {self.unc}
(2,2): {self.unc}
(2,3): {self.unc}
(2,4): {self.unc}
(3,1): {self.unc}
(3,2): {self.flg}
(3,3): {self.unc}
(3,4): 1
(4,1): {self.unc}
(4,2): {self.unc}
(4,3): {self.unc}
(4,4): 1

QUESTION: How many cells \"{self.flg}\" are neighboring (including diagonally) the cell with coordinates (2,1)?
Let's think step by step
ANSWER:

To find out how many cells with the value \"1\" are neighbors of the cell with coordinate (2,1), we need to look at the 8 neighboring cells of (2,1). These coordinates are:
(1,1), (1,2), (3,1), (3,2), (2,2).

Now, we will check the values of these cells on the given Minesweeper board:

(1,1) = {self.flg}
(1,2) = {self.unc}
(3,1) = {self.unc}
(3,2) = {self.flg}
(2,2) = {self.unc}

From of these neighboring cells (1,1) and (3,2) are \"{self.flg}\". So, the number of cells with \"1\" that are neighbors of the cell (2,1) is:

ANSWER: 2.
"""
        return example
