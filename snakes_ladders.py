"""
Snakes and Ladders - Version 1.0
Standalone GUI Desktop Edition
"""

import tkinter as tk
from tkinter import messagebox
import random

# Board rules configuration
LADDERS = {4: 14, 9: 31, 20: 38, 28: 84, 40: 59, 51: 67, 63: 81, 71: 91}
SNAKES = {17: 7, 54: 34, 62: 18, 64: 60, 87: 24, 93: 73, 95: 75, 99: 78}

CELL_SIZE = 50
GRID_COUNT = 10
BOARD_SIZE = CELL_SIZE * GRID_COUNT


class SnakesAndLaddersApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Snakes and Ladders v1.0")
        self.root.resizable(False, False)

        # Game state
        self.p1_pos = 1
        self.p2_pos = 1
        self.current_turn = "Player 1 (You)"
        self.is_animating = False

        self._build_ui()
        self._draw_board()
        self._update_tokens()

    def _get_cell_center(self, pos):
        """Converts a square number (1-100) to Canvas (x, y) coordinates."""
        pos = max(1, min(100, pos))
        row = (pos - 1) // 10
        col = (pos - 1) % 10
        if row % 2 == 1:
            col = 9 - col
        x = col * CELL_SIZE + CELL_SIZE // 2
        y = (9 - row) * CELL_SIZE + CELL_SIZE // 2
        return x, y

    def _build_ui(self):
        main_frame = tk.Frame(self.root, bg="#1e1e2e", padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas for the 10x10 Board
        self.canvas = tk.Canvas(
            main_frame,
            width=BOARD_SIZE,
            height=BOARD_SIZE,
            bg="#f8f9fa",
            highlightthickness=2,
            highlightbackground="#343a40"
        )
        self.canvas.grid(row=0, column=0, rowspan=6, padx=(0, 15))

        # Dashboard / Control Panel
        title_label = tk.Label(
            main_frame,
            text="SNAKES & LADDERS",
            font=("Helvetica", 14, "bold"),
            fg="#f1faee",
            bg="#1e1e2e"
        )
        title_label.grid(row=0, column=1, sticky="nw", pady=(0, 5))

        version_label = tk.Label(
            main_frame,
            text="v1.0 Standard Edition",
            font=("Helvetica", 9, "italic"),
            fg="#a8dadc",
            bg="#1e1e2e"
        )
        version_label.grid(row=0, column=1, sticky="sw", pady=(0, 15))

        # Status cards
        self.turn_display = tk.Label(
            main_frame,
            text="Turn: Player 1 (You)",
            font=("Helvetica", 11, "bold"),
            fg="#e63946",
            bg="#2b2d42",
            padx=10,
            pady=6,
            width=22
        )
        self.turn_display.grid(row=1, column=1, sticky="w", pady=5)

        self.score_display = tk.Label(
            main_frame,
            text="You (Red): 1  |  CPU (Blue): 1",
            font=("Helvetica", 10),
            fg="#edf2f4",
            bg="#2b2d42",
            padx=10,
            pady=6,
            width=22
        )
        self.score_display.grid(row=2, column=1, sticky="w", pady=5)

        # Dice display
        self.dice_box = tk.Label(
            main_frame,
            text="🎲\n-",
            font=("Helvetica", 18, "bold"),
            fg="#1d3557",
            bg="#f1faee",
            relief="groove",
            width=8,
            height=3
        )
        self.dice_box.grid(row=3, column=1, pady=10)

        # Buttons
        self.roll_btn = tk.Button(
            main_frame,
            text="Roll Dice",
            font=("Helvetica", 11, "bold"),
            bg="#457b9d",
            fg="white",
            activebackground="#1d3557",
            activeforeground="white",
            width=18,
            command=self.handle_player_roll
        )
        self.roll_btn.grid(row=4, column=1, pady=5)

        reset_btn = tk.Button(
            main_frame,
            text="Reset Match",
            font=("Helvetica", 10),
            bg="#6c757d",
            fg="white",
            width=18,
            command=self.reset_game
        )
        reset_btn.grid(row=5, column=1, pady=5)

    def _draw_board(self):
        palette = ["#ffffff", "#e9ecef"]
        for pos in range(1, 101):
            row = (pos - 1) // 10
            col = (pos - 1) % 10
            if row % 2 == 1:
                col = 9 - col

            x1 = col * CELL_SIZE
            y1 = (9 - row) * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            bg_col = palette[(row + col) % 2]
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=bg_col, outline="#ced4da")
            self.canvas.create_text(
                x1 + 4, y1 + 4,
                text=str(pos),
                font=("Arial", 8, "bold"),
                anchor="nw",
                fill="#6c757d"
            )

        # Draw Ladders (Green arrows)
        for start, end in LADDERS.items():
            sx, sy = self._get_cell_center(start)
            ex, ey = self._get_cell_center(end)
            self.canvas.create_line(
                sx, sy, ex, ey,
                fill="#2b9348",
                width=4,
                arrow=tk.LAST,
                arrowshape=(10, 12, 5)
            )

        # Draw Snakes (Red arrows)
        for start, end in SNAKES.items():
            sx, sy = self._get_cell_center(start)
            ex, ey = self._get_cell_center(end)
            self.canvas.create_line(
                sx, sy, ex, ey,
                fill="#d90429",
                width=4,
                arrow=tk.LAST,
                arrowshape=(10, 12, 5)
            )

    def _update_tokens(self):
        self.canvas.delete("token")
        p1_x, p1_y = self._get_cell_center(self.p1_pos)
        p2_x, p2_y = self._get_cell_center(self.p2_pos)

        # Player 1 (Red token, offset slightly top-left)
        self.canvas.create_oval(
            p1_x - 14, p1_y - 14, p1_x - 2, p1_y - 2,
            fill="#e63946", outline="#ffffff", width=2, tags="token"
        )

        # Player 2 (Blue token, offset slightly bottom-right)
        self.canvas.create_oval(
            p2_x + 2, p2_y + 2, p2_x + 14, p2_y + 14,
            fill="#1d3557", outline="#ffffff", width=2, tags="token"
        )

        self.score_display.config(
            text=f"You (Red): {self.p1_pos}  |  CPU (Blue): {self.p2_pos}"
        )

    def handle_player_roll(self):
        if self.is_animating or self.current_turn != "Player 1 (You)":
            return
        self._animate_dice(self._execute_player_move)

    def _animate_dice(self, callback, frames=5):
        self.is_animating = True
        self.roll_btn.config(state=tk.DISABLED)

        def step(frame_left):
            temp_val = random.randint(1, 6)
            self.dice_box.config(text=f"🎲\n{temp_val}")
            if frame_left > 0:
                self.root.after(60, step, frame_left - 1)
            else:
                final_val = random.randint(1, 6)
                self.dice_box.config(text=f"🎲\n{final_val}")
                self.is_animating = False
                callback(final_val)

        step(frames)

    def _execute_player_move(self, roll):
        if self.p1_pos + roll <= 100:
            self.p1_pos += roll
            if self.p1_pos in LADDERS:
                self.p1_pos = LADDERS[self.p1_pos]
            elif self.p1_pos in SNAKES:
                self.p1_pos = SNAKES[self.p1_pos]

        self._update_tokens()

        if self.p1_pos == 100:
            messagebox.showinfo("Game Over", "Congratulations! You won the game!")
            self.reset_game()
            return

        self.current_turn = "CPU (Blue)"
        self.turn_display.config(text="Turn: CPU (Thinking...)", fg="#457b9d")
        self.root.after(800, self.handle_cpu_roll)

    def handle_cpu_roll(self):
        self._animate_dice(self._execute_cpu_move)

    def _execute_cpu_move(self, roll):
        if self.p2_pos + roll <= 100:
            self.p2_pos += roll
            if self.p2_pos in LADDERS:
                self.p2_pos = LADDERS[self.p2_pos]
            elif self.p2_pos in SNAKES:
                self.p2_pos = SNAKES[self.p2_pos]

        self._update_tokens()

        if self.p2_pos == 100:
            messagebox.showinfo("Game Over", "The CPU won this round! Better luck next time.")
            self.reset_game()
            return

        self.current_turn = "Player 1 (You)"
        self.turn_display.config(text="Turn: Player 1 (You)", fg="#e63946")
        self.roll_btn.config(state=tk.NORMAL)

    def reset_game(self):
        self.p1_pos = 1
        self.p2_pos = 1
        self.current_turn = "Player 1 (You)"
        self.is_animating = False
        self.roll_btn.config(state=tk.NORMAL)
        self.turn_display.config(text="Turn: Player 1 (You)", fg="#e63946")
        self.dice_box.config(text="🎲\n-")
        self._update_tokens()


if __name__ == "__main__":
    root = tk.Tk()
    app = SnakesAndLaddersApp(root)
    root.mainloop()