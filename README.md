# [PongAI](https://github.com/AG2048/PongAI)
By Andy Gong

## Descriptions

University of Toronto 2022 ESC180 Pong Contest Champion :>

<img width="437" alt="image" src="https://user-images.githubusercontent.com/45613281/206371569-23c39b32-82cc-46d0-a93b-cdc5ecf9d087.png">

**How the bot works:**

1. If the ball is approaching, calculate the ball's landing spot
2. Out of all possible orientation of the paddle that can hit the ball, find the one that maximizes (return velocity) * (landing spot's distance from opponent's paddle). This is slightly different from the approach of simply hitting the ball to a corner.
3. When the ball is leaving, apply the same calculation (landing spot and possible return hits) but uses it to find the average of the position the ball will be returned, and let the paddle wait there.

**Potential improvements:**

1. If no hit position secures a win, force the ball to a corner where the return position can be predicted.
2. Calculate how the ball might be returned before the hit, and eliminate any that will force an opponent victory.

Link to pong demo: https://www.youtube.com/watch?v=FITEjcnJWJ8

## How to Run the Code

You will need to install `pygame`

If you don't have it installed, run `pip install pygame` in terminal or run `pip install -r requirements.txt`

- `PongAIvAI.py` is the game engine that calls pong_ai function from the AI (or takes in keyboard input). 
  - To change bots, simply change `paddles[0].move_getter` or `paddles[1].move_getter` on line 390 and 391 to the function of your choice that returns "up" or "down" given the same input to pong_ai.
  - To speed up the game, increase the `clock_rate` on line 372.
  - To change number of points to win, change `score_to_win` on line 374.
  - To only output game result and not display game (which runs the game faster), replace the `1` with `0` on line 393 and 402.
- `pong_ai.py` includes function `pong_ai()` which is my pong AI. Other functions in the file are helper functions for `pong_ai()`.
- `chaser_ai.py` includes its own `pong_ai()` which is the starter AI that only move up or down based on the ball's current location.
- `requirements.txt` includes the packages required to run the game. In this case, it's only `pygame`.
