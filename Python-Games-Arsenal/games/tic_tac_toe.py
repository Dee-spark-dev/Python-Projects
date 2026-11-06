
import tkinter as tk
from tkinter import ttk
import random

# ==================================================
# 1. GAME CONFIGURATION
# ==================================================

BG_COLOR = "#151525"
PANEL_COLOR = "#252542"
CYAN = "#00e5ff"
PURPLE = "#8e44ad"
WHITE = "#ffffff"
X_COLOR = "#00e5ff"
O_COLOR = "#ff79c6"

# ==================================================
# 2. GAME WINDOW
# ==================================================

def play(root):

    game = tk.Toplevel(root)
    game.title("Tic-Tac-Toe")
    game.geometry("850x750")
    game.minsize(500, 550)
    game.configure(bg=BG_COLOR)

    # Fullscreen state
    is_fullscreen = False

    def toggle_fullscreen(event=None):
        nonlocal is_fullscreen
        is_fullscreen = not is_fullscreen
        game.attributes("-fullscreen", is_fullscreen)

    def exit_fullscreen(event=None):
        nonlocal is_fullscreen
        is_fullscreen = False
        game.attributes("-fullscreen", False)

    game.bind("<F11>", toggle_fullscreen)
    game.bind("<Escape>", exit_fullscreen)

    # ==================================================
    # 3. GAME VARIABLES
    # ==================================================

    board = [""] * 9

    current_player = "X"
    starting_player = "X"

    scores = {
        "X": 0,
        "O": 0,
        "Draw": 0
    }

    game_over = False
    computer_thinking = False
    restart_timer = None

    mode = tk.StringVar(value="Player vs Computer")
    difficulty = tk.StringVar(value="Hard")

    # ==================================================
    # 4. GAME LOGIC
    # ==================================================

    WINNING_COMBINATIONS = [
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6)
    ]

    def check_winner(position_board):
        """Check whether X or O has won."""

        for a, b, c in WINNING_COMBINATIONS:

            if (
                position_board[a]
                and position_board[a] == position_board[b]
                and position_board[a] == position_board[c]
            ):
                return position_board[a]

        return None

    def available_moves(position_board):
        """Return all empty board positions."""

        return [
            index
            for index, value in enumerate(position_board)
            if value == ""
        ]

    # ==================================================
    # 5. COMPUTER INTELLIGENCE
    # ==================================================

    def minimax(position_board, maximizing):
        """Use the Minimax algorithm for unbeatable AI."""

        winner = check_winner(position_board)

        if winner == "O":
            return 10

        if winner == "X":
            return -10

        if not available_moves(position_board):
            return 0

        if maximizing:

            best_score = -float("inf")

            for move in available_moves(position_board):

                position_board[move] = "O"

                score = minimax(position_board, False)

                position_board[move] = ""

                best_score = max(best_score, score)

            return best_score

        else:

            best_score = float("inf")

            for move in available_moves(position_board):

                position_board[move] = "X"

                score = minimax(position_board, True)

                position_board[move] = ""

                best_score = min(best_score, score)

            return best_score

    def computer_choice():
        """Choose a move based on the selected difficulty."""

        moves = available_moves(board)

        if not moves:
            return None

        # Easy: Choose a random available position
        if difficulty.get() == "Easy":
            return random.choice(moves)

        # Medium: Win immediately or block the player
        if difficulty.get() == "Medium":

            for move in moves:

                board[move] = "O"

                if check_winner(board) == "O":
                    board[move] = ""
                    return move

                board[move] = ""

            for move in moves:

                board[move] = "X"

                if check_winner(board) == "X":
                    board[move] = ""
                    return move

                board[move] = ""

            return random.choice(moves)

        # Hard: Use Minimax
        best_score = -float("inf")
        best_move = None

        for move in moves:

            board[move] = "O"

            score = minimax(board, False)

            board[move] = ""

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    # ==================================================
    # 6. MAIN GAME FUNCTIONS
    # ==================================================

    def update_scoreboard():
        """Refresh the scoreboard."""

        score_x.config(text=f"PLAYER X: {scores['X']}")
        score_o.config(text=f"PLAYER O: {scores['O']}")
        score_draw.config(text=f"DRAWS: {scores['Draw']}")

    def update_board():
        """Update the appearance of every board button."""

        for index, button in enumerate(board_buttons):

            value = board[index]

            button.config(text=value)

            if value == "X":
                button.config(fg=X_COLOR)

            elif value == "O":
                button.config(fg=O_COLOR)

            else:
                button.config(fg=WHITE)

    def update_status(message=None):
        """Display the current game status."""

        if message:
            status_label.config(text=message)
            return

        if mode.get() == "Player vs Computer":

            if current_player == "X":
                status_label.config(text="YOUR TURN — X")
            else:
                status_label.config(text="COMPUTER'S TURN — O")

        else:
            status_label.config(
                text=f"PLAYER {current_player}'S TURN"
            )

    def finish_round(result):
        """End a round and schedule the next one."""

        nonlocal game_over, restart_timer

        game_over = True

        if result == "Draw":

            scores["Draw"] += 1
            update_status("IT'S A DRAW!")

        else:

            scores[result] += 1

            if mode.get() == "Player vs Computer":

                if result == "X":
                    update_status("YOU WIN! 🎉")
                else:
                    update_status("COMPUTER WINS!")

            else:
                update_status(f"PLAYER {result} WINS! 🎉")

        update_scoreboard()

        # Automatically begin the next round after 2 seconds
        status_label.config(
            fg=CYAN
        )

        restart_timer = game.after(
            2000,
            next_round
        )

    def make_move(index):
        """Place the current player's symbol."""

        nonlocal current_player

        if game_over:
            return

        if board[index] != "":
            return

        if computer_thinking:
            return

        board[index] = current_player

        update_board()

        winner = check_winner(board)

        if winner:
            finish_round(winner)
            return

        if not available_moves(board):
            finish_round("Draw")
            return

        current_player = "O" if current_player == "X" else "X"

        update_status()

        # Let the computer play when it is O's turn
        if (
            mode.get() == "Player vs Computer"
            and current_player == "O"
        ):
            schedule_computer_move()

    # ==================================================
    # 7. COMPUTER TURN
    # ==================================================

    def schedule_computer_move():
        """Schedule the computer's move."""

        nonlocal computer_thinking

        if game_over:
            return

        computer_thinking = True

        update_status("COMPUTER IS THINKING...")

        game.after(500, computer_move)

    def computer_move():
        """Execute the computer's selected move."""

        nonlocal computer_thinking, current_player

        if game_over:
            computer_thinking = False
            return

        move = computer_choice()

        computer_thinking = False

        if move is None:
            return

        board[move] = "O"

        update_board()

        winner = check_winner(board)

        if winner:
            finish_round(winner)
            return

        if not available_moves(board):
            finish_round("Draw")
            return

        current_player = "X"

        update_status()

    # ==================================================
    # 8. ROUND MANAGEMENT
    # ==================================================

    def start_round():
        """Clear the board and start a new round."""

        nonlocal board, current_player
        nonlocal game_over, computer_thinking

        board = [""] * 9

        current_player = starting_player

        game_over = False
        computer_thinking = False

        update_board()
        update_status()

        # Computer starts if O is the starting player
        if (
            mode.get() == "Player vs Computer"
            and current_player == "O"
        ):
            schedule_computer_move()

    def next_round():
        """Alternate the starting player and begin again."""

        nonlocal starting_player, restart_timer

        restart_timer = None

        starting_player = (
            "O" if starting_player == "X" else "X"
        )

        start_round()

    def restart_game():
        """Restart the current round without clearing scores."""

        nonlocal restart_timer

        if restart_timer is not None:
            game.after_cancel(restart_timer)
            restart_timer = None

        start_round()

    def reset_scores():
        """Clear all scores and restart the game."""

        if restart_timer is not None:
            game.after_cancel(restart_timer)

        restart_timer = None

        for player in scores:
            scores[player] = 0

        update_scoreboard()
        start_round()

    def settings_changed(event=None):
        """Restart the board when game settings change."""

        if restart_timer is not None:
            game.after_cancel(restart_timer)

        restart_game()

    # ==================================================
    # 9. RESPONSIVE WINDOW LAYOUT
    # ==================================================

    game.grid_columnconfigure(0, weight=1)
    game.grid_rowconfigure(2, weight=1)

    # Top navigation
    top_frame = tk.Frame(
        game,
        bg=BG_COLOR
    )
    top_frame.grid(
        row=0,
        column=0,
        sticky="ew",
        padx=15,
        pady=10
    )

    top_frame.grid_columnconfigure(1, weight=1)

    menu_button = tk.Button(
        top_frame,
        text="MAIN MENU",
        font=("Arial", 10, "bold"),
        bg=PURPLE,
        fg=WHITE,
        relief="flat",
        cursor="hand2",
        command=game.destroy
    )
    menu_button.grid(row=0, column=0, padx=5)

    fullscreen_button = tk.Button(
        top_frame,
        text="FULLSCREEN (F11)",
        font=("Arial", 10, "bold"),
        bg=PANEL_COLOR,
        fg=WHITE,
        relief="flat",
        cursor="hand2",
        command=toggle_fullscreen
    )
    fullscreen_button.grid(row=0, column=2, padx=5)

    # Game title
    title = tk.Label(
        game,
        text="TIC-TAC-TOE",
        font=("Arial", 26, "bold"),
        fg=CYAN,
        bg=BG_COLOR
    )
    title.grid(row=1, column=0, pady=10)

    # ==================================================
    # 10. GAME BOARD
    # ==================================================

    board_frame = tk.Frame(
        game,
        bg=BG_COLOR
    )
    board_frame.grid(
        row=2,
        column=0,
        sticky="nsew",
        padx=25,
        pady=10
    )

    # Three equally sized rows and columns
    for index in range(3):
        board_frame.grid_rowconfigure(index, weight=1)
        board_frame.grid_columnconfigure(index, weight=1)

    board_buttons = []

    for index in range(9):

        row = index // 3
        column = index % 3

        button = tk.Button(
            board_frame,
            text="",
            font=("Arial", 40, "bold"),
            bg=PANEL_COLOR,
            fg=WHITE,
            activebackground="#35355c",
            relief="flat",
            cursor="hand2",
            command=lambda i=index: make_move(i)
        )

        button.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=5,
            pady=5
        )

        board_buttons.append(button)

    def resize_board(event):
        """Adjust symbol sizes as the board changes size."""

        if event.widget != board_frame:
            return

        cell_size = min(
            event.width // 3,
            event.height // 3
        )

        font_size = max(
            18,
            min(75, int(cell_size * 0.45))
        )

        for button in board_buttons:
            button.config(
                font=("Arial", font_size, "bold")
            )

    board_frame.bind("<Configure>", resize_board)

    # ==================================================
    # 11. STATUS AND SCOREBOARD
    # ==================================================

    status_label = tk.Label(
        game,
        text="PLAYER X'S TURN",
        font=("Arial", 16, "bold"),
        fg=CYAN,
        bg=BG_COLOR
    )
    status_label.grid(row=3, column=0, pady=10)

    score_frame = tk.Frame(
        game,
        bg=BG_COLOR
    )
    score_frame.grid(
        row=4,
        column=0,
        sticky="ew",
        padx=20,
        pady=5
    )

    score_frame.grid_columnconfigure(
        (0, 1, 2),
        weight=1
    )

    score_x = tk.Label(
        score_frame,
        text="PLAYER X: 0",
        font=("Arial", 12, "bold"),
        fg=X_COLOR,
        bg=BG_COLOR
    )
    score_x.grid(row=0, column=0)

    score_o = tk.Label(
        score_frame,
        text="PLAYER O: 0",
        font=("Arial", 12, "bold"),
        fg=O_COLOR,
        bg=BG_COLOR
    )
    score_o.grid(row=0, column=1)

    score_draw = tk.Label(
        score_frame,
        text="DRAWS: 0",
        font=("Arial", 12, "bold"),
        fg=WHITE,
        bg=BG_COLOR
    )
    score_draw.grid(row=0, column=2)

    # ==================================================
    # 12. GAME SETTINGS
    # ==================================================

    settings_frame = tk.Frame(
        game,
        bg=BG_COLOR
    )
    settings_frame.grid(
        row=5,
        column=0,
        pady=12
    )

    mode_label = tk.Label(
        settings_frame,
        text="GAME MODE:",
        font=("Arial", 10, "bold"),
        fg=WHITE,
        bg=BG_COLOR
    )
    mode_label.grid(row=0, column=0, padx=5)

    mode_menu = ttk.Combobox(
        settings_frame,
        textvariable=mode,
        values=[
            "Player vs Computer",
            "Player vs Player"
        ],
        state="readonly",
        width=20
    )
    mode_menu.grid(row=0, column=1, padx=5)
    mode_menu.bind("<<ComboboxSelected>>", settings_changed)

    difficulty_label = tk.Label(
        settings_frame,
        text="DIFFICULTY:",
        font=("Arial", 10, "bold"),
        fg=WHITE,
        bg=BG_COLOR
    )
    difficulty_label.grid(row=0, column=2, padx=5)

    difficulty_menu = ttk.Combobox(
        settings_frame,
        textvariable=difficulty,
        values=["Easy", "Medium", "Hard"],
        state="readonly",
        width=10
    )
    difficulty_menu.grid(row=0, column=3, padx=5)
    difficulty_menu.bind(
        "<<ComboboxSelected>>",
        settings_changed
    )

    # ==================================================
    # 13. GAME CONTROLS
    # ==================================================

    controls_frame = tk.Frame(
        game,
        bg=BG_COLOR
    )
    controls_frame.grid(
        row=6,
        column=0,
        pady=10
    )

    restart_button = tk.Button(
        controls_frame,
        text="RESTART ROUND",
        font=("Arial", 10, "bold"),
        bg=CYAN,
        fg="black",
        relief="flat",
        cursor="hand2",
        command=restart_game
    )
    restart_button.grid(row=0, column=0, padx=8)

    reset_button = tk.Button(
        controls_frame,
        text="RESET SCORES",
        font=("Arial", 10, "bold"),
        bg="#b83232",
        fg=WHITE,
        relief="flat",
        cursor="hand2",
        command=reset_scores
    )
    reset_button.grid(row=0, column=1, padx=8)

    # ==================================================
    # 14. CLEANUP
    # ==================================================

    def close_game():
        """Cancel pending callbacks when closing the game."""

        nonlocal restart_timer

        if restart_timer is not None:
            game.after_cancel(restart_timer)
            restart_timer = None

        game.destroy()

    game.protocol("WM_DELETE_WINDOW", close_game)

    # ==================================================
    # 15. START THE GAME
    # ==================================================

    update_scoreboard()
    start_round()
