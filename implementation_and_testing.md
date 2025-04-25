# Implementation and Testing Report: Minesweeper LLM Replication Study

## Introduction and Goal

This study replicates and extends the experiments presented in "Assessing Logical Puzzle Solving in Large Language Models: Insights from a Minesweeper Case Study" by Li, Wang, and Zhang. The original work investigated the intrinsic logical reasoning capabilities of LLMs (GPT-3.5 variants, GPT-4) using the game Minesweeper, presented in novel text-based formats absent from training data.

Our primary goal was to reproduce the original findings while extending the analysis to include more recent OpenAI models. Specifically, we aimed to evaluate:
1.  Legacy models used in the original study (GPT-3.5, GPT-4) for baseline comparison.
2.  Newer general-purpose models (GPT-4o).
3.  Recent developmental/specialized models (GPT-4.1 Mini).
4.  OpenAI's reasoning-focused 'o-series' models (o3-mini, o4-mini) to assess their performance on structured logical tasks compared to the GPT series.

A secondary, long-term goal guiding this work is the potential exploration of visual-based systems for this task, comparing performance when models interact with image-based grids versus the text-based coordinate or table representations used currently.

## Methodology

### Base Codebase and Customizations

We utilized the original codebase provided by the authors ([`github.com/Yinghao-Li/Minesweeper-for-LLM`](https://github.com/Yinghao-Li/Minesweeper-for-LLM)) as the foundation for our experiments. Several modifications and customizations were implemented:

1.  **API Key Management:** The original study potentially used enterprise APIs. We adapted the codebase to use standard OpenAI API keys securely loaded from a `.env` file via the `python-dotenv` library. This involved modifying `src/gpt.py` to check for an `ENV:OPENAI_API_KEY` placeholder in the model configuration JSON files and adding `python-dotenv` to `requirements.txt`.
2.  **Metrics Analysis Script (`analyze_results.py`):** The original codebase did not include scripts for aggregating and analyzing results. We developed a custom Python script (`analyze_results.py`) to parse the experiment output JSON files and calculate the objective metrics defined in the original paper (Section 5.2).
    *   Metric definitions were implemented based on the paper's descriptions and verified against the game logic in `src/game/core.py`.
    *   The script calculates: % Solved (Strict), % Failed (Hit Mine), % Valid Actions, % Repeated Actions, and % Mines Flagged.
    *   Alignment with the paper was prioritized. An iterative process refined the script to handle the evolving output format (adding feedback codes per action, saving the final board state) and metric definitions (e.g., using the final board state for accurate flagging/solved checks, excluding the initial action for validity/repetition counts).
    *   The manual analysis of "% Accurate and Coherent Logic" mentioned in the original paper was omitted due to the significant manual overhead involved.
3.  **Parameter Handling:** Adjustments were made to `src/gpt.py` to handle parameter differences required by specific models encountered during testing (e.g., using `max_completion_tokens` instead of `max_tokens`, omitting `temperature` and `top_p` for o1-mini and o3-mini based on API error feedback).
4.  **Argument Requirements:** The `--gpt_resource_path` argument was made effectively required at runtime by adding checks to `tasks/ms.py`, preventing accidental runs with a default model.

### Experiment Configuration

To ensure comparability while testing newer models, we standardized the following configurations across all runs:

*   **Models Tested:** GPT-3.5 Turbo (`gpt-3.5-turbo`), GPT-4 (`gpt-4`), GPT-4o (`gpt-4o`), GPT-4.1 Mini (`gpt-4.1-mini-2025-04-14`), o3-mini, and o4-mini. This selection allows comparison between legacy models (3.5, 4), newer general models (4o, 4.1 Mini), and reasoning-focused models (o3-mini, o4-mini). (Note: `o1-mini` was attempted but excluded due to persistent API/prompt errors).
*   **Board Configuration:** The standard 5x5 grid with 4 mines, using the pre-generated boards from `data/5x5-4-labeled/`.
*   **Number of Runs:** Each model configuration was run on all 100 boards available in the specified directory.
*   **Game Parameters:**
    *   Maximum Steps: 10 (`--max_steps 10`)
    *   Win Condition: Strict (`--strict_winning_condition true`)
*   **Board Representation:** Coordinate format (`--represent_board_as_coordinate true`), based on the original study's finding that it yielded superior performance compared to the table format.
*   **Prompting Mode:** Natural Conversation (NC) mode (`--use_compressed_history false`). This was chosen because the newer models (GPT-4 series, o-series) generally possess large context windows, diminishing the necessity of the Compact History (CH) mode used in the original paper primarily to manage context length for older models. NC mode also provides a more standard chat-like interaction suitable for current models.

### Model Selection Rationale and Expectations

The choice of models aimed to cover a spectrum from baseline general-purpose models to the latest reasoning-focused architectures:

| **Model**           | **Design Purpose**                                                                         | **Expectations for Minesweeper Task**                                                                                                                    |
| :------------------ | :----------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **GPT-3.5 Turbo**   | General-purpose LLM optimized for speed and cost-efficiency.                               | As a baseline model, limited performance anticipated due to focus on general language tasks over structured logical reasoning.                             |
| **GPT-4**           | Enhanced general-purpose model with improved reasoning over GPT-3.5.                       | Expected to outperform GPT-3.5 but still potentially limited by lack of specific tailoring for step-by-step logical problem-solving.                     |
| **GPT-4o**          | Multimodal model (text, image, audio) with improved efficiency.                            | Anticipated to handle structured inputs well, but generalist nature might limit deep logical reasoning depth compared to specialized models.              |
| **GPT-4.1 Mini**    | Developmental model potentially focusing on instruction following/long-context reasoning.    | Expected to potentially perform well by maintaining coherent strategies over multiple steps due to focus on instruction following.                           |
| **o3-mini**         | Reasoning-focused model using internal deliberation ("private chain of thought").           | Specifically trained for complex reasoning. High expectations for accuracy and strategic moves due to internal problem-solving process.                    |
| **o4-mini**         | Successor to o3-mini with enhanced reasoning capabilities and efficiency.                  | Expected to build upon o3-mini's strengths, potentially offering the best performance on logical tasks while being resource-efficient.                   |

## Results

The objective metrics were calculated using the `analyze_results.py` script on the completed experiment runs.

### Quantitative Results Comparison

The table below compares the performance of the models tested in this study against relevant results from the original paper (Li et al.). Our study used NC prompting mode; the paper used CH for GPT-3.5-16k and NC for GPT-4 in the results shown.

| Metric                        | GPT-3.5 Turbo (NC, Ours) | GPT-4 (NC, Ours) | GPT-4o (NC, Ours) | GPT-4.1 Mini (NC, Ours) | o3-mini (NC, Ours) | o4-mini (NC, Ours) | GPT-3.5-16k (CH, Paper) | GPT-4 (NC, Paper) |
| :---------------------------- | :----------------------- | :--------------- | :---------------- | :---------------------- | :----------------- | :----------------- | :---------------------- | :---------------- |
| % Solved (Strict)             | 1.00%                    | 6.00%            | 6.00%             | 12.00%                  | 58.00%             | **70.00%**         | 0.0%                    | 0.0%              |
| % Failed (Hit Mine)           | 34.00%                   | 73.00%           | 93.00%            | 81.00%                  | **15.00%**         | 27.00%             | 35.0%                   | 82.7%             |
| % Valid Actions (Post-Init)   | 20.58%                   | 69.91%           | 70.68%            | 74.02%                  | 73.38%             | **80.97%**         | 22.6%                   | 82.7%             |
| % Repeated Actions (Post-Init)| 74.62%                   | 15.14%           | **2.19%**         | 4.60%                   | 16.34%             | 3.39%              | 45.3%                   | 0.0%              |
| % Mines Flagged               | 15.50%                   | 45.50%           | 32.50%            | 41.25%                  | 80.75%             | **85.50%**         | 9.5%                    | 45.0%             |
| Total Actions (Post-Init)     | 729                      | 535              | 365               | 435                     | 710                | 620                | ~587*                   | ~553*             |

*(*)Note: Total Actions from paper adjusted by subtracting 100 initial actions for rough comparison.*


## Discussion

### Performance Comparison and Alignment with Expectations

This study aimed to evaluate models ranging from general-purpose baselines to newer reasoning-focused architectures. The results generally aligned with, and in some cases exceeded, our initial expectations based on the models' design purposes:

*   **GPT Series vs. O-Series:** The most striking result is the dramatic performance gap between the GPT series (3.5T, 4, 4o, 4.1m) and the o-series models (`o3-mini`, `o4-mini`), **confirming the expectation** that models explicitly designed for reasoning would excel. The o-series demonstrated significantly superior capabilities, achieving high solve rates (58% and 70%) and mine flagging accuracy (~81% and ~86%), where the GPT models struggled (max 12% solves, 46% flagging). This highlights the impact of specialized training for complex logical tasks.

*   **GPT-3.5 Turbo (Baseline):** As anticipated for a baseline generalist model, GPT-3.5 Turbo exhibited **limited performance**, with low solve/flagging rates and very high repetition, confirming its unsuitability for this structured reasoning task.

*   **GPT-4 (Legacy Advanced):** GPT-4 performed **as expected**, showing clear improvements over GPT-3.5 in validity and flagging, but still failing to consistently solve boards, demonstrating the limits of its general reasoning capabilities on this specific logical puzzle.

*   **GPT-4o (Multimodal Generalist):** Results **partially met expectations**. While it handled instructions extremely well (very low repetition), its high failure rate (93%) and lack of improvement in solving/flagging over GPT-4 suggest its generalist, multimodal focus did not translate to significantly deeper logical deduction for this specific task.

*   **GPT-4.1 Mini (Instruction/Context Focused):** Performance **partially met expectations**. It achieved the best solve rate (12%) among the GPT series and showed excellent instruction following (low repetition), hinting at better strategy maintenance as hoped. However, its high failure rate (81%) indicates it still struggled significantly with the core logical challenge.

*   **o3-mini (Reasoning Focused):** This model **met and arguably exceeded expectations**. It drastically outperformed all GPT models, achieving a 58% solve rate and ~81% flagging accuracy, validating the effectiveness of its reasoning-focused design. Its low failure rate (15%) was also notable.

*   **o4-mini (Enhanced Reasoning):** `o4-mini` **met expectations** by building upon `o3-mini`'s success, delivering the best overall performance (70% solve rate, 81% validity, 86% flagging). This confirms its position as the most capable model tested for this reasoning task.

### Comparison with Original Study

*   **Overall Difficulty & Baseline:** Our results for GPT-3.5 Turbo and GPT-4 generally align with the original paper's findings regarding the task's difficulty for standard LLMs. Our GPT-4 flagging accuracy (45.5%) closely matched the paper's (45.0%). Our slightly higher solve rates for GPT models (1-12% vs 0%) could stem from ongoing API updates or minor analysis variations.
*   **Action Validity/Repetition:** Discrepancies persist between our GPT-model results and the paper's for `% Valid` and `% Repeated`, likely due to differing categorizations of non-success feedback codes in the original analysis script vs. ours. However, the low repetition rates observed for GPT-4o and 4.1 Mini align with the paper's trend for GPT-4 (NC), suggesting maintained instruction following in newer GPT models.
*   **O-Series Performance:** The standout performance of `o3-mini` and `o4-mini` represents a significant advancement beyond the capabilities observed in the original study's models, demonstrating a qualitative leap in applying logical deduction within the game's constraints.

### Rationalization and Difficulties Encountered

The results strongly suggest that models explicitly optimized for reasoning (o-series) are substantially better equipped for this type of structured, multi-step logical puzzle than general-purpose chat models (GPT series), even recent ones. While newer GPT models show improved instruction adherence, they lack the consistent planning and inference capabilities demonstrated by the o-series in this task.

The initial difficulties encountered when running the o-series models (unsupported parameters, content filtering for `o1-mini`) highlight the practical challenges of working with specialized models via standard APIs where behavior and parameter support can differ from documentation or across versions, requiring iterative debugging.

## Future Work

The success of the text-based o-series models reinforces the value of specialized reasoning capabilities. However, the inherent spatial nature of Minesweeper still suggests multimodal approaches as a promising future direction. Testing models like GPT-4o with direct visual input of the grid could potentially bypass ambiguities in text representation and leverage different reasoning pathways, offering a valuable comparison point. This would require significant implementation effort to handle image input and action specification within a visual context.

## Conclusion

This replication study validated the original paper's finding that Minesweeper presents a significant logical reasoning challenge for standard LLMs like GPT-3.5 and GPT-4. Our extension to newer models revealed improved instruction following in the GPT-4 series (4o, 4.1 Mini) but limited gains in overall problem-solving ability. Crucially, the reasoning-focused o-series models (`o3-mini`, `o4-mini`) demonstrated dramatically superior performance, achieving high solve rates and mine identification accuracy, confirming their enhanced capabilities for complex, logical tasks. Despite practical challenges in utilizing the o-series models via standard APIs, their success highlights the importance of specialized model architectures for tackling demanding reasoning problems. Future exploration of multimodal interaction remains a compelling avenue for further research.