# Space Invaders – Turtle (Enhanced MVP)

Arcade-style Space Invaders built with Python’s built-in `turtle`. Includes a menu with difficulty, multi-bullet shooting, progressive levels, and a dual-boss fight.

## Features
- 3 difficulties (affect enemy speed only)
- Player movement (Left/Right) and rapid fire (Space)
- Multi-bullets on screen (cooldown-limited)
- Progressive levels 1–3: more rows/cols and faster fleet
- Enemies move as a fleet and shoot periodically
- Final boss phase: two giant turtle bosses with health bars, aggressive fire
- Menu (1–3 select difficulty), HUD (level + difficulty), restart (R), quit (Q)

## Getting Started

### Requirements
- Python 3.10+ (turtle ships with the standard library)
- On some Linux distros you may need `python3-tk` installed

### Run
```bash
python main.py
```

## Controls
- Menu: `1` Easy, `2` Normal, `3` Hard
- Move: `Left` / `Right`
- Shoot: `Space` (hold to auto-fire)
- Restart after win/lose: `R`
- Quit: `Q`

## Sprites (Optional)
Place GIF files in `assets/` to override fallbacks:
- `assets/player.gif`
- `assets/bullet.gif`
- `assets/enemy_a.gif`, `assets/enemy_b.gif` (2 animation frames)
- `assets/boss.gif`

If sprites are missing, fallback shapes are used instead:
- Player: triangle
- Enemies/Boss: turtle
- Bullet: small rectangle

Turtle supports GIF best. Other formats aren’t supported without extra code.

### Example Assets Layout
```
assets/
├─ player.gif
├─ bullet.gif
├─ enemy_a.gif
├─ enemy_b.gif
└─ boss.gif
```

## Project Structure
```
main.py           # Launcher
game.py           # Game state, levels, collisions, HUD, input
player.py         # Player movement + firing cooldown
bullet.py         # Bullets (player + enemy variants)
enemy.py          # Enemy entity with simple animation
boss.py           # Boss entity (used twice in boss phase)
sprites.py        # Registers optional GIF assets with safe fallbacks
space_invaders.py # Original monolithic version (kept for reference)
```

## Notes
- Uses `screen.tracer(0)` and an `ontimer` loop for smooth animation.
- Window close shortcut: on most systems you can press `Q` to quit.
