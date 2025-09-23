import time
import turtle
import random
from typing import List, Optional

from sprites import SpriteLoader
from player import Player
from bullet import Bullet, EnemyBullet
from enemy import Enemy
from boss import Boss


class Game:
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
        # Screen
        self.screen = turtle.Screen()
        self.screen.setup(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.screen.title("Space Invaders - Enhanced MVP")
        self.screen.bgcolor("black")
        self.screen.tracer(0)

        # Sprites
        self.sprites = SpriteLoader()

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

        # Entities
        self.player: Optional[Player] = None
        self.bullets: List[Bullet] = []
        self.enemies: List[Enemy] = []
        self.enemy_dx = 2.2
        self.enemy_drop = 30
        self.boss: Optional[Boss] = None
        self.bosses: List[Boss] = []
        self.enemy_bullets: List[EnemyBullet] = []

        # Game state
        self.state = "menu"  # menu, playing, boss, victory, gameover
        self.level = 1
        self.difficulty = None
        self.diff_mult = 1.0
        self.tick = 0

        # Input
        self.bind_keys()

        # Menu
        self.show_menu()

        # Loop
        self.schedule_next_frame()

    # ---------------------- Input ----------------------
    def bind_keys(self):
        self.screen.listen()
        # Difficulty selection
        self.screen.onkey(lambda: self.start_game("Easy"), "1")
        self.screen.onkey(lambda: self.start_game("Normal"), "2")
        self.screen.onkey(lambda: self.start_game("Hard"), "3")

        # Movement
        self.screen.onkeypress(lambda: self.player and self.player.on_left_press(), "Left")
        self.screen.onkeypress(lambda: self.player and self.player.on_right_press(), "Right")
        try:
            self.screen.onkeyrelease(lambda: self.player and self.player.on_left_release(), "Left")
            self.screen.onkeyrelease(lambda: self.player and self.player.on_right_release(), "Right")
        except Exception:
            pass

        # Shooting (multi-bullets with cooldown on player)
        self.screen.onkeypress(self._player_fire, "space")

        # Restart / Quit
        self.screen.onkey(self.restart_to_menu, "r")
        self.screen.onkey(self.quit_game, "q")

    def _player_fire(self):
        if self.state not in ("playing", "boss") or not self.player:
            return
        self.player.try_fire(self.spawn_bullet)

    # ---------------------- UI / HUD ----------------------
    def show_menu(self):
        self.menu_pen.clear()
        self.menu_pen.goto(0, 140)
        self.menu_pen.write("SPACE INVADERS", align="center", font=("Arial", 32, "bold"))
        self.menu_pen.goto(0, 90)
        self.menu_pen.write("Enhanced MVP", align="center", font=("Arial", 18, "normal"))
        self.menu_pen.goto(0, 30)
        self.menu_pen.write("Select Difficulty:", align="center", font=("Arial", 16, "normal"))
        self.menu_pen.goto(0, 0)
        self.menu_pen.write("1) Easy   2) Normal   3) Hard", align="center", font=("Arial", 16, "normal"))
        self.menu_pen.goto(0, -60)
        self.menu_pen.write("Controls: Left/Right to move, Space to shoot", align="center", font=("Arial", 12, "normal"))
        self.menu_pen.goto(0, -90)
        self.menu_pen.write("R: menu (after game)   Q: quit", align="center", font=("Arial", 12, "normal"))

    def update_hud(self):
        self.hud_pen.clear()
        if self.state in ("playing", "boss"):
            self.hud_pen.goto(self.BORDER_LEFT + 10, self.BORDER_TOP + 10)
            text = f"Level {self.level} | Difficulty: {self.difficulty}"
            self.hud_pen.write(text, font=("Arial", 12, "normal"))

    def draw_boss_health(self):
        self.health_pen.clear()
        if self.state == "boss" and self.bosses:
            bar_width = 280
            bar_height = 14
            y_top = self.BORDER_TOP - 10
            labels = ["Boss A HP", "Boss B HP"]
            for i, boss in enumerate(self.bosses[:2]):
                x = -bar_width // 2
                y = y_top - i * 24
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

                # Fill
                ratio = max(0.0, min(1.0, boss.hp / boss.hp_max))
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
                self.health_pen.write(labels[i], align="center", font=("Arial", 10, "normal"))

    # ---------------------- Game Flow ----------------------
    def start_game(self, difficulty: str):
        if self.state != "menu":
            return
        self.difficulty = difficulty
        self.diff_mult = self.DIFFICULTY_SPEED[difficulty]
        self.menu_pen.clear()
        self.level = 1
        self.setup_player()
        self.spawn_level_enemies(self.level)
        self.state = "playing"
        self.update_hud()

    def setup_player(self):
        self.bullets.clear()
        self.player = Player(self.sprites.player, 0, self.BORDER_BOTTOM + 40)

    def restart_to_menu(self):
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
        # Clear enemies
        for e in self.enemies:
            e.hide()
        self.enemies.clear()
        # Clear bullets
        for b in self.bullets:
            b.deactivate()
        self.bullets.clear()
        # Clear enemy bullets
        for eb in self.enemy_bullets:
            eb.deactivate()
        self.enemy_bullets.clear()
        # Clear player
        if self.player:
            try:
                self.player.t.hideturtle()
            except Exception:
                pass
            self.player = None
        # Clear boss
        if self.boss:
            self.boss.t.hideturtle()
            self.boss = None
        if self.bosses:
            for b in self.bosses:
                try:
                    b.t.hideturtle()
                except Exception:
                    pass
            self.bosses.clear()
        # Clear pens
        self.health_pen.clear()

    # ---------------------- Spawning ----------------------
    def spawn_level_enemies(self, level: int):
        # do not cleanup player or pens here; just enemies and bullets
        for e in self.enemies:
            e.hide()
        self.enemies.clear()
        for b in self.bullets:
            b.deactivate()
        self.bullets.clear()
        for eb in self.enemy_bullets:
            eb.deactivate()
        self.enemy_bullets.clear()

        cfg = self.LEVEL_CONFIG.get(level, self.LEVEL_CONFIG[3])
        rows, cols = cfg["rows"], cfg["cols"]
        spacing_x = 60
        spacing_y = 45
        total_width = (cols - 1) * spacing_x
        start_x = -total_width / 2
        start_y = self.BORDER_TOP - 100

        for r in range(rows):
            for c in range(cols):
                enemy = Enemy(self.sprites.enemy_frames)
                x = start_x + c * spacing_x
                y = start_y - r * spacing_y
                enemy.setpos(x, y)
                self.enemies.append(enemy)

        base = 1.8 + (level - 1) * 0.6
        self.enemy_dx = base * self.diff_mult

    def spawn_boss(self):
        # Clear remaining enemies and bullets
        for e in self.enemies:
            e.hide()
        self.enemies.clear()
        for b in self.bullets:
            b.deactivate()
        self.bullets.clear()
        for eb in self.enemy_bullets:
            eb.deactivate()
        self.enemy_bullets.clear()

        # Two giant turtles moving in opposite directions
        left = Boss("turtle", dx=-3.0, hp=15, size=3.5)
        right = Boss("turtle", dx=3.0, hp=15, size=3.5)
        left.setpos(-140, self.BORDER_TOP - 120)
        right.setpos(140, self.BORDER_TOP - 120)
        self.bosses = [left, right]
        self.draw_boss_health()

    def spawn_bullet(self, x: float, y: float):
        bullet = Bullet(self.sprites.bullet, speed=12.0)
        bullet.fire_from(x, y)
        self.bullets.append(bullet)

    def spawn_enemy_bullet(self, x: float, y: float, speed: float = 6.0):
        eb = EnemyBullet(self.sprites.bullet, speed=speed, color="#ff6666")
        eb.fire_from(x, y)
        self.enemy_bullets.append(eb)

    # ---------------------- Update Loop ----------------------
    def schedule_next_frame(self):
        self.screen.ontimer(self.update, 16)

    def update(self):
        self.tick += 1
        if self.state == "menu":
            pass
        elif self.state == "playing":
            self.update_player()
            self.update_bullets()
            self.update_enemy_bullets()
            self.update_enemies()
            self.check_level_progression()
        elif self.state == "boss":
            self.update_player()
            self.update_bullets()
            self.update_enemy_bullets()
            self.update_bosses()
        elif self.state in ("victory", "gameover"):
            pass

        self.update_hud()
        if self.state == "boss":
            self.draw_boss_health()

        self.screen.update()
        self.schedule_next_frame()

    # ---------------------- Updates ----------------------
    def update_player(self):
        if self.player:
            self.player.update(self.BORDER_LEFT, self.BORDER_RIGHT)

    def update_bullets(self):
        if not self.bullets:
            return
        top = self.BORDER_TOP
        # Update movement
        for b in list(self.bullets):
            b.update()
            if b.offscreen(top):
                b.deactivate()
                self.bullets.remove(b)
                continue
            # Collisions
            if self.state == "playing":
                hit_enemy = None
                for e in self.enemies:
                    if e.is_visible() and b.distance(e.t) < 20:
                        hit_enemy = e
                        break
                if hit_enemy:
                    hit_enemy.hide()
                    if b in self.bullets:
                        b.deactivate()
                        self.bullets.remove(b)
            elif self.state == "boss" and self.bosses:
                hit = False
                for boss in list(self.bosses):
                    if b.distance(boss.t) < 48:
                        boss.hp -= 1
                        hit = True
                        if boss.hp <= 0:
                            boss.t.hideturtle()
                            self.bosses.remove(boss)
                        break
                if hit:
                    b.deactivate()
                    if b in self.bullets:
                        self.bullets.remove(b)
                if not self.bosses:
                    self.state = "victory"
                    self.show_victory()

    def update_enemy_bullets(self):
        if not self.enemy_bullets:
            return
        bottom = self.BORDER_BOTTOM
        for eb in list(self.enemy_bullets):
            eb.update()
            if eb.offscreen(bottom):
                eb.deactivate()
                self.enemy_bullets.remove(eb)
                continue
            # Collision with player
            if self.player and eb.distance(self.player.t) < 18:
                self.state = "gameover"
                self.show_game_over("Hit by enemy fire")
                return

    def update_enemies(self):
        if not self.enemies:
            return
        # Animate
        for e in self.enemies:
            if e.is_visible():
                e.animate(self.tick, period=16)

        # Move as a fleet
        next_hit_border = False
        for e in self.enemies:
            if not e.is_visible():
                continue
            nx = e.xcor() + self.enemy_dx
            if nx < self.BORDER_LEFT or nx > self.BORDER_RIGHT:
                next_hit_border = True
                break

        if next_hit_border:
            self.enemy_dx *= -1
            for e in self.enemies:
                if e.is_visible():
                    e.sety(e.ycor() - self.enemy_drop)
                    if e.ycor() < self.BORDER_BOTTOM + 60:
                        self.state = "gameover"
                        self.show_game_over("Enemies reached the bottom")
                        return

        for e in self.enemies:
            if e.is_visible():
                e.setx(e.xcor() + self.enemy_dx)

        # Fire: every few ticks, one random enemy shoots
        if self.tick % 28 == 0:
            shooters = [e for e in self.enemies if e.is_visible()]
            if shooters:
                shooter = random.choice(shooters)
                self.spawn_enemy_bullet(shooter.xcor(), shooter.ycor() - 12, speed=6.0)

    def check_level_progression(self):
        # Clear out dead enemies from list
        self.enemies = [e for e in self.enemies if e.is_visible()]
        if not self.enemies and self.state == "playing":
            if self.level < 3:
                self.level += 1
                self.spawn_level_enemies(self.level)
            else:
                self.state = "boss"
                self.spawn_boss()

    def update_bosses(self):
        if not self.bosses:
            return
        # Move and check
        for boss in list(self.bosses):
            if boss.update(self.BORDER_LEFT, self.BORDER_RIGHT, self.BORDER_BOTTOM):
                self.state = "gameover"
                self.show_game_over("Boss reached the player line")
                return
            if self.player and self.player.t.distance(boss.t) < 35:
                self.state = "gameover"
                self.show_game_over("Boss collided with player")
                return
        # More aggressive firing: each boss fires frequently in pairs
        if self.tick % 10 == 0:
            for boss in self.bosses:
                y = boss.ycor() - 28
                x = boss.xcor()
                self.spawn_enemy_bullet(x - 14, y, speed=8.0)
                self.spawn_enemy_bullet(x + 14, y, speed=8.0)

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
