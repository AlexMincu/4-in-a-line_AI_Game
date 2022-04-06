# <img src="https://github.com/AlexMincu/4-in-a-line_AI_Game/blob/master/resources/icon.png?raw=true?" width="40px"> 4-In-A-Line With a Twist
## Artificial Intelligence Project


#### About
  A turn-based game where two players, X and O, battle each other to create a straight line of at least four identical symbols. The rules are as follows:
    - Player X starts the game
    - A player can place a symbol only if the cell is empty and the sum of opposite symbols from the neighbors of that cell is equal to or less than the sum of 
    the current player's symbols placed in the neighborhood of that cell.
    - A player can move one of its symbols on an empty cell from its neighborhood. 
    - The game ends when one of the player has succesfully created a line of at least four identical symbols.

### Start
  The project was developed using Python3. It requires pygame to run.
  #### Preview:
  ![Game Preview](https://github.com/AlexMincu/4-in-a-line_AI_Game/blob/master/resources/sample.png?raw=true)
  
### Future
  The project is still on going. The game will have a menu and the possibility of a Player Vs AI match. The AI will use the Alpha-Beta Algorithm to compute the next move depending on the difficulty (depth) selected..
