import os
import random
import sys
import time

try:
    import msvcrt  # type: ignore[attr-defined]
except ImportError:
    msvcrt = None


WIDTH = 30
HEIGHT = 18
INITIAL_SPEED = 0.15
MIN_SPEED = 0.05


def clear_screen() -> None:
    os.system("cls")


def draw_board(snake, fruit, score) -> None:
    clear_screen()
    print("Простая змейка — управление стрелками (или WASD), выход: Q")
    print(f"Очки: {score}")
    horizontal_border = "+" + "-" * WIDTH + "+"
    print(horizontal_border)

    body = set(snake[1:])
    head_y, head_x = snake[0]

    for y in range(HEIGHT):
        row = ["|"]
        for x in range(WIDTH):
            if (y, x) == (head_y, head_x):
                row.append("O")
            elif (y, x) in body:
                row.append("o")
            elif (y, x) == fruit:
                row.append("*")
            else:
                row.append(" ")
        row.append("|")
        print("".join(row))

    print(horizontal_border)


def random_free_cell(snake):
    free_cells = [(y, x) for y in range(HEIGHT) for x in range(WIDTH) if (y, x) not in snake]
    return random.choice(free_cells) if free_cells else None


def read_direction(current_direction):
    opposite = {
        (0, 1): (0, -1),
        (0, -1): (0, 1),
        (1, 0): (-1, 0),
        (-1, 0): (1, 0),
    }

    if msvcrt is None:
        return current_direction

    if not msvcrt.kbhit():
        return current_direction

    key = msvcrt.getch()

    # Arrow keys arrive as two-byte sequences starting with 224 (0xE0)
    if key in (b"\x00", b"\xe0"):
        key = msvcrt.getch()
        mapping = {
            b"H": (-1, 0),  # Up
            b"P": (1, 0),   # Down
            b"K": (0, -1),  # Left
            b"M": (0, 1),   # Right
        }
        new_dir = mapping.get(key, current_direction)
    else:
        key_upper = key.decode("utf-8", errors="ignore").upper()
        mapping = {
            "W": (-1, 0),
            "S": (1, 0),
            "A": (0, -1),
            "D": (0, 1),
        }
        if key_upper == "Q":
            raise KeyboardInterrupt
        new_dir = mapping.get(key_upper, current_direction)

    # Prevent the snake from moving directly backwards
    if new_dir == opposite[current_direction]:
        return current_direction

    return new_dir


def run_game():
    if msvcrt is None:
        print("Эта версия игры работает только в Windows-консоли (нужен модуль msvcrt).")
        print("Запустите скрипт в стандартной командной строке Windows.")
        return

    snake = [(HEIGHT // 2, WIDTH // 2)]
    direction = (0, 1)
    fruit = random_free_cell(snake)
    score = 0
    speed = INITIAL_SPEED

    try:
        while True:
            draw_board(snake, fruit, score)

            start_time = time.time()
            while time.time() - start_time < speed:
                if msvcrt and msvcrt.kbhit():
                    direction = read_direction(direction)
                time.sleep(0.01)

            head_y, head_x = snake[0]
            delta_y, delta_x = direction
            new_head = (head_y + delta_y, head_x + delta_x)

            if (
                new_head[0] < 0
                or new_head[0] >= HEIGHT
                or new_head[1] < 0
                or new_head[1] >= WIDTH
                or new_head in snake
            ):
                draw_board(snake, fruit, score)
                print("\nИгра окончена!")
                print(f"Ваш счёт: {score}")
                break

            snake.insert(0, new_head)

            if new_head == fruit:
                score += 1
                fruit = random_free_cell(snake)
                speed = max(MIN_SPEED, speed * 0.95)
            else:
                snake.pop()

            if fruit is None:
                draw_board(snake, fruit, score)
                print("\nПоздравляем! Вы заполнили всё поле!")
                print(f"Финальный счёт: {score}")
                break

    except KeyboardInterrupt:
        clear_screen()
        print("Вы завершили игру.")
        return
    finally:
        print("\nНажмите любую клавишу для выхода...")
        if msvcrt:
            msvcrt.getch()


if __name__ == "__main__":
    random.seed()
    run_game()
"""Simple Snake game implemented with pygame.

Run the game with:
    python snake.py
"""

import random
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Tuple

try:
    import pygame
except ImportError:  # pragma: no cover - best-effort helper for quick start
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
    import pygame


# Grid configuration
TILE_SIZE = 24
GRID_WIDTH = 25
GRID_HEIGHT = 20
SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE

# Colors (RGB)
BLACK = (22, 22, 22)
DARK_GREY = (40, 40, 40)
LIGHT_GREY = (70, 70, 70)
GREEN = (40, 200, 80)
FOREST = (20, 120, 50)
RED = (220, 50, 50)
WHITE = (240, 240, 240)


class Direction(Enum):
    """Cardinal directions snake can travel in."""

    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

    @property
    def delta(self) -> Tuple[int, int]:
        if self is Direction.UP:
            return (0, -1)
        if self is Direction.DOWN:
            return (0, 1)
        if self is Direction.LEFT:
            return (-1, 0)
        if self is Direction.RIGHT:
            return (1, 0)
        raise ValueError("Unknown direction")

    def is_opposite(self, other: "Direction") -> bool:
        return (
            (self is Direction.UP and other is Direction.DOWN)
            or (self is Direction.DOWN and other is Direction.UP)
            or (self is Direction.LEFT and other is Direction.RIGHT)
            or (self is Direction.RIGHT and other is Direction.LEFT)
        )


@dataclass
class Snake:
    """Represents the snake body and direction."""

    body: List[Tuple[int, int]]
    direction: Direction

    def head(self) -> Tuple[int, int]:
        return self.body[0]

    def move(self, grow: bool = False) -> None:
        dx, dy = self.direction.delta
        x, y = self.head()
        new_head = ((x + dx) % GRID_WIDTH, (y + dy) % GRID_HEIGHT)
        self.body.insert(0, new_head)
        if not grow:
            self.body.pop()

    def will_collide(self, position: Tuple[int, int]) -> bool:
        return position in self.body


def spawn_food(snake: Snake) -> Tuple[int, int]:
    """Spawn food in a random empty tile."""
    while True:
        position = (random.randrange(GRID_WIDTH), random.randrange(GRID_HEIGHT))
        if position not in snake.body:
            return position


def draw_grid(surface: pygame.Surface) -> None:
    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        pygame.draw.line(surface, DARK_GREY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
        pygame.draw.line(surface, DARK_GREY, (0, y), (SCREEN_WIDTH, y))


def draw_snake(surface: pygame.Surface, snake: Snake) -> None:
    for index, (x, y) in enumerate(snake.body):
        rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        color = GREEN if index == 0 else FOREST
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, LIGHT_GREY, rect, width=1)


def draw_food(surface: pygame.Surface, position: Tuple[int, int]) -> None:
    rect = pygame.Rect(
        position[0] * TILE_SIZE,
        position[1] * TILE_SIZE,
        TILE_SIZE,
        TILE_SIZE,
    )
    pygame.draw.rect(surface, RED, rect)


def render_score(surface: pygame.Surface, font: pygame.font.Font, score: int) -> None:
    text = font.render(f"Score: {score}", True, WHITE)
    surface.blit(text, (12, 8))


def game_over_screen(
    surface: pygame.Surface, font_large: pygame.font.Font, font_small: pygame.font.Font, score: int
) -> None:
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(185)
    overlay.fill(BLACK)
    surface.blit(overlay, (0, 0))

    headline = font_large.render("Game Over", True, WHITE)
    prompt = font_small.render("Press SPACE to play again or ESC to quit", True, WHITE)
    stats = font_small.render(f"Final Score: {score}", True, WHITE)

    surface.blit(
        headline,
        (SCREEN_WIDTH // 2 - headline.get_width() // 2, SCREEN_HEIGHT // 2 - 70),
    )
    surface.blit(
        stats,
        (SCREEN_WIDTH // 2 - stats.get_width() // 2, SCREEN_HEIGHT // 2 - 15),
    )
    surface.blit(
        prompt,
        (SCREEN_WIDTH // 2 - prompt.get_width() // 2, SCREEN_HEIGHT // 2 + 40),
    )
    pygame.display.flip()


def run_game() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()
    font_small = pygame.font.SysFont("consolas", 24)
    font_large = pygame.font.SysFont("consolas", 48, bold=True)

    while True:
        snake = Snake(body=[(GRID_WIDTH // 2, GRID_HEIGHT // 2)], direction=Direction.RIGHT)
        snake.body.extend(
            [
                (snake.head()[0] - 1, snake.head()[1]),
                (snake.head()[0] - 2, snake.head()[1]),
            ]
        )
        food = spawn_food(snake)
        score = 0
        game_over = False

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        pygame.quit()
                        sys.exit()
                    if not game_over:
                        if event.key == pygame.K_UP and not snake.direction.is_opposite(Direction.UP):
                            snake.direction = Direction.UP
                        elif event.key == pygame.K_DOWN and not snake.direction.is_opposite(Direction.DOWN):
                            snake.direction = Direction.DOWN
                        elif event.key == pygame.K_LEFT and not snake.direction.is_opposite(Direction.LEFT):
                            snake.direction = Direction.LEFT
                        elif event.key == pygame.K_RIGHT and not snake.direction.is_opposite(Direction.RIGHT):
                            snake.direction = Direction.RIGHT
                    else:
                        if event.key == pygame.K_SPACE:
                            game_over = False
                            break

            if game_over:
                game_over_screen(screen, font_large, font_small, score)
                clock.tick(10)
                continue

            # Move snake
            dx, dy = snake.direction.delta
            new_head = ((snake.head()[0] + dx) % GRID_WIDTH, (snake.head()[1] + dy) % GRID_HEIGHT)

            if snake.will_collide(new_head):
                game_over = True
                continue

            ate_food = new_head == food
            snake.move(grow=ate_food)

            if ate_food:
                score += 10
                food = spawn_food(snake)

            speed = 8 + score // 20
            screen.fill(BLACK)
            draw_grid(screen)
            draw_food(screen, food)
            draw_snake(screen, snake)
            render_score(screen, font_small, score)

            pygame.display.flip()
            clock.tick(speed)


if __name__ == "__main__":
    run_game()

