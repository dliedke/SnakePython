# Competitive Snake Game
# 🐍 Competitive Snake Game 🎮

A two-player snake game where you compete against an AI opponent to collect food and grow your snake. The game features normal and special food items, progressive difficulty, and wrapped screen edges.

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

pip install pyinstaller
pyinstaller --onefile SnakePython.py

## ✨ Game Features

- 🎯 Player vs AI gameplay
- 🍎 Two types of food:
  - Normal food (red) - Worth 1 point and grows snake by 4 segments
  - Special food (gold) - Worth 2 points and grows snake by 8 segments
- ⚡ Dynamic difficulty: Game speed increases every 3 food items collected
- 🌐 Wrapped screen edges (toroidal playing field)
- 📊 Score tracking for both players
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

### 📜 Game Rules

1. 🎯 Control your snake (green with yellow head) to collect food
2. ⚠️ Avoid collisions with:
   - Your own body
   - The AI snake (blue with purple head)
   - The AI snake's head (head-to-head collision results in a tie)
3. 🏆 First to score 20 points wins
4. 💥 Game ends if either snake:
   - Collides with itself
   - Collides with the opponent
   - Reaches the winning score

### 💯 Scoring
- 🔴 Normal Food (Red): 1 point
- 🌟 Special Food (Gold): 2 points

## 🔚 Game Over Conditions

The game ends when:
- 🏅 Either player reaches 20 points
- 💥 A snake collides with itself or the opponent
- ⚔️ Both snakes collide head-on (results in a tie)
- 🚫 A snake has no valid moves remaining

Press Enter to restart the game after it ends! 🎮


