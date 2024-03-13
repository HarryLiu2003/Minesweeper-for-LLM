"""
# Author: Yinghao Li
# Modified: February 19th, 2024
# ---------------------------------------
# Description: Macro description of the game.
"""

import math
from src.game import MineField, ActionFeedback


class GamePlayTablePrompt:
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
        with_row_column_ids: bool = True,
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
        self.with_row_column_ids = with_row_column_ids
        self.nums_str = ",".join([f"`{n}'" for n in self.nums])

    @property
    def wiki_game(self):
        desc = f"""--- MINESWEEPER INTRODUCTION ---
In Minesweeper, {self.n_mines} hidden mines are scattered throughout a {self.n_rows} by {self.n_cols} board, which is divided into cells."""
        desc += " The rows are seperated by newlines, and columns by commas."

        if self.with_row_column_ids:
            desc += f" The board is structured as a {self.n_rows+1} by {self.n_cols+1} table, with the first row and column labeled using numbers in double quotation marks to indicate row and column indices."

        desc += f""" Cells have multiple possible states:
- Unopened cells (represented by `{self.unc}', which cover the board at the start of the game, can also be made by removing flags)
- Numbered cells (represented by {self.nums_str}, which indicate the number of mines in the eight neighboring cells, including those diagonally adjacent)
- Blank cells (represented by `{self.emt}', which have no neighboring mines)
- Flagged cells (represented by `{self.flg}', which are marked by the player to indicate a potential mine location)

A player selects a cell to open it. If a player opens a cell containing a mine, the game ends in a loss. Otherwise, the opened cell displays either a number, indicating the number of mines diagonally and/or adjacent to it, or a blank tile (sometimes shown as a 0), and all adjacent cells will automatically be opened. To win a game of Minesweeper, all non-mine cells must be opened without opening a mine.
"""
        return desc

    @property
    def action_options(self):
        desc = f"""--- ACTION OPTIONS ---
There are three permissible actions in Minesweeper:

- Left-click an unopened cell (`{self.unc}') to reveal it.
- Right-click an unopened cell (`{self.unc}') to place a flag or a flagged cell (`{self.flg}') to remove the flag.
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
"0","1","2","3","4"
"1",`{self.emt}',`{self.nums[0]}',`{self.unc}',`{self.unc}'
"2",`{self.emt}',`{self.nums[0]}',`{self.unc}',`{self.unc}'
"3",`{self.emt}',`{self.nums[0]}',`{self.nums[1]}',`{self.nums[3]}'
"4",`{self.emt}',`{self.emt}',`{self.emt}',`{self.nums[1]}'

REASONING: The cell located at (3,2) displays the number `{self.nums[0]}', indicating there's a single mine in its neighboring cells. Among these neighbors, 7 are opened as empty or numbered, and only one remains unopened at (2,3). Given that there's just one adjacent mine, it's logical to deduce that the unopened cell at (2,3) contains the mine. Thus, our next move is to flag the cell at (2,3) with a right-click.

ACTION: R(2,3)
"""
        return desc

    @property
    def example_2(self):
        desc = f"""Example 2:
Notice that the board is displayed in partial.

--- BOARD ---
"0","4","5","6","7"
"1",`{self.emt}',`{self.nums[0]}',`{self.unc}',`{self.unc}'
"2",`{self.emt}',`{self.nums[0]}',`{self.flg}',`{self.unc}'
"3",`{self.emt}',`{self.nums[0]}',`{self.nums[1]}',`{self.nums[3]}'
"4",`{self.emt}',`{self.emt}',`{self.emt}',`{self.nums[1]}'

REASONING: The cell at (1,5) displays the number `{self.nums[0]}', indicating a single adjacent mine. Upon examining its neighboring cells, only the cell at (2,6) is flagged with `{self.flg}'. This suggests that all mines neighboring (1,5) have been identified. Consequently, we can safely unveil the other surrounding cells by middle-clicking on (1,5).

ACTION: M(1,5)
"""
        return desc

    @property
    def example_3(self):
        desc = f"""Example 3:
Notice that the board is displayed in partial.

--- BOARD ---
"0","1","2","3","4"
"1",`{self.nums[0]}',`{self.nums[0]}',`{self.nums[1]}',`{self.unc}'
"2",`{self.unc}',`{self.unc}',`{self.unc}',`{self.unc}'
"3",`{self.unc}',`{self.unc}',`{self.unc}',`{self.unc}'

REASONING: The cell at (1,1) indicates there's a single mine amongst its neighbors. Examining the cells adjacent to it, both (2,1) and (2,2) remain unopened, implying one of them contains a mine. Similarly, the cell at (1,2) displays a `{self.nums[0]}', suggesting that out of (2,1), (2,2), and (2,3), one holds a mine. Since one of (2,1) or (2,2) already contains a mine, it becomes evident that (2,3) is mine-free. We can then safely uncover (2,3) with a left-click.

ACTION: L(2,3)
"""
        return desc


class Feedback:
    def __init__(self, m: MineField, unchecked_cell: str, flag_cell: str, number_cells: str):
        self.m = m
        self.unchecked_cell = unchecked_cell
        self.flag_cell = flag_cell
        self.number_cells = number_cells

    @property
    def game_feedback_to_prompt(self):
        feedback = {
            ActionFeedback.SUCCESS: "Action successful!",
            ActionFeedback.GAME_WIN: "Congratulations, you've won the game!",
            ActionFeedback.GAME_OVER: "Game over. Better luck next time!",
            ActionFeedback.UNEXIST_CELL: f"Invalid Coordinates! Please make sure your coordinate are within [1, {self.m.n_rows}] for rows and [1, {self.m.n_cols}] for columns.",
            ActionFeedback.LEFT_CLICK_EMPTY_CELL: f"Invalid action: Cannot left-click a blank cell. Left-click is only for unopened cells (`{self.unchecked_cell}').",
            ActionFeedback.LEFT_CLICK_FLAG_CELL: f"Invalid action: Cannot left-click a flagged cell. Left-click is only for unopened cells (`{self.unchecked_cell}').",
            ActionFeedback.LEFT_CLICK_NUMBER_CELL: f"Invalid action: Cannot left-click a numbered cell. Left-click is only for unopened cells (`{self.unchecked_cell}').",
            ActionFeedback.MIDDLE_CLICK_EMPTY_CELL: f"Invalid action: Cannot middle-click a blank cell. Middle-click is only for numbered cells (`{self.number_cells}').",
            ActionFeedback.MIDDLE_CLICK_FLAG_CELL: f"Invalid action: Cannot middle-click a flagged cell. Middle-click is only for numbered cells (`{self.number_cells}').",
            ActionFeedback.MIDDLE_CLICK_UNCHECKED_CELL: f"Invalid action: Cannot middle-click an unopened cell. Middle-click is only for numbered cells (`{self.number_cells}').",
            ActionFeedback.RIGHT_CLICK_EMPTY_CELL: f"Invalid action: Cannot right-click a blank cell. Right-click is only for unopened (`{self.unchecked_cell}') or flagged cells (`{self.flag_cell}').",
            ActionFeedback.RIGHT_CLICK_NUMBER_CELL: f"Invalid action: Cannot right-click a numbered cell. Right-click is only for unopened (`{self.unchecked_cell}') or flagged cells (`{self.flag_cell}').",
            ActionFeedback.MIDDLE_CLICK_NUMBER_CELL_NO_FLAG: f"Error: No flagged cells detected nearby. Flag adjacent mines before middle-clicking.",
            ActionFeedback.MIDDLE_CLICK_NUMBER_CELL_NUMBER_MISMATCH: f"Error: Flag count mismatch. Ensure all adjacent mines are flagged before middle-clicking.",
            ActionFeedback.START_BY_MIDDLE_CLICK: f"Please begin by left-clicking on a cell.",
            ActionFeedback.START_BY_RIGHT_CLICK: f"Please begin by left-clicking on a cell.",
        }
        return feedback
