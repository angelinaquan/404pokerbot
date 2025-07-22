# 404 pokerbot

Competed in the MIT 2025 Pokerbots Competition

# Introduction
Our pokerbot was designed to make strategic decisions based on hand strength, expected value (EV) calculations, and Monte Carlo simulations to estimate win probabilities. The goal was to optimize play across different streets while maintaining a balance between risk and reward.

# Development and Strategy
2.1 Monte Carlo Simulations for Hand Strength Evaluation
To assess our hand’s strength, we implemented a Monte Carlo simulation that:
- Estimated the probabilities of winning (pWin), tying (pTie), and losing (pLose) by simulating random opponent hands and completing the board.
- Used 100 iterations per evaluation for computational efficiency while maintaining reasonable accuracy.
- Converted hole and board cards into `eval7` objects for consistent evaluations.

2.2 Pre-Flop Strategy
- Applied a threshold-based folding rule, where if `strength = pWin + 0.5 * pTie` was below 0.50, the bot folded unless checking was free.
- Ensured the bot only continued with reasonable hands and minimized unnecessary losses.

2.3 Post-Flop Strategy: Expected Value (EV) Calculation
Post-flop, our bot made decisions based on an EV-based approach:
- Calculated the current pot size and potential pot after calling.
- Estimated the expected value of calling using:
  EV_call = pWin * (pot_after_call) + pTie * (pot_after_call / 2) - continue_cost
- If the EV of calling was negative, the bot folded unless forced to continue.
- If the EV of calling was positive, the bot considered raising if `strength > 0.6`.

2.4 Raising Strategy
- When raising was an option, calculated the minimum and maximum raise bounds.
- If our strength was sufficiently high (`strength > 0.6`), we raised a moderate amount to extract value.
- Otherwise, we called to keep the opponent engaged while minimizing risks.
<img width="468" height="658" alt="image" src="https://github.com/user-attachments/assets/ad8075d9-68aa-449f-bbe2-0e2656e519bb" />
