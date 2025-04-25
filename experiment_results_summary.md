# Consolidated Minesweeper LLM Experiment Results

This table summarizes the performance of various OpenAI models on the 5x5 Minesweeper task using the Coordinate representation and Natural Conversation (NC) prompting mode. All metrics are calculated based on 100 game runs.

| Metric                        | GPT-3.5 Turbo (NC) | GPT-4 (NC) | GPT-4o (NC) | GPT-4.1 Mini (NC) | o3-mini (NC) | o4-mini (NC) |
| :---------------------------- | :----------------- | :--------- | :---------- | :---------------- | :----------- | :----------- |
| % Solved (Strict)             | 1.00%              | 6.00%      | 6.00%       | 12.00%            | 58.00%       | **70.00%**   |
| % Failed (Hit Mine)           | 34.00%             | 73.00%     | 93.00%      | 81.00%            | **15.00%**   | 27.00%       |
| % Valid Actions (Post-Init)   | 20.58%             | 69.91%     | 70.68%      | 74.02%            | 73.38%       | **80.97%**   |
| % Repeated Actions (Post-Init)| 74.62%             | 15.14%     | **2.19%**   | 4.60%             | 16.34%       | 3.39%        |
| % Mines Flagged               | 15.50%             | 45.50%     | 32.50%      | 41.25%            | 80.75%       | **85.50%**   |
| Total Actions (Post-Init)     | 729                | 535        | 365         | 435               | 710          | 620          |

**Notes:**

*   'Valid Actions' and 'Repeated Actions' percentages exclude the initial L(3,3) action for each game, following the methodology adjustment.
*   The o-series models (`o3-mini`, `o4-mini`) demonstrated significantly higher performance in solving the game and identifying mines compared to the GPT series models tested.
*   '% Coherent Reasoning' was not evaluated automatically and requires manual inspection of conversation logs. 