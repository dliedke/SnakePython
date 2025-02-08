# Competitive Snake Game
# 🐍 Competitive Snake Game 🎮

A competitive snake game where you face off against AI opponents. Choose your difficulty level and compete to collect food and grow your snake. Features normal and special food items, progressive difficulty, and wrapped screen edges.

## ☀️ Direct run (Compiled exe)

Download compiled version and run locally:
[SnakePython.exe](https://github.com/dliedke/SnakePython/blob/master/dist/SnakePython.exe)

## 🛠️ Installation Requirements

1. Python 3.x
2. Pygame library

To install Pygame, run:

pip install pygame

## 🚀 How to Run

1. Save the game code as `SnakePython.py`
2. Open a terminal/command prompt
3. Navigate to the game directory
4. Run the command:

python SnakePython.py

## Compile to EXE

- pip install pyinstaller
- pyinstaller --onefile SnakePython.py

## ✨ Game Features

- 🎯 Player vs AI gameplay with three difficulty levels:
  - Easy: 1 AI opponent, win score of 15
  - Medium: 2 AI opponents, win score of 20
  - Hard: 3 AI opponents, win score of 25
- 🍎 Three types of food:
  - Normal food (red) - Worth 1 point, grows snake by 4 segments
  - Yellow food - Worth 1 point, grows snake by 4 segments
  - Special food (gold) - Worth 2 points, grows snake by 8 segments
- ⚡ Dynamic difficulty: Game speed increases for every 5 food items collected
- 🌐 Wrapped screen edges (toroidal playing field)
- 📊 Score tracking for all players
- 🖥️ Full-screen display

## 🎮 How to Play

### 🕹️ Controls
- Arrow Keys: Control player snake direction
  - ↑: Move Up
  - ↓: Move Down
  - ←: Move Left
  - →: Move Right
- ESC: Quit game
- Enter: Restart game after game over
- 1, 2, 3: Select difficulty level at start

### 📜 Game Rules

1. 🎯 Control your snake (green with yellow head) to collect food
2. ⚠️ Avoid collisions with:
   - Your own body
   - The AI snakes (blue with purple heads)
   - The AI snakes' heads (head-to-head collision results in a tie)
3. 🏆 First to reach the win score for your difficulty wins:
   - Easy: 15 points
   - Medium: 20 points
   - Hard: 25 points
4. 💥 Game ends if any snake:
   - Collides with itself
   - Collides with an opponent
   - Reaches the winning score

### 💯 Scoring
- 🔴 Normal Food (Red): 1 point
- 🟡 Yellow Food: 1 point
- 🌟 Special Food (Gold): 2 points

## 🔚 Game Over Conditions

The game ends when:
- 🏅 Any player reaches the win score for the chosen difficulty
- 💥 A snake collides with itself or an opponent
- ⚔️ Snakes collide head-on (results in a tie)
- 🚫 A snake has no valid moves remaining

Press Enter to restart the game after it ends! 🎮