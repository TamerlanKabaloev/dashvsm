import random
from dataclasses import dataclass, field
from typing import List, Tuple

import pygame


CELL_SIZE = 24
GRID_WIDTH = 24
GRID_HEIGHT = 20
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS_START = 10
FPS_INCREMENT = 0.6

BACKGROUND_COLOR = (17, 17, 17)
SNAKE_HEAD_COLOR = (80, 220, 100)
SNAKE_BODY_COLOR = (50, 170, 80)
FOOD_COLOR = (230, 70, 70)
GRID_COLOR = (35, 35, 35)
TEXT_COLOR = (240, 240, 240)

DIRECTIONS = {
    pygame.K_UP: (0, -1),
    pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_s: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_d: (1, 0),
}


def add_tuple(a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[int, int]:
    return a[0] + b[0], a[1] + b[1]


@dataclass
class Snake:
    body: List[Tuple[int, int]] = field(default_factory=list)
    direction: Tuple[int, int] = (1, 0)
    grow_pending: int = 0

    def head(self) -> Tuple[int, int]:
        return self.body[0]

    def contains(self, pos: Tuple[int, int]) -> bool:
        return pos in self.body

    def move(self, wrap: bool = True) -> bool:
        new_head = add_tuple(self.head(), self.direction)
        if wrap:
            new_head = (
                new_head[0] % GRID_WIDTH,
                new_head[1] % GRID_HEIGHT,
            )

        if new_head in self.body[:-1] or (
            not wrap
            and (
                new_head[0] < 0
                or new_head[0] >= GRID_WIDTH
                or new_head[1] < 0
                or new_head[1] >= GRID_HEIGHT
            )
        ):
            return False

        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()
        return True

    def grow(self, amount: int = 1) -> None:
        self.grow_pending += amount

    def set_direction(self, new_direction: Tuple[int, int]) -> None:
        if add_tuple(new_direction, self.direction) != (0, 0):
            self.direction = new_direction


def spawn_food(snake: Snake) -> Tuple[int, int]:
    available = [
        (x, y)
        for x in range(GRID_WIDTH)
        for y in range(GRID_HEIGHT)
        if not snake.contains((x, y))
    ]
    if not available:
        return snake.head()
    return random.choice(available)


def draw_grid(surface: pygame.Surface) -> None:
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))


def draw_snake(surface: pygame.Surface, snake: Snake) -> None:
    for index, (x, y) in enumerate(snake.body):
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        color = SNAKE_HEAD_COLOR if index == 0 else SNAKE_BODY_COLOR
        pygame.draw.rect(surface, color, rect, border_radius=6)


def draw_food(surface: pygame.Surface, food: Tuple[int, int]) -> None:
    rect = pygame.Rect(food[0] * CELL_SIZE, food[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surface, FOOD_COLOR, rect, border_radius=6)


def render_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    position: Tuple[int, int],
    center: bool = False,
) -> None:
    rendered = font.render(text, True, TEXT_COLOR)
    rect = rendered.get_rect()
    rect.center = position if center else position
    if not center:
        rect.topleft = position
    surface.blit(rendered, rect)


def new_game() -> Tuple[Snake, Tuple[int, int], int, float]:
    start = Snake(
        body=[
            (GRID_WIDTH // 2, GRID_HEIGHT // 2),
            (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2),
            (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2),
        ],
        direction=(1, 0),
    )
    food = spawn_food(start)
    return start, food, 0, FPS_START


def run() -> None:
    pygame.init()
    pygame.display.set_caption("Змейка 🐍")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 22)
    big_font = pygame.font.SysFont("consolas", 36, bold=True)

    snake, food, score, speed = new_game()
    paused = False
    wrap = True
    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in DIRECTIONS:
                    snake.set_direction(DIRECTIONS[event.key])
                elif event.key == pygame.K_SPACE and not game_over:
                    paused = not paused
                elif event.key == pygame.K_r:
                    snake, food, score, speed = new_game()
                    paused = False
                    game_over = False
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_TAB:
                    wrap = not wrap

        if not paused and not game_over:
            moved = snake.move(wrap=wrap)
            if not moved:
                game_over = True
            elif snake.head() == food:
                snake.grow()
                score += 10
                speed += FPS_INCREMENT
                food = spawn_food(snake)

        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen)
        draw_snake(screen, snake)
        draw_food(screen, food)

        render_text(screen, f"Очки: {score}", font, (12, 8))
        render_text(screen, f"Скорость: {speed:.1f}", font, (12, 36))
        render_text(screen, f"Режим: {'сквозь стены' if wrap else 'стены твердые'}", font, (12, 64))
        render_text(screen, "WASD/стрелки — движение | Пробел — пауза | R — заново | Tab — стены", font, (12, SCREEN_HEIGHT - 32))

        if game_over:
            render_text(screen, "Игра окончена! Нажмите R, чтобы начать заново", big_font, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), center=True)
        elif paused:
            render_text(screen, "Пауза — пробел для продолжения", big_font, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), center=True)
        pygame.display.flip()
        clock.tick(speed if not paused and not game_over else FPS_START)

    pygame.quit()


if __name__ == "__main__":
    run()

