import json
import os
import argparse
from collections import defaultdict
import re # Need re for parsing action strings
import traceback # Import traceback

# --- Verified ActionFeedback Codes from src/game/core.py ---
class ActionFeedbackCodes: # Using a class for namespacing
    SUCCESS = 0                         # Generic success (used for valid reveals/flags/chords)
    UNEXIST_CELL = 1                    # Target cell out of bounds
    MIDDLE_CLICK_UNCHECKED_CELL = 2     # M-click on '?'
    MIDDLE_CLICK_FLAG_CELL = 3          # M-click on 'F'
    MIDDLE_CLICK_EMPTY_CELL = 4         # M-click on '.'
    RIGHT_CLICK_NUMBER_CELL = 5         # R-click on '1'-'8'
    RIGHT_CLICK_EMPTY_CELL = 6          # R-click on '.'
    LEFT_CLICK_NUMBER_CELL = 7          # L-click on '1'-'8'
    LEFT_CLICK_EMPTY_CELL = 8           # L-click on '.'
    LEFT_CLICK_FLAG_CELL = 9            # L-click on 'F'
    GAME_OVER = 10                      # Hit a mine (or invalid M-click verification fail)
    GAME_WIN = 11
    MIDDLE_CLICK_NUMBER_CELL_NO_FLAG = 12 # M-click on number, but no neighbors flagged
    MIDDLE_CLICK_NUMBER_CELL_NUMBER_MISMATCH = 13 # M-click, neighbor flags != cell number
    START_BY_RIGHT_CLICK = 14           # Invalid first move
    START_BY_MIDDLE_CLICK = 15          # Invalid first move

# Define which feedback codes count as "valid" according to the paper
# Still assuming only SUCCESS counts as advancing gameplay without failure.
VALID_FEEDBACK_CODES = {
    ActionFeedbackCodes.SUCCESS,
}

# Define which feedback codes count as "repeated/ineffective"
# Excluding code 13 (M-Click Mismatch) as it's a specific error type.
REPEATED_FEEDBACK_CODES = {
    ActionFeedbackCodes.MIDDLE_CLICK_UNCHECKED_CELL, # 2
    ActionFeedbackCodes.MIDDLE_CLICK_FLAG_CELL,    # 3
    ActionFeedbackCodes.MIDDLE_CLICK_EMPTY_CELL,   # 4
    ActionFeedbackCodes.RIGHT_CLICK_NUMBER_CELL,   # 5
    ActionFeedbackCodes.RIGHT_CLICK_EMPTY_CELL,    # 6
    ActionFeedbackCodes.LEFT_CLICK_NUMBER_CELL,    # 7
    ActionFeedbackCodes.LEFT_CLICK_EMPTY_CELL,     # 8
    ActionFeedbackCodes.LEFT_CLICK_FLAG_CELL,      # 9
    ActionFeedbackCodes.MIDDLE_CLICK_NUMBER_CELL_NO_FLAG, # 12
}

# Action Type Identifier (Verified)
ACTION_TYPE_FLAG = 'R'
ACTION_TYPE_REVEAL = 'L' # Assuming Reveal is 'L'
# -------------------------------------

def parse_action_string(action_str):
    """Parses action string like 'L(1,2)' into type, r, c."""
    match = re.search(r"([LMR])\( *(\\d+) *, *(\\d+) *\)", action_str)
    if match:
        action_type, r_str, c_str = match.groups()
        return action_type, int(r_str), int(c_str)
    return None, None, None # Return None if parsing fails

def analyze_game(output_data, input_data):
    """Analyzes a single game's results."""
    metrics = {
        'is_solved': False,
        'is_failed': False, # Failed by hitting a mine
        'total_actions': 0,
        'valid_actions': 0,
        'repeated_actions': 0,
        'correctly_flagged_mines': 0,
        'incorrectly_flagged_non_mines': 0,
        'final_flags': set(),
        'action_feedbacks': []
    }

    action_history = output_data.get('action_history', [])
    actions_to_analyze = action_history[1:] # Exclude initial L(3,3)
    metrics['total_actions'] = len(actions_to_analyze)

    for action_data in actions_to_analyze:
        feedback = action_data.get('feedback', -1)
        metrics['action_feedbacks'].append(feedback)

        if feedback == ActionFeedbackCodes.GAME_OVER:
            metrics['is_failed'] = True

        if feedback in VALID_FEEDBACK_CODES:
             metrics['valid_actions'] += 1

        if feedback in REPEATED_FEEDBACK_CODES:
            metrics['repeated_actions'] += 1

    # --- Get Final Flags from Saved Board State --- 
    final_flags = set()
    final_board_disp = output_data.get('final_board_disp', [])
    if final_board_disp:
        for r_idx, row in enumerate(final_board_disp):
            for c_idx, cell_state in enumerate(row):
                # Need to know the actual flag symbol used by the game
                # Assuming it's 'F' based on MineField defaults
                FLAG_SYMBOL = 'F' 
                if cell_state == FLAG_SYMBOL:
                    final_flags.add((r_idx, c_idx))
    else:
        print(f"Warning: 'final_board_disp' not found in output file. Cannot accurately calculate flags/solved status.")

    metrics['final_flags'] = final_flags

    # --- Check for win condition based on GAME_WIN feedback --- (Keep this as initial check)
    if action_history and action_history[-1].get('feedback') == ActionFeedbackCodes.GAME_WIN:
        metrics['is_solved'] = True
        metrics['is_failed'] = False

    # --- Calculate flagging accuracy & Re-evaluate Solved based on strict condition --- 
    ground_truth_mines = set()
    board_mine_matrix = input_data.get('board_mine', [])
    if board_mine_matrix:
        for r_idx, row in enumerate(board_mine_matrix):
            for c_idx, cell in enumerate(row):
                if cell == 1:
                    ground_truth_mines.add((r_idx, c_idx))

    if ground_truth_mines: # Only if we have ground truth
        # Correctly flagged = intersection of ACTUAL final flags and ground truth
        correct_flags = metrics['final_flags'].intersection(ground_truth_mines)
        metrics['correctly_flagged_mines'] = len(correct_flags)

        # Incorrectly flagged = final flags that are NOT ground truth mines
        incorrect_flags = metrics['final_flags'].difference(ground_truth_mines)
        metrics['incorrectly_flagged_non_mines'] = len(incorrect_flags)

        # Strict winning condition check using actual final flags
        is_strictly_solved = (metrics['correctly_flagged_mines'] == len(ground_truth_mines) and
                              metrics['incorrectly_flagged_non_mines'] == 0)
                              # The check len(final_flags) == len(ground_truth) is implicit here

        # Override is_solved with the strict check
        metrics['is_solved'] = is_strictly_solved
        if metrics['is_solved']:
            metrics['is_failed'] = False # Ensure consistency
    # else: (Keep solved status based on GAME_WIN if no ground truth)
        # pass

    return metrics

def main(output_dir, input_dir):
    """Parses all JSON files in the output directory and calculates metrics."""
    output_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
    total_games_found = len(output_files)
    processed_games = 0

    if total_games_found == 0:
        print(f"No .json files found in {output_dir}")
        return

    aggregate_metrics = defaultdict(int)
    total_actual_mines = 0 # Initialize BEFORE the loop

    print(f"Analyzing {total_games_found} games found in {output_dir}...")

    for filename in output_files:
        output_filepath = os.path.join(output_dir, filename)
        # Construct corresponding input filename - assumes same name
        input_filepath = os.path.join(input_dir, filename)

        # Load output data
        try:
            with open(output_filepath, 'r') as f:
                output_data = json.load(f)
        except Exception as e:
            print(f"Error loading or parsing output file {output_filepath}: {e}")
            continue # Skip this file

        # Load corresponding input data (for ground truth)
        if not os.path.exists(input_filepath):
             print(f"Warning: Corresponding input file not found: {input_filepath}. Cannot calculate flag metrics for {filename}.")
             input_data = {}
             has_ground_truth = False
        else:
            try:
                with open(input_filepath, 'r') as f:
                    input_data = json.load(f)
                has_ground_truth = True
            except Exception as e:
                print(f"Error loading or parsing input file {input_filepath}: {e}")
                input_data = {}
                has_ground_truth = False

        # Analyze this game
        try:
            game_metrics = analyze_game(output_data, input_data)
            processed_games += 1
        except Exception as e:
            print(f"Error analyzing game {filename}: {e}")
            traceback.print_exc() # Print full traceback
            continue # Skip this game if analysis fails

        # Aggregate results
        aggregate_metrics['solved_games'] += game_metrics['is_solved']
        aggregate_metrics['failed_games'] += game_metrics['is_failed']
        aggregate_metrics['total_actions'] += game_metrics['total_actions']
        aggregate_metrics['valid_actions'] += game_metrics['valid_actions']
        aggregate_metrics['repeated_actions'] += game_metrics['repeated_actions']

        # Aggregate mine counts *after* successful analysis
        if has_ground_truth:
            aggregate_metrics['total_correctly_flagged'] += game_metrics['correctly_flagged_mines']

            # Re-calculate ground truth mines here in main scope to get count
            ground_truth_mines_in_main = set()
            board_mine_matrix = input_data.get('board_mine', [])
            if board_mine_matrix:
                for r_idx, row in enumerate(board_mine_matrix):
                    for c_idx, cell in enumerate(row):
                        if cell == 1:
                            ground_truth_mines_in_main.add((r_idx, c_idx))

            num_mines_in_game = len(ground_truth_mines_in_main)
            if num_mines_in_game > 0:
                total_actual_mines += num_mines_in_game
            # else:
                 # print(f"Warning: Input file {input_filepath} has 'board_mine' but no mines found.")

    # --- Calculate final percentages ---
    print(f"\n--- Aggregate Results ({processed_games}/{total_games_found} games successfully processed) ---")

    if processed_games > 0:
        percent_solved = (aggregate_metrics['solved_games'] / processed_games) * 100
        percent_failed = (aggregate_metrics['failed_games'] / processed_games) * 100

        print(f"\nGame Outcomes:")
        print(f"  Solved (Strict): {aggregate_metrics['solved_games']} ({percent_solved:.2f}%)")
        print(f"  Failed (Hit Mine): {aggregate_metrics['failed_games']} ({percent_failed:.2f}%)")
        # Note: Games might also end by reaching max_steps or invalid responses without win/fail

    if aggregate_metrics['total_actions'] > 0:
        percent_valid = (aggregate_metrics['valid_actions'] / aggregate_metrics['total_actions']) * 100
        percent_repeated = (aggregate_metrics['repeated_actions'] / aggregate_metrics['total_actions']) * 100
        print(f"\nAction Validity (excluding initial action):")
        print(f"  Total Actions (Post-Initial): {aggregate_metrics['total_actions']}")
        print(f"  Valid Actions: {aggregate_metrics['valid_actions']} ({percent_valid:.2f}%)")
        print(f"  Repeated/Ineffective Actions: {aggregate_metrics['repeated_actions']} ({percent_repeated:.2f}%)")

    if total_actual_mines > 0:
        percent_mines_flagged = (aggregate_metrics['total_correctly_flagged'] / total_actual_mines) * 100
        print(f"\nMine Identification:")
        print(f"  Total Actual Mines in Analyzed Games: {total_actual_mines}")
        print(f"  Correctly Flagged Mines: {aggregate_metrics['total_correctly_flagged']} ({percent_mines_flagged:.2f}%)")
    else:
        print(f"\nMine Identification:")
        print(f"  Could not calculate mine flagging accuracy (missing ground truth data or no mines in ground truth).")

    print("\nNote: 'Action Validity' metrics exclude the initial L(3,3) action.")
    print("\nNote: '% Coherent Reasoning' requires manual inspection of conversation logs.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Minesweeper LLM experiment results.")
    parser.add_argument("output_dir", help="Directory containing the output JSON files.")
    parser.add_argument("input_dir", help="Directory containing the corresponding input board JSON files (for ground truth).")
    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        print(f"Error: Output directory not found: {args.output_dir}")
    elif not os.path.isdir(args.input_dir):
        print(f"Error: Input directory not found: {args.input_dir}")
    else:
        main(args.output_dir, args.input_dir)
