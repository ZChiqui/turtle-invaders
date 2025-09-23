import turtle
from typing import List


class Enemy:
    def __init__(self, frames: List[str]):
        self.t = turtle.Turtle()
        self.frames = frames if frames else ["square", "square"]
        self.frame_index = 0
        # self.t.shape(self.frames[self.frame_index])
        self.t.shape("turtle")
        # Face downward toward the player
        try:
            self.t.setheading(270)
        except Exception:
            pass
        # Ensure visibility on dark background when using fallback polygons
        try:
            self.t.color("#66ff66")
        except Exception:
            pass
        self.t.penup()
        self.alive = True

    def setpos(self, x: float, y: float):
        self.t.goto(x, y)

    def xcor(self):
        return self.t.xcor()

    def ycor(self):
        return self.t.ycor()

    def setx(self, x: float):
        self.t.setx(x)

    def sety(self, y: float):
        self.t.sety(y)

    def hide(self):
        self.t.hideturtle()
        self.alive = False

    def is_visible(self):
        return self.alive and self.t.isvisible()

    def animate(self, tick: int, period: int = 20):
        # Swap frames every 'period' ticks
        if period <= 0:
            period = 20
        if tick % period == 0:
            self.frame_index = 1 - self.frame_index
            try:
                self.t.shape(self.frames[self.frame_index])
            except Exception:
                pass
