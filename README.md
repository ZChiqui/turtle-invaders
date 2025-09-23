Space Invaders – Turtle (Enhanced MVP)

Arcade-style Space Invaders built with Python’s built-in turtle. Includes a menu with difficulty, multi-bullet shooting, progressive levels, and a dual-boss fight.

Features
- 3 difficulties (affect enemy speed only)
- Player movement (Left/Right) and rapid fire (Space)
- Multi-bullets on screen (cooldown-limited)
- Progressive levels 1–3: more rows/cols and faster fleet
- Enemies move as a fleet and shoot periodically
- Final boss phase: two giant turtle bosses with health bars, aggressive fire
- Menu (1–3 select difficulty), HUD (level + difficulty), restart (R), quit (Q)

Run
- Python 3.10+ recommended. Turtle comes with standard Python.
- Command: `python main.py`

Controls
- Menu: `1` Easy, `2` Normal, `3` Hard
- Move: `Left` / `Right`
- Shoot: `Space` (hold to auto-fire)
- Restart after win/lose: `R`
- Quit: `Q`

Sprites (optional)
Place GIF files in `assets/` to override fallbacks:
- `assets/player.gif`
- `assets/bullet.gif`
- `assets/enemy_a.gif`, `assets/enemy_b.gif` (2 animation frames)
- `assets/boss.gif`

If sprites are missing, fallback shapes are used (player: triangle; enemies/boss: turtle; bullet: rectangle).

Note: turtle supports GIF best. Other formats aren’t supported without extra code.

Project Structure
- `main.py` — launcher
- `game.py` — game state, levels, collisions, HUD, input
- `player.py` — player movement + firing cooldown
- `bullet.py` — bullets (player + enemy variants)
- `enemy.py` — enemy entity with simple animation
- `boss.py` — boss entity (used twice in boss phase)
- `sprites.py` — registers optional GIF assets with safe fallbacks
- `space_invaders.py` — original monolithic version (kept for reference)

Notes
- macOS/Linux may require tkinter support (usually bundled; on some Linux distros install `python3-tk`).
- The game uses `screen.tracer(0)` with a manual loop via `ontimer` for smoother animation.

