"""
# Author: Yinghao Li
# Modified: February 19th, 2024
# ---------------------------------------
# Description: Macro description of the game.
"""

import math
from src.game import MineField, ActionFeedback


class GamePlayTableObfuscationPrompt:
    def __init__(
        self,
        unchecked_cell: str = "?",
        flag_cell: str = "F",
        empty_cell: str = ".",
        n_rows: int = 9,
        n_cols: int = 9,
        n_mines: int = 10,
        mine_field: MineField = None,
        with_row_column_ids: bool = True,
    ):
        if mine_field is not None:
            self.unchecked_cell = mine_field.unc
            self.flag_cell = mine_field.flg
            self.empty_cell = mine_field.emt
            self.n_rows = mine_field.n_rows
            self.n_cols = mine_field.n_cols
            self.n_mines = mine_field.n_mines
        else:
            self.unchecked_cell: str = unchecked_cell
            self.flag_cell: str = flag_cell
            self.empty_cell: str = empty_cell
            self.n_rows: int = n_rows
            self.n_cols: int = n_cols
            self.n_mines: int = n_mines
        self.with_row_column_ids = with_row_column_ids

    @property
    def wiki_game(self):
        desc = f"""--- GAME INTRODUCTION ---
In this game, {self.n_mines} thorns are scattered throughout a {self.n_rows} by {self.n_cols} field, which is divided into cells."""
        desc += " The rows are seperated by newlines, and columns by commas."

        if self.with_row_column_ids:
            desc += f" The field is structured as a {self.n_rows+1} by {self.n_cols+1} table, with the first row and column labeled using numbers in double quotation marks to indicate row and column indices."

        desc += f""" Cells have multiple possible states:
- Unopened cells (represented by `{self.unchecked_cell}', which cover the field at the start of the game, can also be made by removing flags)
- Numbered cells (represented by `1' to `8', which indicate the number of thorns in the eight neighboring cells, including those diagonally adjacent)
- Blank cells (represented by `{self.empty_cell}', which have no neighboring thorns)
- Flagged cells (represented by `{self.flag_cell}', which are marked by the player to indicate a potential thorn location)

A player selects a cell to open it. If a player opens a cell containing a thorn, the game ends in a loss. Otherwise, the opened cell displays either a number, indicating the number of thorns diagonally and/or adjacent to it, or a blank tile (sometimes shown as a 0), and all adjacent cells will automatically be opened. To win a game, all non-thorn cells must be opened without opening a thorn.
"""
        return desc

    @property
    def action_options(self):
        desc = f"""--- ACTION OPTIONS ---
There are three permissible actions in this game:

- \"L\" an unopened cell (`{self.unchecked_cell}') to reveal it.
- \"R\" an unopened cell (`{self.unchecked_cell}') to place a flag or a flagged cell (`{self.flag_cell}') to remove the flag.
- \"M\" on a numbered cell (`1' to `8') to unveil its neighboring cells, but only if all adjacent thorns have been correctly flagged. If any flags are misplaced, you'll lose the game.
"""
        return desc

    @property
    def action_format(self):
        desc = f"""--- ACTION FORMAT ---
Each of your actions should be formatted as \"A(row,col)\", where:
- \"A\" represents the action type: \"L\", \"R\", and \"M\".
- \"row\" specifies the row number of the targeted cell.
- \"col\" details the column number of the targeted cell.
For instance, an action like \"L(1,2)\" translates to an \"L\" action on the cell located at the first row and second column.
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

Begin by detailing your rationale in the \"REASONING\" section, followed by specifying your move using the previously mentioned format in the \"ACTION\" section. Ensure your reasoning doesn't exceed 200 words. To commence the game, \"L\" the center cell at ({math.ceil(self.n_rows/2)}, {math.ceil(self.n_cols/2)}).

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
"1",`{self.empty_cell}',`1',`{self.unchecked_cell}',`{self.unchecked_cell}'
"2",`{self.empty_cell}',`1',`{self.unchecked_cell}',`{self.unchecked_cell}'
"3",`{self.empty_cell}',`1',`2',`4'
"4",`{self.empty_cell}',`{self.empty_cell}',`{self.empty_cell}',`2'

REASONING: The cell located at (3,2) displays the number `1', indicating there's a single thorn in its neighboring cells. Among these neighbors, 7 are opened as empty or numbered, and only one remains unopened at (2,3). Given that there's just one adjacent thorn, it's logical to deduce that the unopened cell at (2,3) contains the thorn. Thus, our next move is to flag the cell at (2,3) with an \"R\".

ACTION: R(2,3)
"""
        return desc

    @property
    def example_2(self):
        desc = f"""Example 2:
Notice that the board is displayed in partial.

--- BOARD ---
"0","4","5","6","7"
"1",`{self.empty_cell}',`1',`{self.unchecked_cell}',`{self.unchecked_cell}'
"2",`{self.empty_cell}',`1',`{self.flag_cell}',`{self.unchecked_cell}'
"3",`{self.empty_cell}',`1',`2',`4'
"4",`{self.empty_cell}',`{self.empty_cell}',`{self.empty_cell}',`2'

REASONING: The cell at (1,5) displays the number `1', indicating a single adjacent thorn. Upon examining its neighboring cells, only the cell at (2,6) is flagged with `{self.flag_cell}'. This suggests that all thorns neighboring (1,5) have been identified. Consequently, we can safely unveil the other surrounding cells by \"M\" on (1,5).

ACTION: M(1,5)
"""
        return desc

    @property
    def example_3(self):
        desc = f"""Example 3:
Notice that the board is displayed in partial.

--- BOARD ---
"0","1","2","3","4"
"1",`1',`1',`2',`{self.unchecked_cell}'
"2",`{self.unchecked_cell}',`{self.unchecked_cell}',`{self.unchecked_cell}',`{self.unchecked_cell}'
"3",`{self.unchecked_cell}',`{self.unchecked_cell}',`{self.unchecked_cell}',`{self.unchecked_cell}'

REASONING: The cell at (1,1) indicates there's a single thorn amongst its neighbors. Examining the cells adjacent to it, both (2,1) and (2,2) remain unopened, implying one of them contains a thorn. Similarly, the cell at (1,2) displays a `1', suggesting that out of (2,1), (2,2), and (2,3), one holds a thorn. Since one of (2,1) or (2,2) already contains a thorn, it becomes evident that (2,3) is thorn-free. We can then safely uncover (2,3) with an \"L\".

ACTION: L(2,3)
"""
        return desc


class FeedbackWithObfuscation:
    def __init__(self, m: MineField, unchecked_cell: str, flag_cell: str, number_cells: str):
        self.m = m
        self.unchecked_cell = unchecked_cell
        self.flag_cell = flag_cell
        self.number_cells = number_cells

    @property
    def game_feedback_to_prompt(self):
        game_feedback_to_prompt = {
            ActionFeedback.SUCCESS: "Action successful!",
            ActionFeedback.GAME_WIN: "Congratulations, you've won the game!",
            ActionFeedback.GAME_OVER: "Game over. Better luck next time!",
            ActionFeedback.UNEXIST_CELL: f"Invalid Coordinates! Please make sure your coordinate are within [1, {self.m.n_rows}] for rows and [1, {self.m.n_cols}] for columns.",
            ActionFeedback.LEFT_CLICK_EMPTY_CELL: f'Invalid action: Cannot "L" a blank cell. "L" is only for unopened cells (`{self.unchecked_cell}\').',
            ActionFeedback.LEFT_CLICK_FLAG_CELL: f'Invalid action: Cannot "L" a flagged cell. "L" is only for unopened cells (`{self.unchecked_cell}\').',
            ActionFeedback.LEFT_CLICK_NUMBER_CELL: f'Invalid action: Cannot "L" a numbered cell. "L" is only for unopened cells (`{self.unchecked_cell}\').',
            ActionFeedback.MIDDLE_CLICK_EMPTY_CELL: f'Invalid action: Cannot "M" a blank cell. "M" is only for numbered cells (`{self.number_cells}\').',
            ActionFeedback.MIDDLE_CLICK_FLAG_CELL: f'Invalid action: Cannot "M" a flagged cell. "M" is only for numbered cells (`{self.number_cells}\').',
            ActionFeedback.MIDDLE_CLICK_UNCHECKED_CELL: f'Invalid action: Cannot "M" an unopened cell. "M" is only for numbered cells (`{self.number_cells}\').',
            ActionFeedback.RIGHT_CLICK_EMPTY_CELL: f'Invalid action: Cannot "R" a blank cell. "R" is only for unopened (`{self.unchecked_cell}\') or flagged cells (`{self.flag_cell}\').',
            ActionFeedback.RIGHT_CLICK_NUMBER_CELL: f'Invalid action: Cannot "R" a numbered cell. "R" is only for unopened (`{self.unchecked_cell}\') or flagged cells (`{self.flag_cell}\').',
            ActionFeedback.MIDDLE_CLICK_NUMBER_CELL_NO_FLAG: f'Error: No flagged cells detected nearby. Flag adjacent mines before "M".',
            ActionFeedback.MIDDLE_CLICK_NUMBER_CELL_NUMBER_MISMATCH: f'Error: Flag count mismatch. Ensure all adjacent mines are flagged before "M".',
            ActionFeedback.START_BY_MIDDLE_CLICK: f'Please begin by "L" on a cell.',
            ActionFeedback.START_BY_RIGHT_CLICK: f'Please begin by "L" on a cell.',
        }
        return game_feedback_to_prompt
