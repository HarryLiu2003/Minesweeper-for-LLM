# Model Configuration and Nuances

This document outlines the different models configured for the Minesweeper LLM experiments and notes specific adjustments made to the codebase (`src/gpt.py`) to handle variations in their API parameters and behavior.

## Standard GPT Models

These models generally adhere to the standard OpenAI Chat Completions API parameters.

*   **`gpt-3.5-turbo`**: Standard chat model.
*   **`gpt-4`**: Standard chat model.
*   **`gpt-4o`**: Standard chat model.
*   **`gpt-4.1-mini`**: Uses the ID `gpt-4.1-mini-2025-04-14`. Assumed to follow standard chat parameters for now.

**Code Handling:**
*   Uses `max_tokens` parameter (currently default set high, e.g., 30000, in `src/gpt.py`).
*   Uses `temperature` (default 0) and `top_p` (default 0.95).
*   Includes the initial `system` message.

## O-Series Reasoning Models

These models (currently `o3-mini`, `o4-mini`) are designed for reasoning tasks and have specific API differences and characteristics noted during testing and based on documentation.

**Note on `o1-mini`:** Attempts to use `o1-mini` were unsuccessful due to persistent content filter errors from the OpenAI API (`Invalid prompt: your prompt was flagged...`), despite addressing multiple parameter incompatibilities (`system` role, `max_tokens`, `temperature`, `top_p`). Usage of `o1-mini` has been discarded for this project.

**Key Differences & Adjustments (for `o3-mini`, `o4-mini`):**

1.  **Internal Reasoning & Slowness:**
    *   **Behavior:** These models perform significant internal reasoning (generating non-visible "reasoning tokens") before producing output. This makes them inherently slower than GPT models.
    *   **Code Impact:** Requires a much higher token limit to accommodate both reasoning and output tokens. The default `max_tokens` in `GPT.__init__` was increased significantly (e.g., to 30000) to prevent premature termination due to hitting the limit during internal reasoning.

2.  **Max Tokens Parameter:**
    *   **Requirement:** O-series models tested (`o3-mini`) use `max_completion_tokens` instead of the standard `max_tokens` parameter to limit the *total* (reasoning + output) tokens.
    *   **Code Adjustment (`src/gpt.py`):** The `GPT.response` method checks if the `engine` name starts with `'o'`. If yes, it passes the token limit using the `max_completion_tokens` key; otherwise, it uses `max_tokens`.

3.  **`system` Message Role:**
    *   **Requirement:** `o3-mini` and `o4-mini` support the `system` role.
    *   **Code Adjustment (`src/gpt.py`):** No special filtering is applied.

4.  **`temperature` Parameter:**
    *   **Requirement:** Both `o3-mini` and `o4-mini` failed when `temperature=0` was provided, indicating they do not support this value and likely require the API default (1.0).
    *   **Code Adjustment (`src/gpt.py`):** The `GPT.response` method omits the `temperature` parameter from the API call if the `engine` is in the `MODELS_WITH_LIMITED_PARAMS` set (currently `{'o3-mini', 'o4-mini'}`).

5.  **`top_p` Parameter:**
    *   **Requirement:** `o3-mini` failed when `top_p` was provided. `o4-mini` is *assumed* to have the same restriction based on the pattern, although this wasn't explicitly confirmed with an error.
    *   **Code Adjustment (`src/gpt.py`):** The `GPT.response` method omits the `top_p` parameter from the API call if the `engine` is in the `MODELS_WITH_LIMITED_PARAMS` set (currently `{'o3-mini', 'o4-mini'}`).

**Summary Table (O-Series Adjustments in `src/gpt.py`):**

| Model          | System Message Filtered? | Uses `max_completion_tokens`? | `temperature` Omitted? | `top_p` Omitted? |
| :------------- | :----------------------- | :---------------------------- | :--------------------- | :--------------- |
| `o3-mini`      | No                       | Yes                           | Yes                    | Yes              |
| `o4-mini`      | No                       | Yes                           | Yes                    | Yes              |

These adjustments allow the codebase to interact with the tested O-series models despite their API variations compared to the standard GPT models.
