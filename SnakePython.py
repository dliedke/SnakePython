import pygame
import sys
import random

# --- Constants for Food ---
NORMAL_FOOD_VALUE = 1  # Normal food counts as 1 point.
SPECIAL_FOOD_VALUE = 2  # Special food counts as 2 points.
NORMAL_GROWTH = 4  # Normal food makes the snake grow by 4 segments.
SPECIAL_GROWTH = 8  # Special food makes the snake grow by 8 segments.
SPECIAL_PROB = 0.2  # 20% chance for a spawned food to be special.

# --- Utility Functions ---


def compute_direction(current, next_cell, grid_size):
    grid_width, grid_height = grid_size
    dx = next_cell[0] - current[0]
    dy = next_cell[1] - current[1]
    if dx > grid_width // 2:
        dx -= grid_width
    elif dx < -grid_width // 2:
        dx += grid_width
    if dy > grid_height // 2:
        dy -= grid_height
    elif dy < -grid_height // 2:
        dy += grid_height
    return (dx, dy)


def toroidal_distance(a, b, grid_size):
    grid_width, grid_height = grid_size
    dx = abs(a[0] - b[0])
    dx = min(dx, grid_width - dx)
    dy = abs(a[1] - b[1])
    dy = min(dy, grid_height - dy)
    return dx + dy


def is_safe_move(candidate, snake, growth, other_snake):
    """
    Returns True if candidate cell is free for this snake to move into.
    For its own body, moving into the tail cell is allowed if not growing.
    Also, the candidate must not be occupied by any cell of the other snake.
    """
    # Check own snake:
    if candidate in snake:
        if candidate == snake[-1] and growth == 0:
            pass  # allowed: tail cell will be removed.
        else:
            return False
    # Check the other snake (no tail exception for the opponent):
    if candidate in other_snake:
        return False
    return True


def collision_self(snake, new_head, growth):
    """
    Returns True if new_head collides with snake's body—
    except that moving into the tail cell is allowed if not growing.
    (We check all segments except the head.)
    """
    if len(snake) <= 1:
        return False
    for segment in snake[1:-1]:
        if new_head == segment:
            return True
    if new_head == snake[-1] and growth != 0:
        return True
    return False


def collision_other(new_head, other_snake, other_growth):
    """
    Returns True if new_head collides with any part of the other snake’s body
    (excluding a head-to-head case, which is handled separately).
    If new_head equals the other snake’s tail and that snake is not growing,
    then that collision is ignored.
    """
    if len(other_snake) < 2:
        return False
    for i, segment in enumerate(other_snake[1:], start=1):
        if new_head == segment:
            if i == len(other_snake) - 1 and other_growth == 0:
                continue
            return True
    return False


def get_random_food(obstacles, grid_width, grid_height):
    """
    Returns a tuple (position, food_value) where food_value is either 1 (normal) or 2 (special).
    """
    pos = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
    while pos in obstacles:
        pos = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
    if random.random() < SPECIAL_PROB:
        food_value = SPECIAL_FOOD_VALUE
    else:
        food_value = NORMAL_FOOD_VALUE
    return (pos, food_value)


# --- Main Game Loop with Restart ---
def main():
    pygame.init()
    CELL_SIZE = 20  # Pixel size for each grid cell

    # Create a window sized to fill the display.
    info = pygame.display.Info()
    WINDOW_WIDTH, WINDOW_HEIGHT = info.current_w, info.current_h
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
    GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE

    WIN_SCORE = 20  # Individual snake must eat 20 foods to win.
    BASE_FPS = 8  # Base game speed.
    FPS_INCREMENT = 2  # Increase overall FPS by 2 every 3 foods eaten.
    ai_move_delay = 2  # AI snake moves only every 2 frames.

    while True:  # Outer loop for restarting the game.
        # --- Initialize Game State ---
        ai_snake = [(GRID_WIDTH // 4, GRID_HEIGHT // 2)]
        player_snake = [(3 * GRID_WIDTH // 4, GRID_HEIGHT // 2)]
        player_direction = (1, 0)  # Initial direction for the player

        ai_score = 0
        player_score = 0
        ai_growth = 0  # When > 0, tail is not removed (snake grows)
        player_growth = 0

        FOOD_COUNT = 3
        foods = []
        obstacles_all = set(ai_snake + player_snake)
        for _ in range(FOOD_COUNT):
            food = get_random_food(obstacles_all, GRID_WIDTH, GRID_HEIGHT)
            foods.append(food)
            obstacles_all.add(food[0])  # Only the position

        game_over = False
        winner = None
        ai_move_counter = 0  # Counter to delay AI moves

        # --- Game Round Loop ---
        while not game_over:
            # --- Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    # Player controls (avoid direct reversal if snake length > 1)
                    elif event.key == pygame.K_UP:
                        new_dir = (0, -1)
                        if len(player_snake) == 1 or new_dir != (
                            -player_direction[0],
                            -player_direction[1],
                        ):
                            player_direction = new_dir
                    elif event.key == pygame.K_DOWN:
                        new_dir = (0, 1)
                        if len(player_snake) == 1 or new_dir != (
                            -player_direction[0],
                            -player_direction[1],
                        ):
                            player_direction = new_dir
                    elif event.key == pygame.K_LEFT:
                        new_dir = (-1, 0)
                        if len(player_snake) == 1 or new_dir != (
                            -player_direction[0],
                            -player_direction[1],
                        ):
                            player_direction = new_dir
                    elif event.key == pygame.K_RIGHT:
                        new_dir = (1, 0)
                        if len(player_snake) == 1 or new_dir != (
                            -player_direction[0],
                            -player_direction[1],
                        ):
                            player_direction = new_dir

            # --- Compute New Head Positions ---
            new_player_head = (
                (player_snake[0][0] + player_direction[0]) % GRID_WIDTH,
                (player_snake[0][1] + player_direction[1]) % GRID_HEIGHT,
            )

            # Update AI snake only every ai_move_delay frames.
            ai_move_counter += 1
            if ai_move_counter >= ai_move_delay:
                ai_move_counter = 0
                if foods:
                    target_food = min(
                        foods,
                        key=lambda f: toroidal_distance(
                            ai_snake[0], f[0], (GRID_WIDTH, GRID_HEIGHT)
                        ),
                    )
                else:
                    target_food = None
                safe_moves_ai = []
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    candidate = (
                        (ai_snake[0][0] + dx) % GRID_WIDTH,
                        (ai_snake[0][1] + dy) % GRID_HEIGHT,
                    )
                    if is_safe_move(candidate, ai_snake, ai_growth, player_snake):
                        safe_moves_ai.append((dx, dy))
                if safe_moves_ai:
                    if target_food is not None:
                        best_move = None
                        best_distance = float("inf")
                        for move in safe_moves_ai:
                            candidate = (
                                (ai_snake[0][0] + move[0]) % GRID_WIDTH,
                                (ai_snake[0][1] + move[1]) % GRID_HEIGHT,
                            )
                            dist = toroidal_distance(
                                candidate, target_food[0], (GRID_WIDTH, GRID_HEIGHT)
                            )
                            if dist < best_distance:
                                best_distance = dist
                                best_move = move
                        ai_direction = best_move
                    else:
                        ai_direction = random.choice(safe_moves_ai)
                    new_ai_head = (
                        (ai_snake[0][0] + ai_direction[0]) % GRID_WIDTH,
                        (ai_snake[0][1] + ai_direction[1]) % GRID_HEIGHT,
                    )
                else:
                    winner = "Player"
                    game_over = True
                    new_ai_head = ai_snake[0]
            else:
                new_ai_head = ai_snake[0]

            # --- Collision Checks ---
            if new_player_head == new_ai_head:
                winner = "Tie"
                game_over = True
            elif collision_self(player_snake, new_player_head, player_growth):
                winner = "AI"
                game_over = True
            elif collision_other(new_player_head, ai_snake, ai_growth):
                winner = "AI"
                game_over = True
            elif ai_move_counter == 0 and collision_self(
                ai_snake, new_ai_head, ai_growth
            ):
                winner = "Player"
                game_over = True
            elif ai_move_counter == 0 and collision_other(
                new_ai_head, player_snake, player_growth
            ):
                winner = "Player"
                game_over = True

            # --- Update Snake Positions and Process Food ---
            if not game_over:
                player_snake.insert(0, new_player_head)
                eaten_food = None
                for food in foods:
                    if new_player_head == food[0]:
                        eaten_food = food
                        break
                if eaten_food:
                    foods.remove(eaten_food)
                    if eaten_food[1] == NORMAL_FOOD_VALUE:
                        player_score += NORMAL_FOOD_VALUE
                        player_growth += NORMAL_GROWTH
                    else:
                        player_score += SPECIAL_FOOD_VALUE
                        player_growth += SPECIAL_GROWTH
                    obstacles_all = set(ai_snake + player_snake + [f[0] for f in foods])
                    new_food = get_random_food(obstacles_all, GRID_WIDTH, GRID_HEIGHT)
                    foods.append(new_food)
                else:
                    if player_growth > 0:
                        player_growth -= 1
                    else:
                        player_snake.pop()

                if ai_move_counter == 0:
                    ai_snake.insert(0, new_ai_head)
                    eaten_food = None
                    for food in foods:
                        if new_ai_head == food[0]:
                            eaten_food = food
                            break
                    if eaten_food:
                        foods.remove(eaten_food)
                        if eaten_food[1] == NORMAL_FOOD_VALUE:
                            ai_score += NORMAL_FOOD_VALUE
                            ai_growth += NORMAL_GROWTH
                        else:
                            ai_score += SPECIAL_FOOD_VALUE
                            ai_growth += SPECIAL_GROWTH
                        obstacles_all = set(
                            ai_snake + player_snake + [f[0] for f in foods]
                        )
                        new_food = get_random_food(
                            obstacles_all, GRID_WIDTH, GRID_HEIGHT
                        )
                        foods.append(new_food)
                    else:
                        if ai_growth > 0:
                            ai_growth -= 1
                        else:
                            ai_snake.pop()

            # --- Check Winning Condition (Individual Score) ---
            if player_score >= WIN_SCORE:
                game_over = True
                winner = "Player"
            elif ai_score >= WIN_SCORE:
                game_over = True
                winner = "AI"

            # --- Drawing ---
            screen.fill((0, 0, 0))
            for food in foods:
                center = (
                    food[0][0] * CELL_SIZE + CELL_SIZE // 2,
                    food[0][1] * CELL_SIZE + CELL_SIZE // 2,
                )
                radius = CELL_SIZE // 2
                color = (255, 0, 0) if food[1] == NORMAL_FOOD_VALUE else (255, 215, 0)
                pygame.draw.circle(screen, color, center, radius)
            if ai_snake:
                head = ai_snake[0]
                head_rect = pygame.Rect(
                    head[0] * CELL_SIZE, head[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(screen, (255, 0, 255), head_rect)
                for segment in ai_snake[1:]:
                    seg_rect = pygame.Rect(
                        segment[0] * CELL_SIZE,
                        segment[1] * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE,
                    )
                    pygame.draw.rect(screen, (0, 0, 255), seg_rect)
            if player_snake:
                head = player_snake[0]
                head_rect = pygame.Rect(
                    head[0] * CELL_SIZE, head[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(screen, (255, 255, 0), head_rect)
                for segment in player_snake[1:]:
                    seg_rect = pygame.Rect(
                        segment[0] * CELL_SIZE,
                        segment[1] * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE,
                    )
                    pygame.draw.rect(screen, (0, 255, 0), seg_rect)
            score_text = font.render(
                f"Player: {player_score}  AI: {ai_score}", True, (255, 255, 255)
            )
            screen.blit(score_text, (10, 10))
            pygame.display.update()

            current_fps = BASE_FPS + (((player_score + ai_score) // 3) * FPS_INCREMENT)
            clock.tick(current_fps)

        # --- Game Over: Freeze and Display Message ---
        game_over_text = font.render(
            f"{winner} wins! Press Enter to restart", True, (255, 255, 255)
        )
        text_rect = game_over_text.get_rect(midtop=(WINDOW_WIDTH // 2, 10))
        screen.blit(game_over_text, text_rect)
        pygame.display.update()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        waiting = False
            clock.tick(10)


# --- Entry Point ---
if __name__ == "__main__":
    main()
    