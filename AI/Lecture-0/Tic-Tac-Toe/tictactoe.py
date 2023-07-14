"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    player1_counter = 0
    player2_counter = 0

    for row in board:
        for cell in row:
            if cell == "X":
                player1_counter += 1
            elif cell == "O":
                player2_counter += 1
    
    if player1_counter > player2_counter:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = []
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                actions.append((i, j))

    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    b = deepcopy(board)
    b[action[0]][action[1]] = player(board)

    return b


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for row in board:
        if all(element == row[0] for element in row):
            return row[0]

    for i in range(3):
        if all(board[j][i] == board[0][i] for j in range(3)):
            return board[0][i]
    
    for diag in [(board[0][0],board[1][1],board[2][2]), (board[0][2], board[1][1], board[2][0])]:
        if all(element == diag[0] for element in diag):
            return diag[0]
    
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    
    for row in board:
        if any(element == EMPTY for element in row):
            return False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    _winner = winner(board)

    if _winner == X:
        return 1
    elif _winner == O:
        return -1
    else:
        return 0
    

def minvalue(board, v0=-10E9):
    if terminal(board):
        return utility(board)
    
    v = 10E9

    for action in actions(board):
        v = min(v, maxvalue(result(board, action), v))
        if v < v0:
            return v

    return v


def maxvalue(board, v0=10E9):
    if terminal(board):
        return utility(board)
    
    v = -10E9

    for action in actions(board):
        v = max(v, minvalue(result(board, action), v))
        if v > v0:
            return v
    
    return v


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    p = player(board)
    v = None
    best_action = None

    if p == X:
        v = -10E9
        for action in actions(board):
            max_v = minvalue(result(board, action))
            if max_v > v:
                v = max_v
                best_action = action
    else:
        v = 10E9
        for action in actions(board):
            min_v = maxvalue(result(board, action))
            if min_v < v:
                v = min_v
                best_action = action

    return best_action
