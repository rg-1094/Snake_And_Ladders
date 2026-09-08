"""
Snakes and Ladders - Version 1.1
Enhanced Desktop Edition
Features: Step-by-step movement, animated dice, visual snakes & ladders,
multiplayer/CPU modes, event log, and native audio.
"""

import tkinter as tk
from tkinter import messagebox, ttk
import random
import math

# Windows-native audio fallback
try:
    import winsound
    def play_fx(fx_type):
        if fx_type == "roll":
            winsound.Beep(520, 30)
        elif fx_type == "hop":
            winsound.Beep(750, 40)
        elif fx_type == "ladder":
            for freq in (440, 554, 659, 880):
                winsound.Beep(freq, 50)
        elif fx_type == "snake":
            for freq in (600, 480, 360, 240):
                winsound.Beep(freq, 60)
        elif fx_type == "win":
            for freq in (523, 659, 784, 1046, 1318):
                winsound.Beep(freq, 100)
except Exception:
    def play_fx(fx_type):
        pass

# Board Configuration
CELL_SIZE = 54
GRID_COUNT = 10
BOARD_SIZE = CELL_SIZE * GRID_COUNT

LADDERS = {4: 14, 9: 31, 20: 38, 28: 84, 40: 59, 51: 67, 63: 81, 71: 91}
SNAKES = {17: 7, 54: 34, 62: 18, 64: 60, 87: 24, 93: 73, 95: 75, 99: 78}

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


class SnakesLaddersV11:
    def __init__(self, root):
        self.root = root
        self.root.title("Snakes and Ladders v1.1")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f172a")

        self.num_players = 2
        self.is_vs_cpu = True
        self.current_turn_idx = 0
        self.positions = [1, 1, 1, 1]
        self.is_busy = False

        self._setup_layout()
        self._draw_board()
        self._update_all_tokens()

    def _get_cell_coords(self, pos):
        """Converts square number (1-100) into center Canvas pixel coordinates."""
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

        # Left Side: Canvas Board
        self.canvas = tk.Canvas(
            container,
            width=BOARD_SIZE,
            height=BOARD_SIZE,
            bg="#f8fafc",
            highlightthickness=2,
            highlightbackground="#334155"
        )
        self.canvas.grid(row=0, column=0, rowspan=7, padx=(0, 16))

        # Right Side: Dashboard
        header_frame = tk.Frame(container, bg="#0f172a")
        header_frame.grid(row=0, column=1, sticky="w", pady=(0, 10))

        tk.Label(
            header_frame,
            text="SNAKES & LADDERS",
            font=("Segoe UI", 15, "bold"),
            fg="#f8fafc",
            bg="#0f172a"
        ).pack(anchor="w")

        tk.Label(
            header_frame,
            text="v1.1 Deluxe Edition",
            font=("Segoe UI", 9, "italic"),
            fg="#38bdf8",
            bg="#0f172a"
        ).pack(anchor="w")

        # Mode Selection
        mode_frame = tk.LabelFrame(
            container,
            text=" Game Setup ",
            font=("Segoe UI", 9, "bold"),
            fg="#94a3b8",
            bg="#1e293b",
            padx=8,
            pady=6
        )
        mode_frame.grid(row=1, column=1, sticky="ew", pady=4)

        self.mode_var = tk.StringVar(value="vs_cpu")
        modes = [
            ("1P vs Computer", "vs_cpu"),
            ("2 Players (Local)", "2p"),
            ("3 Players (Local)", "3p"),
            ("4 Players (Local)", "4p"),
        ]
        for text, mode_val in modes:
            rb = tk.Radiobutton(
                mode_frame,
                text=text,
                value=mode_val,
                variable=self.mode_var,
                command=self._apply_mode_change,
                bg="#1e293b",
                fg="#f1f5f9",
                selectcolor="#0f172a",
                activebackground="#1e293b",
                activeforeground="#38bdf8",
                font=("Segoe UI", 9)
            )
            rb.pack(anchor="w")

        # Current Turn Banner
        self.turn_banner = tk.Label(
            container,
            text="Turn: Player 1",
            font=("Segoe UI", 11, "bold"),
            bg="#e63946",
            fg="white",
            padx=8,
            pady=6,
            width=24
        )
        self.turn_banner.grid(row=2, column=1, sticky="ew", pady=8)

        # Interactive Canvas Dice
        self.dice_canvas = tk.Canvas(
            container,
            width=64,
            height=64,
            bg="#0f172a",
            highlightthickness=0
        )
        self.dice_canvas.grid(row=3, column=1, pady=4)
        self._render_dice_face(1)

        # Roll Action Button
        self.roll_btn = tk.Button(
            container,
            text="Roll Dice",
            font=("Segoe UI", 11, "bold"),
            bg="#0284c7",
            fg="white",
            activebackground="#0369a1",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=6,
            command=self.handle_human_turn
        )
        self.roll_btn.grid(row=4, column=1, sticky="ew", pady=6)

        # Event Log
        log_frame = tk.LabelFrame(
            container,
            text=" Match Log ",
            font=("Segoe UI", 9, "bold"),
            fg="#94a3b8",
            bg="#1e293b",
            padx=6,
            pady=4
        )
        log_frame.grid(row=5, column=1, sticky="nsew", pady=4)

        self.log_list = tk.Listbox(
            log_frame,
            height=6,
            width=26,
            font=("Consolas", 8),
            bg="#0f172a",
            fg="#e2e8f0",
            relief="flat",
            highlightthickness=0
        )
        self.log_list.pack(fill=tk.BOTH, expand=True)

        # Reset Match Button
        reset_btn = tk.Button(
            container,
            text="Reset Game",
            font=("Segoe UI", 9),
            bg="#475569",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.reset_game
        )
        reset_btn.grid(row=6, column=1, sticky="ew", pady=(4, 0))

    def _render_dice_face(self, val):
        self.dice_canvas.delete("all")
        # Dice body
        self.dice_canvas.create_rectangle(
            4, 4, 60, 60,
            fill="#ffffff",
            outline="#cbd5e1",
            width=2
        )
        # Pips
        for px, py in DICE_PIPS.get(val, []):
            cx = 4 + px * 56
            cy = 4 + py * 56
            r = 3.5
            self.dice_canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill="#0f172a", outline=""
            )

    def _apply_mode_change(self):
        selection = self.mode_var.get()
        if selection == "vs_cpu":
            self.num_players = 2
            self.is_vs_cpu = True
            PLAYER_PRESETS[1]["name"] = "CPU"
            PLAYER_PRESETS[1]["is_cpu"] = True
        else:
            self.is_vs_cpu = False
            self.num_players = int(selection[0])
            PLAYER_PRESETS[1]["name"] = "Player 2"
            PLAYER_PRESETS[1]["is_cpu"] = False
        self.reset_game()

    def _draw_board(self):
        # 1. Tile Grid with alternating pastel shades
        tile_colors = ["#f8fafc", "#e2e8f0"]
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
                bg = "#fef08a"  # Highlight winning tile
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=bg, outline="#cbd5e1")
            self.canvas.create_text(
                x1 + 4, y1 + 3,
                text=str(pos),
                font=("Segoe UI", 7, "bold"),
                anchor="nw",
                fill="#64748b"
            )

        # 2. Draw Ladder Visuals (Parallel rails with cross rungs)
        for bottom, top in LADDERS.items():
            bx, by = self._get_cell_coords(bottom)
            tx, ty = self._get_cell_coords(top)
            dx = tx - bx
            dy = ty - by
            dist = math.hypot(dx, dy)
            if dist == 0:
                continue
            nx = -dy / dist * 6
            ny = dx / dist * 6

            # Rails
            self.canvas.create_line(bx + nx, by + ny, tx + nx, ty + ny, fill="#15803d", width=3)
            self.canvas.create_line(bx - nx, by - ny, tx - nx, ty - ny, fill="#15803d", width=3)

            # Rungs
            rungs = max(3, int(dist // 14))
            for i in range(1, rungs):
                t = i / rungs
                rx = bx + t * dx
                ry = by + t * dy
                self.canvas.create_line(rx + nx, ry + ny, rx - nx, ry - ny, fill="#16a34a", width=2)

        # 3. Draw Snake Visuals (Curved body + head with eyes)
        for head, tail in SNAKES.items():
            hx, hy = self._get_cell_coords(head)
            tx, ty = self._get_cell_coords(tail)
            dx = tx - hx
            dy = ty - hy
            dist = math.hypot(dx, dy)
            if dist == 0:
                continue

            # Perpendicular vector for wave curves
            nx = -dy / dist * 10
            ny = dx / dist * 10

            # Generate sinusoidal path
            segments = 12
            points = []
            for i in range(segments + 1):
                t = i / segments
                wave = math.sin(t * math.pi * 3)
                px = hx + t * dx + wave * nx
                py = hy + t * dy + wave * ny
                points.extend([px, py])

            self.canvas.create_line(points, fill="#dc2626", width=4, smooth=True, capstyle=tk.ROUND)

            # Snake head
            self.canvas.create_oval(hx - 7, hy - 7, hx + 7, hy + 7, fill="#b91c1c", outline="#7f1d1d")
            self.canvas.create_oval(hx - 3, hy - 3, hx - 1, hy - 1, fill="white")
            self.canvas.create_oval(hx + 1, hy - 3, hx + 3, hy - 1, fill="white")

    def _update_all_tokens(self):
        self.canvas.delete("token")
        # Offsets for when multiple tokens land on the same tile
        slot_offsets = [(-8, -8), (8, -8), (-8, 8), (8, 8)]

        for i in range(self.num_players):
            pos = self.positions[i]
            cx, cy = self._get_cell_coords(pos)
            ox, oy = slot_offsets[i]
            x = cx + ox
            y = cy + oy
            color = PLAYER_PRESETS[i]["color"]

            # Token disc
            self.canvas.create_oval(
                x - 7, y - 7, x + 7, y + 7,
                fill=color, outline="#ffffff", width=2, tags="token"
            )
            # Token initial label
            self.canvas.create_text(
                x, y,
                text=str(i + 1),
                font=("Segoe UI", 7, "bold"),
                fill="#ffffff",
                tags="token"
            )

    def _log(self, text):
        self.log_list.insert(tk.END, text)
        self.log_list.see(tk.END)

    def handle_human_turn(self):
        if self.is_busy:
            return
        curr_player = PLAYER_PRESETS[self.current_turn_idx]
        if curr_player["is_cpu"]:
            return
        self._execute_turn()

    def _execute_turn(self):
        self.is_busy = True
        self.roll_btn.config(state=tk.DISABLED)

        # Shake / Roll animation
        def anim_step(frames_left):
            roll_val = random.randint(1, 6)
            self._render_dice_face(roll_val)
            play_fx("roll")
            if frames_left > 0:
                self.root.after(60, anim_step, frames_left - 1)
            else:
                final_roll = random.randint(1, 6)
                self._render_dice_face(final_roll)
                self._start_token_hop(final_roll)

        anim_step(5)

    def _start_token_hop(self, roll):
        p_idx = self.current_turn_idx
        p_info = PLAYER_PRESETS[p_idx]
        current_pos = self.positions[p_idx]

        # Exact roll required to reach 100
        if current_pos + roll > 100:
            self._log(f"{p_info['name']}: rolled {roll} (Overshot!)")
            self.root.after(600, self._advance_to_next_turn)
            return

        self._log(f"{p_info['name']}: rolled {roll}")

        def hop(steps_left):
            if steps_left > 0:
                self.positions[p_idx] += 1
                play_fx("hop")
                self._update_all_tokens()
                self.root.after(110, hop, steps_left - 1)
            else:
                # Landed on final step - check hazards
                self.root.after(160, self._check_tile_effects)

        hop(roll)

    def _check_tile_effects(self):
        p_idx = self.current_turn_idx
        p_info = PLAYER_PRESETS[p_idx]
        pos = self.positions[p_idx]

        if pos in LADDERS:
            dest = LADDERS[pos]
            self._log(f" └─ Ladder! {pos} -> {dest}")
            play_fx("ladder")
            self.positions[p_idx] = dest
            self._update_all_tokens()
        elif pos in SNAKES:
            dest = SNAKES[pos]
            self._log(f" └─ Snake bite! {pos} -> {dest}")
            play_fx("snake")
            self.positions[p_idx] = dest
            self._update_all_tokens()

        # Check win condition
        if self.positions[p_idx] == 100:
            play_fx("win")
            messagebox.showinfo("Victory!", f"{p_info['name']} reached 100 and won the match!")
            self.reset_game()
            return

        self.root.after(400, self._advance_to_next_turn)

    def _advance_to_next_turn(self):
        self.current_turn_idx = (self.current_turn_idx + 1) % self.num_players
        next_player = PLAYER_PRESETS[self.current_turn_idx]

        self.turn_banner.config(
            text=f"Turn: {next_player['name']}",
            bg=next_player["color"]
        )

        if next_player["is_cpu"]:
            self.is_busy = True
            self.roll_btn.config(state=tk.DISABLED)
            self.root.after(700, self._execute_turn)
        else:
            self.is_busy = False
            self.roll_btn.config(state=tk.NORMAL)

    def reset_game(self):
        self.positions = [1, 1, 1, 1]
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
    game = SnakesLaddersV11(app_root)
    app_root.mainloop()
