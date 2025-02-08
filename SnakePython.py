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

# Global speed variables
BASE_FPS = 8  # Base game speed.
FPS_INCREMENT = 1  # Increase overall FPS by 1 every 5 foods eaten.

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
    if candidate in snake:
        if candidate == snake[-1] and growth == 0:
            pass
        else:
            return False
    for other in other_snakes:
        if candidate in other:
            return False
    return True


def collision_self(snake, new_head, growth):
    if len(snake) <= 1:
        return False
    for segment in snake[1:-1]:
        if new_head == segment:
            return True
    if new_head == snake[-1] and growth != 0:
        return True
    return False


def collision_other(new_head, other_snake, other_growth):
    if len(other_snake) < 2:
        return False
    for i, segment in enumerate(other_snake[1:], start=1):
        if new_head == segment:
            if i == len(other_snake) - 1 and other_growth == 0:
                continue
            return True
    return False


def free_area(start, obstacles, grid_size, limit=50):
    grid_width, grid_height = grid_size
    q = deque([start])
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


def will_be_trapped(snake, candidate, growth, grid_size, other_snakes):
    grid_width, grid_height = grid_size
    if growth == 0:
        new_snake = [candidate] + snake[:-1]
    else:
        new_snake = [candidate] + snake
    obstacles = set(new_snake)
    for s in other_snakes:
        obstacles |= set(s)
    threshold = len(new_snake) + 2
    area = free_area(candidate, obstacles, grid_size, limit=threshold + 10)
    return area < threshold


def get_random_food(obstacles, grid_width, grid_height):
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


def start_menu(screen, font, WINDOW_WIDTH, WINDOW_HEIGHT):
    menu = True
    difficulty = None
    while menu:
        screen.fill((0, 0, 0))
        title = font.render("Select Difficulty", True, (255, 255, 255))
        option1 = font.render("1: Easy (1 AI, Win Score: 15)", True, (255, 255, 255))
        option2 = font.render("2: Medium (2 AI, Win Score: 20)", True, (255, 255, 255))
        option3 = font.render("3: Hard (3 AI, Win Score: 25)", True, (255, 255, 255))
        screen.blit(
            title, (WINDOW_WIDTH // 2 - title.get_width() // 2, WINDOW_HEIGHT // 3)
        )
        screen.blit(
            option1,
            (WINDOW_WIDTH // 2 - option1.get_width() // 2, WINDOW_HEIGHT // 3 + 40),
        )
        screen.blit(
            option2,
            (WINDOW_WIDTH // 2 - option2.get_width() // 2, WINDOW_HEIGHT // 3 + 80),
        )
        screen.blit(
            option3,
            (WINDOW_WIDTH // 2 - option3.get_width() // 2, WINDOW_HEIGHT // 3 + 120),
        )
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    difficulty = 1
                    menu = False
                elif event.key == pygame.K_2:
                    difficulty = 2
                    menu = False
                elif event.key == pygame.K_3:
                    difficulty = 3
                    menu = False
        pygame.time.wait(100)
    if difficulty == 1:
        return (15, 1)  # win_score, num_ai
    elif difficulty == 2:
        return (20, 2)
    else:
        return (25, 3)


def main_loop():
    pygame.init()
    CELL_SIZE = 20  # Each grid cell is 20x20 pixels

    # Create window.
    info = pygame.display.Info()
    WINDOW_WIDTH, WINDOW_HEIGHT = info.current_w, info.current_h
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
    GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE

    while True:  # Outer loop to return to start menu.
        # --- Show Start Menu ---
        win_score, num_ai = start_menu(screen, font, WINDOW_WIDTH, WINDOW_HEIGHT)
        screen.fill((0, 0, 0))
        sel_text = font.render(
            f"Difficulty selected: {num_ai} AI, Win Score: {win_score}",
            True,
            (255, 255, 255),
        )
        screen.blit(
            sel_text,
            (WINDOW_WIDTH // 2 - sel_text.get_width() // 2, WINDOW_HEIGHT // 2),
        )
        pygame.display.update()
        pygame.time.wait(1500)

        # --- Initialize Game State ---
        # Player snake:
        player_snake = [(3 * GRID_WIDTH // 4, GRID_HEIGHT // 2)]
        player_direction = (1, 0)
        player_growth = 0
        player_score = 0

        # Create AI snakes based on difficulty.
        ai_snakes = []
        ai_growths = []
        ai_scores = []
        if num_ai == 1:
            ai_snakes.append([(GRID_WIDTH // 4, GRID_HEIGHT // 2)])
            ai_growths.append(0)
            ai_scores.append(0)
        elif num_ai == 2:
            ai_snakes.append([(GRID_WIDTH // 4, GRID_HEIGHT // 2 - 2)])
            ai_snakes.append([(GRID_WIDTH // 4, GRID_HEIGHT // 2 + 2)])
            ai_growths.extend([0, 0])
            ai_scores.extend([0, 0])
        elif num_ai == 3:
            ai_snakes.append([(GRID_WIDTH // 4, GRID_HEIGHT // 2 - 4)])
            ai_snakes.append([(GRID_WIDTH // 4, GRID_HEIGHT // 2)])
            ai_snakes.append([(GRID_WIDTH // 4, GRID_HEIGHT // 2 + 4)])
            ai_growths.extend([0, 0, 0])
            ai_scores.extend([0, 0, 0])

        # Food:
        FOOD_COUNT = 5
        foods = []
        obstacles_all = set(player_snake)
        for snake in ai_snakes:
            obstacles_all |= set(snake)
        for _ in range(FOOD_COUNT):
            food = get_random_food(obstacles_all, GRID_WIDTH, GRID_HEIGHT)
            foods.append(food)
            obstacles_all.add(food[0])

        ai_move_delay = 2  # AI snakes update every 2 frames.
        ai_move_counter = 0
        game_over = False
        winner = None

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

            # --- Update AI Snakes (every ai_move_delay frames) ---
            ai_move_counter += 1
            new_ai_heads = []
            if ai_move_counter >= ai_move_delay:
                ai_move_counter = 0
                for idx, snake in enumerate(ai_snakes):
                    other_obstacles = list(player_snake)
                    for jdx, other in enumerate(ai_snakes):
                        if jdx != idx:
                            other_obstacles += other
                    if foods:
                        target_food = min(
                            foods,
                            key=lambda f: toroidal_distance(
                                snake[0], f[0], (GRID_WIDTH, GRID_HEIGHT)
                            ),
                        )
                    else:
                        target_food = None
                    safe_moves = []
                    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        candidate = (
                            (snake[0][0] + dx) % GRID_WIDTH,
                            (snake[0][1] + dy) % GRID_HEIGHT,
                        )
                        if candidate in player_snake or candidate in other_obstacles:
                            continue
                        if candidate in snake:
                            if candidate == snake[-1] and ai_growths[idx] == 0:
                                pass
                            else:
                                continue
                        if not will_be_trapped(
                            snake,
                            candidate,
                            ai_growths[idx],
                            (GRID_WIDTH, GRID_HEIGHT),
                            other_obstacles,
                        ):
                            safe_moves.append((dx, dy))
                    if safe_moves:
                        if target_food is not None:
                            best_move = None
                            best_distance = float("inf")
                            for move in safe_moves:
                                candidate = (
                                    (snake[0][0] + move[0]) % GRID_WIDTH,
                                    (snake[0][1] + move[1]) % GRID_HEIGHT,
                                )
                                dist = toroidal_distance(
                                    candidate, target_food[0], (GRID_WIDTH, GRID_HEIGHT)
                                )
                                if dist < best_distance:
                                    best_distance = dist
                                    best_move = move
                            ai_direction = best_move
                        else:
                            ai_direction = random.choice(safe_moves)
                        new_head = (
                            (snake[0][0] + ai_direction[0]) % GRID_WIDTH,
                            (snake[0][1] + ai_direction[1]) % GRID_HEIGHT,
                        )
                        new_ai_heads.append(new_head)
                    else:
                        new_ai_heads.append(snake[0])
            else:
                for snake in ai_snakes:
                    new_ai_heads.append(snake[0])

            # --- Collision Checks ---
            for head in new_ai_heads:
                if new_player_head == head:
                    winner = "It is a Tie"
                    game_over = True
                    break

            if not game_over:
                if collision_self(player_snake, new_player_head, player_growth):
                    winner = "AI"
                    game_over = True
                else:
                    for idx, snake in enumerate(ai_snakes):
                        if collision_other(new_player_head, snake, ai_growths[idx]):
                            winner = "AI"
                            game_over = True
                            break

            if ai_move_counter == 0 and not game_over:
                for idx, snake in enumerate(ai_snakes):
                    if collision_self(snake, new_ai_heads[idx], ai_growths[idx]):
                        winner = "Player"
                        game_over = True
                        break
                if not game_over:
                    for head in new_ai_heads:
                        if head in player_snake:
                            winner = "Player"
                            game_over = True
                            break

            # --- Update Positions & Process Food ---
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
                    elif eaten_food[1] == YELLOW_FOOD_VALUE:
                        player_score += YELLOW_FOOD_VALUE
                        player_growth += NORMAL_GROWTH
                    else:
                        player_score += GOLD_FOOD_VALUE
                        player_growth += GOLD_GROWTH
                    obstacles_all = set(player_snake)
                    for snake in ai_snakes:
                        obstacles_all |= set(snake)
                    obstacles_all |= set([f[0] for f in foods])
                    new_food = get_random_food(obstacles_all, GRID_WIDTH, GRID_HEIGHT)
                    foods.append(new_food)
                else:
                    if player_growth > 0:
                        player_growth -= 1
                    else:
                        player_snake.pop()

                if ai_move_counter == 0:
                    for idx in range(len(ai_snakes)):
                        ai_snakes[idx].insert(0, new_ai_heads[idx])
                        eaten_food = None
                        for food in foods:
                            if new_ai_heads[idx] == food[0]:
                                eaten_food = food
                                break
                        if eaten_food:
                            foods.remove(eaten_food)
                            if eaten_food[1] == NORMAL_FOOD_VALUE:
                                ai_scores[idx] += NORMAL_FOOD_VALUE
                                ai_growths[idx] += NORMAL_GROWTH
                            elif eaten_food[1] == YELLOW_FOOD_VALUE:
                                ai_scores[idx] += YELLOW_FOOD_VALUE
                                ai_growths[idx] += NORMAL_GROWTH
                            else:
                                ai_scores[idx] += GOLD_FOOD_VALUE
                                ai_growths[idx] += GOLD_GROWTH
                            obstacles_all = set(player_snake)
                            for snake in ai_snakes:
                                obstacles_all |= set(snake)
                            obstacles_all |= set([f[0] for f in foods])
                            new_food = get_random_food(
                                obstacles_all, GRID_WIDTH, GRID_HEIGHT
                            )
                            foods.append(new_food)
                        else:
                            if ai_growths[idx] > 0:
                                ai_growths[idx] -= 1
                            else:
                                ai_snakes[idx].pop()

            # --- Check Winning Condition (Individual Scores) ---
            if player_score >= win_score:
                game_over = True
                winner = "Player"
            else:
                for idx, score in enumerate(ai_scores):
                    if score >= win_score:
                        game_over = True
                        winner = f"AI Snake {idx+1}"
                        break

            # --- Drawing ---
            screen.fill((0, 0, 0))
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
            for idx, snake in enumerate(ai_snakes):
                if snake:
                    head = snake[0]
                    head_rect = pygame.Rect(
                        head[0] * CELL_SIZE, head[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE
                    )
                    pygame.draw.rect(screen, (255, 0, 255), head_rect)
                    for segment in snake[1:]:
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
            ai_total = "  ".join(
                [f"AI{idx+1}: {score}" for idx, score in enumerate(ai_scores)]
            )
            score_text = font.render(
                f"Player: {player_score}  {ai_total}  (Win Score: {win_score})",
                True,
                (255, 255, 255),
            )
            screen.blit(score_text, (10, 10))
            pygame.display.update()

            total_food = player_score + sum(ai_scores)
            current_fps = BASE_FPS + ((total_food // 5) * FPS_INCREMENT)
            clock.tick(current_fps)

        # --- Game Over Screen (Overlay on Game Screen) ---
        # Instead of clearing the game screen, create a semi-transparent overlay.
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)  # Semi-transparent (0-255)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        if winner == "It is a Tie":
            final_text = "It is a Tie. Press Enter to restart, or ESC to exit."
        else:
            final_text = f"{winner} wins! Press Enter to restart, or ESC to exit."
        game_over_text = font.render(final_text, True, (255, 255, 255))
        text_rect = game_over_text.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        )
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
                        waiting = False  # Return to start menu.
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            clock.tick(10)


if __name__ == "__main__":
    main_loop()
