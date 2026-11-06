
import tkinter as tk
from tkinter import messagebox
import random

# ============================================================
# MATCH CARDS - PYTHON GAMES ARSENAL
# ============================================================

BG = "#101522"
PANEL = "#1b2536"
CARD_BACK = "#26364c"
CYAN = "#00d9ff"
PURPLE = "#a78bfa"
WHITE = "#f4f7ff"
MUTED = "#9aa9bd"
GREEN = "#38d996"
RED = "#ff5263"

SYMBOLS = [
    "🐍", "♟", "⚽", "🎮", "🚀", "🎯",
    "🎲", "🎸", "🌟", "🔥", "💎", "🦊",
    "🐼", "🍕", "🚗", "🌈", "👑", "⚡"
]


class MatchCards:

    def __init__(self, root):

        self.root = root

        self.window = tk.Toplevel(root)
        self.window.title("Match Cards")
        self.window.geometry("950x750")
        self.window.minsize(650, 620)
        self.window.configure(bg=BG)
        self.window.protocol("WM_DELETE_WINDOW", self.return_to_menu)

        self.mode = tk.StringVar(value="Computer")
        self.difficulty = tk.StringVar(value="Medium")

        self.player_names = ["PLAYER 1", "PLAYER 2"]

        self.scores = [0, 0]
        self.moves = 0
        self.round_number = 1

        self.current_player = 0
        self.starting_player = 0

        self.cards = []
        self.buttons = []

        self.flipped = []
        self.matched = set()

        self.locked = False
        self.game_over = False
        self.ai_job = None
        self.mismatch_job = None
        self.next_round_job = None

        self.first_pick = None

        self.pairs_found = [0, 0]

        self.build_interface()
        self.new_game()

        self.window.bind("<F11>", self.toggle_fullscreen)
        self.window.bind("<Escape>", self.exit_fullscreen)

    # ========================================================
    # INTERFACE
    # ========================================================

    def build_interface(self):

        header = tk.Frame(self.window, bg=BG)
        header.pack(fill="x", pady=(12, 5))

        tk.Label(
            header,
            text="MATCH CARDS",
            font=("Arial", 25, "bold"),
            fg=CYAN,
            bg=BG
        ).pack()

        tk.Label(
            header,
            text="Find all matching pairs!",
            font=("Arial", 10),
            fg=MUTED,
            bg=BG
        ).pack(pady=3)

        settings = tk.Frame(self.window, bg=PANEL)
        settings.pack(fill="x", padx=18, pady=6)

        tk.Label(
            settings,
            text="MODE",
            bg=PANEL,
            fg=WHITE,
            font=("Arial", 9, "bold")
        ).pack(side="left", padx=(10, 4), pady=9)

        mode_menu = tk.OptionMenu(
            settings,
            self.mode,
            "Computer",
            "Two Players",
            command=self.change_mode
        )

        mode_menu.config(
            bg=CARD_BACK,
            fg=WHITE,
            highlightthickness=0
        )
        mode_menu["menu"].config(bg=PANEL, fg=WHITE)
        mode_menu.pack(side="left", padx=3)

        tk.Label(
            settings,
            text="DIFFICULTY",
            bg=PANEL,
            fg=WHITE,
            font=("Arial", 9, "bold")
        ).pack(side="left", padx=(12, 4))

        self.difficulty_menu = tk.OptionMenu(
            settings,
            self.difficulty,
            "Easy",
            "Medium",
            "Hard",
            command=self.change_difficulty
        )

        self.difficulty_menu.config(
            bg=CARD_BACK,
            fg=WHITE,
            highlightthickness=0
        )
        self.difficulty_menu["menu"].config(bg=PANEL, fg=WHITE)
        self.difficulty_menu.pack(side="left", padx=3)

        # Current turn
        self.status = tk.Label(
            self.window,
            text="PLAYER 1'S TURN",
            font=("Arial", 13, "bold"),
            fg=CYAN,
            bg=BG
        )
        self.status.pack(pady=5)

        # Scoreboard
        self.score_label = tk.Label(
            self.window,
            text="PLAYER 1: 0     PLAYER 2: 0",
            font=("Arial", 10, "bold"),
            fg=WHITE,
            bg=BG
        )
        self.score_label.pack(pady=3)

        # Round and moves
        self.info_label = tk.Label(
            self.window,
            text="ROUND 1     MOVES: 0     PAIRS: 0",
            font=("Arial", 9),
            fg=MUTED,
            bg=BG
        )
        self.info_label.pack(pady=3)

        # Card area
        self.card_frame = tk.Frame(
            self.window,
            bg=BG
        )

        self.card_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=8
        )

        # Controls
        controls = tk.Frame(self.window, bg=BG)
        controls.pack(
            side="bottom",
            fill="x",
            padx=10,
            pady=(5, 12)
        )

        self.make_button(
            controls, "NEW GAME",
            self.new_game, CYAN
        ).pack(side="left", expand=True, fill="x", padx=3)

        self.make_button(
            controls, "RESET SCORES",
            self.reset_scores, PURPLE
        ).pack(side="left", expand=True, fill="x", padx=3)

        self.make_button(
            controls, "MAIN MENU",
            self.return_to_menu, RED
        ).pack(side="left", expand=True, fill="x", padx=3)

    def make_button(self, parent, text, command, color):

        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=BG,
            activebackground=WHITE,
            font=("Arial", 9, "bold"),
            relief="flat",
            padx=8,
            pady=10,
            cursor="hand2"
        )

    # ========================================================
    # GAME SETUP
    # ========================================================

    def get_pair_count(self):

        difficulty = self.difficulty.get()

        if difficulty == "Easy":
            return 6

        elif difficulty == "Medium":
            return 8

        return 10

    def new_game(self):

        self.cancel_jobs()

        self.round_number = 1 if self.round_number < 1 else self.round_number

        self.moves = 0
        self.current_player = self.starting_player

        self.flipped = []
        self.matched = set()

        self.locked = False
        self.game_over = False

        self.pairs_found = [0, 0]

        self.first_pick = None

        self.create_cards()
        self.update_display()
        self.update_status()

    def create_cards(self):

        for widget in self.card_frame.winfo_children():
            widget.destroy()

        self.buttons = []

        pair_count = self.get_pair_count()

        selected_symbols = random.sample(
            SYMBOLS,
            pair_count
        )

        self.cards = selected_symbols * 2
        random.shuffle(self.cards)

        total_cards = len(self.cards)

        if total_cards == 12:
            columns = 4
        elif total_cards == 16:
            columns = 4
        else:
            columns = 5

        for col in range(columns):
            self.card_frame.grid_columnconfigure(
                col,
                weight=1,
                uniform="cards"
            )

        rows = (total_cards + columns - 1) // columns

        for row in range(rows):
            self.card_frame.grid_rowconfigure(
                row,
                weight=1,
                uniform="cards"
            )

        for index in range(total_cards):

            row = index // columns
            col = index % columns

            button = tk.Button(
                self.card_frame,
                text="?",
                font=("Arial", 23, "bold"),
                bg=CARD_BACK,
                fg=CYAN,
                activebackground="#344963",
                activeforeground=WHITE,
                relief="flat",
                cursor="hand2",
                command=lambda i=index: self.flip_card(i)
            )

            button.grid(
                row=row,
                column=col,
                sticky="nsew",
                padx=5,
                pady=5
            )

            self.buttons.append(button)

    # ========================================================
    # CARD MOVEMENT
    # ========================================================

    def flip_card(self, index):

        if self.game_over or self.locked:
            return

        if index in self.matched or index in self.flipped:
            return

        if self.mode.get() == "Computer" and self.current_player == 1:
            return

        self.flipped.append(index)

        self.buttons[index].config(
            text=self.cards[index],
            bg="#344963",
            fg=WHITE
        )

        if len(self.flipped) == 1:

            self.first_pick = index
            return

        self.moves += 1

        first, second = self.flipped

        if self.cards[first] == self.cards[second]:

            self.handle_match(first, second)

        else:

            self.locked = True

            self.status.config(
                text="NOT A MATCH!",
                fg=RED
            )

            self.mismatch_job = self.window.after(
                900,
                self.hide_cards
            )

    def handle_match(self, first, second):

        self.matched.add(first)
        self.matched.add(second)

        self.buttons[first].config(
            bg=GREEN,
            fg=BG,
            relief="flat"
        )

        self.buttons[second].config(
            bg=GREEN,
            fg=BG,
            relief="flat"
        )

        self.pairs_found[self.current_player] += 1

        self.flipped = []
        self.first_pick = None

        self.update_display()

        # Matching grants another turn.
        if len(self.matched) == len(self.cards):

            self.finish_game()
            return

        self.status.config(
            text="MATCH FOUND! PLAY AGAIN.",
            fg=GREEN
        )

        if self.mode.get() == "Computer" and self.current_player == 0:

            self.ai_job = self.window.after(
                600,
                self.update_status
            )

    def hide_cards(self):

        self.mismatch_job = None

        for index in self.flipped:

            self.buttons[index].config(
                text="?",
                bg=CARD_BACK,
                fg=CYAN
            )

        self.flipped = []
        self.first_pick = None

        self.locked = False

        # Turn changes after a failed match.
        self.current_player = 1 - self.current_player

        self.update_status()

        if self.mode.get() == "Computer" and self.current_player == 1:

            self.ai_job = self.window.after(
                700,
                self.computer_turn
            )

    # ========================================================
    # COMPUTER MEMORY AND AI
    # ========================================================

    def computer_turn(self):

        self.ai_job = None

        if self.game_over or self.current_player != 1:
            return

        self.locked = False

        available = [
            i for i in range(len(self.cards))
            if i not in self.matched
        ]

        if len(available) < 2:
            return

        difficulty = self.difficulty.get()

        # The computer remembers previously revealed cards.
        known = getattr(self, "computer_memory", {})

        known_pairs = {}

        for index, symbol in known.items():

            if index not in self.matched:
                known_pairs.setdefault(symbol, []).append(index)

        pair_choice = None

        if difficulty != "Easy":

            for symbol, positions in known_pairs.items():

                remaining = [
                    p for p in positions
                    if p not in self.matched
                ]

                if len(remaining) >= 2:
                    pair_choice = remaining[:2]
                    break

        if pair_choice:

            first, second = pair_choice

        else:

            first = random.choice(available)

            # Medium and Hard remember the first card they reveal.
            remaining = [
                i for i in available
                if i != first
            ]

            if difficulty == "Easy":
                second = random.choice(remaining)

            else:

                known_matches = [
                    i for i in remaining
                    if known.get(i) == self.cards[first]
                ]

                if known_matches:
                    second = random.choice(known_matches)

                else:
                    second = random.choice(remaining)

        self.reveal_computer_card(first)

        self.window.after(
            450,
            lambda: self.reveal_second_computer_card(second)
        )

    def reveal_computer_card(self, index):

        if self.game_over or index in self.matched:
            return

        self.flipped.append(index)

        self.buttons[index].config(
            text=self.cards[index],
            bg="#344963",
            fg=WHITE
        )

        # Record what the computer has seen.
        if not hasattr(self, "computer_memory"):
            self.computer_memory = {}

        if self.difficulty.get() != "Easy":
            self.computer_memory[index] = self.cards[index]

    def reveal_second_computer_card(self, index):

        if self.game_over or index in self.matched:
            self.flipped = []
            return

        self.flipped.append(index)

        self.buttons[index].config(
            text=self.cards[index],
            bg="#344963",
            fg=WHITE
        )

        if self.difficulty.get() != "Easy":
            self.computer_memory[index] = self.cards[index]

        self.moves += 1

        first, second = self.flipped

        if self.cards[first] == self.cards[second]:

            self.handle_match(first, second)

            if not self.game_over:

                self.ai_job = self.window.after(
                    600,
                    self.computer_turn
                )

        else:

            self.locked = True

            self.mismatch_job = self.window.after(
                900,
                self.hide_computer_cards
            )

    def hide_computer_cards(self):

        self.mismatch_job = None

        for index in self.flipped:

            self.buttons[index].config(
                text="?",
                bg=CARD_BACK,
                fg=CYAN
            )

        self.flipped = []
        self.locked = False

        self.current_player = 0

        self.update_status()

    # ========================================================
    # RESULTS
    # ========================================================

    def finish_game(self):

        self.game_over = True

        if self.ai_job:
            self.window.after_cancel(self.ai_job)
            self.ai_job = None

        if self.pairs_found[0] > self.pairs_found[1]:

            self.scores[0] += 1
            winner = "PLAYER 1 WINS!"

        elif self.pairs_found[1] > self.pairs_found[0]:

            self.scores[1] += 1

            winner = (
                "COMPUTER WINS!"
                if self.mode.get() == "Computer"
                else "PLAYER 2 WINS!"
            )

        else:
            winner = "IT'S A DRAW!"

        self.status.config(
            text=winner + " NEXT ROUND IN 2 SECONDS...",
            fg=CYAN
        )

        self.update_display()

        self.next_round_job = self.window.after(
            2000,
            self.start_next_round
        )

    def start_next_round(self):

        self.next_round_job = None

        self.starting_player = 1 - self.starting_player

        self.round_number += 1

        self.new_game()

    # ========================================================
    # DISPLAY UPDATES
    # ========================================================

    def update_status(self):

        if self.current_player == 0:

            self.status.config(
                text="PLAYER 1'S TURN",
                fg=CYAN
            )

        else:

            name = (
                "COMPUTER"
                if self.mode.get() == "Computer"
                else "PLAYER 2"
            )

            self.status.config(
                text=name + "'S TURN",
                fg=PURPLE
            )

        self.update_display()

    def update_display(self):

        second_name = (
            "COMPUTER"
            if self.mode.get() == "Computer"
            else "PLAYER 2"
        )

        self.score_label.config(
            text=f"PLAYER 1: {self.scores[0]}     "
                 f"{second_name}: {self.scores[1]}"
        )

        self.info_label.config(
            text=f"ROUND {self.round_number}     "
                 f"MOVES: {self.moves}     "
                 f"PAIRS: {len(self.matched) // 2}/{len(self.cards) // 2}"
        )

    # ========================================================
    # RESTART AND SETTINGS
    # ========================================================

    def cancel_jobs(self):

        for job_name in ("ai_job", "mismatch_job", "next_round_job"):

            job = getattr(self, job_name, None)

            if job:

                try:
                    self.window.after_cancel(job)
                except tk.TclError:
                    pass

                setattr(self, job_name, None)

    def reset_scores(self):

        self.scores = [0, 0]
        self.round_number = 1
        self.starting_player = 0

        self.computer_memory = {}

        self.new_game()

    def change_mode(self, selected=None):

        self.starting_player = 0
        self.round_number = 1
        self.computer_memory = {}

        self.new_game()

    def change_difficulty(self, selected=None):

        self.round_number = 1
        self.computer_memory = {}

        self.new_game()

    # ========================================================
    # WINDOW CONTROLS
    # ========================================================

    def toggle_fullscreen(self, event=None):

        self.window.attributes(
            "-fullscreen",
            not self.window.attributes("-fullscreen")
        )

    def exit_fullscreen(self, event=None):

        self.window.attributes("-fullscreen", False)

    def return_to_menu(self):

        self.cancel_jobs()
        self.window.destroy()
        self.root.deiconify()


# ============================================================
# LAUNCHER CONNECTION
# ============================================================

def play(root):

    root.withdraw()

    try:

        MatchCards(root)

    except Exception as error:

        root.deiconify()

        messagebox.showerror(
            "Match Cards Error",
            str(error)
        )
