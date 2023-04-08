import numpy as np
import random
import pygame
import sys
import math
import time
import tkinter as tk
from tkinter import simpledialog, messagebox
from visualiser.visualiser import Visualiser as vs

BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY = (152,153,155)
YELLOW = (0,0,0)

yellowDict = {
	"tan": (230,219,172),
	"beige": (238,220,154),
	"macaroon": (249,224,118),
	"hazelwood": (201,187,142),
	"granola": (214,184,90),
	"oat": (223,201,138),
	"eggnog": (250,226,156),
	"fawn": (200,169,81),
	"sugarcookie": (243,234,175),
	"sand": (216,184,99),
	"sepia": (227,183,120),
	"latte": (231,194,125),
	"oyster": (220,215,160),
	"biscotti": (227,197,101),
	"parmesean": (253,233,146),
	"hazelnut": (189,165,93)
}

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4


def create_board():
	board = np.zeros((ROW_COUNT,COLUMN_COUNT))
	return board

def drop_piece(board, row, col, piece):
	board[row][col] = piece

def is_valid_location(board, col):
	return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
	for r in range(ROW_COUNT):
		if board[r][col] == 0:
			return r

def print_board(board):
	print(np.flip(board, 0))

def winning_move(board, piece):
	#Square configuration win condition
	for c in range(COLUMN_COUNT - 1):
		for r in range(ROW_COUNT - 1):
			if board[r][c] == piece and board[r][c+1] == piece and board[r+1][c] == piece and board[r+1][c+1] == piece:
				return True

def evaluate_window(window, piece):
	#Need to compare the opponent's state with
	score = 0
	#print(window)
	opp_piece = PLAYER_PIECE
	if piece == PLAYER_PIECE:
		opp_piece = AI_PIECE

	if window.count(piece) == 4:
		score += 100
	elif window.count(piece) == 3 and window.count(EMPTY) == 1:
		score += 5
	elif window.count(piece) == 2 and window.count(EMPTY) == 2:
		score += 2

	if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
		score -= 4

	return score

def score_position(board, piece):
	score = 0

	center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
	center_count = center_array.count(piece)
	score += center_count * 3

	for c in range(COLUMN_COUNT - 3):
		for r in range(ROW_COUNT - 3):
			window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
			score += evaluate_window(window, piece)
	
	return score

def is_terminal_node(board):
	return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
	valid_locations = get_valid_locations(board)
	is_terminal = is_terminal_node(board)
	if depth == 0 or is_terminal:	
		if is_terminal:
			if winning_move(board, AI_PIECE):
				return (None, 1000000000000000000000)
			elif winning_move(board, PLAYER_PIECE):
				return (None, -100000000000000000000000)
			else: # Game is over, no more valid moves
				return (None, 0)
		else: # Depth is zero
			return (None, score_position(board, AI_PIECE))
	if maximizingPlayer:
		value = -math.inf
		column = random.choice(valid_locations)
		scoreArr = []
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, AI_PIECE)
			new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
			scoreArr.append(new_score)
			if new_score > value:
				value = new_score
				column = col
			alpha = max(alpha, value)
			if alpha >= beta:
				break
		return column, value

	else: # Minimizing player
		value = math.inf
		column = random.choice(valid_locations)
		scoreArr = []
		for col in valid_locations:
			row = get_next_open_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, PLAYER_PIECE)
			new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
			scoreArr.append(new_score)
			if new_score < value:
				value = new_score
				column = col
			beta = min(beta, value)
			if alpha >= beta:
				break
		return column, value

def get_valid_locations(board):
	valid_locations = []
	for col in range(COLUMN_COUNT):
		if is_valid_location(board, col):
			valid_locations.append(col)
	return valid_locations

def pick_best_move(board, piece):

	valid_locations = get_valid_locations(board)
	best_score = -10000
	best_col = random.choice(valid_locations)
	for col in valid_locations:
		row = get_next_open_row(board, col)
		temp_board = board.copy()
		drop_piece(temp_board, row, col, piece)
		score = score_position(temp_board, piece)
		if score > best_score:
			best_score = score
			best_col = col

	return best_col

def draw_board(board):
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):
			pygame.draw.rect(screen, YELLOW, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			pygame.draw.circle(screen, GRAY, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
	
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT):		
			if board[r][c] == PLAYER_PIECE:
				pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif board[r][c] == AI_PIECE: 
				pygame.draw.circle(screen, WHITE, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	pygame.display.update()


################################ User configuration of Board
ROOT = tk.Tk()

ROOT.withdraw()

indexToColorDict = {}
i = 1
colorString = ""
for color in yellowDict.keys():
	indexToColorDict[i] = color
	colorString = colorString + str(i) + ". " + color + "\n"
	i=i+1

selection = 1

#while(1): 
#	selection = int(simpledialog.askstring(title="Get Depth", prompt= colorString + "Select a board color from the options above (input a number): "))
#	if(selection >= 1 and selection <= 16):
#		break
#	messagebox.showerror("Warning","Please enter a value between 1 and 16, inclusive")

boardRGBValue = yellowDict[indexToColorDict[selection]]
YELLOW = boardRGBValue

#playerName = simpledialog.askstring(title="Get Name", prompt="Enter your name: ")
playerName = "Player 1"
agentName = "James Bond"
firstTurn = 0
#while(1): 
#	firstTurn = int(simpledialog.askstring(title="Get First Turn", prompt="Who will go first, (0) " + playerName + " or your opponent, (1) " + agentName + "?  Enter either (0) or (1) corresponding with player name."))
#	if(firstTurn == 0 or firstTurn == 1):
#		break
#	messagebox.showerror("Warning","Please enter either '0' or '1'")

while(1): 
	minimaxDepth = int(simpledialog.askstring(title="Get Depth", prompt="How deep is the search for Minimax? [1-5]: "))
	if(minimaxDepth >= 1 and minimaxDepth <= 5):
		break
	messagebox.showerror("Warning","Please enter a value between 1 and 5, inclusive")
####################################

board = create_board()
print_board(board)
game_over = False

pygame.init()

SQUARESIZE = 100
totalMovesCounter = 0

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

turn = firstTurn

gameStartTime = time.time()
while not game_over:
	
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

		if event.type == pygame.MOUSEMOTION:
			pygame.draw.rect(screen, GRAY, (0,0, width, SQUARESIZE))
			posx = event.pos[0]
			if turn == PLAYER:
				pygame.draw.circle(screen, BLACK, (posx, int(SQUARESIZE/2)), RADIUS)

		pygame.display.update()

		if event.type == pygame.MOUSEBUTTONDOWN:
			pygame.draw.rect(screen, GRAY, (0,0, width, SQUARESIZE))
			#print(event.pos)
			# Ask for Player 1 Input
			if turn == PLAYER:
				posx = event.pos[0]
				col = int(math.floor(posx/SQUARESIZE))

				if is_valid_location(board, col):
					row = get_next_open_row(board, col)
					drop_piece(board, row, col, PLAYER_PIECE)
					totalMovesCounter += 1

					if winning_move(board, PLAYER_PIECE):
						label = myfont.render(playerName + " wins!!", 1, BLACK)
						screen.blit(label, (40,10))
						game_over = True

					turn += 1
					turn = turn % 2
					print_board(board)
					draw_board(board)


	# # Ask for Player 2 Input
	if turn == AI and not game_over:
		#col = random.randint(0, COLUMN_COUNT-1)
		#col = pick_best_move(board, AI_PIECE)
		col, minimax_score = minimax(board, minimaxDepth, -math.inf, math.inf, True)

		if is_valid_location(board, col):
			#pygame.time.wait(500)
			row = get_next_open_row(board, col)
			drop_piece(board, row, col, AI_PIECE)
			totalMovesCounter += 1

			if winning_move(board, AI_PIECE):
				label = myfont.render(agentName + " wins!!", 1, WHITE)
				screen.blit(label, (40,10))				
				game_over = True

			print_board(board)
			draw_board(board)

			turn += 1
			turn = turn % 2
	if game_over:
		messagebox.showerror("Result","Total Moves: " + str(totalMovesCounter) + ", Time Elapsed: " + str("{:.2f}".format(time.time() - gameStartTime)) + " seconds")
		pygame.time.wait(3000)