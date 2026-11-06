
import tkinter as tk
from tkinter import ttk, messagebox
import random

try:
    import chess
except ImportError:
    raise ImportError(
        "Install python-chess:\n"
        "py -3.14 -m pip install python-chess"
    )


# ============================================================
# THEME
# ============================================================

BG = "#10131C"
PANEL = "#191E2B"
PANEL_LIGHT = "#222A3A"
CYAN = "#00D9FF"
PURPLE = "#9B5DE5"
WHITE = "#F0F0F0"
MUTED = "#AAB2C5"

LIGHT_SQUARE = "#D9DDE8"
DARK_SQUARE = "#59647D"
SELECTED = "#00B8D9"
LEGAL_MOVE = "#65D6A6"
LAST_MOVE = "#E8C547"

PIECE_SYMBOLS = {
    "K": "♔", "Q": "♕", "R": "♖",
    "B": "♗", "N": "♘", "P": "♙",
    "k": "♚", "q": "♛", "r": "♜",
    "b": "♝", "n": "♞", "p": "♟"
}


# ============================================================
# CHESS GAME
# ============================================================

class ChessGame:

    def __init__(self, root):

        self.root = root
        self.window = tk.Toplevel(root)

        self.window.title("Python Games Arsenal - Chess")
        self.window.configure(bg=BG)
        self.window.geometry("1050x760")
        self.window.minsize(750, 600)

        self.board = chess.Board()

        self.mode = tk.StringVar(value="Computer")
        self.difficulty = tk.StringVar(value="Medium")
        self.color_choice = tk.StringVar(value="White")

        self.player_color = chess.WHITE

        self.selected_square = None
        self.legal_moves = []
        self.last_move = None

        self.flipped = False
        self.ai_running = False
        self.game_over = False

        self.white_score = 0
        self.black_score = 0
        self.draw_score = 0

        self.move_history = []

        self.result_recorded = False
        self.last_result = None

        self.ai_job = None

        self.window.protocol(
            "WM_DELETE_WINDOW",
            self.return_to_menu
        )

        self.create_interface()

        self.window.bind("<F11>", self.toggle_fullscreen)
        self.window.bind("<Escape>", self.exit_fullscreen)

        self.draw_board()
        self.update_status()

    # ========================================================
    # INTERFACE
    # ========================================================

    def create_interface(self):

        header = tk.Frame(self.window, bg=BG)
        header.pack(fill="x", padx=15, pady=12)

        tk.Label(
            header,
            text="♔  CHESS",
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
            pady=8
        ).pack(side="right")

        content = tk.Frame(self.window, bg=BG)
        content.pack(fill="both", expand=True, padx=15, pady=5)

        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)

        # Board area
        board_frame = tk.Frame(content, bg=BG)

        board_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 15)
        )

        board_frame.rowconfigure(0, weight=1)
        board_frame.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            board_frame,
            bg=BG,
            highlightthickness=0
        )

        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.canvas.bind("<Configure>", self.draw_board)
        self.canvas.bind("<Button-1>", self.handle_click)

        # Side panel
        side = tk.Frame(
            content,
            bg=PANEL,
            padx=12,
            pady=12
        )

        side.grid(row=0, column=1, sticky="nsew")

        # IMPORTANT:
        # Controls are packed BEFORE move history.
        # This keeps Undo visible when the window is resized.

        tk.Label(
            side,
            text="GAME SETTINGS",
            font=("Arial", 14, "bold"),
            fg=CYAN,
            bg=PANEL
        ).pack(anchor="w", pady=(0, 8))

        # Game mode
        tk.Label(
            side,
            text="Game Mode",
            fg=MUTED,
            bg=PANEL
        ).pack(anchor="w")

        self.mode_box = ttk.Combobox(
            side,
            textvariable=self.mode,
            values=["Computer", "Two Players"],
            state="readonly"
        )

        self.mode_box.pack(fill="x", pady=4)
        self.mode_box.bind(
            "<<ComboboxSelected>>",
            self.change_mode
        )

        # Difficulty
        tk.Label(
            side,
            text="Computer Difficulty",
            fg=MUTED,
            bg=PANEL
        ).pack(anchor="w", pady=(6, 0))

        self.difficulty_box = ttk.Combobox(
            side,
            textvariable=self.difficulty,
            values=["Easy", "Medium", "Hard"],
            state="readonly"
        )

        self.difficulty_box.pack(fill="x", pady=4)

        # Player colour
        tk.Label(
            side,
            text="Play As",
            fg=MUTED,
            bg=PANEL
        ).pack(anchor="w", pady=(6, 0))

        self.color_box = ttk.Combobox(
            side,
            textvariable=self.color_choice,
            values=["White", "Black"],
            state="readonly"
        )

        self.color_box.pack(fill="x", pady=4)

        # Status
        tk.Label(
            side,
            text="GAME STATUS",
            font=("Arial", 11, "bold"),
            fg=CYAN,
            bg=PANEL
        ).pack(anchor="w", pady=(10, 3))

        self.status_label = tk.Label(
            side,
            text="White to move",
            font=("Arial", 11, "bold"),
            fg=WHITE,
            bg=PANEL,
            wraplength=230
        )

        self.status_label.pack(anchor="w", pady=3)

        # Scoreboard
        tk.Label(
            side,
            text="SCOREBOARD",
            font=("Arial", 11, "bold"),
            fg=CYAN,
            bg=PANEL
        ).pack(anchor="w", pady=(10, 3))

        self.score_label = tk.Label(
            side,
            text="White: 0 | Black: 0 | Draws: 0",
            fg=WHITE,
            bg=PANEL,
            font=("Arial", 9)
        )

        self.score_label.pack(anchor="w", pady=3)

        # ====================================================
        # ALWAYS-VISIBLE GAME CONTROLS
        # ====================================================

        controls = tk.Frame(side, bg=PANEL)
        controls.pack(fill="x", pady=(10, 5))

        self.make_button(
            controls,
            "UNDO MOVE",
            self.undo_move,
            PURPLE
        ).pack(fill="x", pady=3)

        self.make_button(
            controls,
            "NEW GAME",
            self.new_game,
            CYAN
        ).pack(fill="x", pady=3)

        self.make_button(
            controls,
            "FLIP BOARD",
            self.flip_board,
            PANEL_LIGHT
        ).pack(fill="x", pady=3)

        self.make_button(
            controls,
            "RESET SCORES",
            self.reset_scores,
            PANEL_LIGHT
        ).pack(fill="x", pady=3)

        # ====================================================
        # MOVE HISTORY
        # ====================================================

        tk.Label(
            side,
            text="MOVE HISTORY",
            font=("Arial", 11, "bold"),
            fg=CYAN,
            bg=PANEL
        ).pack(anchor="w", pady=(10, 4))

        history_frame = tk.Frame(side, bg=PANEL)
        history_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(history_frame)
        scrollbar.pack(side="right", fill="y")

        self.history_box = tk.Listbox(
            history_frame,
            bg=BG,
            fg=WHITE,
            selectbackground=PURPLE,
            font=("Consolas", 9),
            yscrollcommand=scrollbar.set
        )

        self.history_box.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.config(command=self.history_box.yview)

    # ========================================================
    # BUTTON HELPER
    # ========================================================

    def make_button(self, parent, text, command, color):

        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=BG if color == CYAN else WHITE,
            activebackground=CYAN,
            activeforeground=BG,
            relief="flat",
            font=("Arial", 10, "bold"),
            pady=7,
            cursor="hand2"
        )

    # ========================================================
    # BOARD DRAWING
    # ========================================================

    def draw_board(self, event=None):

        if not self.canvas.winfo_exists():
            return

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        size = min(width, height) - 20

        if size <= 0:
            return

        self.square_size = size / 8

        self.board_x = (width - size) / 2
        self.board_y = (height - size) / 2

        self.canvas.delete("all")

        for row in range(8):
            for col in range(8):

                x1 = self.board_x + col * self.square_size
                y1 = self.board_y + row * self.square_size

                x2 = x1 + self.square_size
                y2 = y1 + self.square_size

                square = self.display_to_square(row, col)

                color = (
                    LIGHT_SQUARE
                    if (row + col) % 2 == 0
                    else DARK_SQUARE
                )

                if self.last_move and square in (
                    self.last_move.from_square,
                    self.last_move.to_square
                ):
                    color = LAST_MOVE

                if square == self.selected_square:
                    color = SELECTED

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline=""
                )

                # Legal move indicators
                if square in self.legal_moves:

                    piece = self.board.piece_at(square)

                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2

                    if piece:

                        self.canvas.create_oval(
                            x1 + 5, y1 + 5,
                            x2 - 5, y2 - 5,
                            outline=LEGAL_MOVE,
                            width=4
                        )

                    else:

                        radius = self.square_size * 0.12

                        self.canvas.create_oval(
                            cx - radius,
                            cy - radius,
                            cx + radius,
                            cy + radius,
                            fill=LEGAL_MOVE,
                            outline=""
                        )

                # Chess pieces
                piece = self.board.piece_at(square)

                if piece:

                    symbol = PIECE_SYMBOLS[piece.symbol()]

                    self.canvas.create_text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        text=symbol,
                        font=(
                            "DejaVu Sans",
                            max(12, int(self.square_size * 0.72))
                        ),
                        fill=(
                            "#FFFFFF"
                            if piece.color == chess.WHITE
                            else "#171717"
                        )
                    )

    # ========================================================
    # BOARD COORDINATES
    # ========================================================

    def display_to_square(self, row, col):

        if self.flipped:
            row = 7 - row
            col = 7 - col

        return chess.square(col, 7 - row)

    # ========================================================
    # PAWN PROMOTION
    # ========================================================

    def choose_promotion(self, color):

        choice = {"piece": None}

        dialog = tk.Toplevel(self.window)
        dialog.title("Pawn Promotion")
        dialog.configure(bg=PANEL)
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="CHOOSE YOUR PROMOTION",
            font=("Arial", 14, "bold"),
            fg=CYAN,
            bg=PANEL
        ).pack(padx=20, pady=(18, 8))

        tk.Label(
            dialog,
            text="Your pawn reached the final rank!",
            font=("Arial", 10),
            fg=MUTED,
            bg=PANEL
        ).pack(padx=15, pady=5)

        options = tk.Frame(dialog, bg=PANEL)
        options.pack(padx=15, pady=15)

        pieces = [
            ("Queen", chess.QUEEN, "Q"),
            ("Rook", chess.ROOK, "R"),
            ("Bishop", chess.BISHOP, "B"),
            ("Knight", chess.KNIGHT, "N")
        ]

        for name, piece_type, symbol in pieces:

            symbol = (
                symbol if color == chess.WHITE
                else symbol.lower()
            )

            tk.Button(
                options,
                text=PIECE_SYMBOLS[symbol] + "\n" + name,
                font=("Arial", 15, "bold"),
                bg=PANEL_LIGHT,
                fg=WHITE,
                activebackground=CYAN,
                activeforeground=BG,
                relief="flat",
                width=7,
                height=3,
                cursor="hand2",
                command=lambda p=piece_type: (
                    choice.update({"piece": p}),
                    dialog.destroy()
                )
            ).pack(side="left", padx=4)

        dialog.protocol(
            "WM_DELETE_WINDOW",
            dialog.destroy
        )

        self.window.wait_window(dialog)

        return choice["piece"]

    # ========================================================
    # PLAYER INPUT
    # ========================================================

    def handle_click(self, event):

        if self.game_over or self.ai_running:
            return

        if self.mode.get() == "Computer":
            if self.board.turn != self.player_color:
                return

        if not hasattr(self, "square_size"):
            return

        col = int(
            (event.x - self.board_x) / self.square_size
        )

        row = int(
            (event.y - self.board_y) / self.square_size
        )

        if not (0 <= row < 8 and 0 <= col < 8):
            return

        square = self.display_to_square(row, col)
        piece = self.board.piece_at(square)

        # Select a piece
        if self.selected_square is None:

            if piece and piece.color == self.board.turn:

                self.selected_square = square

                self.legal_moves = [
                    move.to_square
                    for move in self.board.legal_moves
                    if move.from_square == square
                ]

                self.draw_board()

            return

        # Select another friendly piece
        if piece and piece.color == self.board.turn:

            self.selected_square = square

            self.legal_moves = [
                move.to_square
                for move in self.board.legal_moves
                if move.from_square == square
            ]

            self.draw_board()
            return

        selected_piece = self.board.piece_at(
            self.selected_square
        )

        if selected_piece is None:
            self.selected_square = None
            self.legal_moves = []
            self.draw_board()
            return

        move = chess.Move(
            self.selected_square,
            square
        )

        # Promotion
        if (
            selected_piece.piece_type == chess.PAWN
            and chess.square_rank(square) in (0, 7)
        ):

            promotion_moves = [
                m for m in self.board.legal_moves
                if (
                    m.from_square == self.selected_square
                    and m.to_square == square
                    and m.promotion is not None
                )
            ]

            if promotion_moves:

                promotion = self.choose_promotion(
                    selected_piece.color
                )

                if promotion is None:
                    self.selected_square = None
                    self.legal_moves = []
                    self.draw_board()
                    return

                move = chess.Move(
                    self.selected_square,
                    square,
                    promotion=promotion
                )

        if move in self.board.legal_moves:
            self.make_move(move)

        else:
            self.selected_square = None
            self.legal_moves = []
            self.draw_board()

    # ========================================================
    # MAKE MOVE
    # ========================================================

    def make_move(self, move):

        if move not in self.board.legal_moves:
            return

        self.board.push(move)

        self.last_move = move

        self.selected_square = None
        self.legal_moves = []

        self.move_history.append(move)

        self.rebuild_history()
        self.draw_board()
        self.update_status()

        if self.board.is_game_over():
            self.finish_game()
            return

        if (
            self.mode.get() == "Computer"
            and self.board.turn != self.player_color
        ):
            self.schedule_computer_move()

    # ========================================================
    # COMPUTER AI
    # ========================================================

    def schedule_computer_move(self):

        self.cancel_computer_move()

        self.ai_job = self.window.after(
            300,
            self.computer_move
        )

    def cancel_computer_move(self):

        if self.ai_job is not None:

            try:
                self.window.after_cancel(self.ai_job)
            except tk.TclError:
                pass

            self.ai_job = None

    def computer_move(self):

        self.ai_job = None

        if self.game_over or self.board.is_game_over():
            return

        if self.mode.get() != "Computer":
            return

        if self.board.turn == self.player_color:
            return

        self.ai_running = True

        self.status_label.config(
            text="Computer is thinking..."
        )

        self.window.update_idletasks()

        try:

            depth = {
                "Easy": 1,
                "Medium": 2,
                "Hard": 3
            }.get(self.difficulty.get(), 2)

            move = self.find_best_move(depth)

            if move:
                self.make_move(move)

        except Exception as error:

            messagebox.showerror(
                "Chess AI Error",
                str(error),
                parent=self.window
            )

        finally:

            self.ai_running = False

            if not self.game_over:
                self.update_status()

    # ========================================================
    # AI SEARCH
    # ========================================================

    def find_best_move(self, depth):

        moves = list(self.board.legal_moves)

        if not moves:
            return None

        random.shuffle(moves)

        best_move = None
        best_score = float("-inf")

        maximizing_color = self.board.turn

        for move in moves:

            self.board.push(move)

            score = self.minimax(
                depth - 1,
                float("-inf"),
                float("inf"),
                maximizing_color
            )

            self.board.pop()

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def minimax(self, depth, alpha, beta, maximizing_color):

        if depth == 0 or self.board.is_game_over():
            return self.evaluate_board(maximizing_color)

        maximizing = self.board.turn == maximizing_color

        moves = list(self.board.legal_moves)

        if maximizing:

            best_score = float("-inf")

            for move in moves:

                self.board.push(move)

                score = self.minimax(
                    depth - 1,
                    alpha,
                    beta,
                    maximizing_color
                )

                self.board.pop()

                best_score = max(best_score, score)
                alpha = max(alpha, best_score)

                if beta <= alpha:
                    break

            return best_score

        else:

            best_score = float("inf")

            for move in moves:

                self.board.push(move)

                score = self.minimax(
                    depth - 1,
                    alpha,
                    beta,
                    maximizing_color
                )

                self.board.pop()

                best_score = min(best_score, score)
                beta = min(beta, best_score)

                if beta <= alpha:
                    break

            return best_score

    # ========================================================
    # BOARD EVALUATION
    # ========================================================

    def evaluate_board(self, color):

        if self.board.is_checkmate():
            return (
                -100000
                if self.board.turn == color
                else 100000
            )

        if self.board.is_game_over():
            return 0

        values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }

        score = 0

        for square, piece in self.board.piece_map().items():

            value = values[piece.piece_type]

            file = chess.square_file(square)
            rank = chess.square_rank(square)

            centre_bonus = (
                3 - abs(3.5 - file)
                + 3 - abs(3.5 - rank)
            ) * 5

            value += centre_bonus

            if piece.color == color:
                score += value
            else:
                score -= value

        return score

    # ========================================================
    # MOVE HISTORY
    # ========================================================

    def rebuild_history(self):

        self.history_box.delete(0, "end")

        temp_board = chess.Board()

        for move in self.move_history:

            notation = temp_board.san(move)

            if temp_board.turn == chess.WHITE:

                line = (
                    f"{temp_board.fullmove_number}. "
                    f"{notation}"
                )

                self.history_box.insert("end", line)

            else:

                last = self.history_box.size() - 1

                if last >= 0:

                    previous = self.history_box.get(last)

                    self.history_box.delete(last)

                    self.history_box.insert(
                        "end",
                        previous + "    " + notation
                    )

            temp_board.push(move)

        self.history_box.see("end")

    # ========================================================
    # UNDO MOVE
    # ========================================================

    def undo_move(self):

        if not self.move_history:
            return

        self.cancel_computer_move()
        self.ai_running = False

        # Reverse score if the previous game ended.
        if self.result_recorded:

            if self.last_result == chess.WHITE:
                self.white_score = max(
                    0, self.white_score - 1
                )

            elif self.last_result == chess.BLACK:
                self.black_score = max(
                    0, self.black_score - 1
                )

            else:
                self.draw_score = max(
                    0, self.draw_score - 1
                )

            self.result_recorded = False
            self.last_result = None

        self.game_over = False

        if self.mode.get() == "Computer":

            # If it is the player's turn, the computer
            # has already moved. Undo both moves.
            if self.board.turn == self.player_color:
                moves_to_undo = 2

            # If it is the computer's turn, it has not
            # moved yet. Undo only the player's move.
            else:
                moves_to_undo = 1

        else:
            moves_to_undo = 1

        for _ in range(moves_to_undo):

            if self.board.move_stack:

                self.board.pop()
                self.move_history.pop()

        self.last_move = (
            self.board.peek()
            if self.board.move_stack
            else None
        )

        self.selected_square = None
        self.legal_moves = []

        self.rebuild_history()
        self.draw_board()
        self.update_status()

    # ========================================================
    # GAME STATUS
    # ========================================================

    def update_status(self):

        self.score_label.config(
            text=(
                f"White: {self.white_score} | "
                f"Black: {self.black_score} | "
                f"Draws: {self.draw_score}"
            )
        )

        if self.game_over:
            return

        status = (
            "CHECK! "
            if self.board.is_check()
            else ""
        )

        status += (
            "White to move"
            if self.board.turn == chess.WHITE
            else "Black to move"
        )

        self.status_label.config(text=status)

    def finish_game(self):

        self.game_over = True

        outcome = self.board.outcome()

        if outcome is None:
            return

        if outcome.winner == chess.WHITE:

            self.white_score += 1
            result = "White wins!"
            self.last_result = chess.WHITE

        elif outcome.winner == chess.BLACK:

            self.black_score += 1
            result = "Black wins!"
            self.last_result = chess.BLACK

        else:

            self.draw_score += 1
            result = "Game drawn!"
            self.last_result = None

        self.result_recorded = True

        self.update_status()
        self.status_label.config(text=result)

        messagebox.showinfo(
            "Game Over",
            result,
            parent=self.window
        )

    # ========================================================
    # NEW GAME
    # ========================================================

    def new_game(self):

        self.cancel_computer_move()

        self.board.reset()

        self.selected_square = None
        self.legal_moves = []
        self.last_move = None

        self.game_over = False
        self.ai_running = False

        self.move_history.clear()

        self.result_recorded = False
        self.last_result = None

        self.history_box.delete(0, "end")

        self.player_color = (
            chess.WHITE
            if self.color_choice.get() == "White"
            else chess.BLACK
        )

        self.draw_board()
        self.update_status()

        if (
            self.mode.get() == "Computer"
            and self.player_color == chess.BLACK
        ):
            self.schedule_computer_move()

    # ========================================================
    # OTHER CONTROLS
    # ========================================================

    def flip_board(self):

        self.flipped = not self.flipped
        self.draw_board()

    def reset_scores(self):

        self.white_score = 0
        self.black_score = 0
        self.draw_score = 0

        self.update_status()

    def change_mode(self, event=None):

        computer_mode = self.mode.get() == "Computer"

        self.difficulty_box.config(
            state="readonly" if computer_mode else "disabled"
        )

        self.color_box.config(
            state="readonly" if computer_mode else "disabled"
        )

        self.new_game()

    # ========================================================
    # WINDOW CONTROLS
    # ========================================================

    def toggle_fullscreen(self, event=None):

        current = self.window.attributes("-fullscreen")

        self.window.attributes(
            "-fullscreen",
            not current
        )

    def exit_fullscreen(self, event=None):

        self.window.attributes("-fullscreen", False)

    def return_to_menu(self):

        self.cancel_computer_move()
        self.ai_running = False

        self.window.destroy()

        self.root.deiconify()
        self.root.lift()


# ============================================================
# LAUNCHER ENTRY POINT
# ============================================================

def play(root):

    try:

        # Create Chess before hiding the launcher.
        game = ChessGame(root)

        root.withdraw()

        return game

    except Exception as error:

        root.deiconify()
        root.lift()

        messagebox.showerror(
            "Chess Startup Error",
            f"Chess could not start:\n\n{error}",
            parent=root
        )
