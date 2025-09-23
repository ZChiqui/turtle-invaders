import turtle


class Boss:
    def __init__(self, shape_name: str, dx: float = 3.0, hp: int = 15, size: float = 1.0):
        self.t = turtle.Turtle()
        self.t.shape(shape_name)
        self.t.penup()
        self.t.color("#ff5555")
        # Face downward toward the player
        try:
            self.t.setheading(270)
        except Exception:
            pass
        try:
            self.t.shapesize(size, size)
        except Exception:
            pass
        self.dx = dx
        self.hp = hp
        self.hp_max = hp

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

    def update(self, left: float, right: float, bottom: float) -> bool:
        # Returns True if game over due to reaching bottom
        nx = self.xcor() + self.dx
        if nx < left + 30 or nx > right - 30:
            self.dx *= -1
            self.sety(self.ycor() - 20)
            if self.ycor() < bottom + 80:
                return True
        else:
            self.setx(nx)
        return False
