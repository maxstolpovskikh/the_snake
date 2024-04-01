from random import randint
from abc import abstractmethod
from typing import Optional as Opt

import pygame


# Инициализация PyGame:
pygame.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 8  # 20 сильно быстро

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Это базовый класс, от которого наследуются другие игровые объекты."""

    def __init__(self):
        self.position = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2)), ]

    @abstractmethod
    def draw(self) -> None:
        """
        Это абстрактный метод, который предназначен для
        переопределения в дочерних классах.
        """

    @abstractmethod
    def body_color(self):
        """Цвет объекта. Он задаётся в дочернем классе."""
        return self.body_color


class Apple(GameObject):
    """Класс, унаследованный от GameObject,
    описывающий яблоко и действия с ним.
    Яблоко должно отображаться в случайных клетках игрового поля.
    """

    def __init__(self, busy_cells: Opt[list] = None):
        super().__init__()
        self.busy_cells = busy_cells
        self.position = self.randomize_position(self)
        # Неуверен, но... иначе Cannot determine type of (Mypy)
        self.body_color: tuple = APPLE_COLOR

    def draw(self) -> None:
        """Отрисовывает яблоко на игровой поверхности"""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    @staticmethod
    # раз у нас есть busy_cells, сделаем вот так?
    def randomize_position(self) -> tuple:
        """Генерация случайных координат"""
        def rnd_coord(grid_length):
            return randint(0, grid_length - GRID_SIZE) * GRID_SIZE

        while True:
            coordinates = (rnd_coord(GRID_WIDTH), rnd_coord(GRID_HEIGHT))
            if not self.busy_cells:
                break
            if coordinates not in self.busy_cells:
                break

        return coordinates


class Snake(GameObject):
    """
    Змейка — это список координат,
    каждый элемент списка соответствует
    отдельному сегменту тела змейки.
    """

    def __init__(self):
        super().__init__()
        # Неуверен, но... иначе Cannot determine type of (Mypy)
        self.body_color: tuple = SNAKE_COLOR
        self.screen_fill = None
        self.reset()

    def reset(self, direction: tuple = RIGHT,
              next_dir: Opt[tuple] = None) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.direction = direction
        self.next_direction = next_dir
        self.positions: list = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2)), ]
        self.screen_fill = True
        self.last = None

    def draw(self) -> None:
        """Отрисовывает змейку на экране, затирая след"""
        if self.screen_fill:
            screen.fill(BOARD_BACKGROUND_COLOR)
            self.screen_fill = None
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def update_direction(self) -> None:
        """Метод обновления направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self) -> tuple[int, int]:
        """
        Возвращает позицию головы змейки,
        первый элемент в списке positions
        """
        return self.positions[0]

    def move(self) -> None:
        """Отвечает за обновление положения змейки в игре."""
        head = self.get_head_position()
        direction = self.direction
        abscissa, ordinate = (
            head[i] + direction[i] * GRID_SIZE for i in range(0, 2))
        head_new = (abscissa % SCREEN_WIDTH, ordinate % SCREEN_HEIGHT)
        self.positions.insert(0, head_new)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        if head_new in self.positions[1:]:
            self.reset()


# это функция а не метод, поэтому не забыл.
def handle_keys(game_object: Snake) -> None:
    """
    Обрабатывает нажатия клавиш,
    чтобы изменить направление движения змейки
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основной цикл игры"""
    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.position = apple.randomize_position(apple)
        snake.draw()
        apple.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
