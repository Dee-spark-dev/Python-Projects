import tkinter as tk
import random
import time


# ============================================================
# COLORS AND SETTINGS
# ============================================================

BG = "#10131f"
PANEL = "#191e2e"
CYAN = "#00d9ff"
PURPLE = "#9b5cff"
WHITE = "#f4f6ff"
GREEN = "#39e58c"
RED = "#ff5470"
YELLOW = "#ffcc45"

DIRECTIONS = [
    (0, 1), (0, -1),
    (1, 0), (-1, 0),
    (1, 1), (1, -1),
    (-1, 1), (-1, -1)
]

WORD_BANK = [
    "PYTHON", "CODING", "COMPUTER", "KEYBOARD",
    "MONITOR", "SOFTWARE", "HARDWARE", "PROGRAM",
    "NETWORK", "INTERNET", "DATABASE", "VARIABLE",
    "FUNCTION", "SECURITY", "FIREWALL", "ENCRYPT",
    "HACKER", "ROUTER", "SERVER", "LINUX",
    "WINDOWS", "BROWSER", "PASSWORD", "TERMINAL",
    "MALWARE", "VIRUS", "PHISHING", "ETHICAL",
    "DIGITAL", "SCRIPT", "DEBUG", "SYSTEM"
]


# ============================================================
# WORD SEARCH GAME
# ============================================================

class WordSearch:

    def __init__(self, root):

        self.root = root

        self.window = tk.Toplevel(root)
        self.window.title("Word Search")
        self.window.configure(bg=BG)
        self.window.geometry("1050x780")
        self.window.minsize(700, 600)

        self.window.protocol(
            "WM_DELETE_WINDOW",
            self.return_to_menu
        )

        self.difficulty = "Medium"

        self.settings = {
            "Easy": (8, 8, 8),
            "Medium": (10, 10, 12),
            "Hard": (12, 12, 16)
        }

        self.size = 10
        self.words = []
        self.grid = []

        self.found_words = set()
        self.placements = {}

        self.score = 0
        self.total_score = 0
        self.round_number = 1

        self.start_time = None
        self.elapsed = 0
        self.timer_job = None

        self.selecting = False
        self.selection_start = None
        self.selection_end = None
        self.selected_cells = []

        self.game_over = False
        self.round_job = None

        self.cell_size = 38
        self.board_offset_x = 0
        self.board_offset_y = 0

        self.create_interface()
        self.bind_controls()
        self.new_game()

    # ========================================================
    # INTERFACE
    # ========================================================

    def create_interface(self):

        # Header
        header = tk.Frame(self.window, bg=BG)
        header.pack(fill="x", padx=15, pady=10)

        tk.Label(
            header,
            text="WORD SEARCH",
            font=("Arial", 24, "bold"),
            fg=CYAN,
            bg=BG
        ).pack(side="left")

        tk.Button(
            header,
            text="MAIN MENU",
            command=self.return_to_menu,
            bg=PURPLE,
            fg=WHITE,
            relief="flat",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=7
        ).pack(side="right")

        # Statistics
        stats = tk.Frame(self.window, bg=PANEL)
        stats.pack(fill="x", padx=15, pady=5)

        self.score_label = self.make_stat(stats, "SCORE: 0")
        self.round_label = self.make_stat(stats, "ROUND: 1")
        self.timer_label = self.make_stat(stats, "TIME: 00:00")

        # Main content
        content = tk.Frame(self.window, bg=BG)
        content.pack(fill="both", expand=True, padx=15, pady=8)

        # Left: word list
        self.word_panel = tk.Frame(
            content,
            bg=PANEL,
            width=190
        )
        self.word_panel.pack(
            side="left",
            fill="y",
            padx=(0, 12)
        )
        self.word_panel.pack_propagate(False)

        tk.Label(
            self.word_panel,
            text="FIND THESE WORDS",
            font=("Arial", 11, "bold"),
            fg=CYAN,
            bg=PANEL
        ).pack(pady=12)

        self.word_list = tk.Frame(
            self.word_panel,
            bg=PANEL
        )
        self.word_list.pack(fill="both", expand=True, padx=10)

        # Right: game board
        self.board_frame = tk.Frame(content, bg=BG)
        self.board_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.board_frame,
            bg="#080b14",
            highlightthickness=2,
            highlightbackground=PURPLE
        )
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Configure>", self.draw_board)
        self.canvas.bind("<Button-1>", self.start_selection)
        self.canvas.bind("<B1-Motion>", self.drag_selection)
        self.canvas.bind("<ButtonRelease-1>", self.finish_selection)

        # Bottom controls
        controls = tk.Frame(self.window, bg=BG)
        controls.pack(side="bottom", fill="x", padx=15, pady=10)

        tk.Label(
            controls,
            text="Difficulty:",
            fg=WHITE,
            bg=BG,
            font=("Arial", 10, "bold")
        ).pack(side="left", padx=5)

        self.difficulty_var = tk.StringVar(value="Medium")

        self.difficulty_menu = tk.OptionMenu(
            controls,
            self.difficulty_var,
            "Easy",
            "Medium",
            "Hard",
            command=self.change_difficulty
        )
        self.difficulty_menu.config(
            bg=PANEL,
            fg=CYAN,
            activebackground=PURPLE,
            activeforeground=WHITE,
            relief="flat",
            highlightthickness=0
        )
        self.difficulty_menu.pack(side="left", padx=5)

        tk.Button(
            controls,
            text="NEW GAME",
            command=self.new_game,
            bg=PURPLE,
            fg=WHITE,
            relief="flat",
            font=("Arial", 10, "bold"),
            padx=12,
            pady=7
        ).pack(side="left", padx=5)

        tk.Button(
            controls,
            text="HINT",
            command=self.give_hint,
            bg=CYAN,
            fg="#10131f",
            relief="flat",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=7
        ).pack(side="left", padx=5)

        self.status_label = tk.Label(
            controls,
            text="Drag across letters to find words.",
            fg=WHITE,
            bg=BG,
            font=("Arial", 10)
        )
        self.status_label.pack(side="right", padx=5)

    def make_stat(self, parent, text):

        label = tk.Label(
            parent,
            text=text,
            font=("Arial", 11, "bold"),
            fg=CYAN,
            bg=PANEL
        )

        label.pack(side="left", padx=18, pady=12)

        return label

    # ========================================================
    # KEYBOARD CONTROLS
    # ========================================================

    def bind_controls(self):

        self.window.bind(
            "<F11>",
            lambda e: self.toggle_fullscreen()
        )

        self.window.bind(
            "<Escape>",
            lambda e: self.exit_fullscreen()
        )

    # ========================================================
    # GENERATE WORD SEARCH
    # ========================================================

    def generate_grid(self):

        self.grid = [
            [" " for _ in range(self.size)]
            for _ in range(self.size)
        ]

        self.placements = {}

        selected_words = random.sample(
            WORD_BANK,
            min(len(WORD_BANK), self.word_count)
        )

        # Long words first
        selected_words.sort(key=len, reverse=True)

        self.words = []

        for word in selected_words:

            if not self.place_word(word):
                continue

            self.words.append(word)

        # Fill empty cells with random letters
        for row in range(self.size):
            for col in range(self.size):

                if self.grid[row][col] == " ":

                    self.grid[row][col] = random.choice(
                        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    )

    # ========================================================
    # PLACE WORDS IN GRID
    # ========================================================

    def place_word(self, word):

        positions = []

        for _ in range(300):

            row = random.randrange(self.size)
            col = random.randrange(self.size)

            dr, dc = random.choice(DIRECTIONS)

            end_row = row + (len(word) - 1) * dr
            end_col = col + (len(word) - 1) * dc

            if not (
                0 <= end_row < self.size and
                0 <= end_col < self.size
            ):
                continue

            valid = True

            for i, letter in enumerate(word):

                r = row + i * dr
                c = col + i * dc

                existing = self.grid[r][c]

                if existing not in (" ", letter):
                    valid = False
                    break

            if not valid:
                continue

            for i, letter in enumerate(word):

                r = row + i * dr
                c = col + i * dc

                self.grid[r][c] = letter
                positions.append((r, c))

            self.placements[word] = positions

            return True

        return False

    # ========================================================
    # NEW GAME
    # ========================================================

    def new_game(self):

        self.cancel_jobs()

        self.size, _, self.word_count = self.settings[
            self.difficulty
        ]

        self.found_words = set()
        self.score = 0

        self.game_over = False

        self.selecting = False
        self.selected_cells = []

        self.start_time = time.time()
        self.elapsed = 0

        self.generate_grid()
        self.build_word_list()

        self.update_stats()

        self.status_label.config(
            text="Drag across letters to find words."
        )

        self.draw_board()
        self.update_timer()

    # ========================================================
    # BUILD WORD LIST
    # ========================================================

    def build_word_list(self):

        for widget in self.word_list.winfo_children():
            widget.destroy()

        self.word_labels = {}

        for word in sorted(self.words):

            label = tk.Label(
                self.word_list,
                text="○  " + word,
                font=("Arial", 10, "bold"),
                fg=WHITE,
                bg=PANEL,
                anchor="w"
            )

            label.pack(fill="x", pady=4)

            self.word_labels[word] = label

    # ========================================================
    # DRAW BOARD
    # ========================================================

    def draw_board(self, event=None):

        if not hasattr(self, "canvas"):
            return

        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        self.cell_size = min(
            width / self.size,
            height / self.size
        )

        board_width = self.cell_size * self.size
        board_height = self.cell_size * self.size

        self.board_offset_x = (width - board_width) / 2
        self.board_offset_y = (height - board_height) / 2

        for row in range(self.size):
            for col in range(self.size):

                x1 = self.board_offset_x + col * self.cell_size
                y1 = self.board_offset_y + row * self.cell_size

                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                selected = (row, col) in self.selected_cells

                found = any(
                    (row, col) in positions
                    for word, positions in self.placements.items()
                    if word in self.found_words
                )

                color = "#263d4a" if found else PANEL

                if selected:
                    color = "#245b70"

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline="#303b52",
                    width=1
                )

                self.canvas.create_text(
                    (x1 + x2) / 2,
                    (y1 + y2) / 2,
                    text=self.grid[row][col],
                    fill=GREEN if found else WHITE,
                    font=(
                        "Arial",
                        max(8, int(self.cell_size * 0.42)),
                        "bold"
                    )
                )

    # ========================================================
    # GET CELL FROM MOUSE POSITION
    # ========================================================

    def get_cell(self, event):

        col = int(
            (event.x - self.board_offset_x) / self.cell_size
        )

        row = int(
            (event.y - self.board_offset_y) / self.cell_size
        )

        if (
            0 <= row < self.size and
            0 <= col < self.size
        ):
            return row, col

        return None

    # ========================================================
    # SELECTION
    # ========================================================

    def start_selection(self, event):

        if self.game_over:
            return

        cell = self.get_cell(event)

        if cell is None:
            return

        self.selecting = True
        self.selection_start = cell
        self.selection_end = cell

        self.update_selection()

    def drag_selection(self, event):

        if not self.selecting:
            return

        cell = self.get_cell(event)

        if cell is None:
            return

        self.selection_end = cell

        self.update_selection()

    def finish_selection(self, event):

        if not self.selecting:
            return

        self.selecting = False

        cell = self.get_cell(event)

        if cell is not None:
            self.selection_end = cell

        self.update_selection()
        self.check_selected_word()

    # ========================================================
    # BUILD STRAIGHT-LINE SELECTION
    # ========================================================

    def update_selection(self):

        if not self.selection_start or not self.selection_end:
            return

        r1, c1 = self.selection_start
        r2, c2 = self.selection_end

        dr = r2 - r1
        dc = c2 - c1

        # Only straight horizontal, vertical or diagonal lines
        if dr != 0 and dc != 0 and abs(dr) != abs(dc):
            self.selected_cells = [self.selection_start]
            self.draw_board()
            return

        steps = max(abs(dr), abs(dc))

        step_r = 0 if dr == 0 else dr // steps
        step_c = 0 if dc == 0 else dc // steps

        self.selected_cells = [
            (r1 + i * step_r, c1 + i * step_c)
            for i in range(steps + 1)
        ]

        self.draw_board()

    # ========================================================
    # CHECK SELECTED WORD
    # ========================================================

    def check_selected_word(self):

        if not self.selected_cells:
            return

        selected_word = "".join(
            self.grid[row][col]
            for row, col in self.selected_cells
        )

        reversed_word = selected_word[::-1]

        found = None

        for word in self.words:

            if word in self.found_words:
                continue

            if selected_word == word or reversed_word == word:
                found = word
                break

        if found:

            self.found_words.add(found)

            self.score += len(found) * 10

            self.word_labels[found].config(
                text="✓  " + found,
                fg=GREEN
            )

            self.status_label.config(
                text=f"Found {found}! +{len(found) * 10} points"
            )

            self.update_stats()

            if len(self.found_words) == len(self.words):
                self.finish_game()

        else:

            self.status_label.config(
                text="Not a word on the list. Try again!"
            )

        self.selected_cells = []
        self.draw_board()

    # ========================================================
    # HINT
    # ========================================================

    def give_hint(self):

        if self.game_over:
            return

        remaining = [
            word for word in self.words
            if word not in self.found_words
        ]

        if not remaining:
            return

        word = random.choice(remaining)

        self.selected_cells = self.placements[word][:]

        self.score = max(0, self.score - 20)

        self.status_label.config(
            text=f"Hint: Look for {word}. (-20 points)"
        )

        self.update_stats()
        self.draw_board()

        self.window.after(
            1500,
            self.clear_hint
        )

    def clear_hint(self):

        if not self.selecting:
            self.selected_cells = []
            self.draw_board()

    # ========================================================
    # TIMER
    # ========================================================

    def update_timer(self):

        if self.game_over:
            return

        self.elapsed = int(time.time() - self.start_time)

        minutes = self.elapsed // 60
        seconds = self.elapsed % 60

        self.timer_label.config(
            text=f"TIME: {minutes:02d}:{seconds:02d}"
        )

        self.timer_job = self.window.after(
            1000,
            self.update_timer
        )

    # ========================================================
    # UPDATE STATISTICS
    # ========================================================

    def update_stats(self):

        self.score_label.config(
            text=f"SCORE: {self.score}"
        )

        self.round_label.config(
            text=f"ROUND: {self.round_number}"
        )

    # ========================================================
    # FINISH GAME
    # ========================================================

    def finish_game(self):

        self.game_over = True

        self.cancel_timer()

        self.total_score += self.score

        self.status_label.config(
            text="Amazing! You found every word!"
        )

        self.canvas.create_text(
            self.canvas.winfo_width() / 2,
            self.canvas.winfo_height() / 2,
            text="ROUND COMPLETE!",
            fill=GREEN,
            font=("Arial", 25, "bold"),
            tags="completion"
        )

        self.round_job = self.window.after(
            2500,
            self.next_round
        )

    # ========================================================
    # NEXT ROUND
    # ========================================================

    def next_round(self):

        self.round_job = None

        self.round_number += 1

        self.new_game()

    # ========================================================
    # DIFFICULTY
    # ========================================================

    def change_difficulty(self, value):

        self.difficulty = value
        self.round_number = 1

        self.new_game()

    # ========================================================
    # CANCEL JOBS
    # ========================================================

    def cancel_timer(self):

        if self.timer_job is not None:

            try:
                self.window.after_cancel(self.timer_job)
            except tk.TclError:
                pass

            self.timer_job = None

    def cancel_jobs(self):

        self.cancel_timer()

        if self.round_job is not None:

            try:
                self.window.after_cancel(self.round_job)
            except tk.TclError:
                pass

            self.round_job = None

    # ========================================================
    # FULLSCREEN
    # ========================================================

    def toggle_fullscreen(self):

        current = self.window.attributes("-fullscreen")

        self.window.attributes("-fullscreen", not current)

    def exit_fullscreen(self):

        self.window.attributes("-fullscreen", False)

    # ========================================================
    # MAIN MENU
    # ========================================================

    def return_to_menu(self):

        self.cancel_jobs()

        self.window.destroy()

        self.root.deiconify()


# ============================================================
# LAUNCHER FUNCTION
# ============================================================

def play(root):

    root.withdraw()

    try:

        WordSearch(root)

    except Exception as error:

        root.deiconify()

        from tkinter import messagebox

        messagebox.showerror(
            "Word Search Error",
            str(error)
        )