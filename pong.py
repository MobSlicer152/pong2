import math
import pygame
import random

from enum import Enum
from pygame import Color, Rect, Surface, Vector2
from pygame.font import Font

SIZE = Vector2(1024, 576)
ASPECT = SIZE.x / SIZE.y

PADDLE_SIZE = Vector2(16, 128)
BALL_RADIUS = 16

SPEED_FACTOR = 2
BALL_SPEED = 3 * SPEED_FACTOR
PADDLE_SPEED = 5.0 / SIZE.y * SPEED_FACTOR

BORDER_THICKNESS = 5

LEFT_UP = pygame.K_w
LEFT_DOWN = pygame.K_s
RIGHT_UP = pygame.K_UP
RIGHT_DOWN = pygame.K_DOWN

UI_PADDING = 10
UI_FONT = None
UI_FONT_SIZE = 32

BALL_COLOR = "white"
LEFT_COLOR = "blue"
RIGHT_COLOR = "red"
UI_COLOR = "white"

Player = Enum("Player", [("NONE", 0), ("LEFT", 1), ("RIGHT", 2)])


def random_sign() -> int:
    return 1 if random.random() > 0.5 else -1


def get_paddle_rect(pos: float, player: Player) -> Rect:
    rect = Rect(0, pos * (SIZE.y - PADDLE_SIZE.y), PADDLE_SIZE.x, PADDLE_SIZE.y)
    if player == Player.RIGHT:
        rect.left = SIZE.x - PADDLE_SIZE.x
    return rect


# https://developer.mozilla.org/en-US/docs/Games/Techniques/3D_collision_detection
def sphere_rect_distance(sphere: Vector2, rect: Rect) -> float:
    # clamp to the point closest to the center of the sphere
    x = max(rect.left, min(sphere.x, rect.left + rect.width))
    y = max(rect.top, min(sphere.y, rect.top + rect.height))

    # get the distance
    return math.sqrt((x - sphere.x) * (x - sphere.x) + (y - sphere.y) * (y - sphere.y))


def reset_ball() -> tuple[Vector2, Vector2]:
    return (
        Vector2(0, 0),
        Vector2(random_sign() * BALL_SPEED, random_sign() * BALL_SPEED),
    )


def check_ball(
    ball_pos: Vector2, ball_velocity: Vector2, left_pos: float, right_pos: float
) -> tuple[Player, Vector2]:
    ball = ball_pos + Vector2(SIZE.x / 2, SIZE.y / 2)
    left = get_paddle_rect(left_pos, Player.LEFT)
    right = get_paddle_rect(right_pos, Player.RIGHT)
    screen_top = Rect(0, -BORDER_THICKNESS, SIZE.x, BORDER_THICKNESS)
    screen_bottom = Rect(0, SIZE.y, SIZE.x, BORDER_THICKNESS)
    screen_left = Rect(-BORDER_THICKNESS, 0, BORDER_THICKNESS, SIZE.y)
    screen_right = Rect(SIZE.x, 0, BORDER_THICKNESS, SIZE.y)

    point = Player.NONE
    vel = ball_velocity
    for rect in [left, right, screen_top, screen_bottom, screen_left, screen_right]:
        dist = sphere_rect_distance(ball, rect)
        if dist < BALL_RADIUS:
            if rect == left:
                vel.x = 1.1 * abs(vel.x)
            elif rect == right:
                vel.x = -1.1 * abs(vel.x)

            if rect == screen_left:
                point = Player.RIGHT
            elif rect == screen_right:
                point = Player.LEFT

            if rect == screen_top:
                vel.y = 1 * abs(vel.y)
            elif rect == screen_bottom:
                vel.y = -1 * abs(vel.y)

    return (point, vel)


def draw_ui(surf: Surface, font: Font, left_points: int, right_points: int):
    # TODO: make this happen once
    w = font.render("W", False, UI_COLOR)
    w_pos = (UI_PADDING, UI_PADDING)
    s = font.render("S", False, UI_COLOR)
    s_pos = (UI_PADDING, SIZE.y - UI_PADDING - s.get_height())
    up = font.render("/\\", False, UI_COLOR)
    up_pos = (SIZE.x - UI_PADDING - up.get_width(), UI_PADDING)
    down = font.render("\\/", False, UI_COLOR)
    down_pos = (
        SIZE.x - UI_PADDING - down.get_width(),
        SIZE.y - UI_PADDING - down.get_height(),
    )

    left_score = font.render(str(left_points), False, UI_COLOR)
    left_score_pos = ((SIZE.x / 2) - left_score.get_width() - UI_PADDING, UI_PADDING)
    right_score = font.render(str(right_points), False, UI_COLOR)
    right_score_pos = ((SIZE.x / 2) + UI_PADDING, UI_PADDING)

    ui = [
        (w, w_pos),
        (s, s_pos),
        (up, up_pos),
        (down, down_pos),
        (left_score, left_score_pos),
        (right_score, right_score_pos),
    ]

    surf.blits(ui)
    pygame.draw.rect(
        surf,
        UI_COLOR,
        Rect(
            (SIZE.x / 2) - (BORDER_THICKNESS / 2),
            UI_PADDING,
            BORDER_THICKNESS,
            SIZE.y - UI_PADDING * 2,
        ),
    )


def draw_paddle(surf: Surface, pos: float, player: Player):
    right = player == Player.RIGHT
    rect = get_paddle_rect(pos, player)
    pygame.draw.rect(surf, RIGHT_COLOR if right else LEFT_COLOR, rect)


def draw_ball(surf: Surface, pos: Vector2):
    real_pos = pos + Vector2(SIZE.x / 2, SIZE.y / 2)
    pygame.draw.circle(surf, BALL_COLOR, real_pos, BALL_RADIUS)


def scale_surf(screen: Surface, surf: Surface):
    size = screen.get_height()
    if screen.get_width() < screen.get_height():
        size = screen.get_width()
    scaled = pygame.transform.scale(surf, (size * ASPECT, size))
    pos = (
        (screen.get_width() / 2) - ((size * ASPECT) / 2),
        (screen.get_height() / 2) - (size / 2),
    )
    screen.blit(scaled, pos)


def main():
    pygame.init()

    screen = pygame.display.set_mode(SIZE, pygame.RESIZABLE)
    pygame.display.set_caption("Pong")

    clock = pygame.time.Clock()
    running = True

    surf = Surface(SIZE)

    left_pos = 0.5
    left_points = 0
    right_pos = 0.5
    right_points = 0

    (ball_pos, ball_velocity) = reset_ball()

    font = Font(UI_FONT, UI_FONT_SIZE)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        surf.fill(Color(32, 32, 32))

        # check keys
        keys = pygame.key.get_pressed()
        if keys[LEFT_UP] and left_pos > 0:
            left_pos -= PADDLE_SPEED
        elif keys[LEFT_DOWN] and left_pos < 1:
            left_pos += PADDLE_SPEED
        if keys[RIGHT_UP] and right_pos > 0:
            right_pos -= PADDLE_SPEED
        elif keys[RIGHT_DOWN] and right_pos < 1:
            right_pos += PADDLE_SPEED

        # check collision, then move
        (point, ball_velocity) = check_ball(
            ball_pos, ball_velocity, left_pos, right_pos
        )
        if point != Player.NONE:
            (ball_pos, ball_velocity) = reset_ball()
            if point == Player.RIGHT:
                right_points += 1
            elif point == Player.LEFT:
                left_points += 1
        ball_pos += ball_velocity

        # draw
        draw_ball(surf, ball_pos)
        draw_paddle(surf, left_pos, Player.LEFT)
        draw_paddle(surf, right_pos, Player.RIGHT)
        draw_ui(surf, font, left_points, right_points)

        # display stuff
        scale_surf(screen, surf)
        pygame.display.flip()

        clock.tick(60)

    print(f"right: {right_points} left: {left_points}")
    pygame.quit()


if __name__ == "__main__":
    main()
