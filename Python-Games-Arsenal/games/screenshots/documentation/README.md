# 🎮 Python Games Arsenal

A desktop game collection built with Python and Tkinter. Python Games Arsenal brings multiple classic games together in one graphical launcher, with a dark-themed interface and a standalone Windows executable.

## 🚀 Features

- Multiple games accessible from one launcher.
- Dark-themed graphical interface.
- Responsive game selection menu.
- Fullscreen support using F11 and Escape.
- Standalone Windows `.exe` version.
- Modular code structure for easier maintenance and expansion.

## 🕹️ Games Included

- Chess
- Checkers
- Tic-Tac-Toe
- Solitaire
- Snake
- Word Search
- Match Cards
- Brick Breaker
- Connect Four

## 🛠️ Technologies Used

- Python 3.14
- Tkinter – GUI development
- python-chess – Chess functionality
- PyInstaller – Packaging into a Windows executable

## 📂 Project Structure

```text
Python Games Arsenal/
│
├── main.py
├── games/
│   ├── __init__.py
│   ├── chess.py
│   ├── checkers.py
│   ├── tic_tac_toe.py
│   ├── solitaire.py
│   ├── snake.py
│   ├── word_search.py
│   ├── match_cards.py
│   ├── brick_breaker.py
│   └── connect_four.py
│
├── dist/
│   └── Python Games Arsenal.exe
│
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Install dependencies

```bash
pip install python-chess
```

### 3. Run the application

```bash
python main.py
```

## 📦 Building the Windows Executable

Install PyInstaller:

```bash
pip install pyinstaller
```

Build the application:

```bash
python -m PyInstaller --onefile --windowed --name "Python Games Arsenal" --paths "." --collect-submodules games main.py
```

The executable will be generated inside the `dist` folder.

## 🎯 Project Goals

This project was created to strengthen my Python programming skills through practical application, GUI development, modular programming, debugging, and application packaging.

It is also designed to grow as I develop and add more games.

## 👨‍💻 Author

Created as a personal Python development project.

**Python Games Arsenal – Play. Learn. Build.**
