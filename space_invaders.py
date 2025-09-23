import turtle
import time
import random


class SpaceInvaders:
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    BORDER_LEFT = -380
    BORDER_RIGHT = 380
    BORDER_TOP = 280
    BORDER_BOTTOM = -280

    LEVEL_CONFIG = {
        1: {"rows": 3, "cols": 7},
        2: {"rows": 4, "cols": 8},
        3: {"rows": 5, "cols": 9},
    }

    DIFFICULTY_SPEED = {
        "Easy": 1.0,
        "Normal": 1.3,
        "Hard": 1.7,
    }

    def __init__(self):
        # Screen setup
        self.screen = turtle.Screen()
        self.screen.setup(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.screen.title("Space Invaders - Turtle Edition")
        self.screen.bgcolor("black")
        self.screen.tracer(0)

        # Pens / HUD
        self.menu_pen = turtle.Turtle(visible=False)
        self.menu_pen.color("white")
        self.menu_pen.penup()

        self.hud_pen = turtle.Turtle(visible=False)
        self.hud_pen.color("white")
        self.hud_pen.penup()
        self.hud_pen.goto(self.BORDER_LEFT + 10, self.BORDER_TOP + 10)

        self.health_pen = turtle.Turtle(visible=False)
        self.health_pen.hideturtle()
        self.health_pen.penup()
        self.health_pen.color("white")

        # Player
        self.player = turtle.Turtle()
        self.player.shape("triangle")
        self.player.color("cyan")
        self.player.shapesize(stretch_wid=1.2, stretch_len=1.2)
        self.player.penup()
        self.player.setheading(90)
        self.player.goto(0, self.BORDER_BOTTOM + 40)
        self.player_speed = 6
        self.left_pressed = False
        self.right_pressed = False

        # Bullet
        self.bullet = turtle.Turtle(visible=False)
        self.bullet.shape("square")
        self.bullet.color("yellow")
        self.bullet.shapesize(stretch_wid=0.3, stretch_len=0.8)
        self.bullet.penup()
        self.bullet_speed = 12
        self.bullet_active = False

        # Enemies and Boss
        self.enemies = []
        self.enemy_dx = 2.2
        self.enemy_drop = 30

        self.boss = None
        self.boss_dx = 3.0
        self.boss_hp = 0
        self.boss_hp_max = 0

        # Game state
        self.state = "menu"  # menu, playing, boss, victory, gameover
        self.level = 1
        self.difficulty = None
        self.diff_mult = 1.0

        # Input bindings
        self.bind_keys()

        # Show menu initially
        self.show_menu()

        # Kick off update loop
        self.schedule_next_frame()

    # ---------------------- UI / HUD ----------------------
    def show_menu(self):
        self.menu_pen.clear()
        self.menu_pen.goto(0, 140)
        self.menu_pen.write("SPACE INVADERS", align="center", font=("Arial", 32, "bold"))
        self.menu_pen.goto(0, 90)
        self.menu_pen.write("Turtle Edition", align="center", font=("Arial", 18, "normal"))
        self.menu_pen.goto(0, 30)
        self.menu_pen.write("Select Difficulty:", align="center", font=("Arial", 16, "normal"))
        self.menu_pen.goto(0, 0)
        self.menu_pen.write("1) Easy   2) Normal   3) Hard", align="center", font=("Arial", 16, "normal"))
        self.menu_pen.goto(0, -60)
        self.menu_pen.write("Controls: Left/Right Arrows to move, Space to shoot", align="center", font=("Arial", 12, "normal"))
        self.menu_pen.goto(0, -90)
        self.menu_pen.write("Press Q to quit", align="center", font=("Arial", 12, "normal"))

    def clear_menu(self):
        self.menu_pen.clear()

    def update_hud(self):
        self.hud_pen.clear()
        if self.state in ("playing", "boss"):
            self.hud_pen.goto(self.BORDER_LEFT + 10, self.BORDER_TOP + 10)
            text = f"Level {self.level} | Difficulty: {self.difficulty}"
            self.hud_pen.write(text, font=("Arial", 12, "normal"))

    def draw_boss_health(self):
        self.health_pen.clear()
        if self.state == "boss" and self.boss and self.boss_hp_max > 0:
            # Draw a static health bar at the top center
            bar_width = 300
            bar_height = 16
            x = -bar_width // 2
            y = self.BORDER_TOP - 10
            # Outline
            self.health_pen.goto(x, y)
            self.health_pen.pendown()
            self.health_pen.pencolor("white")
            self.health_pen.fillcolor("black")
            self.health_pen.begin_fill()
            for _ in range(2):
                self.health_pen.forward(bar_width)
                self.health_pen.right(90)
                self.health_pen.forward(bar_height)
                self.health_pen.right(90)
            self.health_pen.end_fill()
            self.health_pen.penup()

            # Fill amount
            ratio = max(0.0, min(1.0, self.boss_hp / self.boss_hp_max))
            fill_w = int(bar_width * ratio)
            self.health_pen.goto(x, y)
            self.health_pen.pendown()
            self.health_pen.fillcolor("red")
            self.health_pen.begin_fill()
            for _ in range(2):
                self.health_pen.forward(fill_w)
                self.health_pen.right(90)
                self.health_pen.forward(bar_height)
                self.health_pen.right(90)
            self.health_pen.end_fill()
            self.health_pen.penup()

            # Label
            self.health_pen.goto(0, y - 22)
            self.health_pen.write(f"Boss HP: {self.boss_hp}/{self.boss_hp_max}", align="center", font=("Arial", 12, "normal"))

    # ---------------------- Input ----------------------
    def bind_keys(self):
        self.screen.listen()

        # Difficulty selection
        self.screen.onkey(lambda: self.start_game("Easy"), "1")
        self.screen.onkey(lambda: self.start_game("Normal"), "2")
        self.screen.onkey(lambda: self.start_game("Hard"), "3")

        # Movement (press/release)
        self.screen.onkeypress(self.on_left_press, "Left")
        self.screen.onkeypress(self.on_right_press, "Right")
        # onkeyrelease is supported in modern turtle; if not, movement will still work but may be a bit sticky.
        try:
            self.screen.onkeyrelease(self.on_left_release, "Left")
            self.screen.onkeyrelease(self.on_right_release, "Right")
        except Exception:
            pass

        # Shooting
        self.screen.onkey(self.fire_bullet, "space")

        # Restart / Quit
        self.screen.onkey(self.restart_to_menu, "r")
        self.screen.onkey(self.quit_game, "q")

    def on_left_press(self):
        self.left_pressed = True

    def on_right_press(self):
        self.right_pressed = True

    def on_left_release(self):
        self.left_pressed = False

    def on_right_release(self):
        self.right_pressed = False

    # ---------------------- Game Flow ----------------------
    def start_game(self, difficulty: str):
        if self.state != "menu":
            return
        self.difficulty = difficulty
        self.diff_mult = self.DIFFICULTY_SPEED[difficulty]
        self.clear_menu()
        self.level = 1
        self.reset_player()
        self.spawn_level_enemies(self.level)
        self.state = "playing"
        self.update_hud()

    def reset_player(self):
        self.player.goto(0, self.BORDER_BOTTOM + 40)
        self.left_pressed = False
        self.right_pressed = False
        self.reset_bullet()

    def reset_bullet(self):
        self.bullet.hideturtle()
        self.bullet_active = False

    def restart_to_menu(self):
        # Allow restart from game over / victory screens
        if self.state in ("menu",):
            return
        if self.state in ("gameover", "victory"):
            self.cleanup_all()
            self.state = "menu"
            self.show_menu()
            self.update_hud()

    def quit_game(self):
        try:
            turtle.bye()
        except Exception:
            pass

    def cleanup_all(self):
        for e in self.enemies:
            e.hideturtle()
        self.enemies.clear()
        if self.boss:
            self.boss.hideturtle()
            self.boss = None
        self.reset_bullet()
        self.health_pen.clear()

    # ---------------------- Spawning ----------------------
    def spawn_level_enemies(self, level: int):
        self.cleanup_all()
        cfg = self.LEVEL_CONFIG.get(level, self.LEVEL_CONFIG[3])
        rows, cols = cfg["rows"], cfg["cols"]
        spacing_x = 60
        spacing_y = 45
        total_width = (cols - 1) * spacing_x
        start_x = -total_width / 2
        start_y = self.BORDER_TOP - 100
        colors = ["#66ff66", "#99ff99", "#55ddff", "#ffcc66", "#ff8888"]

        for r in range(rows):
            for c in range(cols):
                enemy = turtle.Turtle()
                enemy.shape("square")
                enemy.color(colors[r % len(colors)])
                enemy.shapesize(stretch_wid=1.1, stretch_len=1.1)
                enemy.penup()
                x = start_x + c * spacing_x
                y = start_y - r * spacing_y
                enemy.goto(x, y)
                self.enemies.append(enemy)

        # Set fleet movement speed scaled by level and difficulty
        base = 1.8 + (level - 1) * 0.6
        self.enemy_dx = base * self.diff_mult

    def spawn_boss(self):
        self.cleanup_all()
        self.boss = turtle.Turtle()
        self.boss.shape("square")
        self.boss.color("#ff5555")
        self.boss.shapesize(stretch_wid=2.5, stretch_len=4.0)
        self.boss.penup()
        self.boss.goto(0, self.BORDER_TOP - 120)
        # Boss speed and HP are fixed (difficulty affects only enemies)
        self.boss_dx = 3.0
        self.boss_hp_max = 15
        self.boss_hp = self.boss_hp_max
        self.draw_boss_health()

    # ---------------------- Actions ----------------------
    def fire_bullet(self):
        if self.state not in ("playing", "boss"):
            return
        if not self.bullet_active:
            self.bullet_active = True
            self.bullet.goto(self.player.xcor(), self.player.ycor() + 12)
            self.bullet.showturtle()
            self.bullet.setheading(90)

    # ---------------------- Update Loop ----------------------
    def schedule_next_frame(self):
        self.screen.ontimer(self.update, 16)  # ~60 FPS

    def update(self):
        # State machine
        if self.state == "menu":
            pass  # menu is static, waiting for key press
        elif self.state == "playing":
            self.update_player()
            self.update_bullet()
            self.update_enemies()
            self.check_level_progression()
        elif self.state == "boss":
            self.update_player()
            self.update_bullet()
            self.update_boss()
        elif self.state in ("victory", "gameover"):
            pass

        self.update_hud()
        if self.state == "boss":
            self.draw_boss_health()

        self.screen.update()
        self.schedule_next_frame()

    # ---------------------- Per-entity updates ----------------------
    def update_player(self):
        dx = 0
        if self.left_pressed and not self.right_pressed:
            dx = -self.player_speed
        elif self.right_pressed and not self.left_pressed:
            dx = self.player_speed

        if dx != 0:
            nx = self.player.xcor() + dx
            nx = max(self.BORDER_LEFT + 15, min(self.BORDER_RIGHT - 15, nx))
            self.player.setx(nx)

    def update_bullet(self):
        if not self.bullet_active:
            return
        ny = self.bullet.ycor() + self.bullet_speed
        self.bullet.sety(ny)
        if ny > self.BORDER_TOP:
            self.reset_bullet()
            return

        if self.state == "playing":
            # Check collisions with enemies
            hit_indices = []
            for i, e in enumerate(self.enemies):
                if e.isvisible() and self.bullet.distance(e) < 20:
                    hit_indices.append(i)
            if hit_indices:
                # Remove the first hit enemy
                idx = hit_indices[0]
                self.enemies[idx].hideturtle()
                self.enemies.pop(idx)
                self.reset_bullet()

        elif self.state == "boss" and self.boss is not None:
            if self.bullet.distance(self.boss) < 40:
                self.boss_hp -= 1
                self.reset_bullet()
                if self.boss_hp <= 0:
                    self.boss.hideturtle()
                    self.boss = None
                    self.state = "victory"
                    self.show_victory()

    def update_enemies(self):
        if not self.enemies:
            return
        # Determine if any will hit border next move
        next_hit_border = False
        for e in self.enemies:
            if not e.isvisible():
                continue
            nx = e.xcor() + self.enemy_dx
            if nx < self.BORDER_LEFT or nx > self.BORDER_RIGHT:
                next_hit_border = True
                break

        if next_hit_border:
            self.enemy_dx *= -1
            for e in self.enemies:
                if e.isvisible():
                    e.sety(e.ycor() - self.enemy_drop)
                    if e.ycor() < self.BORDER_BOTTOM + 60:
                        self.state = "gameover"
                        self.show_game_over(reason="Enemies reached the bottom")
                        return

        for e in self.enemies:
            if e.isvisible():
                e.setx(e.xcor() + self.enemy_dx)

    def check_level_progression(self):
        if not self.enemies and self.state == "playing":
            if self.level < 3:
                self.level += 1
                self.spawn_level_enemies(self.level)
            else:
                self.state = "boss"
                self.spawn_boss()

    def update_boss(self):
        if not self.boss:
            return
        nx = self.boss.xcor() + self.boss_dx
        if nx < self.BORDER_LEFT + 30 or nx > self.BORDER_RIGHT - 30:
            self.boss_dx *= -1
            # Shift down slightly when bouncing
            self.boss.sety(self.boss.ycor() - 20)
            if self.boss.ycor() < self.BORDER_BOTTOM + 80:
                self.state = "gameover"
                self.show_game_over(reason="Boss reached the player line")
                return
        else:
            self.boss.setx(nx)

        # Collision with player -> game over
        if self.player and self.boss and self.player.distance(self.boss) < 35:
            self.state = "gameover"
            self.show_game_over(reason="Boss collided with player")

    # ---------------------- End States ----------------------
    def show_victory(self):
        self.menu_pen.clear()
        self.menu_pen.goto(0, 60)
        self.menu_pen.color("#66ff66")
        self.menu_pen.write("VICTORY!", align="center", font=("Arial", 32, "bold"))
        self.menu_pen.color("white")
        self.menu_pen.goto(0, 10)
        self.menu_pen.write("You defeated the boss.", align="center", font=("Arial", 16, "normal"))
        self.menu_pen.goto(0, -40)
        self.menu_pen.write("Press R to return to main menu.", align="center", font=("Arial", 14, "normal"))

    def show_game_over(self, reason: str = ""):
        self.menu_pen.clear()
        self.menu_pen.goto(0, 60)
        self.menu_pen.color("#ff6666")
        self.menu_pen.write("GAME OVER", align="center", font=("Arial", 32, "bold"))
        self.menu_pen.color("white")
        self.menu_pen.goto(0, 10)
        self.menu_pen.write(reason, align="center", font=("Arial", 14, "normal"))
        self.menu_pen.goto(0, -40)
        self.menu_pen.write("Press R to return to main menu.", align="center", font=("Arial", 14, "normal"))

    # ---------------------- Entrypoint ----------------------
    def run(self):
        turtle.done()


if __name__ == "__main__":
    game = SpaceInvaders()
    game.run()
