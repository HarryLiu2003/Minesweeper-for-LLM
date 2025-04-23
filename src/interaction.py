"""
# Author: Yinghao Li
# Modified: February 19th, 2024
# ---------------------------------------
# Description: Interaction functions
"""

import re
import logging
from .prompts import (
    GamePlayTablePrompt,
    GamePlayCoordinatePrompt,
    GamePlayCoordinateObfuscationPrompt,
    Feedback,
    GamePlayTableObfuscationPrompt,
    FeedbackWithObfuscation,
)
from .game import MineField, ActionFeedback
from .gpt import GPT, MessageCache

logger = logging.getLogger(__name__)

action_map = {
    "L": "left_click",
    "M": "middle_click",
    "R": "right_click",
}

number_cells = ",".join([f"`{i}'" for i in range(1, 8)])

system_prompt = "You are a helpful assistant who is good at playing Minesweeper."
system_prompt_obfuscation = (
    "You are a helpful assistant who is good at playing strategic games that requires logical reasoning."
)


class Interaction:
    def __init__(
        self,
        gpt_resource_path: str,
        board_path: str = None,
        empty_cell: str = ".",
        mine_cell: str = "*",
        flag_cell: str = "F",
        unchecked_cell: str = "?",
        number_cells: list[str] = None,
        n_rows: int = 9,
        n_cols: int = 9,
        n_mines: int = 10,
        seed: int = 42,
        use_row_column_indices: bool = True,
        represent_board_as_coordinate: bool = False,
        use_compressed_history: bool = False,
        strict_winning_condition: bool = False,
        obfuscation: bool = False,
        no_example_1: bool = False,
        no_example_2: bool = False,
        no_example_3: bool = False,
        **kwargs,
    ) -> None:
        self.use_compressed_history = use_compressed_history
        self.no_example_1 = no_example_1
        self.no_example_2 = no_example_2
        self.no_example_3 = no_example_3

        if board_path is not None:
            self.m = MineField(
                empty_cell=empty_cell,
                mine_cell=mine_cell,
                flag_cell=flag_cell,
                unchecked_cell=unchecked_cell,
                number_cells=number_cells,
                strict_winning_condition=strict_winning_condition,
            ).load_board(board_path)
        else:
            self.m = MineField(
                n_rows=n_rows,
                n_cols=n_cols,
                n_mines=n_mines,
                seed=seed,
                empty_cell=empty_cell,
                mine_cell=mine_cell,
                flag_cell=flag_cell,
                unchecked_cell=unchecked_cell,
                number_cells=number_cells,
                strict_winning_condition=strict_winning_condition,
            )

        self.gpt = GPT(resource_path=gpt_resource_path)
        self.represent_board_as_coordinate = represent_board_as_coordinate

        if represent_board_as_coordinate:
            if not obfuscation:
                self.prompt = GamePlayCoordinatePrompt(mine_field=self.m)
                self.messages = MessageCache(system_role=system_prompt)
            else:
                self.prompt = GamePlayCoordinateObfuscationPrompt(mine_field=self.m)
                self.messages = MessageCache(system_role=system_prompt_obfuscation)
        else:
            if not obfuscation:
                self.prompt = GamePlayTablePrompt(mine_field=self.m, with_row_column_ids=use_row_column_indices)
                self.messages = MessageCache(system_role=system_prompt)
            else:
                self.prompt = GamePlayTableObfuscationPrompt(
                    mine_field=self.m, with_row_column_ids=use_row_column_indices
                )
                self.messages = MessageCache(system_role=system_prompt_obfuscation)

        init_examples = (
            f"--- EXAMPLES ---\n"
            f"{self.prompt.example_1 if not self.no_example_1 else ''}\n"
            f"{self.prompt.example_2 if not self.no_example_1 else ''}\n"
            f"{self.prompt.example_3 if not self.no_example_1 else ''}"
            "--- END OF EXAMPLES ---\n\n"
        )
        init_table = self.m.to_str_repr() if not represent_board_as_coordinate else self.m.to_coord_repr()
        self.init_prompt = (
            f"{self.prompt.wiki_game}\n"
            f"{self.prompt.action_options}\n"
            f"{self.prompt.action_format}\n"
            f"{self.prompt.action_regulation}\n"
            f"{init_examples}"
            f"--- CURRENT BOARD ---\n```\n{init_table}\n```\n\n"
            f"{self.prompt.init_response_guide}"
        )
        self.step_idx = 1
        self.action_feedback = ActionFeedback.SUCCESS
        self.action_feedback_list = list()
        self.action_history = list()

        if not obfuscation:
            self.game_feedback_to_prompt = Feedback(
                m=self.m, unchecked_cell=unchecked_cell, flag_cell=flag_cell, number_cells=number_cells
            ).game_feedback_to_prompt
        else:
            self.game_feedback_to_prompt = FeedbackWithObfuscation(
                m=self.m, unchecked_cell=unchecked_cell, flag_cell=flag_cell, number_cells=number_cells
            ).game_feedback_to_prompt

    def step(self) -> str:
        self.update_user_prompt()

        response = self.gpt(self.messages)
        self.messages.add_assistant_message(response)

        try:
            action, row_idx, col_idx = self.parse_action_str(response)
        except ValueError as e:
            # Log the prompt (last user message) that led to the error
            last_prompt = "Could not retrieve last prompt."
            if self.messages.message_cache and self.messages.message_cache[-2]['role'] == 'user': # [-1] is assistant msg
                last_prompt = self.messages.message_cache[-2]['content']
            logger.error(f"Failed to parse action string.\nPROMPT:\n---\n{last_prompt}\n---\nRaw response:\n---\n{response}\n---")
            raise e # Re-raise the error after logging
        
        self.action_history.append(f"{action}({row_idx},{col_idx})")

        self.action_feedback = self.excute_action(action, row_idx, col_idx)
        self.action_feedback_list.append(self.action_feedback)

        self.step_idx += 1
        return response

    def excute_action(self, action: str, row_idx: str, col_idx: str):
        action = action_map[action]
        row_idx = int(row_idx)
        col_idx = int(col_idx)
        excute_func = getattr(self.m, f"on_{action}")
        action_response = excute_func(row_idx, col_idx)

        return action_response

    def update_user_prompt(self) -> str:
        if self.use_compressed_history:
            prompt = self.update_user_prompt_compressed_history()
        else:
            prompt = self.update_user_prompt_natural_conversation()
        return prompt

    def update_user_prompt_natural_conversation(self) -> str:
        if self.step_idx == 1:
            prompt = f"{self.init_prompt}"
            self.messages.add_user_message(prompt)
        else:
            prompt = self.feedback_to_prompt()
            if self.represent_board_as_coordinate:
                prompt += f"--- CURRENT BOARD ---\n```\n{self.m.to_coord_repr()}\n```\n\n"
            else:
                prompt += f"--- CURRENT BOARD ---\n```\n{self.m.to_str_repr()}\n```\n\n"

            prompt += f"{self.prompt.action_regulation}\n"
            prompt += "REASONING:\n\nACTION:\n"
            self.messages.add_user_message(prompt)
        return prompt

    def update_user_prompt_compressed_history(self) -> str:
        if self.step_idx == 1:
            prompt = f"{self.init_prompt}"
            self.messages.add_user_message(prompt)
        else:
            if self.represent_board_as_coordinate:
                current_board = f"--- CURRENT BOARD ---\n```\n{self.m.to_coord_repr()}\n```\n"
            else:
                current_board = f"--- CURRENT BOARD ---\n```\n{self.m.to_str_repr()}\n```\n"

            examples = (
                f"--- EXAMPLES ---\n"
                f"{self.prompt.example_1 if not self.no_example_1 else ''}\n"
                f"{self.prompt.example_2 if not self.no_example_1 else ''}\n"
                f"{self.prompt.example_3 if not self.no_example_1 else ''}"
                "--- END OF EXAMPLES ---\n\n"
            )
            prompt = (
                f"{self.prompt.wiki_game}\n"
                f"{self.prompt.action_options}\n"
                f"{self.prompt.action_format}\n"
                f"{self.prompt.action_regulation}\n"
                f"{examples}"
                f"--- YOUR ACTION HISTORY ---\n{self.compose_action_history_and_feedbacks()}\n\n"
                f"{current_board}\n"
                f"{self.prompt.response_guide}"
            )
            # clear the message cache
            self.messages = MessageCache()
            self.messages.add_user_message(prompt)
        return prompt

    def compose_action_history_and_feedbacks(self) -> str:
        text = ""
        for i, (action, feedback) in enumerate(zip(self.action_history, self.action_feedback_list)):
            text += f"[Action {i + 1}]: ACTION: {action} -> FEEDBACK: {self.game_feedback_to_prompt[feedback]}\n"
        return text

    def feedback_to_prompt(self) -> str:
        if self.action_feedback == ActionFeedback.SUCCESS:
            return ""
        feedback_str = f'Your previous action "{self.action_history[-1]}" is invalid. Error Message:\n'
        feedback_str += self.game_feedback_to_prompt[self.action_feedback]
        feedback_str += "\nPlease follow the instructions and try again.\n\n"
        return feedback_str

    def save_messages(self, path: str) -> None:
        self.messages.save_plain(path)

    def parse_action_str(self, response: str) -> tuple[str, str, str]:
        response_ = re.sub(r"(?s)(.*)ACTION:", "", response)
        response_ = response_.strip()
        match_result = re.search(r"([LMR]) *\(( *\d+) *, *(\d+) *\)", response_)
        try:
            action, row_idx, col_idx = match_result.groups()
        except (AttributeError, TypeError):
            action, row_idx, col_idx = self.parse_action_str_in_natural_language(response)

        return action, row_idx, col_idx

    @staticmethod
    def parse_action_str_in_natural_language(response: str) -> tuple[str, str, str]:
        response = re.findall(r"^(ACTION:.*(?:\r?\n|$))", response, re.MULTILINE)
        if len(response) == 0:
            raise ValueError("Invalid response format.")
        response = response[-1].strip()

        try:
            action = re.findall(r"(?:left|middle|right)[- ]?click(?:ing)?", response)[-1]
            row_idx, col_idx = re.search(r"\(( *\d+) *, *(\d+) *\)", response).groups()
        except (AttributeError, TypeError, IndexError):
            raise ValueError("Invalid response format.")

        if "left" in action:
            action = "L"
        elif "middle" in action:
            action = "M"
        elif "right" in action:
            action = "R"

        return action, row_idx, col_idx
