import os
import turtle


class SpriteLoader:
    """Registers optional GIF sprites if present, with safe fallbacks.

    Looks for files in ./assets/ by default:
      - player.gif
      - bullet.gif
      - enemy_a.gif, enemy_b.gif (2-frame animation)
      - boss.gif

    Fallbacks use simple registered polygons so the game runs without assets.
    """

    def __init__(self, assets_dir: str = "assets"):
        self.assets_dir = assets_dir
        self._shapes_registered = set()

        # Pre-register fallback polygonal shapes
        self.fallback_player = self._register_polygon(
            name="fallback_player",
            points=[(-10, -10), (10, -10), (0, 12)],
            outline="white",
            fill="cyan",
        )
        self.fallback_bullet = self._register_polygon(
            name="fallback_bullet",
            points=[(-2, -6), (2, -6), (2, 6), (-2, 6)],
            outline="yellow",
            fill="yellow",
        )
        # For enemies, use the built-in 'turtle' shape as fallback (per request)
        self.fallback_enemy_a = "turtle"
        self.fallback_enemy_b = "turtle"
        self.fallback_boss = self._register_polygon(
            name="fallback_boss",
            points=[(-30, -20), (30, -20), (30, 20), (-30, 20)],
            outline="#ff5555",
            fill="#ff5555",
        )

        # Try to register GIFs if present
        self.player = self._register_gif("player.gif") or self.fallback_player
        self.bullet = self._register_gif("bullet.gif") or self.fallback_bullet
        self.enemy_frames = [
            self._register_gif("enemy_a.gif") or self.fallback_enemy_a,
            self._register_gif("enemy_b.gif") or self.fallback_enemy_b,
        ]
        self.boss = self._register_gif("boss.gif") or self.fallback_boss

    def _register_gif(self, filename: str):
        path = os.path.join(self.assets_dir, filename)
        if os.path.exists(path):
            try:
                turtle.register_shape(path)
                self._shapes_registered.add(path)
                return path
            except Exception:
                return None
        return None

    def _register_polygon(self, name: str, points, outline: str, fill: str):
        shape = turtle.Shape("polygon", points)
        try:
            turtle.register_shape(name, shape)
        except Exception:
            # If already registered, ignore
            pass
        return name
