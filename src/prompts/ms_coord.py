"""
# Author: Yinghao Li
# Modified: February 19th, 2024
# ---------------------------------------
# Description: Macro description of the game.
"""

import math
from src.game import MineField


class GamePlayCoordinatePrompt:
    def __init__(
        self,
        unchecked_cell: str = "?",
        flag_cell: str = "F",
        empty_cell: str = ".",
        number_cells: list[str] = None,
        n_rows: int = 9,
        n_cols: int = 9,
        n_mines: int = 10,
        mine_field: MineField = None,
        **kwargs,
    ):
        if number_cells is not None:
            assert len(number_cells) == 8, "Number cells should have 8 elements."

        if mine_field is not None:
            self.unc = mine_field.unc
            self.flg = mine_field.flg
            self.emt = mine_field.emt
            self.nums = mine_field.nums_disp
            self.n_rows = mine_field.n_rows
            self.n_cols = mine_field.n_cols
            self.n_mines = mine_field.n_mines
        else:
            self.unc: str = unchecked_cell
            self.flg: str = flag_cell
            self.emt: str = empty_cell
            self.nums: list[str] = (
                number_cells if number_cells is not None else ["1", "2", "3", "4", "5", "6", "7", "8"]
            )
            self.n_rows: int = n_rows
            self.n_cols: int = n_cols
            self.n_mines: int = n_mines
        self.nums_str = ",".join([f'"{n}"' for n in self.nums])

    @property
    def wiki_game(self):
        desc = f"""--- MINESWEEPER INTRODUCTION ---
In Minesweeper, {self.n_mines} hidden mines are scattered throughout a {self.n_rows} by {self.n_cols} board, which is divided into cells."""

        desc += f' The cells are presented as "coordinate: state" mappings. A coordinate (x,y) represents the element at the x-th row and y-th column in the board, where x and y, starting from 1, are the row and column indices, respectively.'

        desc += f""" Cells have multiple possible states:
- Unopened cells (represented by \"{self.unc}\", which cover the board at the start of the game, can also be made by removing flags)
- Numbered cells (represented by {self.nums_str}, which indicate the number of mines in the eight neighboring cells, including those diagonally adjacent)
- Blank cells (represented by \"{self.emt}\", which have no neighboring mines)
- Flagged cells (represented by \"{self.flg}\", which are marked by the player to indicate a potential mine location)

A player selects a cell to open it. If a player opens a cell containing a mine, the game ends in a loss. Otherwise, the opened cell displays either a number, indicating the number of mines diagonally and/or adjacent to it, or a blank tile (sometimes shown as a 0), and all adjacent cells will automatically be opened. To win a game of Minesweeper, all non-mine cells must be opened without opening a mine.
"""
        return desc

    @property
    def action_options(self):
        desc = f"""--- ACTION OPTIONS ---
There are three permissible actions in Minesweeper:

- Left-click an unopened cell (\"{self.unc}\") to reveal it.
- Right-click an unopened cell (\"{self.unc}\") to place a flag or a flagged cell (\"{self.flg}\") to remove the flag.
- Middle-click on a numbered cell ({self.nums_str}) to unveil its neighboring cells, but only if all adjacent mines have been correctly flagged. If any flags are misplaced, you'll lose the game.
"""
        return desc

    @property
    def action_format(self):
        desc = f"""--- ACTION FORMAT ---
Each of your actions should be formatted as \"A(row,col)\", where:
- \"A\" represents the action type: \"L\" denotes a left-click, \"R\" indicates a right-click, and \"M\" signifies a middle-click.
- \"row\" specifies the row number of the targeted cell.
- \"col\" details the column number of the targeted cell.
For instance, an action like \"L(1,2)\" translates to a left-click on the cell located at the first row and second column.
"""
        return desc

    @property
    def action_regulation(self):
        desc = f"""please ensure:
- You do not duplicate actions.
- You submit only one action at a time.
"""
        return desc

    @property
    def init_response_guide(self):
        desc = f"""--- RESPONSE GUIDE ---
Let's think step by step.

Begin by detailing your rationale in the \"REASONING\" section, followed by specifying your move using the previously mentioned format in the \"ACTION\" section. Ensure your reasoning doesn't exceed 200 words. To commence the game, left-click the center cell at ({math.ceil(self.n_rows/2)}, {math.ceil(self.n_cols/2)}).

REASONING:
ACTION:
"""
        return desc

    @property
    def response_guide(self):
        desc = f"""--- RESPONSE GUIDE ---
Let's think step by step.

Begin by detailing your rationale in the \"REASONING\" section, followed by specifying your move using the previously mentioned format in the \"ACTION\" section. Ensure your reasoning doesn't exceed 200 words.

REASONING:
ACTION:
"""
        return desc

    @property
    def example_1(self):
        desc = f"""Example 1:
Notice that the board is displayed in partial.

--- BOARD ---
(1,1): {self.emt}
(1,2): {self.nums[0]}
(1,3): {self.unc}
(1,4): {self.unc}
(2,1): {self.emt}
(2,2): {self.nums[0]}
(2,3): {self.unc}
(2,4): {self.unc}
(3,1): {self.emt}
(3,2): {self.nums[0]}
(3,3): {self.nums[1]}
(3,4): {self.nums[3]}
(4,1): {self.emt}
(4,2): {self.emt}
(4,3): {self.emt}
(4,4): {self.nums[1]}

REASONING: The cell located at (3,2) displays the number \"{self.nums[0]}\", indicating there's a single mine in its neighboring cells. Among these neighbors, 7 are opened as empty or numbered, and only one remains unopened at (2,3). Given that there's just one adjacent mine, it's logical to deduce that the unopened cell at (2,3) contains the mine. Thus, our next move is to flag the cell at (2,3) with a right-click.

ACTION: R(2,3)
"""
        return desc

    @property
    def example_2(self):
        desc = f"""Example 2:
Notice that the board is displayed in partial.

--- BOARD ---
(1,4): {self.emt}
(1,5): {self.nums[0]}
(1,6): {self.unc}
(1,7): {self.unc}
(2,4): {self.emt}
(2,5): {self.nums[0]}
(2,6): {self.flg}
(2,7): {self.unc}
(3,4): {self.emt}
(3,5): {self.nums[0]}
(3,6): {self.nums[1]}
(3,7): {self.nums[3]}
(4,4): {self.emt}
(4,5): {self.emt}
(4,6): {self.emt}
(4,7): {self.nums[1]}

REASONING: The cell at (1,5) displays the number \"{self.nums[0]}\", indicating a single adjacent mine. Upon examining its neighboring cells, only the cell at (2,6) is flagged with \"{self.flg}\". This suggests that all mines neighboring (1,5) have been identified. Consequently, we can safely unveil the other surrounding cells by middle-clicking on (1,5).

ACTION: M(1,5)
"""
        return desc

    @property
    def example_3(self):
        desc = f"""Example 3:
Notice that the board is displayed in partial.

--- BOARD ---
(1,1): {self.nums[0]}
(1,2): {self.nums[0]}
(1,3): {self.nums[1]}
(1,4): {self.unc}
(2,1): {self.unc}
(2,2): {self.unc}
(2,3): {self.unc}
(2,4): {self.unc}
(3,1): {self.unc}
(3,2): {self.unc}
(3,3): {self.unc}
(3,4): {self.unc}

REASONING: The cell at (1,1) indicates there's a single mine amongst its neighbors. Examining the cells adjacent to it, both (2,1) and (2,2) remain unopened, implying one of them contains a mine. Similarly, the cell at (1,2) displays a \"{self.nums[0]}\", suggesting that out of (2,1), (2,2), and (2,3), one holds a mine. Since one of (2,1) or (2,2) already contains a mine, it becomes evident that (2,3) is mine-free. We can then safely uncover (2,3) with a left-click.

ACTION: L(2,3)
"""
        return desc
