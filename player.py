import time
import turtle
from typing import Callable


class Player:
    def __init__(self, shape_name: str, start_x: float, start_y: float, speed: float = 6.0):
        self.t = turtle.Turtle()
        self.t.shape(shape_name)
        self.t.color("cyan")
        self.t.penup()
        self.t.setheading(90)
        self.t.goto(start_x, start_y)
        self.speed = speed
        self.moving_left = False
        self.moving_right = False
        self.last_fire_time = 0.0
        self.fire_cooldown = 0.18  # seconds

    def on_left_press(self):
        self.moving_left = True

    def on_left_release(self):
        self.moving_left = False

    def on_right_press(self):
        self.moving_right = True

    def on_right_release(self):
        self.moving_right = False

    def update(self, left_bound: float, right_bound: float):
        dx = 0
        if self.moving_left and not self.moving_right:
            dx = -self.speed
        elif self.moving_right and not self.moving_left:
            dx = self.speed
        if dx != 0:
            nx = max(left_bound + 15, min(right_bound - 15, self.t.xcor() + dx))
            self.t.setx(nx)

    def try_fire(self, spawn_bullet_fn: Callable[[float, float], None]):
        now = time.perf_counter()
        if now - self.last_fire_time >= self.fire_cooldown:
            self.last_fire_time = now
            spawn_bullet_fn(self.t.xcor(), self.t.ycor() + 12)

