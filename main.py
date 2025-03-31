import math
import pygame
import random

from enum import Enum
from pygame import Color, Rect, Surface, Vector2

SIZE = Vector2(512, 512)
ASPECT = SIZE.x / SIZE.y
PADDLE_SIZE = Vector2(16, 72)
BALL_RADIUS = 16
BALL_SPEED = 5
BORDER_THICKNESS = 5
PADDLE_SPEED = 5.0 / SIZE.y
LEFT_UP = pygame.K_UP
LEFT_DOWN = pygame.K_DOWN
RIGHT_UP = pygame.K_w
RIGHT_DOWN = pygame.K_s

Player = Enum('Player', [('NONE', 0), ('LEFT', 1), ('RIGHT', 2)])

def random_sign() -> int:
    return 1 if random.random() > 0.5 else -1

def get_paddle_rect(pos: float, player: Player) -> Rect:
    rect = Rect(0, (pos * SIZE.y) - (PADDLE_SIZE.y / 2), PADDLE_SIZE.x, PADDLE_SIZE.y)
    if player == Player.RIGHT:
        rect.left = SIZE.x - PADDLE_SIZE.x
    return rect

def draw_paddle(surf: Surface, pos: float, player: Player):
    right = player == Player.RIGHT
    rect = get_paddle_rect(pos, player)
    pygame.draw.rect(surf, "red" if right else "blue", rect)

# https://developer.mozilla.org/en-US/docs/Games/Techniques/3D_collision_detection
def sphere_rect_distance(sphere: Vector2, rect: Rect) -> float:
    # clamp to the point closest to the center of the sphere
    x = max(rect.left, min(sphere.x, rect.left + rect.width))
    y = max(rect.top, min(sphere.y, rect.top + rect.height))

    # get the distance
    return math.sqrt((x - sphere.x) * (x - sphere.x) + (y - sphere.y) * (y - sphere.y))

def check_ball(ball_pos: Vector2, ball_velocity: Vector2, left_pos: float, right_pos: float) -> (Player, Vector2):
    ball = ball_pos + Vector2(SIZE.x / 2, SIZE.y / 2)
    left = get_paddle_rect(left_pos, False)
    right = get_paddle_rect(right_pos, True)
    screen_top = Rect(0, -BORDER_THICKNESS, SIZE.x, BORDER_THICKNESS)
    screen_bottom = Rect(0, SIZE.y, SIZE.x, BORDER_THICKNESS)
    screen_left = Rect(-BORDER_THICKNESS, 0, BORDER_THICKNESS, SIZE.y)
    screen_right = Rect(SIZE.x, 0, BORDER_THICKNESS, SIZE.y)

    point = Player.NONE
    vel = ball_velocity
    for rect in [left, right, screen_top, screen_bottom, screen_left, screen_right]:
        dist = sphere_rect_distance(ball, rect)
        if dist > BALL_RADIUS:
            if rect in [left, right, screen_left, screen_right]:
                vel.x *= -1
                if rect == screen_left:
                    point = Player.RIGHT
                elif rect == screen_right:
                    point = Player.LEFT
            elif rect in [screen_top, screen_bottom]:
                vel.y *= -1

    return (point, vel)


def draw_ball(surf: Surface, pos: Vector2):
    real_pos = pos + Vector2(SIZE.x / 2, SIZE.y / 2)
    pygame.draw.circle(surf, "white", real_pos, BALL_RADIUS)

def scale_surf(screen: Surface, surf: Surface):
    size = screen.get_height()
    if screen.get_width() < screen.get_height():
        size = screen.get_width()
    scaled = pygame.transform.scale(surf, (size * ASPECT, size))
    pos = ((screen.get_width() / 2) - ((size * ASPECT) / 2), (screen.get_height() / 2) - (size / 2))
    screen.blit(scaled, pos)

def reset_ball() -> (Vector2, Vector2):
    return (Vector2(0, 0), Vector2(random_sign() * BALL_SPEED, random_sign() * BALL_SPEED / 3.0))

def main():
    pygame.init()

    screen = pygame.display.set_mode(SIZE, pygame.RESIZABLE)
    clock = pygame.time.Clock()
    running = True

    surf = Surface(SIZE)

    left_pos = 0.5
    left_points = 0
    right_pos = 0.5
    right_points = 0

    (ball_pos, ball_velocity) = reset_ball()

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
        if keys[RIGHT_UP] and left_pos > 0:
            right_pos -= PADDLE_SPEED
        elif keys[RIGHT_DOWN] and right_pos < 1:
            right_pos += PADDLE_SPEED

        # check collision, then move
        (point, ball_velocity) = check_ball(ball_pos, ball_velocity, left_pos, right_pos)
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

        # display stuff
        scale_surf(screen, surf)
        pygame.display.flip()

        clock.tick(60)

    print(f"right: {right_points} left: {left_points}")
    pygame.quit()

if __name__ == "__main__":
    main()

