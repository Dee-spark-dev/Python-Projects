
import tkinter as tk
import random
import math

# ==========================================================
# BRICK BREAKER - PYTHON GAMES ARSENAL
# ==========================================================

BG = "#10131f"
PANEL = "#191e2e"
CYAN = "#00d9ff"
PURPLE = "#9b5de5"
WHITE = "#f5f5f5"
RED = "#e74c3c"
GREEN = "#00e676"
GOLD = "#ffd166"

GAME_WIDTH = 800
GAME_HEIGHT = 600


class BrickBreaker:

    def __init__(self, root):

        self.root = root
        self.window = tk.Toplevel(root)

        self.window.title("Brick Breaker")
        self.window.geometry("900x750")
        self.window.minsize(650, 600)
        self.window.configure(bg=BG)
        self.window.protocol("WM_DELETE_WINDOW", self.close_game)

        # Fullscreen controls
        self.fullscreen = False
        self.window.bind("<F11>", self.toggle_fullscreen)
        self.window.bind("<Escape>", self.exit_fullscreen)

        # Game state
        self.score = 0
        self.lives = 3
        self.level = 1
        self.high_score = 0

        self.running = False
        self.paused = False
        self.game_over = False

        self.game_job = None
        self.keys = set()

        # Game objects
        self.ball = {
            "x": 400,
            "y": 450,
            "radius": 9,
            "dx": 4,
            "dy": -4
        }

        self.paddle = {
            "x": 400,
            "y": 550,
            "width": 110,
            "height": 14,
            "speed": 8
        }

        self.bricks = []

        # Display scaling
        self.scale = 1
        self.offset_x = 0
        self.offset_y = 0

        self.create_interface()
        self.create_level()
        self.draw_game()

    # ======================================================
    # INTERFACE
    # ======================================================

    def create_interface(self):

        header = tk.Frame(self.window, bg=BG)
        header.pack(fill="x", padx=15, pady=10)

        tk.Label(
            header,
            text="BRICK BREAKER",
            font=("Arial", 23, "bold"),
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

        # Scoreboard
        scoreboard = tk.Frame(self.window, bg=PANEL)
        scoreboard.pack(fill="x", padx=15, pady=5)

        self.score_label = tk.Label(
            scoreboard,
            text="SCORE: 0",
            font=("Arial", 12, "bold"),
            fg=CYAN,
            bg=PANEL
        )
        self.score_label.pack(side="left", padx=15, pady=10)

        self.lives_label = tk.Label(
            scoreboard,
            text="LIVES: 3",
            font=("Arial", 12, "bold"),
            fg=RED,
            bg=PANEL
        )
        self.lives_label.pack(side="left", padx=15)

        self.level_label = tk.Label(
            scoreboard,
            text="LEVEL: 1",
            font=("Arial", 12, "bold"),
            fg=GOLD,
            bg=PANEL
        )
        self.level_label.pack(side="left", padx=15)

        self.high_label = tk.Label(
            scoreboard,
            text="BEST: 0",
            font=("Arial", 12, "bold"),
            fg=GREEN,
            bg=PANEL
        )
        self.high_label.pack(side="right", padx=15)

        # Game canvas
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

        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Motion>", self.mouse_move)
        self.canvas.bind("<Button-1>", self.canvas_click)

        # Keyboard controls
        self.window.bind("<KeyPress-Left>", self.key_down)
        self.window.bind("<KeyRelease-Left>", self.key_up)
        self.window.bind("<KeyPress-Right>", self.key_down)
        self.window.bind("<KeyRelease-Right>", self.key_up)

        self.window.bind("<KeyPress-a>", self.key_down)
        self.window.bind("<KeyRelease-a>", self.key_up)
        self.window.bind("<KeyPress-d>", self.key_down)
        self.window.bind("<KeyRelease-d>", self.key_up)

        self.window.bind("<space>", self.toggle_pause)
        self.window.bind("<Return>", self.start_or_restart)

        # Bottom controls
        controls = tk.Frame(self.window, bg=BG)
        controls.pack(fill="x", padx=15, pady=10)

        tk.Button(
            controls,
            text="START / RESUME",
            command=self.start_game,
            bg=CYAN,
            fg=BG,
            relief="flat",
            padx=15,
            pady=8
        ).pack(side="left", padx=5)

        tk.Button(
            controls,
            text="PAUSE",
            command=self.toggle_pause,
            bg=PURPLE,
            fg=WHITE,
            relief="flat",
            padx=15,
            pady=8
        ).pack(side="left", padx=5)

        tk.Button(
            controls,
            text="RESTART",
            command=self.restart_game,
            bg=RED,
            fg=WHITE,
            relief="flat",
            padx=15,
            pady=8
        ).pack(side="right", padx=5)

    # ======================================================
    # LEVEL GENERATION
    # ======================================================

    def create_level(self):

        self.bricks = []

        rows = min(4 + self.level, 8)
        cols = 10

        brick_width = 68
        brick_height = 23
        gap = 8

        total_width = cols * brick_width + (cols - 1) * gap
        start_x = (GAME_WIDTH - total_width) / 2

        colors = [
            "#e74c3c",
            "#ff8c42",
            "#ffd166",
            "#06d6a0",
            "#00d9ff",
            "#9b5de5",
            "#e056fd",
            "#f78fb3"
        ]

        for row in range(rows):

            for col in range(cols):

                x = start_x + col * (brick_width + gap)
                y = 55 + row * (brick_height + gap)

                self.bricks.append({
                    "x": x,
                    "y": y,
                    "width": brick_width,
                    "height": brick_height,
                    "color": colors[row % len(colors)],
                    "alive": True
                })

    # ======================================================
    # BALL AND PADDLE SETUP
    # ======================================================

    def reset_ball(self):

        self.ball = {
            "x": 400,
            "y": 450,
            "radius": 9,
            "dx": random.choice([-4, 4]),
            "dy": -4
        }

        self.paddle["x"] = GAME_WIDTH / 2

    def restart_game(self):

        self.stop_loop()

        self.score = 0
        self.lives = 3
        self.level = 1

        self.running = False
        self.paused = False
        self.game_over = False

        self.keys.clear()

        self.paddle = {
            "x": 400,
            "y": 550,
            "width": 110,
            "height": 14,
            "speed": 8
        }

        self.reset_ball()
        self.create_level()
        self.update_labels()
        self.draw_game()

    # ======================================================
    # GAME CONTROLS
    # ======================================================

    def start_game(self):

        if self.game_over:
            return

        if not self.running:

            self.running = True
            self.paused = False
            self.game_loop()

        elif self.paused:

            self.paused = False
            self.game_loop()

        self.draw_game()

    def start_or_restart(self, event=None):

        if self.game_over:
            self.restart_game()
        else:
            self.start_game()

    def stop_loop(self):

        if self.game_job is not None:

            try:
                self.window.after_cancel(self.game_job)
            except tk.TclError:
                pass

        self.game_job = None

    def toggle_pause(self, event=None):

        if self.game_over:
            return

        if not self.running:
            self.start_game()
            return

        self.paused = not self.paused

        if not self.paused:
            self.game_loop()
        else:
            self.stop_loop()

        self.draw_game()

    def key_down(self, event):

        self.keys.add(event.keysym.lower())

    def key_up(self, event):

        self.keys.discard(event.keysym.lower())

    def mouse_move(self, event):

        x, y = self.to_game_coordinates(event.x, event.y)

        if 0 <= x <= GAME_WIDTH:
            self.paddle["x"] = max(
                self.paddle["width"] / 2,
                min(
                    GAME_WIDTH - self.paddle["width"] / 2,
                    x
                )
            )

    def canvas_click(self, event):

        if not self.running and not self.game_over:
            self.start_game()

    # ======================================================
    # COORDINATE CONVERSION
    # ======================================================

    def on_resize(self, event=None):

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width < 10 or height < 10:
            return

        self.scale = min(
            width / GAME_WIDTH,
            height / GAME_HEIGHT
        )

        self.offset_x = (width - GAME_WIDTH * self.scale) / 2
        self.offset_y = (height - GAME_HEIGHT * self.scale) / 2

        self.draw_game()

    def to_game_coordinates(self, x, y):

        return (
            (x - self.offset_x) / self.scale,
            (y - self.offset_y) / self.scale
        )

    def screen_coordinates(self, x, y):

        return (
            self.offset_x + x * self.scale,
            self.offset_y + y * self.scale
        )

    # ======================================================
    # GAME LOOP
    # ======================================================

    def game_loop(self):

        if not self.running or self.paused or self.game_over:
            return

        self.move_paddle()
        self.move_ball()
        self.check_bricks()
        self.check_level()
        self.check_game_over()

        self.draw_game()
        self.update_labels()

        if self.running and not self.paused and not self.game_over:
            self.game_job = self.window.after(
                16,
                self.game_loop
            )

    # ======================================================
    # PADDLE MOVEMENT
    # ======================================================

    def move_paddle(self):

        speed = self.paddle["speed"]

        if "left" in self.keys or "a" in self.keys:
            self.paddle["x"] -= speed

        if "right" in self.keys or "d" in self.keys:
            self.paddle["x"] += speed

        half = self.paddle["width"] / 2

        self.paddle["x"] = max(
            half,
            min(GAME_WIDTH - half, self.paddle["x"])
        )

    # ======================================================
    # BALL MOVEMENT
    # ======================================================

    def move_ball(self):

        ball = self.ball
        radius = ball["radius"]

        ball["x"] += ball["dx"]
        ball["y"] += ball["dy"]

        # Left and right walls
        if ball["x"] - radius <= 0:
            ball["x"] = radius
            ball["dx"] = abs(ball["dx"])

        elif ball["x"] + radius >= GAME_WIDTH:
            ball["x"] = GAME_WIDTH - radius
            ball["dx"] = -abs(ball["dx"])

        # Top wall
        if ball["y"] - radius <= 0:
            ball["y"] = radius
            ball["dy"] = abs(ball["dy"])

        # Paddle collision
        paddle = self.paddle

        paddle_left = paddle["x"] - paddle["width"] / 2
        paddle_right = paddle["x"] + paddle["width"] / 2

        paddle_top = paddle["y"] - paddle["height"] / 2
        paddle_bottom = paddle["y"] + paddle["height"] / 2

        if (
            ball["dy"] > 0
            and ball["y"] + radius >= paddle_top
            and ball["y"] - radius <= paddle_bottom
            and ball["x"] + radius >= paddle_left
            and ball["x"] - radius <= paddle_right
        ):

            ball["y"] = paddle_top - radius

            hit_position = (
                ball["x"] - paddle["x"]
            ) / (paddle["width"] / 2)

            hit_position = max(-1, min(1, hit_position))

            speed = math.hypot(ball["dx"], ball["dy"])

            angle = hit_position * math.radians(65)

            ball["dx"] = speed * math.sin(angle)
            ball["dy"] = -abs(speed * math.cos(angle))

        # Ball lost
        if ball["y"] - radius > GAME_HEIGHT:

            self.lives -= 1

            if self.lives <= 0:

                self.end_game()
                return

            self.reset_ball()

            self.running = False
            self.stop_loop()

    # ======================================================
    # BRICK COLLISIONS
    # ======================================================

    def check_bricks(self):

        ball = self.ball
        radius = ball["radius"]

        for brick in self.bricks:

            if not brick["alive"]:
                continue

            left = brick["x"]
            right = left + brick["width"]

            top = brick["y"]
            bottom = top + brick["height"]

            closest_x = max(left, min(ball["x"], right))
            closest_y = max(top, min(ball["y"], bottom))

            distance_x = ball["x"] - closest_x
            distance_y = ball["y"] - closest_y

            distance_squared = (
                distance_x ** 2 + distance_y ** 2
            )

            if distance_squared <= radius ** 2:

                brick["alive"] = False
                self.score += 10

                distance = math.sqrt(distance_squared)

                if distance > 0:

                    nx = distance_x / distance
                    ny = distance_y / distance

                    dot = ball["dx"] * nx + ball["dy"] * ny

                    if dot < 0:

                        ball["dx"] -= 2 * dot * nx
                        ball["dy"] -= 2 * dot * ny

                else:

                    # Fallback for a ball exactly at a corner.
                    ball["dy"] *= -1

                self.update_high_score()
                break

    # ======================================================
    # LEVEL PROGRESSION
    # ======================================================

    def check_level(self):

        if not any(brick["alive"] for brick in self.bricks):

            self.level += 1

            self.create_level()

            # Increase ball speed slightly.
            speed = math.hypot(
                self.ball["dx"],
                self.ball["dy"]
            )

            new_speed = min(speed + 0.5, 9)

            angle = math.atan2(
                self.ball["dx"],
                abs(self.ball["dy"])
            )

            self.ball["dx"] = new_speed * math.sin(angle)
            self.ball["dy"] = -new_speed * abs(math.cos(angle))

    # ======================================================
    # SCORE AND GAME OVER
    # ======================================================

    def update_high_score(self):

        if self.score > self.high_score:
            self.high_score = self.score

    def check_game_over(self):

        if self.lives <= 0:
            self.end_game()

    def end_game(self):

        self.running = False
        self.game_over = True

        self.stop_loop()
        self.update_high_score()
        self.update_labels()
        self.draw_game()

    # ======================================================
    # SCOREBOARD
    # ======================================================

    def update_labels(self):

        self.score_label.config(
            text=f"SCORE: {self.score}"
        )

        self.lives_label.config(
            text=f"LIVES: {self.lives}"
        )

        self.level_label.config(
            text=f"LEVEL: {self.level}"
        )

        self.high_label.config(
            text=f"BEST: {self.high_score}"
        )

    # ======================================================
    # DRAWING
    # ======================================================

    def draw_game(self):

        self.canvas.delete("all")

        # Draw centered game area
        x1, y1 = self.screen_coordinates(0, 0)
        x2, y2 = self.screen_coordinates(
            GAME_WIDTH,
            GAME_HEIGHT
        )

        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=BG,
            outline=CYAN,
            width=2
        )

        # Bricks
        for brick in self.bricks:

            if not brick["alive"]:
                continue

            bx1, by1 = self.screen_coordinates(
                brick["x"], brick["y"]
            )

            bx2, by2 = self.screen_coordinates(
                brick["x"] + brick["width"],
                brick["y"] + brick["height"]
            )

            self.canvas.create_rectangle(
                bx1, by1, bx2, by2,
                fill=brick["color"],
                outline=BG,
                width=2
            )

        # Paddle
        paddle = self.paddle

        px1, py1 = self.screen_coordinates(
            paddle["x"] - paddle["width"] / 2,
            paddle["y"] - paddle["height"] / 2
        )

        px2, py2 = self.screen_coordinates(
            paddle["x"] + paddle["width"] / 2,
            paddle["y"] + paddle["height"] / 2
        )

        self.canvas.create_rectangle(
            px1, py1, px2, py2,
            fill=CYAN,
            outline=WHITE,
            width=2
        )

        # Ball
        ball = self.ball
        radius = ball["radius"]

        bx1, by1 = self.screen_coordinates(
            ball["x"] - radius,
            ball["y"] - radius
        )

        bx2, by2 = self.screen_coordinates(
            ball["x"] + radius,
            ball["y"] + radius
        )

        self.canvas.create_oval(
            bx1, by1, bx2, by2,
            fill=GOLD,
            outline=WHITE
        )

        # Start screen
        if not self.running and not self.game_over:

            self.canvas.create_text(
                self.screen_coordinates(400, 300),
                text="PRESS START TO PLAY",
                fill=WHITE,
                font=("Arial", int(23 * self.scale), "bold")
            )

        # Pause screen
        if self.paused:

            self.canvas.create_text(
                self.screen_coordinates(400, 300),
                text="PAUSED",
                fill=CYAN,
                font=("Arial", int(35 * self.scale), "bold")
            )

        # Game over screen
        if self.game_over:

            self.canvas.create_text(
                self.screen_coordinates(400, 260),
                text="GAME OVER",
                fill=RED,
                font=("Arial", int(38 * self.scale), "bold")
            )

            self.canvas.create_text(
                self.screen_coordinates(400, 315),
                text=f"FINAL SCORE: {self.score}",
                fill=WHITE,
                font=("Arial", int(20 * self.scale), "bold")
            )

            self.canvas.create_text(
                self.screen_coordinates(400, 355),
                text="Press ENTER or RESTART to play again",
                fill=CYAN,
                font=("Arial", int(13 * self.scale))
            )

    # ======================================================
    # FULLSCREEN
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

    # ======================================================
    # CLOSE GAME
    # ======================================================

    def close_game(self):

        self.running = False
        self.stop_loop()
        self.window.destroy()


# ==========================================================
# MAIN LAUNCHER CONNECTION
# ==========================================================

def play(root):

    BrickBreaker(root)
