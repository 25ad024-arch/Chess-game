
import tkinter as tk
from tkinter import messagebox
import chess
import random

# ---------------- GAME SETTINGS ----------------

board = chess.Board()
selected_square = None
game_over = False

PIECES = {
    "K": "\u2654", "Q": "\u2655", "R": "\u2656",
    "B": "\u2657", "N": "\u2658", "P": "\u2659",
    "k": "\u265A", "q": "\u265B", "r": "\u265C",
    "b": "\u265D", "n": "\u265E", "p": "\u265F"
}

VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}


# ---------------- AI EVALUATION ----------------

def evaluate_position(position):
    if position.is_checkmate():
        return -100000 if position.turn == chess.WHITE else 100000

    if position.is_game_over():
        return 0

    score = 0

    for piece_type, value in VALUES.items():
        score += len(position.pieces(piece_type, chess.WHITE)) * value
        score -= len(position.pieces(piece_type, chess.BLACK)) * value

    return score


# ---------------- MINIMAX ALGORITHM ----------------

def minimax(position, depth, alpha, beta):
    if depth == 0 or position.is_game_over():
        return evaluate_position(position)

    if position.turn == chess.WHITE:
        best_score = -float("inf")

        for move in list(position.legal_moves):
            position.push(move)
            score = minimax(position, depth - 1, alpha, beta)
            position.pop()

            best_score = max(best_score, score)
            alpha = max(alpha, best_score)

            if beta <= alpha:
                break

        return best_score

    else:
        best_score = float("inf")

        for move in list(position.legal_moves):
            position.push(move)
            score = minimax(position, depth - 1, alpha, beta)
            position.pop()

            best_score = min(best_score, score)
            beta = min(beta, best_score)

            if beta <= alpha:
                break

        return best_score


def find_ai_move():
    best_score = float("inf")
    best_moves = []

    moves = list(board.legal_moves)
    random.shuffle(moves)

    for move in moves:
        board.push(move)
        score = minimax(board, 1, -float("inf"), float("inf"))
        board.pop()

        if score < best_score:
            best_score = score
            best_moves = [move]
        elif score == best_score:
            best_moves.append(move)

    return random.choice(best_moves) if best_moves else None


# ---------------- BOARD DISPLAY ----------------

def refresh_board():
    for row in range(8):
        for col in range(8):
            square = chess.square(col, 7 - row)
            piece = board.piece_at(square)

            color = "#F0D9B5" if (row + col) % 2 == 0 else "#779556"

            if selected_square == square:
                color = "#F6F669"

            elif selected_square is not None:
                move = chess.Move(selected_square, square)
                if move in board.legal_moves:
                    color = "#BACA44"

            symbol = PIECES.get(piece.symbol(), "") if piece else ""

            buttons[row][col].config(
                text=symbol,
                bg=color,
                fg="#202020",
                activebackground="#D6E85D"
            )

    if board.is_checkmate():
        status_label.config(text="CHECKMATE!")
    elif board.is_stalemate():
        status_label.config(text="DRAW - STALEMATE")
    elif board.is_check():
        status_label.config(
            text=("White" if board.turn else "Black AI") + " is in CHECK!"
        )
    elif board.is_game_over():
        status_label.config(text="GAME OVER - " + board.result())
    elif board.turn == chess.WHITE:
        status_label.config(text="YOUR TURN - WHITE")
    else:
        status_label.config(text="AI IS THINKING...")


# ---------------- GAME RESULT ----------------

def finish_if_needed():
    global game_over

    if board.is_game_over():
        game_over = True
        refresh_board()

        if board.is_checkmate():
            winner = "Black AI" if board.turn == chess.WHITE else "You"
            messagebox.showinfo("Game Over", winner + " wins by checkmate!")
        elif board.is_stalemate():
            messagebox.showinfo("Game Over", "Draw by stalemate!")
        else:
            messagebox.showinfo("Game Over", "Result: " + board.result())

        return True

    return False


# ---------------- AI TURN ----------------

def ai_turn():
    if game_over or board.is_game_over():
        finish_if_needed()
        return

    move = find_ai_move()

    if move:
        board.push(move)

    refresh_board()
    finish_if_needed()


# ---------------- PLAYER MOVE ----------------

def on_square_click(row, col):
    global selected_square

    if game_over or board.is_game_over():
        return

    if board.turn != chess.WHITE:
        return

    clicked = chess.square(col, 7 - row)

    if selected_square is None:
        piece = board.piece_at(clicked)

        if piece and piece.color == chess.WHITE:
            selected_square = clicked

        refresh_board()
        return

    piece = board.piece_at(selected_square)
    move = chess.Move(selected_square, clicked)

    # Promote a pawn to a queen automatically
    if (
        piece
        and piece.piece_type == chess.PAWN
        and chess.square_rank(clicked) == 7
    ):
        move = chess.Move(
            selected_square,
            clicked,
            promotion=chess.QUEEN
        )

    if move in board.legal_moves:
        board.push(move)
        selected_square = None
        refresh_board()

        if not finish_if_needed():
            root.after(200, ai_turn)

    else:
        clicked_piece = board.piece_at(clicked)

        if clicked_piece and clicked_piece.color == chess.WHITE:
            selected_square = clicked
        else:
            selected_square = None

        refresh_board()


# ---------------- RESET GAME ----------------

def reset_game():
    global board, selected_square, game_over

    board = chess.Board()
    selected_square = None
    game_over = False

    refresh_board()


# ---------------- GRAPHICAL INTERFACE ----------------

root = tk.Tk()
root.title("AI Chess Arena | AIDM Project")
root.geometry("610x700")
root.configure(bg="#172033")
root.resizable(False, False)

title_label = tk.Label(
    root,
    text="♟ AI CHESS ARENA ♟",
    font=("Arial", 24, "bold"),
    bg="#172033",
    fg="#F5D76E"
)
title_label.pack(pady=(15, 5))

subtitle = tk.Label(
    root,
    text="Artificial Intelligence & Decision Making",
    font=("Arial", 10),
    bg="#172033",
    fg="#D6DEEF"
)
subtitle.pack(pady=3)

status_label = tk.Label(
    root,
    text="YOUR TURN - WHITE",
    font=("Arial", 13, "bold"),
    bg="#172033",
    fg="#FFFFFF"
)
status_label.pack(pady=10)

board_frame = tk.Frame(root, bg="#172033")
board_frame.pack(pady=5)

buttons = []

for row in range(8):
    button_row = []

    for col in range(8):
        button = tk.Button(
            board_frame,
            text="",
            font=("Segoe UI Symbol", 30),
            width=2,
            height=1,
            relief="flat",
            bd=0,
            highlightthickness=0,
            command=lambda r=row, c=col: on_square_click(r, c)
        )

        button.grid(row=row, column=col)
        button_row.append(button)

    buttons.append(button_row)

reset_button = tk.Button(
    root,
    text="NEW GAME",
    font=("Arial", 12, "bold"),
    bg="#F5D76E",
    fg="#172033",
    activebackground="#FFE99A",
    relief="flat",
    padx=25,
    pady=8,
    command=reset_game
)
reset_button.pack(pady=12)

footer = tk.Label(
    root,
    text="YOU: WHITE     |     COMPUTER: BLACK",
    font=("Arial", 10, "bold"),
    bg="#172033",
    fg="#AAB7CF"
)
footer.pack(pady=3)

refresh_board()
root.mainloop()
