
import tkinter as tk
from tkinter import messagebox
import random
import math

# ==========================================================
# CHECKERS - PYTHON GAMES ARSENAL
# ==========================================================

BG = "#10131f"
PANEL = "#191e2e"
CYAN = "#00d9ff"
PURPLE = "#9b5de5"
WHITE = "#f5f5f5"
RED = "#e74c3c"
BLACK = "#252b3b"
LIGHT = "#d8d8d8"
DARK = "#454b60"
GREEN = "#00e676"
GOLD = "#ffd166"


class CheckersGame:

    def __init__(self, root):

        self.root = root
        self.window = tk.Toplevel(root)
        self.window.title("Checkers")
        self.window.geometry("850x750")
        self.window.minsize(600, 600)
        self.window.configure(bg=BG)
        self.window.protocol("WM_DELETE_WINDOW", self.close_game)

        self.fullscreen = False
        self.window.bind("<F11>", self.toggle_fullscreen)
        self.window.bind("<Escape>", self.exit_fullscreen)

        self.mode = tk.StringVar(value="Computer")
        self.difficulty = tk.StringVar(value="Hard")

        self.scores = {"Red": 0, "Black": 0, "Draws": 0}

        self.board = []
        self.current_player = "Red"
        self.selected_piece = None
        self.valid_moves = []
        self.forced_piece = None

        self.game_over = False
        self.ai_job = None

        self.create_interface()
        self.new_game()

    # ======================================================
    # INTERFACE
    # ======================================================

    def create_interface(self):

        header = tk.Frame(self.window, bg=BG)
        header.pack(fill="x", padx=15, pady=10)

        tk.Label(
            header,
            text="CHECKERS",
            font=("Arial", 24, "bold"),
            fg=CYAN,
            bg=BG
        ).pack(side="left")

        tk.Button(
            header,
            text="MAIN MENU",
            command=self.close_game,
            bg=PURPLE,
            fg=WHITE,
            relief="flat",
            padx=12,
            pady=7
        ).pack(side="right")

        settings = tk.Frame(self.window, bg=PANEL)
        settings.pack(fill="x", padx=15, pady=5)

        tk.Label(
            settings,
            text="MODE:",
            bg=PANEL,
            fg=WHITE
        ).pack(side="left", padx=8)

        tk.OptionMenu(
            settings,
            self.mode,
            "Computer",
            "2 Players",
            command=lambda _: self.new_game()
        ).pack(side="left", padx=5, pady=8)

        tk.Label(
            settings,
            text="DIFFICULTY:",
            bg=PANEL,
            fg=WHITE
        ).pack(side="left", padx=8)

        tk.OptionMenu(
            settings,
            self.difficulty,
            "Easy",
            "Hard"
        ).pack(side="left", padx=5)

        self.score_label = tk.Label(
            self.window,
            text="",
            font=("Arial", 13, "bold"),
            bg=BG,
            fg=WHITE
        )
        self.score_label.pack(pady=8)

        self.turn_label = tk.Label(
            self.window,
            text="",
            font=("Arial", 14, "bold"),
            bg=BG,
            fg=CYAN
        )
        self.turn_label.pack(pady=5)

        self.canvas = tk.Canvas(
            self.window,
            bg=BG,
            highlightthickness=0
        )
        self.canvas.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind(
            "<Configure>",
            lambda event: self.draw_board()
        )

        controls = tk.Frame(self.window, bg=BG)
        controls.pack(fill="x", padx=15, pady=12)

        tk.Button(
            controls,
            text="NEW GAME",
            command=self.new_game,
            bg=CYAN,
            fg=BG,
            relief="flat",
            padx=15,
            pady=8
        ).pack(side="left", padx=5)

        tk.Button(
            controls,
            text="RESET SCORES",
            command=self.reset_scores,
            bg=PURPLE,
            fg=WHITE,
            relief="flat",
            padx=15,
            pady=8
        ).pack(side="right", padx=5)

    # ======================================================
    # GAME SETUP
    # ======================================================

    def cancel_ai(self):

        if self.ai_job is not None:
            try:
                self.window.after_cancel(self.ai_job)
            except tk.TclError:
                pass

        self.ai_job = None

    def new_game(self):

        self.cancel_ai()

        self.board = [[None for _ in range(8)] for _ in range(8)]

        # Black pieces
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:
                    self.board[row][col] = "B"

        # Red pieces
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    self.board[row][col] = "R"

        self.current_player = "Red"
        self.selected_piece = None
        self.valid_moves = []
        self.forced_piece = None
        self.game_over = False

        self.update_labels()
        self.draw_board()

    def reset_scores(self):

        self.scores = {
            "Red": 0,
            "Black": 0,
            "Draws": 0
        }

        self.new_game()

    # ======================================================
    # BOARD DRAWING
    # ======================================================

    def draw_board(self):

        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width < 10 or height < 10:
            return

        self.board_size = min(width, height) * 0.95
        self.square_size = self.board_size / 8

        self.board_x = (width - self.board_size) / 2
        self.board_y = (height - self.board_size) / 2

        for row in range(8):
            for col in range(8):

                x1 = self.board_x + col * self.square_size
                y1 = self.board_y + row * self.square_size

                color = DARK if (row + col) % 2 else LIGHT

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x1 + self.square_size,
                    y1 + self.square_size,
                    fill=color,
                    outline=""
                )

                piece = self.board[row][col]

                if piece:
                    self.draw_piece(row, col, piece)

        if self.selected_piece:

            row, col = self.selected_piece
            self.highlight_square(row, col, GOLD)

        for row, col in self.valid_moves:

            x = self.board_x + (col + 0.5) * self.square_size
            y = self.board_y + (row + 0.5) * self.square_size

            radius = self.square_size * 0.13

            self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=GREEN,
                outline=""
            )

    def draw_piece(self, row, col, piece):

        x = self.board_x + (col + 0.5) * self.square_size
        y = self.board_y + (row + 0.5) * self.square_size

        radius = self.square_size * 0.37

        color = RED if piece.upper() == "R" else BLACK

        self.canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill=color,
            outline=WHITE,
            width=2
        )

        if piece.islower():

            self.canvas.create_text(
                x,
                y,
                text="♛",
                fill=GOLD,
                font=("Arial", int(self.square_size * 0.35), "bold")
            )

    def highlight_square(self, row, col, color):

        x1 = self.board_x + col * self.square_size
        y1 = self.board_y + row * self.square_size

        self.canvas.create_rectangle(
            x1,
            y1,
            x1 + self.square_size,
            y1 + self.square_size,
            outline=color,
            width=4
        )

    # ======================================================
    # PIECE MOVEMENT RULES
    # ======================================================

    def belongs_to(self, piece, player):

        if piece is None:
            return False

        return piece.upper() == ("R" if player == "Red" else "B")

    def get_directions(self, piece):

        # Kings move in all four diagonal directions.
        if piece.islower():
            return [
                (-1, -1),
                (-1, 1),
                (1, -1),
                (1, 1)
            ]

        # Red men move upwards.
        if piece == "R":
            return [(-1, -1), (-1, 1)]

        # Black men move downwards.
        return [(1, -1), (1, 1)]

    def get_piece_moves(self, board, row, col):

        piece = board[row][col]

        if piece is None:
            return []

        player = "Red" if piece.upper() == "R" else "Black"

        normal_moves = []
        capture_moves = []

        for dr, dc in self.get_directions(piece):

            r = row + dr
            c = col + dc

            if not (0 <= r < 8 and 0 <= c < 8):
                continue

            target = board[r][c]

            # Normal move
            if target is None:
                normal_moves.append((r, c))

            # Capture
            elif not self.belongs_to(target, player):

                jump_r = r + dr
                jump_c = c + dc

                if (
                    0 <= jump_r < 8
                    and 0 <= jump_c < 8
                    and board[jump_r][jump_c] is None
                ):
                    capture_moves.append((jump_r, jump_c))

        return capture_moves if capture_moves else normal_moves

    def get_all_moves(self, board, player):

        normal_moves = []
        capture_moves = []

        for row in range(8):
            for col in range(8):

                piece = board[row][col]

                if not self.belongs_to(piece, player):
                    continue

                for destination in self.get_piece_moves(
                    board, row, col
                ):

                    move = ((row, col), destination)

                    if abs(destination[0] - row) == 2:
                        capture_moves.append(move)
                    else:
                        normal_moves.append(move)

        # Captures are compulsory.
        return capture_moves if capture_moves else normal_moves

    # ======================================================
    # APPLY A MOVE
    # ======================================================

    def make_move(self, board, start, end):

        new_board = [row[:] for row in board]

        r1, c1 = start
        r2, c2 = end

        piece = new_board[r1][c1]
        new_board[r1][c1] = None

        captured = abs(r2 - r1) == 2
        promoted = False

        if captured:

            middle_r = (r1 + r2) // 2
            middle_c = (c1 + c2) // 2

            new_board[middle_r][middle_c] = None

        # King promotion
        if piece == "R" and r2 == 0:
            piece = "r"
            promoted = True

        elif piece == "B" and r2 == 7:
            piece = "b"
            promoted = True

        new_board[r2][c2] = piece

        return new_board, captured, promoted

    # ======================================================
    # COMPLETE CAPTURE SEQUENCES
    # ======================================================

    def capture_sequences(self, board, current, path):

        row, col = current

        piece = board[row][col]

        # A newly crowned king ends its turn.
        if piece is None:
            return [(board, path)]

        moves = self.get_piece_moves(board, row, col)

        captures = [
            move for move in moves
            if abs(move[0] - row) == 2
        ]

        if not captures:
            return [(board, path)]

        results = []

        for destination in captures:

            new_board, captured, promoted = self.make_move(
                board, current, destination
            )

            if promoted:

                results.append((new_board, path + [destination]))
                continue

            continuations = self.capture_sequences(
                new_board,
                destination,
                path + [destination]
            )

            results.extend(continuations)

        return results

    def get_turn_options(self, board, player):

        moves = self.get_all_moves(board, player)

        if not moves:
            return []

        options = []

        for start, end in moves:

            new_board, captured, promoted = self.make_move(
                board, start, end
            )

            if captured and not promoted:

                sequences = self.capture_sequences(
                    new_board,
                    end,
                    [end]
                )

                for final_board, path in sequences:

                    options.append(
                        (start, path, final_board)
                    )

            else:

                options.append(
                    (start, [end], new_board)
                )

        return options

    # ======================================================
    # HUMAN PLAYER INPUT
    # ======================================================

    def handle_click(self, event):

        if self.game_over:
            return

        if (
            self.mode.get() == "Computer"
            and self.current_player == "Black"
        ):
            return

        if not hasattr(self, "square_size"):
            return

        if self.square_size <= 0:
            return

        col = int((event.x - self.board_x) / self.square_size)
        row = int((event.y - self.board_y) / self.square_size)

        if not (0 <= row < 8 and 0 <= col < 8):
            return

        if self.selected_piece:

            if (row, col) in self.valid_moves:

                self.complete_move(
                    self.selected_piece,
                    (row, col)
                )
                return

        piece = self.board[row][col]

        if self.belongs_to(piece, self.current_player):

            if self.forced_piece and self.forced_piece != (row, col):
                return

            all_moves = self.get_all_moves(
                self.board,
                self.current_player
            )

            self.selected_piece = (row, col)

            self.valid_moves = [
                destination
                for start, destination in all_moves
                if start == (row, col)
            ]

        else:

            self.selected_piece = None
            self.valid_moves = []

        self.draw_board()

    # ======================================================
    # COMPLETE HUMAN MOVE
    # ======================================================

    def complete_move(self, start, end):

        new_board, captured, promoted = self.make_move(
            self.board, start, end
        )

        self.board = new_board

        row, col = end

        if captured and not promoted:

            moves = self.get_piece_moves(
                self.board, row, col
            )

            captures = [
                move for move in moves
                if abs(move[0] - row) == 2
            ]

            if captures:

                self.selected_piece = (row, col)
                self.valid_moves = captures
                self.forced_piece = (row, col)

                self.draw_board()
                return

        self.selected_piece = None
        self.valid_moves = []
        self.forced_piece = None

        self.finish_turn()

    # ======================================================
    # TURN MANAGEMENT
    # ======================================================

    def finish_turn(self):

        self.current_player = (
            "Black" if self.current_player == "Red" else "Red"
        )

        self.update_labels()
        self.draw_board()

        if self.check_game_over():
            return

        self.schedule_computer()

    # ======================================================
    # COMPUTER OPPONENT
    # ======================================================

    def schedule_computer(self):

        if (
            self.mode.get() == "Computer"
            and self.current_player == "Black"
            and not self.game_over
        ):

            self.cancel_ai()

            self.ai_job = self.window.after(
                350,
                self.computer_move
            )

    def computer_move(self):

        self.ai_job = None

        if self.game_over or self.current_player != "Black":
            return

        options = self.get_turn_options(
            self.board,
            "Black"
        )

        if not options:
            self.check_game_over()
            return

        if self.difficulty.get() == "Easy":

            start, path, final_board = random.choice(options)

        else:

            best_score = -math.inf
            best_options = []

            for start, path, final_board in options:

                score = self.minimax(
                    final_board,
                    3,
                    False,
                    -math.inf,
                    math.inf
                )

                if score > best_score:

                    best_score = score
                    best_options = [(start, path)]

                elif score == best_score:

                    best_options.append((start, path))

            start, path = random.choice(best_options)

        self.animate_ai_move(start, path, 0)

    def animate_ai_move(self, start, path, index):

        if self.game_over or self.current_player != "Black":
            return

        if index >= len(path):

            self.selected_piece = None
            self.valid_moves = []
            self.forced_piece = None

            self.finish_turn()
            return

        destination = path[index]

        self.board, captured, promoted = self.make_move(
            self.board,
            start,
            destination
        )

        self.draw_board()

        self.ai_job = self.window.after(
            180,
            lambda: self.animate_ai_move(
                destination,
                path,
                index + 1
            )
        )

    # ======================================================
    # MINIMAX AI WITH ALPHA-BETA PRUNING
    # ======================================================

    def evaluate_board(self, board):

        score = 0

        for row in range(8):
            for col in range(8):

                piece = board[row][col]

                if piece is None:
                    continue

                value = 5 if piece.islower() else 3

                if piece == "B":
                    score += value + row * 0.1

                elif piece == "R":
                    score -= value + (7 - row) * 0.1

                elif piece == "b":
                    score += value

                elif piece == "r":
                    score -= value

        return score

    def minimax(self, board, depth, maximizing, alpha, beta):

        if depth == 0:
            return self.evaluate_board(board)

        player = "Black" if maximizing else "Red"

        options = self.get_turn_options(board, player)

        if not options:
            return -1000 if maximizing else 1000

        if maximizing:

            best = -math.inf

            for start, path, final_board in options:

                score = self.minimax(
                    final_board,
                    depth - 1,
                    False,
                    alpha,
                    beta
                )

                best = max(best, score)
                alpha = max(alpha, best)

                if beta <= alpha:
                    break

            return best

        else:

            best = math.inf

            for start, path, final_board in options:

                score = self.minimax(
                    final_board,
                    depth - 1,
                    True,
                    alpha,
                    beta
                )

                best = min(best, score)
                beta = min(beta, best)

                if beta <= alpha:
                    break

            return best

    # ======================================================
    # GAME OVER
    # ======================================================

    def check_game_over(self):

        red_pieces = sum(
            1 for row in self.board
            for piece in row
            if self.belongs_to(piece, "Red")
        )

        black_pieces = sum(
            1 for row in self.board
            for piece in row
            if self.belongs_to(piece, "Black")
        )

        red_moves = self.get_all_moves(self.board, "Red")
        black_moves = self.get_all_moves(self.board, "Black")

        winner = None

        if red_pieces == 0 or not red_moves:
            winner = "Black"

        elif black_pieces == 0 or not black_moves:
            winner = "Red"

        if winner:

            self.game_over = True
            self.scores[winner] += 1
            self.update_labels()

            messagebox.showinfo(
                "Game Over",
                f"{winner} wins!",
                parent=self.window
            )

            return True

        return False

    # ======================================================
    # SCOREBOARD AND TURN LABEL
    # ======================================================

    def update_labels(self):

        self.score_label.config(
            text=(
                f"RED: {self.scores['Red']}     "
                f"BLACK: {self.scores['Black']}     "
                f"DRAWS: {self.scores['Draws']}"
            )
        )

        if self.mode.get() == "Computer":

            turn = (
                "YOUR TURN (RED)"
                if self.current_player == "Red"
                else "COMPUTER THINKING..."
            )

        else:

            turn = f"{self.current_player.upper()}'S TURN"

        self.turn_label.config(text=turn)

    # ======================================================
    # WINDOW CONTROLS
    # ======================================================

    def toggle_fullscreen(self, event=None):

        self.fullscreen = not self.fullscreen

        self.window.attributes(
            "-fullscreen",
            self.fullscreen
        )

    def exit_fullscreen(self, event=None):

        self.fullscreen = False
        self.window.attributes("-fullscreen", False)

    def close_game(self):

        self.cancel_ai()
        self.window.destroy()


# ==========================================================
# MAIN LAUNCHER CONNECTION
# ==========================================================

def play(root):
    CheckersGame(root)
