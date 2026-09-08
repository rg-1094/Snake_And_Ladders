# 🐍 Snakes & Ladders (Desktop Edition)

![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows)
![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python)
![Latest Release](https://img.shields.io/badge/Release-v2.0_Infinite-success?style=for-the-badge)
![Dependencies](https://img.shields.io/badge/Dependencies-Zero%20External-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

A feature-rich, portable desktop implementation of the classic board game built with Python and **Tkinter**. Engineered with smooth hop animations, procedural board generation, customizable player avatars, tactical power-ups, retro audio synthesis, and match state saving—compiled into a clean, standalone Windows `.exe` with **zero external dependencies**.

---

## ⚡ Quick Start: Play Immediately (Windows)

No Python installation required. Download the pre-built binary and launch:

1. Open the **[Releases](../../releases/latest)** tab.
2. Download the latest binary: `SnakesAndLadders_v2.0.exe`.
3. Double-click the file to play.

---

## 🌟 Key Highlights

* **Multiple Board Modes:** Play the classic 10×10 marathon (100 tiles) or jump into a fast-paced 8×8 Blitz match (64 tiles).
* **Procedural Map Generator:** Break away from standard boards. Generate endless, mathematically validated random maps where no traps overlap and all paths remain solvable.
* **Tactical Power-Up System:** Turn classic luck into strategy with Shields, Star Boosts, Freeze Traps, and Free Rerolls.
* **Custom Avatars:** Choose from 6 unique player symbols (🚀, 🤖, ⚡, 💎, 👑, 🦁) and signature token colors.
* **Hop-by-Hop Animation Engine:** Pawns physically hop cell-by-cell across the board with customizable speed pacing (**Normal**, **Fast**, **Instant**).
* **Game State Persistence (Save & Resume):** Match states auto-save to `snakes_save.json` so you can close the window and resume your game at any time.
* **Hall of Fame & Statistics:** Built-in leaderboard tracks total matches, cumulative player wins, and record-fastest finishes in `snakes_stats.json`.
* **Zero External Dependencies:** Runs purely on Python standard library modules (`tkinter`, `random`, `math`, `json`, `winsound`).

---

## 📊 Version Evolution & Feature Comparison

| Feature | v1.0 Baseline | v1.1 Deluxe | v1.2 Power-Ups | v2.0 Infinite (Latest) |
| :--- | :---: | :---: | :---: | :---: |
| **Board Grid** | 10×10 Classic | 10×10 Classic | 10×10 Classic | **10×10 & 8×8 Blitz** |
| **Map Architecture** | Fixed Layout | Fixed Layout | Fixed Layout | **Fixed + Procedural** |
| **Game Modes** | Solo vs. CPU | 1–4 Players / CPU | 1–4 Players / CPU | **1–4 Players / CPU** |
| **Movement** | Instant Jump | Hop-by-Hop Hop | Hop-by-Hop Hop | **Paced Hop-by-Hop** |
| **Board Rendering** | Line Arrows | Rendered Snakes/Rails | Rendered Snakes/Rails | **Dark-Themed HD Graphics** |
| **Player Tokens** | Plain Discs | Numbered Discs | Status-Ring Discs | **Custom Token Avatars** |
| **Audio Engine** | Silent | Native Windows SFX | SFX + Mute Switch | **SFX + Mute Switch** |
| **Finish Mechanics** | Standard Landing | Exact Roll (100) | Exact Roll (100) | **Exact Roll (64 / 100)** |
| **Match Activity Log** | ❌ | Live Event Ticker | Live Event Ticker | **Live Event Ticker** |
| **Special Power-Ups** | ❌ | ❌ | ⭐, 🛡️, ❄️ | **⭐, 🛡️, ❄️, 🎲 (Reroll)** |
| **Leaderboard / Stats** | ❌ | ❌ | Local JSON Records | **Local JSON Records** |
| **Save / Resume State**| ❌ | ❌ | ❌ | **Auto/Manual JSON State**|
| **Animation Speed** | Fixed | Fixed | Fixed | **Normal / Fast / Instant** |
| **Hotkeys** | ❌ | ❌ | ❌ | **Spacebar / Enter Roll** |
| **Victory VFX** | Dialog Box | Dialog Box | Confetti Burst | **Fireworks Engine** |

---

## 🕹️ Game Rules & Board Mechanics

### The Core Objective
Roll the die and maneuver your token from tile 1 to the final tile (tile 64 on Blitz, tile 100 on Classic). The first player to reach the final tile wins.

* **Ladders:** Landing on the base of a green ladder propels your pawn directly to the top rung.
* **Snakes:** Landing on a red serpent's head forces your pawn to slide down to the tip of its tail.
* **Exact Finish Required:** You must roll the exact number remaining to reach the final tile. Any overshoot results in a forfeited turn.

### Power-Ups & Modifier Tiles (Toggleable)
When enabled, landing on marked squares activates unique effects:

| Icon | Name | In-Game Effect |
| :---: | :--- | :--- |
| ⭐ | **Star Surge** | Grants an immediate bonus forward leap (+3 squares). |
| 🛡️ | **Aegis Shield** | Grants passive immunity that absorbs and cancels the next snake bite you hit. |
| ❄️ | **Cryo Trap** | Freezes your pawn in ice, forcing you to forfeit your next roll. |
| 🎲 | **Lucky Tile** | Grants an immediate, free second dice roll during your turn. |

---

## ⌨️ Controls & Shortcuts

* **Left Click / Spacebar / Enter:** Roll the dice when it is your turn.
* **Speed Selector:** Toggle between **Normal** (cinematic), **Fast** (rapid play), and **Instant** (teleport hopping) at any point during a match.
* **Save Button:** Commits the current game board, player positions, power-ups, and turns to `snakes_save.json`.
* **Audio Checkbox:** Instantly toggles synthesized Windows sound effects on or off.

---

## 🛠️ Running from Source

### Prerequisites
* **Python 3.8+** installed and added to your system `PATH`.
* Compatible with Windows, macOS, and Linux (Audio features utilize Windows `winsound` and fail gracefully and silently on non-Windows platforms).

### Execution
```bash
# Clone the repository
git clone [https://github.com/YOUR_USERNAME/YOUR_REPO.git](https://github.com/YOUR_USERNAME/YOUR_REPO.git)
cd YOUR_REPO

# Launch the latest edition
python snakes_ladders_v2.0.py
