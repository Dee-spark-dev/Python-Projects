# 🎮 Python Games Arsenal

A collection of nine classic games built with Python and Tkinter, brought together in one desktop application.

## 🕹️ Games Included

1. Chess
2. Checkers
3. Tic-Tac-Toe
4. Solitaire
5. Snake
6. Word Search
7. Match Cards
8. Brick Breaker
9. Connect Four

## ✨ Features

- Dark-themed graphical interface
- Central game launcher
- Responsive layout
- Fullscreen support
- Standalone Windows executable

## 🛠️ Technologies

- Python 3.14
- Tkinter
- python-chess
- PyInstaller

## 🚀 How to Run

Clone this repository:

```bash
git clone YOUR_REPOSITORY_URL
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

## 📦 Build Windows Executable

```bash
python -m PyInstaller --onefile --windowed --name "Python Games Arsenal" --paths "." --collect-submodules games main.py
```

The executable will be generated in the `dist` folder.

## 🎯 Project Purpose

This project was developed to improve my Python programming skills through practical experience with game logic, GUI development, modular programming, debugging and application packaging.

## 👨‍💻 Author

A personal Python development project.

**Play. Learn. Build.**
