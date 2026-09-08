"""
Snakes and Ladders - Version 2.0 (Infinite Edition)
Major Release: Multi-board scaling, procedural maps, custom avatars,
expanded power-ups, save/resume, and speed controls.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import random
import math
import json
import os

# Platform Sound Engine
SOUND_ON = True
try:
    import winsound
    def play_fx(sound_name):
        if not SOUND_ON:
            return
        try:
            if sound_name == "roll":
                winsound.Beep(520, 20)
            elif sound_name == "hop":
                winsound.Beep(740, 25)
            elif sound_name == "ladder":
                for f in (440, 554, 659, 880):
                    winsound.Beep(f, 35)
            elif sound_name == "snake":
                for f in (620, 480, 340, 220):
                    winsound.Beep(f, 40)
            elif sound_name == "powerup":
                for f in (523, 659, 784, 1046):
                    winsound.Beep(f, 45)
            elif sound_name == "freeze":
                winsound.Beep(200, 120)
            elif sound_name == "win":
                for f in (440, 554, 659, 880, 1108, 1318):
                    winsound.Beep(f, 80)
        except Exception:
            pass
except Exception:
    def play_fx(sound_name):
        pass

CANVAS_PX = 560
SAVE_FILE = "snakes_save.json"
STATS_FILE = "snakes_stats.json"

AVATARS = [
    {"symbol": "🚀", "name": "Rocket", "color": "#ef4444"},
    {"symbol": "🤖", "name": "Bot",    "color": "#3b82f6"},
    {"symbol": "⚡", "name": "Volt",   "color": "#eab308"},
    {"symbol": "💎", "name": "Gem",    "color": "#06b6d4"},
    {"symbol": "👑", "name": "Crown",  "color": "#a855f7"},
    {"symbol": "🦁", "name": "Lion",   "color": "#f97316"}
]

DICE_PIPS = {
    1: [(0.5, 0.5)],
    2: [(0.25, 0.25), (0.75, 0.75)],
    3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
    4: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)],
    5: [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)],
    6: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.5), (0.75, 0.5), (0.25, 0.75), (0.75, 0.75)]
}


class SnakesLaddersV2:
    def __init__(self, root):
        self.root = root
        self.root.title("Snakes & Ladders v2.0 - Infinite Edition")
        self.root.resizable(False, False)
        self.root.configure(bg="#0b0f19")

        # Config variables
        self.grid_size = 10
        self.total_tiles = 100
        self.cell_size = CANVAS_PX // self.grid_size

        self.num_players = 2
        self.is_procedural = tk.BooleanVar(value=False)
        self.powerups_enabled = tk.BooleanVar(value=True)
        self.anim_speed_var = tk.StringVar(value="Normal")  # Normal, Fast, Instant
        self.sound_enabled_var = tk.BooleanVar(value=True)

        # Player states
        self.players = []
        self.current_idx = 0
        self.is_busy = False
        self.fireworks = []

        # Maps
        self.ladders = {}
        self.snakes = {}
        self.stars = set()
        self.shields = set()
        self.freezes = set()
        self.rerolls = set()

        self._load_stats()
        self._init_player_profiles()
        self._setup_ui()
        self._build_board_layout()
        self._check_resume_option()

        # Keyboard shortcuts
        self.root.bind("<space>", lambda e: self.trigger_roll_from_key())
        self.root.bind("<Return>", lambda e: self.trigger_roll_from_key())

    def _init_player_profiles(self):
        self.players = [
            {"id": 0, "name": "Player 1", "avatar": AVATARS[0], "pos": 1, "is_cpu": False, "shield": False, "frozen": False, "turns": 0},
            {"id": 1, "name": "CPU",      "avatar": AVATARS[1], "pos": 1, "is_cpu": True,  "shield": False, "frozen": False, "turns": 0},
            {"id": 2, "name": "Player 3", "avatar": AVATARS[2], "pos": 1, "is_cpu": False, "shield": False, "frozen": False, "turns": 0},
            {"id": 3, "name": "Player 4", "avatar": AVATARS[3], "pos": 1, "is_cpu": False, "shield": False, "frozen": False, "turns": 0},
        ]

    def _get_delays(self):
        mode = self.anim_speed_var.get()
        if mode == "Instant":
            return {"dice_frames": 1, "frame_ms": 10, "hop_ms": 10, "step_pause": 20}
        elif mode == "Fast":
            return {"dice_frames": 3, "frame_ms": 30, "hop_ms": 50, "step_pause": 150}
        else:
            return {"dice_frames": 5, "frame_ms": 50, "hop_ms": 90, "step_pause": 300}

    def _get_cell_center(self, pos):
        pos = max(1, min(self.total_tiles, pos))
        row = (pos - 1) // self.grid_size
        col = (pos - 1) % self.grid_size
        if row % 2 == 1:
            col = (self.grid_size - 1) - col
        x = col * self.cell_size + self.cell_size // 2
        y = (self.grid_size - 1 - row) * self.cell_size + self.cell_size // 2
        return x, y

    def _setup_ui(self):
        container = tk.Frame(self.root, bg="#0b0f19", padx=14, pady=14)
        container.pack()

        # Canvas Board
        self.canvas = tk.Canvas(
            container, width=CANVAS_PX, height=CANVAS_PX,
            bg="#111827", highlightthickness=2, highlightbackground="#1f2937"
        )
        self.canvas.grid(row=0, column=0, rowspan=10, padx=(0, 16))

        # Dashboard sidebar
        header = tk.Frame(container, bg="#0b0f19")
        header.grid(row=0, column=1, sticky="w", pady=(0, 4))
        tk.Label(
            header, text="SNAKES & LADDERS", font=("Segoe UI", 16, "bold"),
            fg="#f9fafb", bg="#0b0f19"
        ).pack(anchor="w")
        tk.Label(
            header, text="v2.0 Infinite Edition", font=("Segoe UI", 9, "italic"),
            fg="#38bdf8", bg="#0b0f19"
        ).pack(anchor="w")

        # Board Setup Box
        cfg_box = tk.LabelFrame(
            container, text=" Match Customization ", font=("Segoe UI", 8, "bold"),
            fg="#9ca3af", bg="#182234", padx=8, pady=4
        )
        cfg_box.grid(row=1, column=1, sticky="ew", pady=4)

        # Mode
        self.mode_var = tk.StringVar(value="vs_cpu")
        modes = [("1P vs CPU", "vs_cpu"), ("2 Players", "2p"), ("3 Players", "3p"), ("4 Players", "4p")]
        m_row = tk.Frame(cfg_box, bg="#182234")
        m_row.pack(anchor="w", fill=tk.X)
        for t, v in modes:
            tk.Radiobutton(
                m_row, text=t, value=v, variable=self.mode_var,
                command=self._apply_mode_change, bg="#182234", fg="#f3f4f6",
                selectcolor="#0b0f19", font=("Segoe UI", 8)
            ).pack(side=tk.LEFT, padx=3)

        # Board Size & Procedural Options
        opts_row = tk.Frame(cfg_box, bg="#182234")
        opts_row.pack(anchor="w", fill=tk.X, pady=(4, 0))

        self.size_var = tk.StringVar(value="10x10")
        for size_lbl in ["10x10", "8x8"]:
            tk.Radiobutton(
                opts_row, text=size_lbl, value=size_lbl, variable=self.size_var,
                command=self._change_board_size, bg="#182234", fg="#93c5fd",
                selectcolor="#0b0f19", font=("Segoe UI", 8, "bold")
            ).pack(side=tk.LEFT, padx=3)

        tk.Checkbutton(
            opts_row, text="Procedural Map", variable=self.is_procedural,
            command=self._build_board_layout, bg="#182234", fg="#f3f4f6",
            selectcolor="#0b0f19", font=("Segoe UI", 8)
        ).pack(side=tk.RIGHT)

        # Mechanics Toggles
        toggles = tk.Frame(container, bg="#0b0f19")
        toggles.grid(row=2, column=1, sticky="ew", pady=2)
        tk.Checkbutton(
            toggles, text="Power-Ups (⭐,🛡️,❄️,🎲)", variable=self.powerups_enabled,
            command=self._draw_board, bg="#0b0f19", fg="#d1d5db",
            selectcolor="#1f2937", activebackground="#0b0f19", font=("Segoe UI", 8)
        ).pack(side=tk.LEFT)

        tk.Checkbutton(
            toggles, text="Audio", variable=self.sound_enabled_var,
            command=self._toggle_sound, bg="#0b0f19", fg="#d1d5db",
            selectcolor="#1f2937", activebackground="#0b0f19", font=("Segoe UI", 8)
        ).pack(side=tk.RIGHT)

        # Speed Control
        spd_frame = tk.Frame(container, bg="#0b0f19")
        spd_frame.grid(row=3, column=1, sticky="w", pady=2)
        tk.Label(spd_frame, text="Speed:", font=("Segoe UI", 8), fg="#9ca3af", bg="#0b0f19").pack(side=tk.LEFT, padx=(0, 4))
        for spd in ["Normal", "Fast", "Instant"]:
            tk.Radiobutton(
                spd_frame, text=spd, value=spd, variable=self.anim_speed_var,
                bg="#0b0f19", fg="#cbd5e1", selectcolor="#1e293b", font=("Segoe UI", 8)
            ).pack(side=tk.LEFT, padx=2)

        # Turn Banner
        self.turn_banner = tk.Label(
            container, text="Turn: Player 1", font=("Segoe UI", 11, "bold"),
            bg="#ef4444", fg="white", padx=6, pady=5, width=24
        )
        self.turn_banner.grid(row=4, column=1, sticky="ew", pady=6)

        # Interactive Canvas Dice
        self.dice_canvas = tk.Canvas(container, width=54, height=54, bg="#0b0f19", highlightthickness=0)
        self.dice_canvas.grid(row=5, column=1, pady=2)
        self._render_dice(1)

        # Roll Action Button
        self.roll_btn = tk.Button(
            container, text="Roll Dice [Space]", font=("Segoe UI", 10, "bold"),
            bg="#2563eb", fg="white", activebackground="#1d4ed8", activeforeground="white",
            relief="flat", cursor="hand2", pady=5, command=self.handle_human_turn
        )
        self.roll_btn.grid(row=6, column=1, sticky="ew", pady=3)

        # Match Ticker
        ticker_box = tk.LabelFrame(
            container, text=" Event Ticker ", font=("Segoe UI", 8, "bold"),
            fg="#9ca3af", bg="#182234", padx=6, pady=3
        )
        ticker_box.grid(row=7, column=1, sticky="nsew", pady=3)
        self.log_list = tk.Listbox(
            ticker_box, height=5, width=28, font=("Consolas", 8),
            bg="#0f172a", fg="#e2e8f0", relief="flat", highlightthickness=0
        )
        self.log_list.pack(fill=tk.BOTH, expand=True)

        # Bottom Bar: Stats, Avatars, Save & Reset
        bar = tk.Frame(container, bg="#0b0f19")
        bar.grid(row=8, column=1, sticky="ew", pady=(4, 0))

        tk.Button(
            bar, text="Avatars", font=("Segoe UI", 8), bg="#334155", fg="white",
            relief="flat", cursor="hand2", command=self.open_avatar_picker
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

        tk.Button(
            bar, text="Records", font=("Segoe UI", 8), bg="#334155", fg="white",
            relief="flat", cursor="hand2", command=self.show_records_dialog
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

        tk.Button(
            bar, text="Save", font=("Segoe UI", 8), bg="#1e293b", fg="#38bdf8",
            relief="flat", cursor="hand2", command=self.save_match_state
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

        tk.Button(
            bar, text="New Game", font=("Segoe UI", 8), bg="#475569", fg="white",
            relief="flat", cursor="hand2", command=self.reset_match
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)

    def _toggle_sound(self):
        global SOUND_ON
        SOUND_ON = self.sound_enabled_var.get()

    def _change_board_size(self):
        val = self.size_var.get()
        if val == "8x8":
            self.grid_size = 8
            self.total_tiles = 64
        else:
            self.grid_size = 10
            self.total_tiles = 100
        self.cell_size = CANVAS_PX // self.grid_size
        self._build_board_layout()
        self.reset_match()

    def _apply_mode_change(self):
        selection = self.mode_var.get()
        if selection == "vs_cpu":
            self.num_players = 2
            self.players[1]["name"] = "CPU"
            self.players[1]["is_cpu"] = True
        else:
            self.num_players = int(selection[0])
            self.players[1]["name"] = "Player 2"
            self.players[1]["is_cpu"] = False
        self.reset_match()

    def _build_board_layout(self):
        self.ladders.clear()
        self.snakes.clear()
        self.stars.clear()
        self.shields.clear()
        self.freezes.clear()
        self.rerolls.clear()

        if not self.is_procedural.get():
            # Standard layouts
            if self.total_tiles == 100:
                self.ladders = {4: 14, 9: 31, 20: 38, 28: 84, 40: 59, 51: 67, 63: 81, 71: 91}
                self.snakes = {17: 7, 54: 34, 62: 18, 64: 60, 87: 24, 93: 73, 95: 75, 99: 78}
                self.stars = {25, 55, 80}
                self.shields = {12, 45, 70}
                self.freezes = {33, 76}
                self.rerolls = {15, 66}
            else:
                self.ladders = {3: 16, 10: 25, 21: 42, 34: 52}
                self.snakes = {19: 5, 31: 14, 47: 23, 61: 37}
                self.stars = {12, 40}
                self.shields = {8, 35}
                self.freezes = {28, 50}
                self.rerolls = {18, 44}
        else:
            # Procedural Generation with safety validation
            occupied = {1, self.total_tiles}
            count = 6 if self.total_tiles == 64 else 8

            # Build Ladders
            attempts = 0
            while len(self.ladders) < count and attempts < 300:
                attempts += 1
                b = random.randint(2, self.total_tiles - 15)
                t = random.randint(b + 8, self.total_tiles - 1)
                if b not in occupied and t not in occupied:
                    self.ladders[b] = t
                    occupied.update([b, t])

            # Build Snakes
            attempts = 0
            while len(self.snakes) < count and attempts < 300:
                attempts += 1
                h = random.randint(15, self.total_tiles - 1)
                t = random.randint(2, h - 8)
                if h not in occupied and t not in occupied:
                    self.snakes[h] = t
                    occupied.update([h, t])

            # Randomize Power-Ups on remaining cells
            free_cells = [p for p in range(5, self.total_tiles - 2) if p not in occupied]
            random.shuffle(free_cells)
            self.stars = set(free_cells[0:2])
            self.shields = set(free_cells[2:4])
            self.freezes = set(free_cells[4:6])
            self.rerolls = set(free_cells[6:8])

        self._draw_board()
        self._update_tokens()

    def _draw_board(self):
        self.canvas.delete("all")
        pups = self.powerups_enabled.get()

        for pos in range(1, self.total_tiles + 1):
            row = (pos - 1) // self.grid_size
            col = (pos - 1) % self.grid_size
            if row % 2 == 1:
                col = (self.grid_size - 1) - col

            x1 = col * self.cell_size
            y1 = (self.grid_size - 1 - row) * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size

            # Dark theme tile shades
            base_color = "#1e293b" if (row + col) % 2 == 0 else "#0f172a"
            if pos == self.total_tiles:
                base_color = "#713f12"
            elif pups:
                if pos in self.stars:
                    base_color = "#3730a3"
                elif pos in self.shields:
                    base_color = "#075985"
                elif pos in self.freezes:
                    base_color = "#1e3a5f"
                elif pos in self.rerolls:
                    base_color = "#14532d"

            self.canvas.create_rectangle(x1, y1, x2, y2, fill=base_color, outline="#334155")
            self.canvas.create_text(
                x1 + 3, y1 + 3, text=str(pos),
                font=("Segoe UI", 7, "bold"), anchor="nw", fill="#64748b"
            )

            # Draw Icons
            if pups:
                if pos in self.stars:
                    self.canvas.create_text(x2 - 10, y1 + 10, text="⭐", font=("Segoe UI", 8))
                elif pos in self.shields:
                    self.canvas.create_text(x2 - 10, y1 + 10, text="🛡️", font=("Segoe UI", 8))
                elif pos in self.freezes:
                    self.canvas.create_text(x2 - 10, y1 + 10, text="❄️", font=("Segoe UI", 8))
                elif pos in self.rerolls:
                    self.canvas.create_text(x2 - 10, y1 + 10, text="🎲", font=("Segoe UI", 8))

        # Render Ladders
        for b, t in self.ladders.items():
            bx, by = self._get_cell_center(b)
            tx, ty = self._get_cell_center(t)
            dx, dy = tx - bx, ty - by
            dist = math.hypot(dx, dy)
            if dist == 0:
                continue
            nx, ny = -dy / dist * 6, dx / dist * 6

            self.canvas.create_line(bx + nx, by + ny, tx + nx, ty + ny, fill="#22c55e", width=3)
            self.canvas.create_line(bx - nx, by - ny, tx - nx, ty - ny, fill="#22c55e", width=3)
            rungs = max(3, int(dist // 14))
            for i in range(1, rungs):
                frac = i / rungs
                self.canvas.create_line(
                    bx + frac*dx + nx, by + frac*dy + ny,
                    bx + frac*dx - nx, by + frac*dy - ny,
                    fill="#4ade80", width=2
                )

        # Render Snakes
        for h, t in self.snakes.items():
            hx, hy = self._get_cell_center(h)
            tx, ty = self._get_cell_center(t)
            dx, dy = tx - hx, ty - hy
            dist = math.hypot(dx, dy)
            if dist == 0:
                continue
            nx, ny = -dy / dist * 9, dx / dist * 9
            pts = []
            for i in range(13):
                frac = i / 12
                wave = math.sin(frac * math.pi * 3)
                pts.extend([hx + frac*dx + wave*nx, hy + frac*dy + wave*ny])

            self.canvas.create_line(pts, fill="#ef4444", width=4, smooth=True, capstyle=tk.ROUND)
            self.canvas.create_oval(hx - 7, hy - 7, hx + 7, hy + 7, fill="#b91c1c", outline="#7f1d1d")
            self.canvas.create_oval(hx - 3, hy - 3, hx - 1, hy - 1, fill="white")
            self.canvas.create_oval(hx + 1, hy - 3, hx + 3, hy - 1, fill="white")

    def _update_tokens(self):
        self.canvas.delete("token")
        offsets = [(-8, -8), (8, -8), (-8, 8), (8, 8)]

        for i in range(self.num_players):
            p = self.players[i]
            cx, cy = self._get_cell_center(p["pos"])
            ox, oy = offsets[i]
            x, y = cx + ox, cy + oy

            # Token body
            self.canvas.create_oval(
                x - 8, y - 8, x + 8, y + 8,
                fill=p["avatar"]["color"], outline="#ffffff", width=2, tags="token"
            )
            # Token Avatar
            self.canvas.create_text(
                x, y, text=p["avatar"]["symbol"],
                font=("Segoe UI", 7), fill="white", tags="token"
            )

            # Status rings
            if p["shield"]:
                self.canvas.create_oval(x - 11, y - 11, x + 11, y + 11, outline="#38bdf8", width=2, tags="token")
            if p["frozen"]:
                self.canvas.create_text(x, y - 12, text="❄️", font=("Segoe UI", 6), tags="token")

    def _render_dice(self, val):
        self.dice_canvas.delete("all")
        self.dice_canvas.create_rectangle(3, 3, 51, 51, fill="#ffffff", outline="#e2e8f0", width=2)
        for px, py in DICE_PIPS.get(val, []):
            cx = 3 + px * 48
            cy = 3 + py * 48
            self.dice_canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill="#0f172a", outline="")

    def _log(self, txt):
        self.log_list.insert(tk.END, txt)
        self.log_list.see(tk.END)

    def trigger_roll_from_key(self):
        if not self.is_busy and not self.players[self.current_idx]["is_cpu"]:
            self.handle_human_turn()

    def handle_human_turn(self):
        if self.is_busy or self.players[self.current_idx]["is_cpu"]:
            return
        self._execute_turn()

    def _execute_turn(self):
        p = self.players[self.current_idx]
        delays = self._get_delays()

        # Handle freeze state
        if p["frozen"]:
            self._log(f"{p['name']} is frozen! Skipped turn.")
            play_fx("freeze")
            p["frozen"] = False
            self._update_tokens()
            self.root.after(delays["step_pause"], self._advance_turn)
            return

        self.is_busy = True
        self.roll_btn.config(state=tk.DISABLED)
        p["turns"] += 1

        def anim(step):
            val = random.randint(1, 6)
            self._render_dice(val)
            play_fx("roll")
            if step > 0:
                self.root.after(delays["frame_ms"], anim, step - 1)
            else:
                final_val = random.randint(1, 6)
                self._render_dice(final_val)
                self._start_hopping(final_val)

        anim(delays["dice_frames"])

    def _start_hopping(self, roll):
        p = self.players[self.current_idx]
        delays = self._get_delays()

        if p["pos"] + roll > self.total_tiles:
            self._log(f"{p['name']}: rolled {roll} (Needs exact {self.total_tiles - p['pos']})")
            self.root.after(delays["step_pause"], self._advance_turn)
            return

        self._log(f"{p['name']}: rolled {roll}")

        def hop(rem):
            if rem > 0:
                p["pos"] += 1
                play_fx("hop")
                self._update_tokens()
                self.root.after(delays["hop_ms"], hop, rem - 1)
            else:
                self.root.after(delays["step_pause"] // 2, self._evaluate_destination)

        hop(roll)

    def _evaluate_destination(self):
        p = self.players[self.current_idx]
        pos = p["pos"]
        pups = self.powerups_enabled.get()
        extra_turn = False
        delays = self._get_delays()

        # Ladders
        if pos in self.ladders:
            dest = self.ladders[pos]
            self._log(f" ├─ Ladder! {pos} ➔ {dest}")
            play_fx("ladder")
            p["pos"] = dest
            self._update_tokens()
            pos = dest

        # Snakes & Shield Defense
        elif pos in self.snakes:
            if pups and p["shield"]:
                p["shield"] = False
                self._log(" ├─ 🛡️ Shield shattered snake attack!")
                play_fx("powerup")
                self._update_tokens()
            else:
                dest = self.snakes[pos]
                self._log(f" ├─ Snake drop! {pos} ➔ {dest}")
                play_fx("snake")
                p["pos"] = dest
                self._update_tokens()
                pos = dest

        # Power-ups
        if pups:
            if pos in self.stars:
                boost = min(self.total_tiles, pos + 3)
                self._log(f" ├─ ⭐ Star Surge! +3 ➔ {boost}")
                play_fx("powerup")
                p["pos"] = boost
                self._update_tokens()
            elif pos in self.shields and not p["shield"]:
                p["shield"] = True
                self._log(" ├─ 🛡️ Aegis Shield acquired!")
                play_fx("powerup")
                self._update_tokens()
            elif pos in self.freezes:
                p["frozen"] = True
                self._log(" ├─ ❄️ Cryo Trap! Frozen next turn.")
                play_fx("freeze")
                self._update_tokens()
            elif pos in self.rerolls:
                extra_turn = True
                self._log(" ├─ 🎲 Lucky Tile! Free extra turn!")
                play_fx("powerup")

        # Win check
        if p["pos"] == self.total_tiles:
            play_fx("win")
            self._record_win(p["name"], p["turns"])
            self._launch_fireworks()
            messagebox.showinfo("VICTORY!", f"{p['name']} won the match in {p['turns']} turns!")
            self._clear_save()
            self.reset_match()
            return

        if extra_turn:
            self.root.after(delays["step_pause"], self._prompt_active_player)
        else:
            self.root.after(delays["step_pause"], self._advance_turn)

    def _advance_turn(self):
        self.current_idx = (self.current_idx + 1) % self.num_players
        self._prompt_active_player()

    def _prompt_active_player(self):
        nxt = self.players[self.current_idx]
        self.turn_banner.config(text=f"Turn: {nxt['name']}", bg=nxt["avatar"]["color"])
        delays = self._get_delays()

        if nxt["is_cpu"]:
            self.is_busy = True
            self.roll_btn.config(state=tk.DISABLED)
            self.root.after(delays["step_pause"] + 200, self._execute_turn)
        else:
            self.is_busy = False
            self.roll_btn.config(state=tk.NORMAL)

    def _launch_fireworks(self):
        palette = ["#f43f5e", "#38bdf8", "#eab308", "#10b981", "#a855f7", "#fb923c"]
        self.fireworks = []
        for _ in range(60):
            x = random.randint(30, CANVAS_PX - 30)
            y = random.randint(30, CANVAS_PX // 2)
            vx = random.uniform(-3, 3)
            vy = random.uniform(-4, 4)
            col = random.choice(palette)
            pid = self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=col, outline="")
            self.fireworks.append({"id": pid, "vx": vx, "vy": vy, "life": 30})

        def step():
            alive = False
            for fw in self.fireworks:
                if fw["life"] > 0:
                    self.canvas.move(fw["id"], fw["vx"], fw["vy"])
                    fw["life"] -= 1
                    alive = True
                else:
                    self.canvas.delete(fw["id"])
            if alive:
                self.root.after(30, step)

        step()

    def open_avatar_picker(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Choose Player Avatars")
        dlg.geometry("300x260")
        dlg.resizable(False, False)
        dlg.configure(bg="#182234", padx=12, pady=10)

        tk.Label(dlg, text="Select Avatar & Color", font=("Segoe UI", 10, "bold"), fg="#f3f4f6", bg="#182234").pack(anchor="w", pady=(0, 6))

        for i in range(self.num_players):
            row = tk.Frame(dlg, bg="#182234")
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=self.players[i]["name"], font=("Segoe UI", 8), fg="#cbd5e1", bg="#182234", width=10, anchor="w").pack(side=tk.LEFT)

            av_var = tk.StringVar(value=self.players[i]["avatar"]["name"])
            combo = ttk.Combobox(row, textvariable=av_var, values=[a["name"] for a in AVATARS], state="readonly", width=12)
            combo.pack(side=tk.RIGHT)

            def make_setter(idx, var):
                def set_avatar(event):
                    chosen = next(a for a in AVATARS if a["name"] == var.get())
                    self.players[idx]["avatar"] = chosen
                    self._update_tokens()
                    self.turn_banner.config(bg=self.players[self.current_idx]["avatar"]["color"])
                return set_avatar

            combo.bind("<<ComboboxSelected>>", make_setter(i, av_var))

        tk.Button(dlg, text="Done", command=dlg.destroy, bg="#334155", fg="white", relief="flat", pady=3).pack(fill=tk.X, pady=(12, 0))

    def save_match_state(self):
        state = {
            "grid_size": self.grid_size,
            "total_tiles": self.total_tiles,
            "num_players": self.num_players,
            "current_idx": self.current_idx,
            "players": self.players,
            "ladders": self.ladders,
            "snakes": self.snakes,
            "stars": list(self.stars),
            "shields": list(self.shields),
            "freezes": list(self.freezes),
            "rerolls": list(self.rerolls)
        }
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(state, f, indent=2)
            self._log("Match successfully saved.")
            messagebox.showinfo("Saved", "Match state saved. You can resume next time you launch!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save state: {e}")

    def _check_resume_option(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    data = json.load(f)
                if messagebox.askyesno("Resume Game", "Saved match found. Do you want to resume?"):
                    self.grid_size = data["grid_size"]
                    self.total_tiles = data["total_tiles"]
                    self.cell_size = CANVAS_PX // self.grid_size
                    self.num_players = data["num_players"]
                    self.current_idx = data["current_idx"]
                    self.players = data["players"]
                    self.ladders = {int(k): v for k, v in data["ladders"].items()}
                    self.snakes = {int(k): v for k, v in data["snakes"].items()}
                    self.stars = set(data["stars"])
                    self.shields = set(data["shields"])
                    self.freezes = set(data["freezes"])
                    self.rerolls = set(data["rerolls"])
                    self.size_var.set(f"{self.grid_size}x{self.grid_size}")
                    self._draw_board()
                    self._update_tokens()
                    self._prompt_active_player()
                    self._log("Resumed saved match.")
            except Exception:
                pass

    def _clear_save(self):
        if os.path.exists(SAVE_FILE):
            try:
                os.remove(SAVE_FILE)
            except Exception:
                pass

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

    def _record_win(self, winner, turns):
        self.stats["matches_played"] += 1
        self.stats["wins"][winner] = self.stats["wins"].get(winner, 0) + 1
        if self.stats["record_turns"] is None or turns < self.stats["record_turns"]:
            self.stats["record_turns"] = turns
        self._save_stats()

    def show_records_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Records & Hall of Fame")
        dlg.geometry("260x220")
        dlg.resizable(False, False)
        dlg.configure(bg="#182234", padx=12, pady=10)

        tk.Label(dlg, text="Hall of Fame", font=("Segoe UI", 11, "bold"), fg="#38bdf8", bg="#182234").pack(anchor="w", pady=(0, 4))
        tk.Label(dlg, text=f"Total Matches: {self.stats['matches_played']}", font=("Segoe UI", 8), fg="#f3f4f6", bg="#182234").pack(anchor="w")

        rec = self.stats['record_turns'] or "N/A"
        tk.Label(dlg, text=f"Fastest Win: {rec} turns", font=("Segoe UI", 8, "bold"), fg="#eab308", bg="#182234").pack(anchor="w", pady=(0, 6))

        tk.Label(dlg, text="Win Counter:", font=("Segoe UI", 8, "underline"), fg="#cbd5e1", bg="#182234").pack(anchor="w")
        for p_name, wins in self.stats["wins"].items():
            tk.Label(dlg, text=f"• {p_name}: {wins} wins", font=("Segoe UI", 8), fg="#e2e8f0", bg="#182234").pack(anchor="w")

        tk.Button(dlg, text="Close", command=dlg.destroy, bg="#334155", fg="white", relief="flat", pady=2).pack(fill=tk.X, pady=(10, 0))

    def reset_match(self):
        self._init_player_profiles()
        self.current_idx = 0
        self.is_busy = False
        self.log_list.delete(0, tk.END)
        self._log(f"Match initialized ({self.grid_size}x{self.grid_size}). Roll to start!")
        p1 = self.players[0]
        self.turn_banner.config(text=f"Turn: {p1['name']}", bg=p1["avatar"]["color"])
        self.roll_btn.config(state=tk.NORMAL)
        self._render_dice(1)
        self._update_tokens()


if __name__ == "__main__":
    app_root = tk.Tk()
    game = SnakesLaddersV2(app_root)
    app_root.mainloop()
