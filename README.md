# 🐍 Snakes and Ladders (Desktop Edition)

![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat&logo=windows)
![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat&logo=python)
![Latest Release](https://img.shields.io/github/v/release/YOUR_USERNAME/YOUR_REPO?label=Release&color=success)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

A modern, standalone desktop implementation of the classic board game built in Python using **Tkinter**. Enjoy smooth animations, retro sound effects, custom game modes, toggleable power-ups, and persistent match statistics—packaged with **zero external runtime dependencies**.

---

## 🎮 Quick Download (No Installation Required)

If you just want to play the game on Windows without installing Python:

1. Head over to the **[Latest Release](../../releases/latest)** page.
2. Under **Assets**, download `SnakesAndLadders_v1.2.exe`.
3. Double-click the file to launch and play immediately!

---

## ✨ Features

- **Classic 10×10 Grid:** Faithful serpentine numbering (squares 1 to 100).
- **Flexible Match Modes:** 
  - Solo vs. Computer opponent
  - 2 to 4 Players local Pass-and-Play
- **Fluid Hop Animations:** Tokens hop tile-by-tile across the board instead of teleporting.
- **Graphic Assets:** Custom procedural canvas rendering for curving snakes and wooden ladders with cross rungs.
- **Retro Native Audio:** Windows `winsound` sound effects for rolls, hops, ladders, snake bites, and fanfares (fails gracefully on other OS platforms).
- **Mystery Power-Up Tiles (Toggleable):**
  - ⭐ **Star Boost (+3):** Leap 3 tiles forward.
  - 🛡️ **Snake Shield:** Absorbs and cancels the next snake bite.
  - ❄️ **Freeze Trap:** Forces the player to skip their next turn.
- **Exact Finish Rule:** Players must roll the exact number required to hit tile 100.
- **Match Tracker & Stats:** Real-time event ticker and a persistent local leaderboard (`snakes_stats.json`) tracking wins and fastest finishes.
- **Audio & Visual Polish:** Victory confetti animations and instant audio mute toggle.

---

## 📊 Version Comparison

| Feature | v1.0 | v1.1 | v1.2 (Latest) |
|:---|:---:|:---:|:---:|
| 10×10 Serpentine Grid | ✅ | ✅ | ✅ |
| Solo vs. CPU Mode | ✅ | ✅ | ✅ |
| 2–4 Local Pass-and-Play | ❌ | ✅ | ✅ |
| Hop-by-Hop Animations | ❌ | ✅ | ✅ |
| Illustrated Snakes & Ladders | ❌ | ✅ | ✅ |
| Retro Sound Effects | ❌ | ✅ | ✅ |
| Live Match Activity Log | ❌ | ✅ | ✅ |
| Exact Finish at 100 | ❌ | ✅ | ✅ |
| Power-Up Tiles (⭐, 🛡️, ❄️) | ❌ | ❌ | ✅ |
| Persistent Leaderboard (`.json`) | ❌ | ❌ | ✅ |
| Audio Mute Toggle | ❌ | ❌ | ✅ |
| Victory Confetti Burst | ❌ | ❌ | ✅ |

---

## 🕹️ Game Rules & Power-Ups

- **Movement:** Take turns rolling a 6-sided die. First player to reach square **100** wins.
- **Ladders:** Land on the base of a green ladder to climb immediately to the top rung.
- **Snakes:** Land on a red snake's head to slide all the way down to its tail.
- **Overshooting:** To reach 100, your roll must match the exact number of squares needed. If you overshoot, your turn is forfeited.
- **Power-Ups (v1.2):**
  - **Star (Tiles 25, 55, 80):** Grants 3 additional spaces.
  - **Shield (Tiles 12, 45, 70):** Provides passive immunity against the next snake you land on.
  - **Freeze (Tiles 33, 76):** Freezes your piece, causing you to forfeit your next roll.

---

## 🛠️ Running from Source

### Prerequisites
* [Python 3.8+](https://www.python.org/downloads/) installed and added to your system `PATH`.
* Uses standard library modules only (`tkinter`, `random`, `math`, `json`, `winsound`).

### Instructions
```bash
# 1. Clone this repository
git clone [https://github.com/YOUR_USERNAME/YOUR_REPO.git](https://github.com/YOUR_USERNAME/YOUR_REPO.git)
cd YOUR_REPO

# 2. Run the latest version
python snakes_ladders_v1.2.py
```

---

## 📦 Building the Standalone Executable (.exe)

You can compile any version of the script into a single binary using [PyInstaller](https://pyinstaller.org/):

```bash
# Install PyInstaller
pip install pyinstaller

# Compile standalone executable (no terminal popup)
pyinstaller --noconsole --onefile --name "SnakesAndLadders_v1.2" snakes_ladders_v1.2.py

```

The completed executable will appear in the newly generated `dist/` folder:

```text
dist/SnakesAndLadders_v1.2.exe

```

---

## 📁 Repository Structure

```text
├── dist/                          # Generated standalone binaries (.exe)
├── snakes_ladders.py              # Version 1.0 baseline
├── snakes_ladders_v1.1.py         # Version 1.1 with multiplayer & hop animations
├── snakes_ladders_v1.2.py         # Version 1.2 with power-ups & leaderboard (Current)
├── snakes_stats.json              # Local match history & leaderboard (created on run)
├── .gitignore                     # Ignores build artifacts and temp files
├── LICENSE                        # MIT License
└── README.md                      # Project documentation

```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.
