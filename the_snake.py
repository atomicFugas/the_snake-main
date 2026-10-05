from random import randint
from enum import Enum
import pygame


# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)
SNAKE_HEAD_COLOR = (0, 200, 0)

# Скорость движения змейки:
SPEED = 10

# Инициализация Pygame и окна:
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption("Змейка")
clock = pygame.time.Clock()


class Direction(Enum):
    """Перечисление направлений движения змейки."""

    RIGHT = (1, 0)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    UP = (0, -1)

    @classmethod
    def index(cls, direction):
        """Индекс направления для доступа к массивам текстур."""
        members = list(cls)
        if direction in members:
            return members.index(direction)
        raise ValueError("Must be an instance of Direction")


def load_texture(path):
    """Загружает PNG и масштабирует под размер сетки."""
    try:
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, (GRID_SIZE, GRID_SIZE))
    except (pygame.error, FileNotFoundError):
        return None


APPLE_TEXTURE = load_texture("src/Graphics/apple.png")
SNAKE_HEAD = (
    load_texture("src/Graphics/head_right.png"),
    load_texture("src/Graphics/head_down.png"),
    load_texture("src/Graphics/head_left.png"),
    load_texture("src/Graphics/head_up.png"),
)
SNAKE_BODY_H = load_texture("src/Graphics/body_horizontal.png")
SNAKE_BODY_V = load_texture("src/Graphics/body_vertical.png")
SNAKE_CORNER_TL = load_texture("src/Graphics/body_topleft.png")
SNAKE_CORNER_TR = load_texture("src/Graphics/body_topright.png")
SNAKE_CORNER_BL = load_texture("src/Graphics/body_bottomleft.png")
SNAKE_CORNER_BR = load_texture("src/Graphics/body_bottomright.png")
SNAKE_TAIL = (
    load_texture("src/Graphics/tail_left.png"),
    load_texture("src/Graphics/tail_up.png"),
    load_texture("src/Graphics/tail_right.png"),
    load_texture("src/Graphics/tail_down.png"),
)
BACKGROUND_TEXTURES = load_texture("src/Graphics/grass.png")
STONE_TEXTURE = load_texture("src/Graphics/stone2_26.png")
PEAR_TEXTURE = load_texture("src/Graphics/peer.png")


class GameObject:
    """Базовый класс для всех объектов игры."""

    def __init__(self, position=None, body_color=None):
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Метод отрисовки объекта на игровом поле."""
        pass

    def draw_texture(self):
        """Метод отрисовки текстуры объекта на игровом поле."""
        pass


class Snake(GameObject):
    """Класс змейки, которая управляется игроком."""

    def __init__(
        self,
        position=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
        body_color=SNAKE_COLOR,
        head_color=SNAKE_HEAD_COLOR,
    ):
        super().__init__(position, body_color)
        self.head_color = head_color
        self.positions = [
            (position[0], position[1]),
            (position[0] - GRID_SIZE, position[1]),
        ]
        self.length = 2
        self.direction = Direction.RIGHT
        self.next_direction = None
        self.last = self.positions[-1]

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def draw(self):
        """Отрисовывает змейку стандартными прямоугольниками."""
        for position in self.positions[1:]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.head_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

    def __get_segment_direction_tail(self, from_pos, to_pos):
        """Определяет индекс направления от from_pos к to_pos с учетом переноса экрана."""
        dx = (to_pos[0] - from_pos[0]) % SCREEN_WIDTH
        if dx > GRID_SIZE:
            dx -= SCREEN_WIDTH

        dy = (to_pos[1] - from_pos[1]) % SCREEN_HEIGHT
        if dy > GRID_SIZE:
            dy -= SCREEN_HEIGHT

        if dx > 0:
            return 0  # RIGHT
        if dx < 0:
            return 2  # LEFT
        if dy > 0:
            return 1  # DOWN
        if dy < 0:
            return 3  # UP
        return 0

    def draw_texture(self):
        """Метод отрисовки текстуры змейки на игровом поле."""
        if not all(SNAKE_HEAD):
            self.draw()
            return

        head_pos = self.positions[0]
        head_img = SNAKE_HEAD[Direction.index(self.direction)]
        screen.blit(head_img, head_pos)

        tail_pos = self.positions[-1]
        before_tail_pos = self.positions[-2]

        tail_dir = self.__get_segment_direction_tail(tail_pos, before_tail_pos)

        if len(self.positions) == 2:
            screen.blit(SNAKE_TAIL[tail_dir], tail_pos)
            return

        for i in range(1, len(self.positions) - 1):
            prev_p = self.positions[i - 1]
            curr_p = self.positions[i]
            next_p = self.positions[i + 1]

            dx_prev = (prev_p[0] - curr_p[0]) % SCREEN_WIDTH
            if dx_prev > GRID_SIZE:
                dx_prev -= SCREEN_WIDTH

            dy_prev = (prev_p[1] - curr_p[1]) % SCREEN_HEIGHT
            if dy_prev > GRID_SIZE:
                dy_prev -= SCREEN_HEIGHT

            dx_next = (next_p[0] - curr_p[0]) % SCREEN_WIDTH
            if dx_next > GRID_SIZE:
                dx_next -= SCREEN_WIDTH

            dy_next = (next_p[1] - curr_p[1]) % SCREEN_HEIGHT
            if dy_next > GRID_SIZE:
                dy_next -= SCREEN_HEIGHT

            if dx_prev == 0 and dx_next == 0:
                screen.blit(SNAKE_BODY_V, curr_p)
            elif dy_prev == 0 and dy_next == 0:
                screen.blit(SNAKE_BODY_H, curr_p)
            else:
                has_left = dx_prev < 0 or dx_next < 0
                has_right = dx_prev > 0 or dx_next > 0
                has_top = dy_prev < 0 or dy_next < 0
                has_bottom = dy_prev > 0 or dy_next > 0

                if has_left and has_top:
                    screen.blit(SNAKE_CORNER_TL, curr_p)
                elif has_right and has_top:
                    screen.blit(SNAKE_CORNER_TR, curr_p)
                elif has_left and has_bottom:
                    screen.blit(SNAKE_CORNER_BL, curr_p)
                elif has_right and has_bottom:
                    screen.blit(SNAKE_CORNER_BR, curr_p)

        screen.blit(SNAKE_TAIL[tail_dir], tail_pos)

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.positions = [
            self.position,
            (self.position[0] - GRID_SIZE, self.position[1]),
        ]
        self.length = 2
        self.direction = Direction.RIGHT
        self.next_direction = None

    def move(self, apple, pears, stones):
        """Перемещает змейку в текущем направлении и обрабатывает столкновения."""
        cur_x, cur_y = self.get_head_position()
        dir_x, dir_y = self.direction.value

        new_x = (cur_x + (dir_x * GRID_SIZE)) % SCREEN_WIDTH
        new_y = (cur_y + (dir_y * GRID_SIZE)) % SCREEN_HEIGHT
        new_head = (new_x, new_y)

        if new_head in self.positions[2:]:
            self.reset_all(apple, pears, stones)
            return

        for stone in stones:
            if new_head == stone.position:
                self.reset_all(apple, pears, stones)
                return

        eaten_pear = None
        for pear in pears:
            if new_head == pear.position:
                eaten_pear = pear
                break

        if eaten_pear:
            if len(self.positions) <= 2:
                self.reset_all(apple, pears, stones)
                return

            self.positions.insert(0, new_head)

            self.positions.pop()
            self.positions.pop()
            self.length -= 1

            occupied = self.get_occupied_positions(pears, stones, apple)
            eaten_pear.randomize_position(occupied)
            return

        self.positions.insert(0, new_head)

        if new_head == apple.position:
            self.length += 1
            occupied = self.get_occupied_positions(pears, stones)
            apple.randomize_position(occupied)
            return

        self.last = self.positions.pop()

    def get_occupied_positions(self, pears=None, stones=None, apple=None):
        """Собирает список всех занятых позиций \
            для правильного спавна объектов."""
        occupied = list(self.positions)
        if apple and apple.position:
            occupied.append(apple.position)
        if pears:
            occupied.extend([p.position for p in pears if p.position])
        if stones:
            occupied.extend([s.position for s in stones if s.position])
        return occupied

    def reset_all(self, apple, pears, stones):
        """Полный сброс игры при поражении."""
        self.reset()

        occupied = list(self.positions)

        for stone in stones:
            stone.randomize_position(occupied)
            occupied.append(stone.position)

        apple.randomize_position(occupied)
        occupied.append(apple.position)

        for pear in pears:
            pear.randomize_position(occupied)
            occupied.append(pear.position)


class Apple(GameObject):
    """Класс яблока, которое появляется на игровом поле."""

    def __init__(self, position=None, body_color=APPLE_COLOR):
        super().__init__(position, body_color)

    def randomize_position(self, occupied_positions):
        """Возвращает случайную свободную позицию для яблока."""
        while True:
            position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if position not in occupied_positions:
                self.position = position
                break

    def draw(self):
        """Метод отрисовки яблока текстурой или прямоугольником."""
        if APPLE_TEXTURE:
            screen.blit(APPLE_TEXTURE, self.position)
        else:
            rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Pear(GameObject):
    """Класс груши, которая уменьшает длину змейки."""

    def __init__(self, position=None, body_color=(255, 255, 0)):
        super().__init__(position, body_color)

    def randomize_position(self, occupied_positions):
        """Возвращает случайную свободную позицию для груши."""
        while True:
            position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if position not in occupied_positions:
                self.position = position
                break

    def draw(self):
        """Метод отрисовки груши текстурой или прямоугольником."""
        if PEAR_TEXTURE:
            screen.blit(PEAR_TEXTURE, self.position)
        else:
            rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Stone(GameObject):
    """Класс препятствия-камня."""

    def __init__(self, position=None, body_color=(128, 128, 128)):
        super().__init__(position, body_color)

    def randomize_position(self, occupied_positions):
        """Возвращает случайную свободную позицию для камня."""
        while True:
            position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if position not in occupied_positions:
                self.position = position
                break

    def draw(self):
        """Метод отрисовки камня текстурой или прямоугольником."""
        if STONE_TEXTURE:
            screen.blit(STONE_TEXTURE, self.position)
        else:
            rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш для управления змейкой."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != Direction.DOWN:
                game_object.next_direction = Direction.UP
            elif event.key == pygame.K_DOWN and game_object.direction != Direction.UP:
                game_object.next_direction = Direction.DOWN
            elif (
                event.key == pygame.K_LEFT and game_object.direction != Direction.RIGHT
            ):
                game_object.next_direction = Direction.LEFT
            elif (
                event.key == pygame.K_RIGHT and game_object.direction != Direction.LEFT
            ):
                game_object.next_direction = Direction.RIGHT


def draw_background(screen):
    """Отрисовка фона игры."""
    if BACKGROUND_TEXTURES:
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                screen.blit(
                    BACKGROUND_TEXTURES,
                    (x * GRID_SIZE, y * GRID_SIZE)
                )
    else:
        screen.fill(BOARD_BACKGROUND_COLOR)


def main():
    """Главная функция игры."""
    snake = Snake(
        ((GRID_WIDTH // 2) * GRID_SIZE, (GRID_HEIGHT // 2) * GRID_SIZE),
        SNAKE_COLOR,
        SNAKE_HEAD_COLOR,
    )

    occupied = list(snake.positions)

    stones = [Stone() for _ in range(3)]
    for stone in stones:
        stone.randomize_position(occupied)
        occupied.append(stone.position)

    apple = Apple(None, APPLE_COLOR)
    apple.randomize_position(occupied)
    occupied.append(apple.position)

    pears = [Pear() for _ in range(2)]
    for pear in pears:
        pear.randomize_position(occupied)
        occupied.append(pear.position)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)

        snake.update_direction()
        snake.move(apple, pears, stones)

        draw_background(screen)

        for stone in stones:
            stone.draw()

        apple.draw()

        for pear in pears:
            pear.draw()

        snake.draw_texture()

        pygame.display.update()


if __name__ == "__main__":
    main()