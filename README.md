# PongAI
By Andy Gong

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
