import sys
import pygame
import numpy as np
import sqlite3

pygame.init()

# SQLite database setup
conn = sqlite3.connect('tic_tac_toe.db')
cursor = conn.cursor()

# Create a table for storing game results if it doesn't already exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS game_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    board TEXT,
    winner TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

# Define colors and proportions for the game
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WIDTH = 300
HEIGHT = 300
LINE_WIDTH = 5
BOARD_ROWS = 3
BOARD_COLS = 3
SQUARE_SIZE = WIDTH // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = SQUARE_SIZE // 4

# Set up the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tic Tac Toe')
screen.fill(BLACK)

# Initialize the game board as a 3x3 matrix of zeros
board = np.zeros((BOARD_ROWS, BOARD_COLS))

# Convert the board state into a string format for storing in the database
def board_to_string(board):
    """Convert the game board to a string representation for database storage."""
    return ','.join(map(str, board.flatten()))

# Save the game result (winner or draw) to the database
def save_game_result(winner):
    """Insert the game result into the database with the current board state and winner."""
    board_state = board_to_string(board)
    cursor.execute("INSERT INTO game_results (board, winner) VALUES (?, ?)", (board_state, winner))
    conn.commit()

# Display the last winner from the database
def display_last_winner():
    """Fetch and print the last winner from the game results database."""
    cursor.execute("SELECT winner FROM game_results ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    if result:
        print("Winner:", result[0])

# Draw grid lines on the game board
def draw_lines(color=WHITE):
    """Draw the grid lines on the board with the specified color."""
    for i in range(1, BOARD_ROWS):
        pygame.draw.line(screen, color, (0, SQUARE_SIZE * i), (WIDTH, SQUARE_SIZE * i), width=LINE_WIDTH)
        pygame.draw.line(screen, color, (SQUARE_SIZE * i, 0), (SQUARE_SIZE * i, HEIGHT), width=LINE_WIDTH)

# Draw Xs and Os on the board based on the current game state
def draw_figures(color=WHITE):
    """Draw the current Xs and Os on the board based on player moves."""
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 1:  # Player 1 (X)
                pygame.draw.circle(screen, WHITE, (int(col * SQUARE_SIZE + SQUARE_SIZE // 2), int(row * SQUARE_SIZE + SQUARE_SIZE // 2)), CIRCLE_RADIUS, CIRCLE_WIDTH)
            elif board[row][col] == 2:  # Player 2 (O)
                pygame.draw.line(screen, WHITE, (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE), (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), CROSS_WIDTH)
                pygame.draw.line(screen, WHITE, (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE), (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE), CROSS_WIDTH)

# Mark a square on the board for the current player
def mark_square(row, col, player):
    """Mark the specified square for the given player (1 or 2)."""
    board[row][col] = player

# Check if a square is available for marking
def available_square(row, col):
    """Check if the specified square is unoccupied (0)."""
    return board[row][col] == 0

# Check if the board is full (i.e., no empty squares)
def is_board_full(check_board=board):
    """Return True if the board is full; otherwise, False."""
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if check_board[row][col] == 0:
                return False
    return True

# Check if the specified player has won the game
def check_win(player, check_board=board):
    """Check if the specified player has a winning combination on the board."""
    for col in range(BOARD_COLS):
        if check_board[0][col] == player and check_board[1][col] == player and check_board[2][col] == player:
            return True

    for row in range(BOARD_ROWS):
        if check_board[row][0] == player and check_board[row][1] == player and check_board[row][2] == player:
            return True

    if check_board[0][0] == player and check_board[1][1] == player and check_board[2][2] == player:
        return True

    if check_board[0][2] == player and check_board[1][1] == player and check_board[2][0] == player:
        return True

    return False

# AI implementation using the minimax algorithm
def minimax(minimax_board, depth, is_maximizing):
    """Minimax algorithm to calculate the best move for the AI."""
    if check_win(2, minimax_board):  # AI wins
        return float('inf')
    if check_win(1, minimax_board):  # Human wins
        return float('-inf')
    if is_board_full(minimax_board):  # Draw
        return 0

    if is_maximizing:  # AI is the maximizing player
        best_score = -1000
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if minimax_board[row][col] == 0:
                    minimax_board[row][col] = 2  # AI's move
                    score = minimax(minimax_board, depth + 1, False)
                    minimax_board[row][col] = 0
                    best_score = max(best_score, score)
        return best_score
    else:  # Human is the minimizing player
        best_score = 1000
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if minimax_board[row][col] == 0:
                    minimax_board[row][col] = 1  # Human's move
                    score = minimax(minimax_board, depth + 1, True)
                    minimax_board[row][col] = 0
                    best_score = min(score, best_score)
        return best_score

# Determine the best move for the AI
def best_move():
    """Calculate the best move for the AI based on the current board state using minimax."""
    best_score = -1000
    move = (-1, -1)
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 0:
                board[row][col] = 2  # AI's move
                score = minimax(board, 0, False)
                board[row][col] = 0
                if score > best_score:
                    best_score = score
                    move = (row, col)
    if move != (-1, -1):
        mark_square(move[0], move[1], 2)  # Mark the best move
        return True
    return False

# Display past game results from the database
def display_game_results():
    """Fetch and display all past game results from the database."""
    cursor.execute("SELECT * FROM game_results ORDER BY timestamp DESC")
    games = cursor.fetchall()
    
    print("Past Game Results:")
    for game in games:
        print(f"ID: {game[0]}, Board: {game[1]}, Winner: {game[2]}, Time: {game[3]}")

# Call this function to see the game history when the program starts
display_game_results()

# Game loop
draw_lines()
player = 1
game_over = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            mouseX = event.pos[0] // SQUARE_SIZE
            mouseY = event.pos[1] // SQUARE_SIZE

            if available_square(mouseY, mouseX):
                mark_square(mouseY, mouseX, player)
                if check_win(player):
                    save_game_result('Player ' + str(player))  # Save the winner
                    display_last_winner()  # Display the winner
                    game_over = True
                player = player % 2 + 1
                
                if not game_over:
                    if best_move():
                        if check_win(2):
                            save_game_result('AI')  # Save AI win
                            display_last_winner()  # Display the winner
                            game_over = True
                        player = player % 2 + 1

                # Check for a draw
                if not game_over and is_board_full():
                    save_game_result('Draw')  # Save draw result
                    print("Game ended in a draw!")
                    game_over = True

    if not game_over:
        draw_figures()
    else:
        if check_win(1):
            draw_figures(GREEN)
            draw_lines(GREEN) 
        elif check_win(2):
            draw_figures(RED) 
            draw_lines(RED)
        else:
            draw_figures(GRAY)
            draw_lines(GRAY)                              
    
    pygame.display.update()
