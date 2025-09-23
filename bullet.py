import turtle


class Bullet:
    def __init__(self, shape_name: str, speed: float = 12.0):
        self.t = turtle.Turtle(visible=False)
        self.t.shape(shape_name)
        self.t.color("yellow")
        self.t.penup()
        self.speed = speed
        self.active = False

    def fire_from(self, x: float, y: float):
        self.t.goto(x, y)
        self.t.setheading(90)
        self.t.showturtle()
        self.active = True

    def update(self):
        if not self.active:
            return
        self.t.sety(self.t.ycor() + self.speed)

    def offscreen(self, top: float) -> bool:
        return self.t.ycor() > top

    def deactivate(self):
        self.t.hideturtle()
        self.active = False

    def distance(self, other_turtle: turtle.Turtle) -> float:
        return self.t.distance(other_turtle)


class EnemyBullet:
    def __init__(self, shape_name: str, speed: float = 6.0, color: str = "red"):
        self.t = turtle.Turtle(visible=False)
        self.t.shape(shape_name)
        try:
            self.t.color(color)
        except Exception:
            pass
        self.t.penup()
        self.speed = speed
        self.active = False

    def fire_from(self, x: float, y: float):
        self.t.goto(x, y)
        self.t.setheading(270)
        self.t.showturtle()
        self.active = True

    def update(self):
        if not self.active:
            return
        self.t.sety(self.t.ycor() - self.speed)

    def offscreen(self, bottom: float) -> bool:
        return self.t.ycor() < bottom

    def deactivate(self):
        self.t.hideturtle()
        self.active = False

    def distance(self, other_turtle: turtle.Turtle) -> float:
        return self.t.distance(other_turtle)
