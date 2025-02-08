import pygame
import sys
import random
from collections import deque

# --- Constants for Food Types ---
NORMAL_FOOD_VALUE = 1  # Red food (normal) counts as 1 point.
YELLOW_FOOD_VALUE = 1  # Yellow food counts as 1 point.
GOLD_FOOD_VALUE = 2  # Gold food (special) counts as 2 points.

NORMAL_GROWTH = 4  # Red and yellow food cause 4 segments of growth.
GOLD_GROWTH = 8  # Gold food causes 8 segments of growth.

# Food type probabilities:
PROB_RED = 0.3
PROB_YELLOW = 0.5
# (Remaining probability for gold is 0.2)

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


def is_safe_move(candidate, snake, growth, other_snakes):
    """
    Returns True if candidate cell is free for this snake to move into.
    - Allowed to move into its own tail if not growing.
    - The candidate must not be in any cell of any snake in other_snakes.
    """
    if candidate in snake:
        if candidate == snake[-1] and growth == 0:
            pass  # Allowed: tail cell will be removed.
        else:
            return False
    for other in other_snakes:
        if candidate in other:
            return False
    return True


def collision_self(snake, new_head, growth):
    """
    Returns True if new_head collides with the snake's own body
    (moving into the tail cell is allowed if not growing).
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
    (ignoring head-to-head collisions, which are handled separately).
    If new_head equals the other snake’s tail and that snake is not growing,
    then the collision is ignored.
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
    Returns a tuple (position, food_value, food_type) where:
      - 'red' food: NORMAL_FOOD_VALUE, NORMAL_GROWTH (30% chance)
      - 'yellow' food: YELLOW_FOOD_VALUE, NORMAL_GROWTH (50% chance)
      - 'gold' food: GOLD_FOOD_VALUE, GOLD_GROWTH (20% chance)
    """
    pos = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
    while pos in obstacles:
        pos = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
    p = random.random()
    if p < PROB_RED:
        return (pos, NORMAL_FOOD_VALUE, "red")
    elif p < PROB_RED + PROB_YELLOW:
        return (pos, YELLOW_FOOD_VALUE, "yellow")
    else:
        return (pos, GOLD_FOOD_VALUE, "gold")


def free_area(start, obstacles, grid_size, limit=50):
    """
    Performs a BFS from 'start' and returns the number of free cells reachable,
    up to a maximum of 'limit'.
    """
    grid_width, grid_height = grid_size
    q = deque()
    q.append(start)
    seen = set([start])
    count = 0
    while q and count < limit:
        cell = q.popleft()
        count += 1
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nxt = ((cell[0] + dx) % grid_width, (cell[1] + dy) % grid_height)
            if nxt not in seen and nxt not in obstacles:
                seen.add(nxt)
                q.append(nxt)
    return count


def will_be_trapped(snake, candidate, growth, grid_size, other_snakes, threshold=None):
    """
    Uses flood fill to compute the free area available from candidate.
    If the free area is less than a threshold (by default, the new snake's length + 2),
    returns True (i.e. the candidate move would trap the snake).
    """
    grid_width, grid_height = grid_size
    # Simulate new snake state: if not growing, tail is removed.
    if growth == 0:
        new_snake = [candidate] + snake[:-1]
    else:
        new_snake = [candidate] + snake
    # Define obstacles as the union of the new snake and all cells from other snakes.
    obstacles = set(new_snake)
    for s in other_snakes:
        obstacles |= set(s)
    if threshold is None:
        threshold = len(new_snake) + 2
    area = free_area(candidate, obstacles, grid_size, limit=threshold + 10)
    return area < threshold


# --- Main Game Loop with Restart ---
def main():
    pygame.init()
    CELL_SIZE = 20  # Each grid cell is 20x20 pixels

    # Create a window sized to fill the display.
    info = pygame.display.Info()
    WINDOW_WIDTH, WINDOW_HEIGHT = info.current_w, info.current_h
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
    GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE

    WIN_SCORE = 25  # A snake wins when its individual score reaches 25.
    BASE_FPS = 8  # Base game speed.
    FPS_INCREMENT = 1  # Increase overall FPS by 1 every 5 foods eaten.
    ai_move_delay = 2  # AI snakes update their move every 2 frames.

    while True:  # Outer loop for restarting the game.
        # --- Initialize Game State ---
        # Player snake:
        player_snake = [(3 * GRID_WIDTH // 4, GRID_HEIGHT // 2)]
        player_direction = (1, 0)
        player_growth = 0
        player_score = 0

        # AI Snake 1:
        ai_snake1 = [(GRID_WIDTH // 4, GRID_HEIGHT // 2 - 2)]
        ai_growth1 = 0
        ai_score1 = 0

        # AI Snake 2:
        ai_snake2 = [(GRID_WIDTH // 4, GRID_HEIGHT // 2 + 2)]
        ai_growth2 = 0
        ai_score2 = 0

        # Food:
        FOOD_COUNT = 5
        foods = []
        obstacles_all = set(player_snake + ai_snake1 + ai_snake2)
        for _ in range(FOOD_COUNT):
            food = get_random_food(obstacles_all, GRID_WIDTH, GRID_HEIGHT)
            foods.append(food)
            obstacles_all.add(food[0])

        game_over = False
        winner = None
        ai_move_counter = 0  # Counter for AI update delay

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

            # --- Compute New Head for Player ---
            new_player_head = (
                (player_snake[0][0] + player_direction[0]) % GRID_WIDTH,
                (player_snake[0][1] + player_direction[1]) % GRID_HEIGHT,
            )

            # --- Update AI Snakes (only every ai_move_delay frames) ---
            ai_move_counter += 1
            if ai_move_counter >= ai_move_delay:
                ai_move_counter = 0

                # For AI Snake 1:
                if foods:
                    target_food1 = min(
                        foods,
                        key=lambda f: toroidal_distance(
                            ai_snake1[0], f[0], (GRID_WIDTH, GRID_HEIGHT)
                        ),
                    )
                else:
                    target_food1 = None
                safe_moves_ai1 = []
                # For AI Snake 1, obstacles: player_snake (complete) + ai_snake2.
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    candidate = (
                        (ai_snake1[0][0] + dx) % GRID_WIDTH,
                        (ai_snake1[0][1] + dy) % GRID_HEIGHT,
                    )
                    # Use a stricter check for obstacles (no tail exception for others).
                    if candidate in player_snake or candidate in ai_snake2:
                        continue
                    if candidate in ai_snake1:
                        if candidate == ai_snake1[-1] and ai_growth1 == 0:
                            pass
                        else:
                            continue
                    # Now check if moving to candidate would trap the snake.
                    if not will_be_trapped(
                        ai_snake1,
                        candidate,
                        ai_growth1,
                        (GRID_WIDTH, GRID_HEIGHT),
                        player_snake + ai_snake2,
                    ):
                        safe_moves_ai1.append((dx, dy))
                if safe_moves_ai1:
                    if target_food1 is not None:
                        best_move = None
                        best_distance = float("inf")
                        for move in safe_moves_ai1:
                            candidate = (
                                (ai_snake1[0][0] + move[0]) % GRID_WIDTH,
                                (ai_snake1[0][1] + move[1]) % GRID_HEIGHT,
                            )
                            dist = toroidal_distance(
                                candidate, target_food1[0], (GRID_WIDTH, GRID_HEIGHT)
                            )
                            if dist < best_distance:
                                best_distance = dist
                                best_move = move
                        ai_direction1 = best_move
                    else:
                        ai_direction1 = random.choice(safe_moves_ai1)
                    new_ai_head1 = (
                        (ai_snake1[0][0] + ai_direction1[0]) % GRID_WIDTH,
                        (ai_snake1[0][1] + ai_direction1[1]) % GRID_HEIGHT,
                    )
                else:
                    winner = "Player"
                    game_over = True
                    new_ai_head1 = ai_snake1[0]

                # For AI Snake 2:
                if foods:
                    target_food2 = min(
                        foods,
                        key=lambda f: toroidal_distance(
                            ai_snake2[0], f[0], (GRID_WIDTH, GRID_HEIGHT)
                        ),
                    )
                else:
                    target_food2 = None
                safe_moves_ai2 = []
                # For AI Snake 2, obstacles: player_snake (complete) + ai_snake1.
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    candidate = (
                        (ai_snake2[0][0] + dx) % GRID_WIDTH,
                        (ai_snake2[0][1] + dy) % GRID_HEIGHT,
                    )
                    if candidate in player_snake or candidate in ai_snake1:
                        continue
                    if candidate in ai_snake2:
                        if candidate == ai_snake2[-1] and ai_growth2 == 0:
                            pass
                        else:
                            continue
                    if not will_be_trapped(
                        ai_snake2,
                        candidate,
                        ai_growth2,
                        (GRID_WIDTH, GRID_HEIGHT),
                        player_snake + ai_snake1,
                    ):
                        safe_moves_ai2.append((dx, dy))
                if safe_moves_ai2:
                    if target_food2 is not None:
                        best_move = None
                        best_distance = float("inf")
                        for move in safe_moves_ai2:
                            candidate = (
                                (ai_snake2[0][0] + move[0]) % GRID_WIDTH,
                                (ai_snake2[0][1] + move[1]) % GRID_HEIGHT,
                            )
                            dist = toroidal_distance(
                                candidate, target_food2[0], (GRID_WIDTH, GRID_HEIGHT)
                            )
                            if dist < best_distance:
                                best_distance = dist
                                best_move = move
                        ai_direction2 = best_move
                    else:
                        ai_direction2 = random.choice(safe_moves_ai2)
                    new_ai_head2 = (
                        (ai_snake2[0][0] + ai_direction2[0]) % GRID_WIDTH,
                        (ai_snake2[0][1] + ai_direction2[1]) % GRID_HEIGHT,
                    )
                else:
                    winner = "Player"
                    game_over = True
                    new_ai_head2 = ai_snake2[0]
            else:
                new_ai_head1 = ai_snake1[0]
                new_ai_head2 = ai_snake2[0]

            # --- Collision Checks ---
            # Head-to-head: if player's new head equals any AI snake's new head → Tie.
            if new_player_head == new_ai_head1 or new_player_head == new_ai_head2:
                winner = "Tie"
                game_over = True
            # Player collision checks:
            elif collision_self(player_snake, new_player_head, player_growth):
                winner = "AI"
                game_over = True
            elif collision_other(
                new_player_head, ai_snake1, ai_growth1
            ) or collision_other(new_player_head, ai_snake2, ai_growth2):
                winner = "AI"
                game_over = True
            # AI collision checks (only when updating):
            elif ai_move_counter == 0 and collision_self(
                ai_snake1, new_ai_head1, ai_growth1
            ):
                winner = "Player"
                game_over = True
            elif ai_move_counter == 0 and collision_self(
                ai_snake2, new_ai_head2, ai_growth2
            ):
                winner = "Player"
                game_over = True
            # Check if AI snake's new head is in any cell of the player's snake:
            elif ai_move_counter == 0 and (new_ai_head1 in player_snake):
                winner = "Player"
                game_over = True
            elif ai_move_counter == 0 and (new_ai_head2 in player_snake):
                winner = "Player"
                game_over = True

            # --- Update Positions & Process Food ---
            if not game_over:
                # Update player snake:
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
                    elif eaten_food[1] == YELLOW_FOOD_VALUE:
                        player_score += YELLOW_FOOD_VALUE
                        player_growth += NORMAL_GROWTH
                    else:
                        player_score += GOLD_FOOD_VALUE
                        player_growth += GOLD_GROWTH
                    obstacles_all = set(
                        player_snake + ai_snake1 + ai_snake2 + [f[0] for f in foods]
                    )
                    new_food = get_random_food(obstacles_all, GRID_WIDTH, GRID_HEIGHT)
                    foods.append(new_food)
                else:
                    if player_growth > 0:
                        player_growth -= 1
                    else:
                        player_snake.pop()

                if ai_move_counter == 0:
                    # Update AI Snake 1:
                    ai_snake1.insert(0, new_ai_head1)
                    eaten_food = None
                    for food in foods:
                        if new_ai_head1 == food[0]:
                            eaten_food = food
                            break
                    if eaten_food:
                        foods.remove(eaten_food)
                        if eaten_food[1] == NORMAL_FOOD_VALUE:
                            ai_score1 += NORMAL_FOOD_VALUE
                            ai_growth1 += NORMAL_GROWTH
                        elif eaten_food[1] == YELLOW_FOOD_VALUE:
                            ai_score1 += YELLOW_FOOD_VALUE
                            ai_growth1 += NORMAL_GROWTH
                        else:
                            ai_score1 += GOLD_FOOD_VALUE
                            ai_growth1 += GOLD_GROWTH
                        obstacles_all = set(
                            player_snake + ai_snake1 + ai_snake2 + [f[0] for f in foods]
                        )
                        new_food = get_random_food(
                            obstacles_all, GRID_WIDTH, GRID_HEIGHT
                        )
                        foods.append(new_food)
                    else:
                        if ai_growth1 > 0:
                            ai_growth1 -= 1
                        else:
                            ai_snake1.pop()

                    # Update AI Snake 2:
                    ai_snake2.insert(0, new_ai_head2)
                    eaten_food = None
                    for food in foods:
                        if new_ai_head2 == food[0]:
                            eaten_food = food
                            break
                    if eaten_food:
                        foods.remove(eaten_food)
                        if eaten_food[1] == NORMAL_FOOD_VALUE:
                            ai_score2 += NORMAL_FOOD_VALUE
                            ai_growth2 += NORMAL_GROWTH
                        elif eaten_food[1] == YELLOW_FOOD_VALUE:
                            ai_score2 += YELLOW_FOOD_VALUE
                            ai_growth2 += NORMAL_GROWTH
                        else:
                            ai_score2 += GOLD_FOOD_VALUE
                            ai_growth2 += GOLD_GROWTH
                        obstacles_all = set(
                            player_snake + ai_snake1 + ai_snake2 + [f[0] for f in foods]
                        )
                        new_food = get_random_food(
                            obstacles_all, GRID_WIDTH, GRID_HEIGHT
                        )
                        foods.append(new_food)
                    else:
                        if ai_growth2 > 0:
                            ai_growth2 -= 1
                        else:
                            ai_snake2.pop()

            # --- Check Winning Condition (Individual Scores) ---
            if player_score >= WIN_SCORE:
                game_over = True
                winner = "Player"
            elif ai_score1 >= WIN_SCORE:
                game_over = True
                winner = "AI Snake 1"
            elif ai_score2 >= WIN_SCORE:
                game_over = True
                winner = "AI Snake 2"

            # --- Drawing ---
            screen.fill((0, 0, 0))
            # Draw food as filled circles.
            for food in foods:
                center = (
                    food[0][0] * CELL_SIZE + CELL_SIZE // 2,
                    food[0][1] * CELL_SIZE + CELL_SIZE // 2,
                )
                radius = CELL_SIZE // 2
                if food[1] == NORMAL_FOOD_VALUE:
                    color = (255, 0, 0)  # Red
                elif food[1] == YELLOW_FOOD_VALUE:
                    color = (255, 255, 0)  # Yellow
                else:
                    color = (255, 215, 0)  # Gold
                pygame.draw.circle(screen, color, center, radius)
            # Draw AI Snake 1:
            if ai_snake1:
                head = ai_snake1[0]
                head_rect = pygame.Rect(
                    head[0] * CELL_SIZE, head[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(
                    screen, (255, 0, 255), head_rect
                )  # Bright magenta head
                for segment in ai_snake1[1:]:
                    seg_rect = pygame.Rect(
                        segment[0] * CELL_SIZE,
                        segment[1] * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE,
                    )
                    pygame.draw.rect(screen, (0, 0, 255), seg_rect)  # Light blue body
            # Draw AI Snake 2:
            if ai_snake2:
                head = ai_snake2[0]
                head_rect = pygame.Rect(
                    head[0] * CELL_SIZE, head[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(screen, (255, 0, 255), head_rect)
                for segment in ai_snake2[1:]:
                    seg_rect = pygame.Rect(
                        segment[0] * CELL_SIZE,
                        segment[1] * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE,
                    )
                    pygame.draw.rect(screen, (0, 0, 255), seg_rect)
            # Draw Player Snake:
            if player_snake:
                head = player_snake[0]
                head_rect = pygame.Rect(
                    head[0] * CELL_SIZE, head[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(screen, (255, 255, 0), head_rect)  # Bright yellow head
                for segment in player_snake[1:]:
                    seg_rect = pygame.Rect(
                        segment[0] * CELL_SIZE,
                        segment[1] * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE,
                    )
                    pygame.draw.rect(screen, (0, 255, 0), seg_rect)  # Light green body
            score_text = font.render(
                f"Player: {player_score}  AI1: {ai_score1}  AI2: {ai_score2}",
                True,
                (255, 255, 255),
            )
            screen.blit(score_text, (10, 10))
            pygame.display.update()

            total_food = player_score + ai_score1 + ai_score2
            current_fps = BASE_FPS + ((total_food // 5) * FPS_INCREMENT)
            clock.tick(current_fps)

        # --- Game Over Screen ---
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
