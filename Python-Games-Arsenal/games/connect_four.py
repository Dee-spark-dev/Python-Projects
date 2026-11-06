
import tkinter as tk
from tkinter import messagebox
import random
import math

# ============================================================
# CONNECT FOUR - PYTHON GAMES ARSENAL
# ============================================================

ROWS = 6
COLS = 7

EMPTY = 0
RED = 1
YELLOW = 2

BG = "#101522"
PANEL = "#1b2536"
BOARD = "#24344d"
RED_COLOR = "#ff5263"
YELLOW_COLOR = "#ffd166"
CYAN = "#00d9ff"
WHITE = "#f4f7ff"
MUTED = "#9aa9bd"


class ConnectFour:

    def __init__(self, root):

        self.root = root

        self.window = tk.Toplevel(root)
        self.window.title("Connect Four")
        self.window.geometry("850x720")
        self.window.minsize(600, 650)
        self.window.configure(bg=BG)
        self.window.protocol("WM_DELETE_WINDOW", self.return_to_menu)

        self.board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

        self.current_player = RED
        self.starting_player = RED

        self.game_over = False
        self.computer_thinking = False

        self.mode = tk.StringVar(value="Computer")
        self.difficulty = tk.StringVar(value="Medium")

        self.red_score = 0
        self.yellow_score = 0
        self.draw_score = 0

        self.history = []
        self.ai_job = None
        self.next_round_job = None
        self.last_result = None

        self.cell_size = 65
        self.board_x = 0
        self.board_y = 0

        self.build_interface()

        self.window.bind("<F11>", self.toggle_fullscreen)
        self.window.bind("<Escape>", self.exit_fullscreen)

        self.window.after(100, self.draw_board)

    # ========================================================
    # INTERFACE
    # ========================================================

    def build_interface(self):

        # Header
        header = tk.Frame(self.window, bg=BG)
        header.pack(fill="x", padx=10, pady=(10, 4))

        tk.Label(
            header,
            text="CONNECT FOUR",
            font=("Arial", 23, "bold"),
            fg=CYAN,
            bg=BG
        ).pack()

        tk.Label(
            header,
            text="Connect four pieces in a row to win!",
            font=("Arial", 9),
            fg=MUTED,
            bg=BG
        ).pack(pady=2)

        # Settings
        settings = tk.Frame(self.window, bg=PANEL)
        settings.pack(fill="x", padx=15, pady=5)

        tk.Label(
            settings,
            text="MODE",
            bg=PANEL,
            fg=WHITE,
            font=("Arial", 9, "bold")
        ).pack(side="left", padx=(10, 4), pady=8)

        mode_menu = tk.OptionMenu(
            settings,
            self.mode,
            "Computer",
            "Two Players",
            command=self.change_mode
        )

        mode_menu.config(
            bg="#26364c",
            fg=WHITE,
            highlightthickness=0,
            font=("Arial", 9)
        )
        mode_menu["menu"].config(bg=PANEL, fg=WHITE)
        mode_menu.pack(side="left", padx=3)

        tk.Label(
            settings,
            text="LEVEL",
            bg=PANEL,
            fg=WHITE,
            font=("Arial", 9, "bold")
        ).pack(side="left", padx=(12, 4))

        self.difficulty_menu = tk.OptionMenu(
            settings,
            self.difficulty,
            "Easy",
            "Medium",
            "Hard"
        )

        self.difficulty_menu.config(
            bg="#26364c",
            fg=WHITE,
            highlightthickness=0,
            font=("Arial", 9)
        )
        self.difficulty_menu["menu"].config(bg=PANEL, fg=WHITE)
        self.difficulty_menu.pack(side="left", padx=3)

        # Status
        self.status = tk.Label(
            self.window,
            text="RED'S TURN",
            font=("Arial", 13, "bold"),
            fg=RED_COLOR,
            bg=BG
        )
        self.status.pack(pady=4)

        # Score
        self.score_label = tk.Label(
            self.window,
            text="RED: 0     YELLOW: 0     DRAWS: 0",
            font=("Arial", 10, "bold"),
            fg=WHITE,
            bg=BG
        )
        self.score_label.pack(pady=3)

        # Board area - fixed logical aspect ratio
        self.canvas = tk.Canvas(
            self.window,
            bg=BG,
            highlightthickness=0,
            height=390
        )
        self.canvas.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5
        )

        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<Configure>", self.on_resize)

        # Controls are packed BEFORE any expanding widgets.
        # This keeps them visible even when the window is small.
        controls = tk.Frame(self.window, bg=BG)
        controls.pack(
            side="bottom",
            fill="x",
            padx=8,
            pady=(4, 12)
        )

        self.make_button(
            controls, "NEW GAME",
            self.new_game, CYAN
        ).pack(side="left", expand=True, fill="x", padx=3)

        self.make_button(
            controls, "UNDO",
            self.undo_move, "#a78bfa"
        ).pack(side="left", expand=True, fill="x", padx=3)

        self.make_button(
            controls, "RESET SCORES",
            self.reset_scores, "#52647c"
        ).pack(side="left", expand=True, fill="x", padx=3)

        self.make_button(
            controls, "MAIN MENU",
            self.return_to_menu, "#e05c70"
        ).pack(side="left", expand=True, fill="x", padx=3)

    def make_button(self, parent, text, command, color):

        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="#101522",
            activebackground=WHITE,
            activeforeground=BG,
            font=("Arial", 8, "bold"),
            relief="flat",
            padx=5,
            pady=10,
            cursor="hand2"
        )

    # ========================================================
    # RESPONSIVE BOARD
    # ========================================================

    def on_resize(self, event):

        if event.width < 100 or event.height < 100:
            return

        self.draw_board()

    def draw_board(self):

        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width < 100 or height < 100:
            return

        # Fit the entire board inside the available canvas.
        self.cell_size = min(
            (width - 20) / COLS,
            (height - 20) / ROWS
        )

        board_width = self.cell_size * COLS
        board_height = self.cell_size * ROWS

        self.board_x = (width - board_width) / 2
        self.board_y = (height - board_height) / 2

        self.canvas.create_rectangle(
            self.board_x,
            self.board_y,
            self.board_x + board_width,
            self.board_y + board_height,
            fill=BOARD,
            outline=CYAN,
            width=3
        )

        for row in range(ROWS):
            for col in range(COLS):

                x = self.board_x + col * self.cell_size
                y = self.board_y + row * self.cell_size

                padding = self.cell_size * 0.10

                color = BG

                if self.board[row][col] == RED:
                    color = RED_COLOR

                elif self.board[row][col] == YELLOW:
                    color = YELLOW_COLOR

                self.canvas.create_oval(
                    x + padding,
                    y + padding,
                    x + self.cell_size - padding,
                    y + self.cell_size - padding,
                    fill=color,
                    outline="#34445b",
                    width=2
                )

        # Column numbers
        for col in range(COLS):

            x = self.board_x + (col + 0.5) * self.cell_size

            self.canvas.create_text(
                x,
                max(5, self.board_y - 10),
                text=str(col + 1),
                fill=MUTED,
                font=("Arial", 9, "bold")
            )

    # ========================================================
    # GAME LOGIC
    # ========================================================

    def get_valid_columns(self, board=None):

        if board is None:
            board = self.board

        return [
            col for col in range(COLS)
            if board[0][col] == EMPTY
        ]

    def get_next_open_row(self, board, col):

        for row in range(ROWS - 1, -1, -1):

            if board[row][col] == EMPTY:
                return row

        return None

    def drop_piece(self, board, row, col, piece):

        board[row][col] = piece

    def winning_move(self, board, piece):

        # Horizontal
        for row in range(ROWS):
            for col in range(COLS - 3):

                if all(board[row][col + i] == piece for i in range(4)):
                    return True

        # Vertical
        for row in range(ROWS - 3):
            for col in range(COLS):

                if all(board[row + i][col] == piece for i in range(4)):
                    return True

        # Positive diagonal
        for row in range(ROWS - 3):
            for col in range(COLS - 3):

                if all(board[row + i][col + i] == piece for i in range(4)):
                    return True

        # Negative diagonal
        for row in range(3, ROWS):
            for col in range(COLS - 3):

                if all(board[row - i][col + i] == piece for i in range(4)):
                    return True

        return False

    def update_status(self):

        if self.current_player == RED:
            self.status.config(text="RED'S TURN", fg=RED_COLOR)
        else:
            self.status.config(text="YELLOW'S TURN", fg=YELLOW_COLOR)

    def update_scores(self):

        self.score_label.config(
            text=f"RED: {self.red_score}     "
                 f"YELLOW: {self.yellow_score}     "
                 f"DRAWS: {self.draw_score}"
        )

    # ========================================================
    # PLAYER MOVEMENT
    # ========================================================

    def handle_click(self, event):

        if self.game_over or self.computer_thinking:
            return

        if self.mode.get() == "Computer" and self.current_player == YELLOW:
            return

        col = int((event.x - self.board_x) / self.cell_size)

        if col < 0 or col >= COLS:
            return

        self.play_column(col)

    def play_column(self, col):

        if self.game_over or col not in self.get_valid_columns():
            return

        row = self.get_next_open_row(self.board, col)

        self.history.append([
            [r[:] for r in self.board],
            self.current_player
        ])

        self.drop_piece(self.board, row, col, self.current_player)
        self.draw_board()

        if self.winning_move(self.board, self.current_player):
            self.finish_game(self.current_player)
            return

        if not self.get_valid_columns():
            self.finish_game(EMPTY)
            return

        self.current_player = YELLOW if self.current_player == RED else RED
        self.update_status()

        if self.mode.get() == "Computer" and self.current_player == YELLOW:

            self.computer_thinking = True
            self.status.config(text="COMPUTER THINKING...", fg=CYAN)

            self.ai_job = self.window.after(500, self.computer_move)

    # ========================================================
    # COMPUTER AI
    # ========================================================

    def computer_move(self):

        if self.game_over:
            return

        valid = self.get_valid_columns()

        if not valid:
            return

        difficulty = self.difficulty.get()

        if difficulty == "Easy":
            col = random.choice(valid)

        elif difficulty == "Medium":

            col = self.find_winning_move(self.board, YELLOW)

            if col is None:
                col = self.find_winning_move(self.board, RED)

            if col is None:
                col = self.best_move(self.board, 3)

        else:
            col = self.best_move(self.board, 5)

        self.computer_thinking = False
        self.ai_job = None

        self.play_column(col)

    def find_winning_move(self, board, piece):

        for col in self.get_valid_columns(board):

            temp = [r[:] for r in board]
            row = self.get_next_open_row(temp, col)

            self.drop_piece(temp, row, col, piece)

            if self.winning_move(temp, piece):
                return col

        return None

    def evaluate_window(self, window, piece):

        opponent = RED if piece == YELLOW else YELLOW
        score = 0

        if window.count(piece) == 4:
            score += 100

        elif window.count(piece) == 3 and window.count(EMPTY) == 1:
            score += 8

        elif window.count(piece) == 2 and window.count(EMPTY) == 2:
            score += 3

        if window.count(opponent) == 3 and window.count(EMPTY) == 1:
            score -= 10

        return score

    def score_position(self, board, piece):

        score = 0

        center = [board[r][COLS // 2] for r in range(ROWS)]
        score += center.count(piece) * 6

        for r in range(ROWS):
            for c in range(COLS - 3):
                score += self.evaluate_window(board[r][c:c + 4], piece)

        for c in range(COLS):
            for r in range(ROWS - 3):
                window = [board[r + i][c] for i in range(4)]
                score += self.evaluate_window(window, piece)

        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                window = [board[r + i][c + i] for i in range(4)]
                score += self.evaluate_window(window, piece)

        for r in range(3, ROWS):
            for c in range(COLS - 3):
                window = [board[r - i][c + i] for i in range(4)]
                score += self.evaluate_window(window, piece)

        return score

    def minimax(self, board, depth, alpha, beta, maximizing):

        valid = self.get_valid_columns(board)

        terminal = (
            self.winning_move(board, RED)
            or self.winning_move(board, YELLOW)
            or not valid
        )

        if depth == 0 or terminal:

            if self.winning_move(board, YELLOW):
                return None, 100000 + depth

            if self.winning_move(board, RED):
                return None, -100000 - depth

            if not valid:
                return None, 0

            return None, self.score_position(board, YELLOW)

        valid = sorted(valid, key=lambda c: abs(c - COLS // 2))

        if maximizing:

            value = -math.inf
            best_col = random.choice(valid)

            for col in valid:

                temp = [r[:] for r in board]
                row = self.get_next_open_row(temp, col)
                self.drop_piece(temp, row, col, YELLOW)

                score = self.minimax(
                    temp, depth - 1, alpha, beta, False
                )[1]

                if score > value:
                    value = score
                    best_col = col

                alpha = max(alpha, value)

                if alpha >= beta:
                    break

            return best_col, value

        else:

            value = math.inf
            best_col = random.choice(valid)

            for col in valid:

                temp = [r[:] for r in board]
                row = self.get_next_open_row(temp, col)
                self.drop_piece(temp, row, col, RED)

                score = self.minimax(
                    temp, depth - 1, alpha, beta, True
                )[1]

                if score < value:
                    value = score
                    best_col = col

                beta = min(beta, value)

                if alpha >= beta:
                    break

            return best_col, value

    def best_move(self, board, depth):

        col, _ = self.minimax(
            board, depth,
            -math.inf, math.inf, True
        )

        return col

    # ========================================================
    # RESULTS AND AUTOMATIC NEXT ROUND
    # ========================================================

    def finish_game(self, winner):

        self.game_over = True
        self.computer_thinking = False
        self.last_result = winner

        if self.ai_job:
            self.window.after_cancel(self.ai_job)
            self.ai_job = None

        if winner == RED:

            self.red_score += 1
            message = "RED WINS!"

        elif winner == YELLOW:

            self.yellow_score += 1
            message = (
                "COMPUTER WINS!"
                if self.mode.get() == "Computer"
                else "YELLOW WINS!"
            )

        else:

            self.draw_score += 1
            message = "IT'S A DRAW!"

        self.status.config(
            text=message + " NEXT ROUND IN 2 SECONDS...",
            fg=CYAN if winner == EMPTY else (
                RED_COLOR if winner == RED else YELLOW_COLOR
            )
        )

        self.update_scores()

        self.next_round_job = self.window.after(
            2000, self.start_next_round
        )

    def start_next_round(self):

        self.next_round_job = None

        self.starting_player = (
            YELLOW if self.starting_player == RED else RED
        )

        self.new_game()

    # ========================================================
    # UNDO
    # ========================================================

    def undo_move(self):

        if not self.history:
            return

        if self.ai_job:
            self.window.after_cancel(self.ai_job)
            self.ai_job = None

        if self.next_round_job:
            self.window.after_cancel(self.next_round_job)
            self.next_round_job = None

        if self.game_over and self.last_result is not None:

            if self.last_result == RED:
                self.red_score -= 1
            elif self.last_result == YELLOW:
                self.yellow_score -= 1
            else:
                self.draw_score -= 1

            self.update_scores()

        self.last_result = None
        self.game_over = False
        self.computer_thinking = False

        steps = 1

        if self.mode.get() == "Computer" and len(self.history) >= 2:
            steps = 2

        for _ in range(min(steps, len(self.history))):
            self.board, self.current_player = self.history.pop()

        self.update_status()
        self.draw_board()

    # ========================================================
    # RESTART AND SETTINGS
    # ========================================================

    def new_game(self):

        if self.ai_job:
            self.window.after_cancel(self.ai_job)
            self.ai_job = None

        if self.next_round_job:
            self.window.after_cancel(self.next_round_job)
            self.next_round_job = None

        self.board = [
            [EMPTY for _ in range(COLS)]
            for _ in range(ROWS)
        ]

        self.current_player = self.starting_player
        self.game_over = False
        self.computer_thinking = False
        self.last_result = None

        self.history.clear()

        self.update_status()
        self.draw_board()

        if (
            self.mode.get() == "Computer"
            and self.current_player == YELLOW
        ):

            self.computer_thinking = True
            self.status.config(text="COMPUTER THINKING...", fg=CYAN)

            self.ai_job = self.window.after(
                500, self.computer_move
            )

    def reset_scores(self):

        self.red_score = 0
        self.yellow_score = 0
        self.draw_score = 0

        self.starting_player = RED

        self.update_scores()
        self.new_game()

    def change_mode(self, selected=None):

        self.difficulty_menu.config(
            state="normal" if self.mode.get() == "Computer" else "disabled"
        )

        self.starting_player = RED
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

        if self.ai_job:
            self.window.after_cancel(self.ai_job)

        if self.next_round_job:
            self.window.after_cancel(self.next_round_job)

        self.window.destroy()
        self.root.deiconify()


# ============================================================
# LAUNCHER CONNECTION
# ============================================================

def play(root):

    root.withdraw()

    try:
        ConnectFour(root)

    except Exception as error:

        root.deiconify()

        messagebox.showerror(
            "Connect Four Error",
            str(error)
        )
