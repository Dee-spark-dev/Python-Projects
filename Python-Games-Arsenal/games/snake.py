import tkinter as tk
import random


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
FOOD_COLOR = "#ffcc45"

CELL_SIZE = 25
GRID_WIDTH = 28
GRID_HEIGHT = 20

START_SPEED = 130
MIN_SPEED = 55


# ============================================================
# SNAKE GAME
# ============================================================

class SnakeGame:

    def __init__(self, root):

        self.root = root

        self.window = tk.Toplevel(root)
        self.window.title("Snake")
        self.window.configure(bg=BG)
        self.window.geometry("950x750")
        self.window.minsize(650, 550)

        self.window.protocol("WM_DELETE_WINDOW", self.return_to_menu)

        self.running = False
        self.paused = False
        self.game_over = False

        self.score = 0
        self.high_score = 0
        self.level = 1

        self.direction = "Right"
        self.next_direction = "Right"

        self.snake = []
        self.food = None

        self.after_job = None

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
            text="SNAKE",
            font=("Arial", 25, "bold"),
            fg=CYAN,
            bg=BG
        ).pack(side="left")

        tk.Button(
            header,
            text="MAIN MENU",
            command=self.return_to_menu,
            bg=PURPLE,
            fg=WHITE,
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=15,
            pady=7
        ).pack(side="right")

        # Scoreboard
        scoreboard = tk.Frame(
            self.window,
            bg=PANEL
        )
        scoreboard.pack(fill="x", padx=15, pady=5)

        self.score_label = tk.Label(
            scoreboard,
            text="SCORE: 0",
            font=("Arial", 12, "bold"),
            fg=CYAN,
            bg=PANEL
        )
        self.score_label.pack(side="left", padx=20, pady=12)

        self.high_label = tk.Label(
            scoreboard,
            text="HIGH SCORE: 0",
            font=("Arial", 12, "bold"),
            fg=GREEN,
            bg=PANEL
        )
        self.high_label.pack(side="left", padx=20)

        self.level_label = tk.Label(
            scoreboard,
            text="LEVEL: 1",
            font=("Arial", 12, "bold"),
            fg=PURPLE,
            bg=PANEL
        )
        self.level_label.pack(side="right", padx=20)

        # Controls at bottom
        controls = tk.Frame(self.window, bg=BG)
        controls.pack(side="bottom", fill="x", pady=12)

        self.pause_button = tk.Button(
            controls,
            text="PAUSE",
            command=self.toggle_pause,
            bg=CYAN,
            fg="#10131f",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=18,
            pady=8
        )
        self.pause_button.pack(side="left", padx=15)

        tk.Button(
            controls,
            text="RESTART",
            command=self.new_game,
            bg=PURPLE,
            fg=WHITE,
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=18,
            pady=8
        ).pack(side="left", padx=5)

        self.status_label = tk.Label(
            controls,
            text="Use Arrow Keys or WASD",
            font=("Arial", 10, "bold"),
            fg=WHITE,
            bg=BG
        )
        self.status_label.pack(side="right", padx=15)

        # Game canvas
        self.canvas = tk.Canvas(
            self.window,
            bg="#080b14",
            highlightthickness=2,
            highlightbackground=PURPLE
        )
        self.canvas.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        self.canvas.bind("<Configure>", self.draw_game)

    # ========================================================
    # KEYBOARD CONTROLS
    # ========================================================

    def bind_controls(self):

        self.window.bind("<Up>", lambda e: self.change_direction("Up"))
        self.window.bind("<Down>", lambda e: self.change_direction("Down"))
        self.window.bind("<Left>", lambda e: self.change_direction("Left"))
        self.window.bind("<Right>", lambda e: self.change_direction("Right"))

        self.window.bind("w", lambda e: self.change_direction("Up"))
        self.window.bind("s", lambda e: self.change_direction("Down"))
        self.window.bind("a", lambda e: self.change_direction("Left"))
        self.window.bind("d", lambda e: self.change_direction("Right"))

        self.window.bind("W", lambda e: self.change_direction("Up"))
        self.window.bind("S", lambda e: self.change_direction("Down"))
        self.window.bind("A", lambda e: self.change_direction("Left"))
        self.window.bind("D", lambda e: self.change_direction("Right"))

        self.window.bind("<space>", lambda e: self.toggle_pause())
        self.window.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.window.bind("<Escape>", lambda e: self.exit_fullscreen())

    # ========================================================
    # START NEW GAME
    # ========================================================

    def new_game(self):

        self.cancel_loop()

        self.score = 0
        self.level = 1

        self.direction = "Right"
        self.next_direction = "Right"

        center_x = GRID_WIDTH // 2
        center_y = GRID_HEIGHT // 2

        self.snake = [
            (center_x, center_y),
            (center_x - 1, center_y),
            (center_x - 2, center_y)
        ]

        self.running = True
        self.paused = False
        self.game_over = False

        self.pause_button.config(text="PAUSE")
        self.status_label.config(text="Use Arrow Keys or WASD")

        self.create_food()
        self.update_scoreboard()
        self.draw_game()

        self.schedule_next_move()

        self.window.focus_set()

    # ========================================================
    # FOOD GENERATION
    # ========================================================

    def create_food(self):

        available = [
            (x, y)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x, y) not in self.snake
        ]

        if not available:
            self.win_game()
            return

        self.food = random.choice(available)

    # ========================================================
    # CHANGE DIRECTION
    # ========================================================

    def change_direction(self, new_direction):

        if self.game_over:
            return

        opposites = {
            "Up": "Down",
            "Down": "Up",
            "Left": "Right",
            "Right": "Left"
        }

        if new_direction == opposites[self.direction]:
            return

        self.next_direction = new_direction

    # ========================================================
    # GAME LOOP
    # ========================================================

    def schedule_next_move(self):

        if self.running and not self.paused and not self.game_over:
            speed = max(
                MIN_SPEED,
                START_SPEED - (self.level - 1) * 8
            )

            self.after_job = self.window.after(
                speed,
                self.move_snake
            )

    def move_snake(self):

        self.after_job = None

        if not self.running or self.paused or self.game_over:
            return

        self.direction = self.next_direction

        head_x, head_y = self.snake[0]

        # Calculate next position
        if self.direction == "Up":
            head_y -= 1

        elif self.direction == "Down":
            head_y += 1

        elif self.direction == "Left":
            head_x -= 1

        elif self.direction == "Right":
            head_x += 1

        new_head = (head_x, head_y)

        # Check wall collision
        if (
            head_x < 0 or
            head_x >= GRID_WIDTH or
            head_y < 0 or
            head_y >= GRID_HEIGHT
        ):
            self.end_game()
            return

        eating = new_head == self.food

        # Allow movement into the old tail position
        # if the snake is not growing.
        body = self.snake if eating else self.snake[:-1]

        if new_head in body:
            self.end_game()
            return

        self.snake.insert(0, new_head)

        # Eating food
        if eating:

            self.score += 10

            self.level = 1 + self.score // 100

            self.create_food()
            self.update_scoreboard()

            if self.game_over:
                return

        else:
            self.snake.pop()

        self.draw_game()
        self.schedule_next_move()

    # ========================================================
    # SCOREBOARD
    # ========================================================

    def update_scoreboard(self):

        if self.score > self.high_score:
            self.high_score = self.score

        self.score_label.config(
            text=f"SCORE: {self.score}"
        )

        self.high_label.config(
            text=f"HIGH SCORE: {self.high_score}"
        )

        self.level_label.config(
            text=f"LEVEL: {self.level}"
        )

    # ========================================================
    # DRAW GAME
    # ========================================================

    def draw_game(self, event=None):

        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        # Calculate responsive cell size
        cell = min(
            width / GRID_WIDTH,
            height / GRID_HEIGHT
        )

        board_width = cell * GRID_WIDTH
        board_height = cell * GRID_HEIGHT

        offset_x = (width - board_width) / 2
        offset_y = (height - board_height) / 2

        # Draw background grid
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):

                x1 = offset_x + x * cell
                y1 = offset_y + y * cell

                x2 = x1 + cell
                y2 = y1 + cell

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill="#0d1220",
                    outline="#171e30"
                )

        # Draw food
        if self.food:

            fx, fy = self.food

            x1 = offset_x + fx * cell
            y1 = offset_y + fy * cell

            self.canvas.create_oval(
                x1 + cell * 0.15,
                y1 + cell * 0.15,
                x1 + cell * 0.85,
                y1 + cell * 0.85,
                fill=FOOD_COLOR,
                outline=""
            )

        # Draw snake
        for index, (x, y) in enumerate(self.snake):

            x1 = offset_x + x * cell
            y1 = offset_y + y * cell

            x2 = x1 + cell
            y2 = y1 + cell

            color = CYAN if index == 0 else GREEN

            self.canvas.create_rectangle(
                x1 + 1,
                y1 + 1,
                x2 - 1,
                y2 - 1,
                fill=color,
                outline="#080b14",
                width=1
            )

            # Eyes on snake head
            if index == 0:

                eye_size = max(2, cell * 0.10)

                if self.direction in ("Right", "Left"):
                    eye_x = x1 + cell * (
                        0.72 if self.direction == "Right" else 0.28
                    )

                    for eye_y in (y1 + cell * 0.3, y1 + cell * 0.7):
                        self.canvas.create_oval(
                            eye_x - eye_size,
                            eye_y - eye_size,
                            eye_x + eye_size,
                            eye_y + eye_size,
                            fill="#10131f",
                            outline=""
                        )

                else:
                    eye_y = y1 + cell * (
                        0.28 if self.direction == "Up" else 0.72
                    )

                    for eye_x in (x1 + cell * 0.3, x1 + cell * 0.7):
                        self.canvas.create_oval(
                            eye_x - eye_size,
                            eye_y - eye_size,
                            eye_x + eye_size,
                            eye_y + eye_size,
                            fill="#10131f",
                            outline=""
                        )

        # Pause overlay
        if self.paused and not self.game_over:

            self.canvas.create_rectangle(
                0, 0, width, height,
                fill="#080b14",
                stipple="gray50",
                outline=""
            )

            self.canvas.create_text(
                width / 2,
                height / 2,
                text="PAUSED",
                fill=CYAN,
                font=("Arial", 35, "bold")
            )

        # Game over overlay
        if self.game_over:

            self.canvas.create_rectangle(
                0, 0, width, height,
                fill="#080b14",
                stipple="gray50",
                outline=""
            )

            self.canvas.create_text(
                width / 2,
                height / 2 - 30,
                text="GAME OVER",
                fill=RED,
                font=("Arial", 35, "bold")
            )

            self.canvas.create_text(
                width / 2,
                height / 2 + 20,
                text=f"Final Score: {self.score}",
                fill=WHITE,
                font=("Arial", 17, "bold")
            )

            self.canvas.create_text(
                width / 2,
                height / 2 + 55,
                text="Press RESTART to play again",
                fill=CYAN,
                font=("Arial", 12)
            )

    # ========================================================
    # PAUSE AND RESUME
    # ========================================================

    def toggle_pause(self):

        if self.game_over:
            return

        self.paused = not self.paused

        if self.paused:

            self.cancel_loop()
            self.pause_button.config(text="RESUME")
            self.status_label.config(text="Game paused")

        else:

            self.pause_button.config(text="PAUSE")
            self.status_label.config(text="Keep playing!")
            self.schedule_next_move()

        self.draw_game()

    # ========================================================
    # GAME OVER
    # ========================================================

    def end_game(self):

        self.game_over = True
        self.running = False

        self.cancel_loop()

        self.status_label.config(text="Game over!")
        self.pause_button.config(text="PAUSE")

        self.update_scoreboard()
        self.draw_game()

    # ========================================================
    # WIN CONDITION
    # ========================================================

    def win_game(self):

        self.game_over = True
        self.running = False

        self.cancel_loop()

        self.status_label.config(text="You filled the board!")

        self.draw_game()

    # ========================================================
    # CANCEL SCHEDULED MOVEMENT
    # ========================================================

    def cancel_loop(self):

        if self.after_job is not None:

            try:
                self.window.after_cancel(self.after_job)
            except tk.TclError:
                pass

            self.after_job = None

    # ========================================================
    # FULLSCREEN
    # ========================================================

    def toggle_fullscreen(self):

        current = self.window.attributes("-fullscreen")

        self.window.attributes("-fullscreen", not current)

    def exit_fullscreen(self):

        self.window.attributes("-fullscreen", False)

    # ========================================================
    # RETURN TO MAIN MENU
    # ========================================================

    def return_to_menu(self):

        self.cancel_loop()

        self.running = False

        self.window.destroy()

        self.root.deiconify()


# ============================================================
# LAUNCHER FUNCTION
# ============================================================

def play(root):

    root.withdraw()

    try:
        SnakeGame(root)

    except Exception as error:

        root.deiconify()

        tk.messagebox.showerror(
            "Snake Error",
            str(error)
        )