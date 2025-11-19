import sys
from dataclasses import dataclass
from typing import List, Tuple, Dict

import pygame


WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540
FPS = 60

TILE_SIZE = 48
GRAVITY = 0.7
PLAYER_SPEED = 5
JUMP_VELOCITY = -13
TERMINAL_VELOCITY = 16

BACKGROUND_COLOR = (135, 206, 235)
TILE_COLOR = (60, 110, 40)
PLAYER_COLOR = (230, 40, 40)
ENEMY_COLOR = (240, 200, 40)
FLAG_COLOR = (255, 255, 255)
TEXT_COLOR = (25, 25, 25)

LEVEL_MAP = [
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    ".................E..............",
    "..............#####.............",
    ".........................F......",
    "#####.............###...........",
    "#####.....###...................",
    "#####...........................",
    "#####...............#####.......",
    "#####...............#####.......",
]


Enemy = Dict[str, object]


@dataclass
class GameObject:
    rect: pygame.Rect
    velocity: pygame.Vector2


def load_level(layout: List[str]) -> Tuple[List[pygame.Rect], List[Enemy], pygame.Rect]:
    tiles: List[pygame.Rect] = []
    enemies: List[Enemy] = []
    flag_rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE * 2)

    for row, line in enumerate(layout):
        for col, char in enumerate(line):
            x = col * TILE_SIZE
            y = row * TILE_SIZE
            if char == "#":
                tiles.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
            elif char == "E":
                enemy_rect = pygame.Rect(x + 8, y + 8, TILE_SIZE - 16, TILE_SIZE - 16)
                enemies.append({"rect": enemy_rect, "direction": 1})
            elif char == "F":
                flag_rect = pygame.Rect(x + TILE_SIZE // 4, y - TILE_SIZE, TILE_SIZE // 2, TILE_SIZE * 2)
    return tiles, enemies, flag_rect


def move_and_collide(player: GameObject, tiles: List[pygame.Rect]) -> Tuple[bool, bool]:
    on_ground = False
    hitting_ceiling = False

    player.rect.x += int(player.velocity.x)
    collisions = [tile for tile in tiles if player.rect.colliderect(tile)]
    for tile in collisions:
        if player.velocity.x > 0:
            player.rect.right = tile.left
        elif player.velocity.x < 0:
            player.rect.left = tile.right
        player.velocity.x = 0

    player.velocity.y = max(min(player.velocity.y + GRAVITY, TERMINAL_VELOCITY), -TERMINAL_VELOCITY)
    player.rect.y += int(player.velocity.y)
    collisions = [tile for tile in tiles if player.rect.colliderect(tile)]
    for tile in collisions:
        if player.velocity.y > 0:
            player.rect.bottom = tile.top
            player.velocity.y = 0
            on_ground = True
        elif player.velocity.y < 0:
            player.rect.top = tile.bottom
            player.velocity.y = 0
            hitting_ceiling = True
    return on_ground, hitting_ceiling


def update_enemies(enemies: List[Enemy], tiles: List[pygame.Rect]) -> None:
    for enemy in enemies:
        rect = enemy["rect"]
        direction = enemy["direction"]
        rect.x += int(direction) * 2

        for tile in tiles:
            if rect.colliderect(tile):
                if direction > 0:
                    rect.right = tile.left
                else:
                    rect.left = tile.right
                enemy["direction"] = -direction
                break


def draw_text(surface: pygame.Surface, text: str, font: pygame.font.Font, position: Tuple[int, int]) -> None:
    rendered = font.render(text, True, TEXT_COLOR)
    surface.blit(rendered, position)


def run() -> None:
    pygame.init()
    pygame.display.set_caption("Мини Марио")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 24)
    big_font = pygame.font.SysFont("consolas", 36, bold=True)

    tiles, enemies, flag = load_level(LEVEL_MAP)
    player = GameObject(pygame.Rect(64, WINDOW_HEIGHT - 180, TILE_SIZE - 12, TILE_SIZE - 6), pygame.Vector2(0, 0))

    camera_x = 0
    running = True
    game_over = False
    win = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                tiles, enemies, flag = load_level(LEVEL_MAP)
                player.rect.topleft = (64, WINDOW_HEIGHT - 180)
                player.velocity.xy = (0, 0)
                camera_x = 0
                game_over = False
                win = False

        keys = pygame.key.get_pressed()
        if not game_over:
            player.velocity.x = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player.velocity.x = -PLAYER_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player.velocity.x = PLAYER_SPEED

            on_ground, _ = move_and_collide(player, tiles)
            if on_ground and (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]):
                player.velocity.y = JUMP_VELOCITY

            update_enemies(enemies, tiles)

            for enemy_data in enemies[:]:
                enemy_rect = enemy_data["rect"]
                if player.rect.colliderect(enemy_rect):
                    if player.velocity.y > 0 and player.rect.bottom - enemy_rect.top < TILE_SIZE // 2:
                        player.velocity.y = JUMP_VELOCITY * 0.7
                        enemies.remove(enemy_data)
                    else:
                        game_over = True
                        win = False
                        break

            if player.rect.colliderect(flag):
                game_over = True
                win = True

            if player.rect.top > WINDOW_HEIGHT:
                game_over = True
                win = False

            camera_x = max(0, player.rect.centerx - WINDOW_WIDTH // 2)

        screen.fill(BACKGROUND_COLOR)
        for tile in tiles:
            offset_rect = tile.move(-camera_x, 0)
            pygame.draw.rect(screen, TILE_COLOR, offset_rect)
        for enemy_data in enemies:
            offset_rect = enemy_data["rect"].move(-camera_x, 0)
            pygame.draw.rect(screen, ENEMY_COLOR, offset_rect, border_radius=8)
        pygame.draw.rect(screen, FLAG_COLOR, flag.move(-camera_x, 0))
        pygame.draw.rect(screen, PLAYER_COLOR, player.rect.move(-camera_x, 0), border_radius=6)

        draw_text(screen, "Стрелки/AD — движение, Пробел/↑/W — прыжок, R — рестарт", font, (16, 16))

        if game_over:
            message = "Победа! Нажмите R, чтобы сыграть снова" if win else "Поражение! Нажмите R, чтобы перезапустить"
            draw_text(screen, message, big_font, (80, WINDOW_HEIGHT // 2 - 32))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run()

