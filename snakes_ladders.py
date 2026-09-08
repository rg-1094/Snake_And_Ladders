"""
Snakes and Ladders - Version 1.2
Power-Ups, Stats, and FX Edition
Requires Python 3.8+ (Zero external dependencies).
"""

import tkinter as tk
from tkinter import messagebox, ttk
import random
import math
import json
import os

# Audio engine (Windows native fallback)
SOUND_ENABLED = True
try:
    import winsound
    def play_sound(fx_type):
        if not SOUND_ENABLED:
            return
        try:
            if fx_type == "roll":
                winsound.Beep(520, 25)
            elif fx_type == "hop":
                winsound.Beep(700, 35)
            elif fx_type == "ladder":
                for f in (440, 554, 659, 880):
                    winsound.Beep(f, 40)
            elif fx_type == "snake":
                for f in (600, 450, 300, 200):
                    winsound.Beep(f, 50)
            elif fx_type == "powerup":
                for f in (587, 880, 1174):
                    winsound.Beep(f, 60)
            elif fx_type == "freeze":
                winsound.Beep(220, 150)
            elif fx_type == "win":
                for f in (523, 659, 784, 1046, 1318):
                    winsound.Beep(f, 90)
        except Exception:
            pass
except Exception:
    def play_sound(fx_type):
        pass

# Board & Game Parameters
CELL_SIZE = 54
GRID_COUNT = 10
BOARD_SIZE = CELL_SIZE * GRID_COUNT

LADDERS = {4: 14, 9: 31, 20: 38, 28: 84, 40: 59, 51: 67, 63: 81, 71: 91}
SNAKES = {17: 7, 54: 34, 62: 18, 64: 60, 87: 24, 93: 73, 95: 75, 99: 78}

# Special tiles: Star (+3), Shield (blocks 1 snake), Freeze (skips 1 turn)
STAR_TILES = {25, 55, 80}
SHIELD_TILES = {12, 45, 70}
FREEZE_TILES = {33, 76}

PLAYER_PRESETS = [
    {"name": "Player 1", "color": "#e63946", "is_cpu": False},
    {"name": "CPU",      "color": "#1d3557", "is_cpu": True},
    {"name": "Player 3", "color": "#2a9d8f", "is_cpu": False},
    {"name": "Player 4", "color": "#e76f51", "is_cpu": False},
]

DICE_PIPS = {
    1: [(0.5, 0.5)],
    2: [(0.25, 0.25), (0.75, 0.75)],
    3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
    4: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)],
    5: [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)],
    6: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.5), (0.75, 0.5), (0.25, 0.75), (0.75, 0.75)]
}

STATS_FILE = "snakes_stats.json"


class SnakesLaddersV12:
    def __init__(self, root):
        self.root = root
        self.root.title("Snakes and Ladders v1.2")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f172a")

        self.num_players = 2
        self.current_turn_idx = 0
        self.positions = [1, 1, 1, 1]
        self.turns_taken = [0, 0, 0, 0]
        self.has_shield = [False, False, False, False]
        self.is_frozen = [False, False, False, False]
        self.powerups_enabled = tk.BooleanVar(value=True)
        self.sound_enabled_var = tk.BooleanVar(value=True)

        self.is_busy = False
        self.confetti_particles = []

        self._load_stats()
        self._setup_layout()
        self._draw_board()
        self._update_all_tokens()

    def _get_cell_coords(self, pos):
        pos = max(1, min(100, pos))
        row = (pos - 1) // 10
        col = (pos - 1) % 10
        if row % 2 == 1:
            col = 9 - col
        x = col * CELL_SIZE + CELL_SIZE // 2
        y = (9 - row) * CELL_SIZE + CELL_SIZE // 2
        return x, y

    def _setup_layout(self):
        container = tk.Frame(self.root, bg="#0f172a", padx=12, pady=12)
        container.pack()

        # Canvas Board
        self.canvas = tk.Canvas(
            container,
            width=BOARD_SIZE,
            height=BOARD_SIZE,
            bg="#f8fafc",
            highlightthickness=2,
            highlightbackground="#334155"
        )
        self.canvas.grid(row=0, column=0, rowspan=9, padx=(0, 16))

        # Header
        header = tk.Frame(container, bg="#0f172a")
        header.grid(row=0, column=1, sticky="w", pady=(0, 4))
        tk.Label(
            header, text="SNAKES & LADDERS", font=("Segoe UI", 15, "bold"),
            fg="#f8fafc", bg="#0f172a"
        ).pack(anchor="w")
        tk.Label(
            header, text="v1.2 Power-Up Edition", font=("Segoe UI", 9, "italic"),
            fg="#38bdf8", bg="#0f172a"
        ).pack(anchor="w")

        # Game Mode Setup
        mode_frame = tk.LabelFrame(
            container, text=" Match Setup ", font=("Segoe UI", 8, "bold"),
            fg="#94a3b8", bg="#1e293b", padx=6, pady=4
        )
        mode_frame.grid(row=1, column=1, sticky="ew", pady=4)

        self.mode_var = tk.StringVar(value="vs_cpu")
        modes = [("1P vs CPU", "vs_cpu"), ("2 Players", "2p"), ("3 Players", "3p"), ("4 Players", "4p")]
        for text, val in modes:
            tk.Radiobutton(
                mode_frame, text=text, value=val, variable=self.mode_var,
                command=self._apply_mode_change, bg="#1e293b", fg="#f1f5f9",
                selectcolor="#0f172a", font=("Segoe UI", 8)
            ).pack(anchor="w")

        # Modifier Toggles
        toggle_frame = tk.Frame(container, bg="#0f172a")
        toggle_frame.grid(row=2, column=1, sticky="ew", pady=2)

        tk.Checkbutton(
            toggle_frame, text="Power-Ups (⭐,🛡️,❄️)", variable=self.powerups_enabled,
            command=self._draw_board, bg="#0f172a", fg="#e2e8f0",
            selectcolor="#1e293b", activebackground="#0f172a", font=("Segoe UI", 8)
        ).pack(anchor="w")

        tk.Checkbutton(
            toggle_frame, text="Audio FX", variable=self.sound_enabled_var,
            command=self._toggle_sound, bg="#0f172a", fg="#e2e8f0",
            selectcolor="#1e293b", activebackground="#0f172a", font=("Segoe UI", 8)
        ).pack(anchor="w")

        # Turn Banner
        self.turn_banner = tk.Label(
            container, text="Turn: Player 1", font=("Segoe UI", 10, "bold"),
            bg="#e63946", fg="white", padx=6, pady=5, width=24
        )
        self.turn_banner.grid(row=3, column=1, sticky="ew", pady=6)

        # Interactive Canvas Dice
        self.dice_canvas = tk.Canvas(container, width=54, height=54, bg="#0f172a", highlightthickness=0)
        self.dice_canvas.grid(row=4, column=1, pady=2)
        self._render_dice_face(1)

        # Roll Action Button
        self.roll_btn = tk.Button(
            container, text="Roll Dice", font=("Segoe UI", 10, "bold"),
            bg="#0284c7", fg="white", activebackground="#0369a1", activeforeground="white",
            relief="flat", cursor="hand2", pady=5, command=self.handle_human_turn
        )
        self.roll_btn.grid(row=5, column=1, sticky="ew", pady=4)

        # Match Action Log
        log_frame = tk.LabelFrame(
            container, text=" Match Ticker ", font=("Segoe UI", 8, "bold"),
            fg="#94a3b8", bg="#1e293b", padx=6, pady=3
        )
        log_frame.grid(row=6, column=1, sticky="nsew", pady=4)

        self.log_list = tk.Listbox(
            log_frame, height=5, width=27, font=("Consolas", 8),
            bg="#0f172a", fg="#e2e8f0", relief="flat", highlightthickness=0
        )
        self.log_list.pack(fill=tk.BOTH, expand=True)

        # Control & Stats Buttons
        btn_box = tk.Frame(container, bg="#0f172a")
        btn_box.grid(row=7, column=1, sticky="ew", pady=(2, 0))

        tk.Button(
            btn_box, text="Leaderboard", font=("Segoe UI", 8),
            bg="#334155", fg="white", relief="flat", cursor="hand2",
            command=self.show_stats_dialog
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))

        tk.Button(
            btn_box, text="Reset", font=("Segoe UI", 8),
            bg="#475569", fg="white", relief="flat", cursor="hand2",
            command=self.reset_game
        ).pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(2, 0))

    def _toggle_sound(self):
        global SOUND_ENABLED
        SOUND_ENABLED = self.sound_enabled_var.get()

    def _apply_mode_change(self):
        selection = self.mode_var.get()
        if selection == "vs_cpu":
            self.num_players = 2
            PLAYER_PRESETS[1]["name"] = "CPU"
            PLAYER_PRESETS[1]["is_cpu"] = True
        else:
            self.num_players = int(selection[0])
            PLAYER_PRESETS[1]["name"] = "Player 2"
            PLAYER_PRESETS[1]["is_cpu"] = False
        self.reset_game()

    def _render_dice_face(self, val):
        self.dice_canvas.delete("all")
        self.dice_canvas.create_rectangle(3, 3, 51, 51, fill="#ffffff", outline="#cbd5e1", width=2)
        for px, py in DICE_PIPS.get(val, []):
            cx = 3 + px * 48
            cy = 3 + py * 48
            self.dice_canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill="#0f172a", outline="")

    def _draw_board(self):
        self.canvas.delete("board_tile", "board_icon")
        tile_colors = ["#f8fafc", "#e2e8f0"]
        pups = self.powerups_enabled.get()

        for pos in range(1, 101):
            row = (pos - 1) // 10
            col = (pos - 1) % 10
            if row % 2 == 1:
                col = 9 - col
            x1 = col * CELL_SIZE
            y1 = (9 - row) * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            bg = tile_colors[(row + col) % 2]
            if pos == 100:
                bg = "#fef08a"
            elif pups and pos in STAR_TILES:
                bg = "#fef9c3"
            elif pups and pos in SHIELD_TILES:
                bg = "#e0f2fe"
            elif pups and pos in FREEZE_TILES:
                bg = "#f1f5f9"

            self.canvas.create_rectangle(x1, y1, x2, y2, fill=bg, outline="#cbd5e1", tags="board_tile")
            self.canvas.create_text(
                x1 + 3, y1 + 2, text=str(pos),
                font=("Segoe UI", 7, "bold"), anchor="nw", fill="#64748b", tags="board_tile"
            )

            # Draw Modifier Icons
            if pups:
                if pos in STAR_TILES:
                    self.canvas.create_text(x2 - 10, y1 + 10, text="⭐", font=("Segoe UI", 9), tags="board_icon")
                elif pos in SHIELD_TILES:
                    self.canvas.create_text(x2 - 10, y1 + 10, text="🛡️", font=("Segoe UI", 9), tags="board_icon")
                elif pos in FREEZE_TILES:
                    self.canvas.create_text(x2 - 10, y1 + 10, text="❄️", font=("Segoe UI", 9), tags="board_icon")

        # Draw Ladders
        for bottom, top in LADDERS.items():
            bx, by = self._get_cell_coords(bottom)
            tx, ty = self._get_cell_coords(top)
            dx, dy = tx - bx, ty - by
            dist = math.hypot(dx, dy)
            if dist == 0:
                continue
            nx, ny = -dy / dist * 6, dx / dist * 6
            self.canvas.create_line(bx + nx, by + ny, tx + nx, ty + ny, fill="#15803d", width=3)
            self.canvas.create_line(bx - nx, by - ny, tx - nx, ty - ny, fill="#15803d", width=3)
            rungs = max(3, int(dist // 14))
            for i in range(1, rungs):
                t = i / rungs
                self.canvas.create_line(bx + t*dx + nx, by + t*dy + ny, bx + t*dx - nx, by + t*dy - ny, fill="#16a34a", width=2)

        # Draw Snakes
        for head, tail in SNAKES.items():
            hx, hy = self._get_cell_coords(head)
            tx, ty = self._get_cell_coords(tail)
            dx, dy = tx - hx, ty - hy
            dist = math.hypot(dx, dy)
            if dist == 0:
                continue
            nx, ny = -dy / dist * 9, dx / dist * 9
            segments = 12
            pts = []
            for i in range(segments + 1):
                t = i / segments
                wave = math.sin(t * math.pi * 3)
                pts.extend([hx + t * dx + wave * nx, hy + t * dy + wave * ny])
            self.canvas.create_line(pts, fill="#dc2626", width=4, smooth=True, capstyle=tk.ROUND)
            self.canvas.create_oval(hx - 7, hy - 7, hx + 7, hy + 7, fill="#b91c1c", outline="#7f1d1d")
            self.canvas.create_oval(hx - 3, hy - 3, hx - 1, hy - 1, fill="white")
            self.canvas.create_oval(hx + 1, hy - 3, hx + 3, hy - 1, fill="white")

    def _update_all_tokens(self):
        self.canvas.delete("token")
        slot_offsets = [(-8, -8), (8, -8), (-8, 8), (8, 8)]

        for i in range(self.num_players):
            pos = self.positions[i]
            cx, cy = self._get_cell_coords(pos)
            ox, oy = slot_offsets[i]
            x, y = cx + ox, cy + oy
            color = PLAYER_PRESETS[i]["color"]

            self.canvas.create_oval(
                x - 7, y - 7, x + 7, y + 7,
                fill=color, outline="#ffffff", width=2, tags="token"
            )
            self.canvas.create_text(
                x, y, text=str(i + 1),
                font=("Segoe UI", 7, "bold"), fill="#ffffff", tags="token"
            )

            # Status ring indicators (Shield / Frozen)
            if self.has_shield[i]:
                self.canvas.create_oval(x - 9, y - 9, x + 9, y + 9, outline="#38bdf8", width=2, tags="token")
            if self.is_frozen[i]:
                self.canvas.create_text(x, y - 11, text="❄️", font=("Segoe UI", 6), tags="token")

    def _log(self, msg):
        self.log_list.insert(tk.END, msg)
        self.log_list.see(tk.END)

    def handle_human_turn(self):
        if self.is_busy:
            return
        if PLAYER_PRESETS[self.current_turn_idx]["is_cpu"]:
            return
        self._execute_turn()

    def _execute_turn(self):
        p_idx = self.current_turn_idx
        p_name = PLAYER_PRESETS[p_idx]["name"]

        # Check Freeze Condition
        if self.is_frozen[p_idx]:
            self._log(f"{p_name} is frozen! Misses turn.")
            play_sound("freeze")
            self.is_frozen[p_idx] = False
            self._update_all_tokens()
            self.root.after(700, self._advance_to_next_turn)
            return

        self.is_busy = True
        self.roll_btn.config(state=tk.DISABLED)
        self.turns_taken[p_idx] += 1

        def anim(frames_left):
            roll_val = random.randint(1, 6)
            self._render_dice_face(roll_val)
            play_sound("roll")
            if frames_left > 0:
                self.root.after(50, anim, frames_left - 1)
            else:
                final_roll = random.randint(1, 6)
                self._render_dice_face(final_roll)
                self._start_token_hop(final_roll)

        anim(5)

    def _start_token_hop(self, roll):
        p_idx = self.current_turn_idx
        p_name = PLAYER_PRESETS[p_idx]["name"]
        curr_pos = self.positions[p_idx]

        if curr_pos + roll > 100:
            self._log(f"{p_name}: rolled {roll} (Need exact {100 - curr_pos})")
            self.root.after(600, self._advance_to_next_turn)
            return

        self._log(f"{p_name}: rolled {roll}")

        def hop(steps_left):
            if steps_left > 0:
                self.positions[p_idx] += 1
                play_sound("hop")
                self._update_all_tokens()
                self.root.after(100, hop, steps_left - 1)
            else:
                self.root.after(150, self._check_tile_effects)

        hop(roll)

    def _check_tile_effects(self):
        p_idx = self.current_turn_idx
        p_name = PLAYER_PRESETS[p_idx]["name"]
        pos = self.positions[p_idx]
        pups = self.powerups_enabled.get()

        # Check Ladders
        if pos in LADDERS:
            dest = LADDERS[pos]
            self._log(f" ├─ Ladder! {pos} -> {dest}")
            play_sound("ladder")
            self.positions[p_idx] = dest
            self._update_all_tokens()
            pos = dest

        # Check Snakes & Shield Protection
        elif pos in SNAKES:
            if pups and self.has_shield[p_idx]:
                self.has_shield[p_idx] = False
                self._log(f" ├─ 🛡️ Shield absorbed snake bite!")
                play_sound("powerup")
                self._update_all_tokens()
            else:
                dest = SNAKES[pos]
                self._log(f" ├─ Snake bite! {pos} -> {dest}")
                play_sound("snake")
                self.positions[p_idx] = dest
                self._update_all_tokens()
                pos = dest

        # Check Power-Up Tiles
        if pups:
            if pos in STAR_TILES:
                boost = min(100, pos + 3)
                self._log(f" ├─ ⭐ Star boost! +3 -> {boost}")
                play_sound("powerup")
                self.positions[p_idx] = boost
                self._update_all_tokens()
            elif pos in SHIELD_TILES and not self.has_shield[p_idx]:
                self.has_shield[p_idx] = True
                self._log(f" ├─ 🛡️ Acquired Snake Shield!")
                play_sound("powerup")
                self._update_all_tokens()
            elif pos in FREEZE_TILES:
                self.is_frozen[p_idx] = True
                self._log(f" ├─ ❄️ Trap! Frozen next turn.")
                play_sound("freeze")
                self._update_all_tokens()

        # Check Win Condition
        if self.positions[p_idx] == 100:
            play_sound("win")
            self._record_win(p_name, self.turns_taken[p_idx])
            self._trigger_confetti()
            messagebox.showinfo("Champion!", f"{p_name} won the match in {self.turns_taken[p_idx]} turns!")
            self.reset_game()
            return

        self.root.after(350, self._advance_to_next_turn)

    def _advance_to_next_turn(self):
        self.current_turn_idx = (self.current_turn_idx + 1) % self.num_players
        nxt = PLAYER_PRESETS[self.current_turn_idx]
        self.turn_banner.config(text=f"Turn: {nxt['name']}", bg=nxt["color"])

        if nxt["is_cpu"]:
            self.is_busy = True
            self.roll_btn.config(state=tk.DISABLED)
            self.root.after(650, self._execute_turn)
        else:
            self.is_busy = False
            self.roll_btn.config(state=tk.NORMAL)

    def _trigger_confetti(self):
        colors = ["#f43f5e", "#38bdf8", "#fbbf24", "#34d399", "#a855f7"]
        self.confetti_particles = []
        for _ in range(45):
            x = random.randint(20, BOARD_SIZE - 20)
            y = random.randint(10, 150)
            vx = random.uniform(-2, 2)
            vy = random.uniform(2, 6)
            col = random.choice(colors)
            size = random.randint(4, 7)
            pid = self.canvas.create_rectangle(x, y, x + size, y + size, fill=col, outline="")
            self.confetti_particles.append({"id": pid, "vx": vx, "vy": vy, "life": 25})

        def drop_step():
            alive = False
            for p in self.confetti_particles:
                if p["life"] > 0:
                    self.canvas.move(p["id"], p["vx"], p["vy"])
                    p["life"] -= 1
                    alive = True
                else:
                    self.canvas.delete(p["id"])
            if alive:
                self.root.after(40, drop_step)

        drop_step()

    def _load_stats(self):
        self.stats = {"matches_played": 0, "wins": {}, "record_turns": None}
        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, "r") as f:
                    self.stats = json.load(f)
            except Exception:
                pass

    def _save_stats(self):
        try:
            with open(STATS_FILE, "w") as f:
                json.dump(self.stats, f, indent=2)
        except Exception:
            pass

    def _record_win(self, winner_name, turns):
        self.stats["matches_played"] += 1
        self.stats["wins"][winner_name] = self.stats["wins"].get(winner_name, 0) + 1
        if self.stats["record_turns"] is None or turns < self.stats["record_turns"]:
            self.stats["record_turns"] = turns
        self._save_stats()

    def show_stats_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Match History & Leaderboard")
        dlg.geometry("280x240")
        dlg.resizable(False, False)
        dlg.configure(bg="#1e293b", padx=12, pady=12)

        tk.Label(
            dlg, text="Hall of Fame", font=("Segoe UI", 12, "bold"),
            fg="#38bdf8", bg="#1e293b"
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            dlg, text=f"Total Matches Played: {self.stats['matches_played']}",
            font=("Segoe UI", 9), fg="#f8fafc", bg="#1e293b"
        ).pack(anchor="w")

        rec = self.stats['record_turns'] if self.stats['record_turns'] else "N/A"
        tk.Label(
            dlg, text=f"Fastest Win: {rec} turns",
            font=("Segoe UI", 9, "bold"), fg="#fbbf24", bg="#1e293b"
        ).pack(anchor="w", pady=(0, 8))

        tk.Label(dlg, text="Player Win Counts:", font=("Segoe UI", 9, "underline"), fg="#cbd5e1", bg="#1e293b").pack(anchor="w")
        for player, wins in self.stats["wins"].items():
            tk.Label(dlg, text=f"• {player}: {wins} wins", font=("Segoe UI", 9), fg="#f1f5f9", bg="#1e293b").pack(anchor="w")

        tk.Button(dlg, text="Close", command=dlg.destroy, bg="#475569", fg="white", relief="flat", pady=3).pack(fill=tk.X, pady=(12, 0))

    def reset_game(self):
        self.positions = [1, 1, 1, 1]
        self.turns_taken = [0, 0, 0, 0]
        self.has_shield = [False, False, False, False]
        self.is_frozen = [False, False, False, False]
        self.current_turn_idx = 0
        self.is_busy = False
        self.log_list.delete(0, tk.END)
        self._log("Game initialized. Roll to start!")
        p1 = PLAYER_PRESETS[0]
        self.turn_banner.config(text=f"Turn: {p1['name']}", bg=p1["color"])
        self.roll_btn.config(state=tk.NORMAL)
        self._render_dice_face(1)
        self._update_all_tokens()


if __name__ == "__main__":
    app_root = tk.Tk()
    game = SnakesLaddersV12(app_root)
    app_root.mainloop()
