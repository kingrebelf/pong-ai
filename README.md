# PONG - Player vs Adaptive AI

Classic Pong rebuilt in Python with an AI opponent that learns and adapts.

## Features
- Player vs AI gameplay
- Adaptive AI that gets harder as you score
- Sound effects (paddle hit, wall bounce, scoring)
- Clean retro look
- AI difficulty level displayed on screen

## Requirements
- Python 3.10+
- pygame-ce

## Quick Start
```bash
pip install pygame-ce
python pong.py
```

## Build Windows .exe
Run `build.bat` — it installs dependencies and builds a standalone executable in the `dist/` folder.

## Controls
| Key | Action |
|-----|--------|
| ↑ Arrow | Move paddle up |
| ↓ Arrow | Move paddle down |
| Space | Start / Pause |
| Escape | Quit |

## AI Difficulty
The AI starts easy and gets progressively harder each time you score. It tracks the ball more accurately and reacts faster at higher levels. Level is displayed in the top-left corner.

## Credits
Built by Nova (AI orchestrator) and Gemma (AI worker) for Ben Weissig.
