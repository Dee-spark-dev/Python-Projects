
import tkinter as tk
from tkinter import messagebox
import random
import time
import copy


def play(root):
    window = tk.Toplevel(root)
    window.title("Solitaire")
    window.geometry("1100x780")
    window.minsize(850, 650)
    window.configure(bg="#101522")
    root.withdraw()

    BG = "#101522"
    PANEL = "#1b2638"
    CYAN = "#00d9ff"
    PURPLE = "#a855f7"
    GREEN = "#14532d"
    WHITE = "#f8fafc"

    CARD_W = 76
    CARD_H = 105

    SUITS = ["♠", "♥", "♦", "♣"]
    COLORS = {
        "♠": "#111827",
        "♣": "#111827",
        "♥": "#dc2626",
        "♦": "#dc2626"
    }

    class Solitaire:

        def __init__(self):
            self.canvas = tk.Canvas(
                window,
                bg=BG,
                highlightthickness=0
            )
            self.canvas.pack(
                fill="both",
                expand=True,
                padx=10,
                pady=5
            )

            self.status = tk.Label(
                window,
                bg=BG,
                fg=CYAN,
                font=("Segoe UI", 12, "bold")
            )
            self.status.pack(pady=3)

            controls = tk.Frame(window, bg=BG)
            controls.pack(fill="x", padx=10, pady=8)

            self.button(controls, "NEW GAME", self.new_game)
            self.button(controls, "UNDO", self.undo)
            self.button(controls, "MAIN MENU", self.return_to_menu)

            self.canvas.bind("<Button-1>", self.click)
            self.canvas.bind("<Configure>", self.draw)

            window.bind("<F11>", self.toggle_fullscreen)
            window.bind("<Escape>", self.escape)
            window.bind("<Control-z>", lambda e: self.undo())

            self.fullscreen = False
            self.timer_job = None

            self.new_game()

        # ---------------- BUTTONS ----------------

        def button(self, parent, text, command):
            tk.Button(
                parent,
                text=text,
                command=command,
                bg=PANEL,
                fg=CYAN,
                activebackground=PURPLE,
                activeforeground="white",
                relief="flat",
                font=("Segoe UI", 10, "bold"),
                padx=16,
                pady=9,
                cursor="hand2"
            ).pack(side="left", padx=6)

        def toggle_fullscreen(self, event=None):
            self.fullscreen = not self.fullscreen
            window.attributes("-fullscreen", self.fullscreen)

        def escape(self, event=None):
            if self.fullscreen:
                self.fullscreen = False
                window.attributes("-fullscreen", False)
            else:
                self.return_to_menu()

        # ---------------- GAME SETUP ----------------

        def new_game(self):
            self.stop_timer()

            deck = [
                (rank, suit)
                for suit in SUITS
                for rank in range(1, 14)
            ]
            random.shuffle(deck)

            self.tableau = [[] for _ in range(7)]
            self.foundations = [[] for _ in range(4)]

            self.stock = []
            self.waste = []

            for col in range(7):
                for row in range(col + 1):
                    rank, suit = deck.pop()
                    self.tableau[col].append(
                        [rank, suit, row == col]
                    )

            self.stock = deck

            self.selected = None
            self.history = []

            self.score = 0
            self.moves = 0
            self.game_over = False

            self.start_time = time.time()
            self.elapsed = 0

            self.update_timer()
            self.draw()

        def stop_timer(self):
            if self.timer_job:
                try:
                    window.after_cancel(self.timer_job)
                except tk.TclError:
                    pass
                self.timer_job = None

        def update_timer(self):
            if self.game_over:
                return

            self.elapsed = int(time.time() - self.start_time)
            minutes, seconds = divmod(self.elapsed, 60)

            self.status.config(
                text=(
                    f"Score: {self.score}     "
                    f"Moves: {self.moves}     "
                    f"Time: {minutes:02}:{seconds:02}"
                )
            )

            self.timer_job = window.after(
                1000, self.update_timer
            )

        # ---------------- UNDO ----------------

        def save_state(self):
            self.history.append({
                "tableau": copy.deepcopy(self.tableau),
                "foundations": copy.deepcopy(self.foundations),
                "stock": copy.deepcopy(self.stock),
                "waste": copy.deepcopy(self.waste),
                "score": self.score,
                "moves": self.moves
            })

        def undo(self):
            if not self.history or self.game_over:
                return

            state = self.history.pop()

            self.tableau = state["tableau"]
            self.foundations = state["foundations"]
            self.stock = state["stock"]
            self.waste = state["waste"]

            self.score = state["score"]
            self.moves = state["moves"]

            self.selected = None
            self.draw()

        # ---------------- DRAW CARD ----------------

        def draw_card(self):
            if self.game_over:
                return

            if not self.stock and not self.waste:
                return

            self.save_state()
            self.selected = None

            if self.stock:
                self.waste.append(self.stock.pop())
            else:
                # Recycle the waste pile in the correct order
                self.stock = list(reversed(self.waste))
                self.waste = []

                self.score = max(0, self.score - 5)

            self.moves += 1
            self.draw()

        # ---------------- CARD LAYOUT ----------------

        def layout(self):
            width = max(self.canvas.winfo_width(), 850)

            gap = 12
            total_width = 7 * CARD_W + 6 * gap

            start_x = max(
                10,
                (width - total_width) / 2
            )

            return start_x, gap

        def column_positions(self, col):
            start_x, gap = self.layout()
            return start_x + col * (CARD_W + gap)

        def card_positions(self, col):
            """
            Calculate the exact vertical position of every
            card in a tableau pile.

            Drawing and mouse detection both use this method.
            """
            pile = self.tableau[col]
            height = self.canvas.winfo_height()

            tableau_y = 165

            offsets = []
            for card in pile:
                offsets.append(15 if not card[2] else 23)

            total_offset = sum(offsets)

            available = max(
                20,
                height - tableau_y - CARD_H - 25
            )

            scale = min(
                1.0,
                available / max(total_offset, 1)
            )

            positions = []
            current_y = tableau_y

            for offset in offsets:
                positions.append(current_y)
                current_y += offset * scale

            return positions

        # ---------------- DRAWING ----------------

        def draw_slot(self, x, y, label=""):
            self.canvas.create_rectangle(
                x, y,
                x + CARD_W, y + CARD_H,
                fill=GREEN,
                outline="#64748b",
                width=2
            )

            if label:
                self.canvas.create_text(
                    x + CARD_W / 2,
                    y + CARD_H / 2,
                    text=label,
                    fill="#bbf7d0",
                    font=("Segoe UI", 15, "bold")
                )

        def draw_back(self, x, y):
            self.canvas.create_rectangle(
                x, y,
                x + CARD_W, y + CARD_H,
                fill="#263b63",
                outline=CYAN,
                width=2
            )

            self.canvas.create_rectangle(
                x + 6, y + 6,
                x + CARD_W - 6, y + CARD_H - 6,
                outline="#60a5fa",
                width=2
            )

        def draw_face(self, x, y, card, selected=False):
            rank, suit = card

            names = {
                1: "A",
                11: "J",
                12: "Q",
                13: "K"
            }

            rank_text = names.get(rank, str(rank))
            color = COLORS[suit]

            self.canvas.create_rectangle(
                x, y,
                x + CARD_W, y + CARD_H,
                fill=WHITE,
                outline=CYAN if selected else "#cbd5e1",
                width=3 if selected else 1
            )

            self.canvas.create_text(
                x + 9,
                y + 13,
                text=f"{rank_text}{suit}",
                fill=color,
                font=("Segoe UI", 13, "bold"),
                anchor="nw"
            )

            self.canvas.create_text(
                x + CARD_W / 2,
                y + CARD_H / 2,
                text=suit,
                fill=color,
                font=("Segoe UI", 32, "bold")
            )

        def draw(self, event=None):
            if not hasattr(self, "tableau"):
                return

            self.canvas.delete("all")

            start_x, gap = self.layout()
            top_y = 20

            # Stock
            if self.stock:
                self.draw_back(start_x, top_y)
            else:
                self.draw_slot(start_x, top_y, "↻")

            self.canvas.create_text(
                start_x + CARD_W / 2,
                top_y + CARD_H + 14,
                text="DRAW CARD",
                fill=CYAN,
                font=("Segoe UI", 9, "bold")
            )

            # Waste pile: show the latest drawn card
            waste_x = start_x + CARD_W + 15

            if self.waste:
                self.draw_face(
                    waste_x,
                    top_y,
                    self.waste[-1],
                    self.selected == ("waste", 0)
                )
            else:
                self.draw_slot(waste_x, top_y)

            self.canvas.create_text(
                waste_x + CARD_W / 2,
                top_y + CARD_H + 14,
                text="DRAWN CARD",
                fill="#94a3b8",
                font=("Segoe UI", 8, "bold")
            )

            # Foundations
            foundation_x = start_x + 3 * (CARD_W + gap)

            for i, pile in enumerate(self.foundations):
                x = foundation_x + i * (CARD_W + 10)

                if pile:
                    self.draw_face(x, top_y, pile[-1])
                else:
                    self.draw_slot(x, top_y, SUITS[i])

            # Tableau
            for col, pile in enumerate(self.tableau):
                x = self.column_positions(col)

                if not pile:
                    self.draw_slot(x, 165, "K")
                    continue

                positions = self.card_positions(col)

                for row, card in enumerate(pile):
                    y = positions[row]

                    is_selected = (
                        self.selected is not None
                        and self.selected[0] == "tableau"
                        and self.selected[1] == col
                        and row >= self.selected[2]
                    )

                    if card[2]:
                        self.draw_face(
                            x,
                            y,
                            (card[0], card[1]),
                            is_selected
                        )
                    else:
                        self.draw_back(x, y)

            if self.game_over:
                self.canvas.create_text(
                    self.canvas.winfo_width() / 2,
                    self.canvas.winfo_height() - 30,
                    text="YOU WIN! ALL CARDS COMPLETED!",
                    fill=CYAN,
                    font=("Segoe UI", 19, "bold")
                )

        # ---------------- MOUSE DETECTION ----------------

        def get_card_at(self, x, y):
            start_x, gap = self.layout()
            top_y = 20

            # Stock
            if (
                start_x <= x <= start_x + CARD_W
                and top_y <= y <= top_y + CARD_H
            ):
                return ("stock", 0)

            # Waste
            waste_x = start_x + CARD_W + 15

            if (
                waste_x <= x <= waste_x + CARD_W
                and top_y <= y <= top_y + CARD_H
            ):
                return ("waste", 0)

            # Foundations
            foundation_x = start_x + 3 * (CARD_W + gap)

            for i in range(4):
                fx = foundation_x + i * (CARD_W + 10)

                if (
                    fx <= x <= fx + CARD_W
                    and top_y <= y <= top_y + CARD_H
                ):
                    return ("foundation", i)

            # Tableau
            for col, pile in enumerate(self.tableau):
                cx = self.column_positions(col)

                if not (cx <= x <= cx + CARD_W):
                    continue

                if y < 165:
                    continue

                if not pile:
                    if y <= 165 + CARD_H:
                        return ("tableau", col, 0)
                    continue

                positions = self.card_positions(col)

                # Find the card whose visible section was clicked
                for row in range(len(pile) - 1, -1, -1):
                    card_y = positions[row]

                    if row == len(pile) - 1:
                        bottom = card_y + CARD_H
                    else:
                        bottom = positions[row + 1]

                    if card_y <= y < bottom:
                        return ("tableau", col, row)

            return None

        # ---------------- CLICK HANDLING ----------------

        def click(self, event):
            if self.game_over:
                return

            target = self.get_card_at(event.x, event.y)

            if target is None:
                return

            kind = target[0]

            if kind == "stock":
                self.draw_card()
                return

            if kind == "waste":
                if self.waste:
                    self.handle_waste_click()
                return

            if kind == "foundation":
                if self.selected:
                    self.move_to_foundation(target[1])
                return

            if kind == "tableau":
                self.handle_tableau_click(
                    target[1], target[2]
                )

        def handle_waste_click(self):
            if not self.waste:
                return

            if self.selected == ("waste", 0):
                self.selected = None
                self.draw()
                return

            if self.selected:
                # Clicking waste while another card is selected
                # cancels selection and selects the waste card.
                self.selected = ("waste", 0)
                self.draw()
                return

            self.selected = ("waste", 0)

            if self.auto_foundation():
                return

            self.draw()

        def handle_tableau_click(self, col, row):
            pile = self.tableau[col]

            # Empty column
            if not pile:
                if self.selected:
                    self.move_to_tableau(col)
                return

            if row >= len(pile):
                return

            # Flip a face-down card only when it is exposed
            if not pile[row][2]:
                if row == len(pile) - 1:
                    self.flip_card(col)
                return

            # Deselect same card
            if self.selected == ("tableau", col, row):
                self.selected = None
                self.draw()
                return

            # Try moving the selected cards to this column
            if self.selected:
                if self.move_to_tableau(col):
                    return

            # Select the clicked face-up card
            self.selected = ("tableau", col, row)

            # Only a single top card can go to a foundation
            if row == len(pile) - 1:
                if self.auto_foundation():
                    return

            self.draw()

        # ---------------- CARD MOVEMENT ----------------

        def flip_card(self, col):
            pile = self.tableau[col]

            if pile and not pile[-1][2]:
                self.save_state()

                pile[-1][2] = True
                self.score += 5
                self.moves += 1

                self.draw()

        def selected_cards(self):
            if not self.selected:
                return []

            if self.selected[0] == "waste":
                if self.waste:
                    return [self.waste[-1]]
                return []

            if self.selected[0] == "tableau":
                _, col, row = self.selected
                return self.tableau[col][row:]

            return []

        def remove_selected(self):
            if self.selected[0] == "waste":
                return [self.waste.pop()]

            _, col, row = self.selected

            cards = self.tableau[col][row:]
            self.tableau[col] = self.tableau[col][:row]

            # Reveal the card underneath
            if (
                self.tableau[col]
                and not self.tableau[col][-1][2]
            ):
                self.tableau[col][-1][2] = True
                self.score += 5

            return cards

        def can_place_on_tableau(self, cards, target_col):
            if not cards:
                return False

            moving = cards[0]
            target = self.tableau[target_col]

            # Only kings can go into empty columns
            if not target:
                return moving[0] == 13

            top = target[-1]

            return (
                top[2]
                and moving[0] == top[0] - 1
                and COLORS[moving[1]] != COLORS[top[1]]
            )

        def move_to_tableau(self, target_col):
            if not self.selected:
                return False

            cards = self.selected_cards()

            if not self.can_place_on_tableau(
                cards, target_col
            ):
                return False

            if (
                self.selected[0] == "tableau"
                and self.selected[1] == target_col
            ):
                return False

            self.save_state()

            moving = self.remove_selected()
            self.tableau[target_col].extend(moving)

            self.selected = None
            self.moves += 1

            self.draw()
            return True

        # ---------------- FOUNDATIONS ----------------

        def can_place_on_foundation(self, card, foundation):
            pile = self.foundations[foundation]

            if not pile:
                return card[0] == 1

            top = pile[-1]

            return (
                card[1] == top[1]
                and card[0] == top[0] + 1
            )

        def auto_foundation(self):
            if not self.selected:
                return False

            cards = self.selected_cards()

            if len(cards) != 1:
                return False

            card = cards[0]

            for i in range(4):
                if self.can_place_on_foundation(card, i):
                    return self.move_to_foundation(i)

            return False

        def move_to_foundation(self, foundation):
            if not self.selected:
                return False

            cards = self.selected_cards()

            if len(cards) != 1:
                return False

            card = cards[0]

            if not self.can_place_on_foundation(
                card, foundation
            ):
                return False

            self.save_state()

            moving = self.remove_selected()

            self.foundations[foundation].append(
                (moving[0][0], moving[0][1])
            )

            self.selected = None
            self.score += 10
            self.moves += 1

            self.check_win()
            self.draw()

            return True

        # ---------------- WIN ----------------

        def check_win(self):
            total = sum(
                len(pile)
                for pile in self.foundations
            )

            if total == 52:
                self.game_over = True
                self.stop_timer()

                self.status.config(
                    text=f"YOU WIN! Final score: {self.score}"
                )

                messagebox.showinfo(
                    "Solitaire",
                    "Congratulations! You completed Solitaire!"
                )

        # ---------------- EXIT ----------------

        def return_to_menu(self):
            self.stop_timer()
            window.destroy()
            root.deiconify()

    game = Solitaire()

    def close_game():
        game.stop_timer()
        window.destroy()
        root.deiconify()

    window.protocol("WM_DELETE_WINDOW", close_game)


