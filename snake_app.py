import random
import time
from typing import List, Tuple

import streamlit as st

BOARD_WIDTH = 20
BOARD_HEIGHT = 15


def reset_game() -> None:
    center = (BOARD_WIDTH // 2, BOARD_HEIGHT // 2)
    st.session_state.snake: List[Tuple[int, int]] = [
        center,
        (center[0] - 1, center[1]),
        (center[0] - 2, center[1]),
    ]
    st.session_state.direction: Tuple[int, int] = (1, 0)
    st.session_state.pending_direction: Tuple[int, int] = (1, 0)
    st.session_state.food: Tuple[int, int] = spawn_food(st.session_state.snake)
    st.session_state.game_over = False
    st.session_state.score = 0
    st.session_state.speed = 0.25
    st.session_state.last_move = time.time()


def spawn_food(snake: List[Tuple[int, int]]) -> Tuple[int, int]:
    while True:
        position = (random.randrange(BOARD_WIDTH), random.randrange(BOARD_HEIGHT))
        if position not in snake:
            return position


def move_snake() -> None:
    head_x, head_y = st.session_state.snake[0]
    dir_x, dir_y = st.session_state.direction
    new_head = ((head_x + dir_x) % BOARD_WIDTH, (head_y + dir_y) % BOARD_HEIGHT)

    if new_head in st.session_state.snake:
        st.session_state.game_over = True
        return

    st.session_state.snake.insert(0, new_head)
    if new_head == st.session_state.food:
        st.session_state.score += 10
        st.session_state.food = spawn_food(st.session_state.snake)
        st.session_state.speed = max(0.08, st.session_state.speed * 0.97)
    else:
        st.session_state.snake.pop()


def render_board() -> None:
    board = [["⬛" for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
    for index, (x, y) in enumerate(st.session_state.snake):
        board[y][x] = "🟢" if index == 0 else "🟩"
    food_x, food_y = st.session_state.food
    board[food_y][food_x] = "🍎"

    grid_str = "\n".join("".join(row) for row in board)
    st.markdown(
        f"""
        <pre style="
            font-size: 18px;
            line-height: 1.1;
            padding: 12px;
            background-color: #111;
            border-radius: 12px;
            color: #f5f5f5;
        ">{grid_str}</pre>
        """,
        unsafe_allow_html=True,
    )


def set_direction(new_direction: Tuple[int, int]) -> None:
    current_dir = st.session_state.direction
    if (current_dir[0] + new_direction[0], current_dir[1] + new_direction[1]) != (0, 0):
        st.session_state.pending_direction = new_direction


def main() -> None:
    st.set_page_config(page_title="Змейка", page_icon="🐍", layout="centered")
    st.title("🐍 Змейка")
    st.caption("Управление стрелками или кнопками ниже. Змейка проходит сквозь стены.")

    if "snake" not in st.session_state:
        reset_game()

    with st.sidebar:
        st.header("Настройки")
        st.write("- `⟳` — начать заново\n- `⬆⬇⬅➡` — сменить направление\n- Скорость увеличивается вместе с очками.")
        if st.button("⟳ Начать заново"):
            reset_game()
            st.experimental_rerun()

    control_cols = st.columns([3, 3, 3])
    with control_cols[1]:
        if st.button("⬆️", use_container_width=True):
            set_direction((0, -1))

    with st.columns([3, 3, 3])[0]:
        if st.button("⬅️", use_container_width=True):
            set_direction((-1, 0))
    with st.columns([3, 3, 3])[1]:
        if st.button("⬇️", use_container_width=True):
            set_direction((0, 1))
    with st.columns([3, 3, 3])[2]:
        if st.button("➡️", use_container_width=True):
            set_direction((1, 0))

    st.metric("Очки", st.session_state.score)

    if not st.session_state.game_over:
        now = time.time()
        if now - st.session_state.last_move >= st.session_state.speed:
            st.session_state.direction = st.session_state.pending_direction
            move_snake()
            st.session_state.last_move = now

    render_board()

    if st.session_state.game_over:
        st.error("Игра окончена! Нажмите ⟳, чтобы начать заново.")
    else:
        time.sleep(st.session_state.speed)
        st.experimental_rerun()


if __name__ == "__main__":
    main()









