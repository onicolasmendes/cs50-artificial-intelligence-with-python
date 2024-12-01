"""
Tic Tac Toe Player
"""

import math
import sys
import copy

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
    # Conta a quantidade de Xs e Os presentes no tabuleiro atual
    x_active = sum(line.count(X) for line in board)
    o_active = sum(line.count(O) for line in board)
    
    # Caso o numero de Xs e Os seja iguais, é a vez do X
    if x_active == o_active:
        return X
    # Caso contrário, é a vez do O
    else:
        return O
    
    
def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # Possíveis jogadas
    possible_moves = set()
    
    # Iterando pelo tabuleiro
    for i in range(3):
        for j in range(3):
            # Caso a posição esteja vazia, é possível jogar naquela posição
            if board[i][j] == EMPTY:
                possible_moves.add((i, j))
                
    return possible_moves                


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # Copia do tabuleiro original
    new_board = copy.deepcopy(board)
    
    # Informações referentes a jogada
    (i, j) = action
    
    if i < 0 or i > 2 or j < 0 or j > 2:
        raise "Move out of bounds"
    
    # Verifica a viabilidade da jogada
    if new_board[i][j] != EMPTY:
        # Lanca uma excecao caso seja uma jogada invalida
        raise "It's a invalid move"
    else:
        # Verifica de quem é a vez e marca o tabuleiro
        turn = player(board)
        new_board[i][j] = turn
        return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Verificacao horizontal
    for i in range(3):
        if board[i].count(X) == 3:
            return X
        elif board[i].count(O) == 3:
            return O
    # Verificacao vertical
    for i in range(3):
        count_x = 0
        count_o = 0
        for j in range(3):
            if board[j][i] == X:
                count_x += 1
            elif board[j][i] == O:
                count_o += 1
        
        if count_x == 3:
            return X
        elif count_o == 3:
            return O
        
    # Verificacao da diagonal secundaria
    if board[0][2] == X and board[1][1] == X and board[2][0] == X:
        return X
    elif board[0][2] == O and board[1][1] == O and board[2][0] == O:
        return O
    
    # Verificacao da diagonal principal
    count_x = 0
    count_o = 0
    for i in range(3):
        if board[i][i] == X:
            count_x += 1
        elif board[i][i] == O:
            count_o += 1
            
    if count_x == 3:
        return X
    elif count_o == 3:
        return O
    
    # Caso nao tenha um vencedor
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # Caso o jogo tenha um vencedor
    if winner(board) != None:
        return True
    
    # Caso haja espaço vazio no jogo sem um vencedor, o jo esta em progresso
    for i in range(3):
        if EMPTY in board[i]:
            return False
    # Caso contrario, o jogo acabou
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # Verifica se ha um vencedor no jogo
    result = winner(board)
    
    # Se X for o vencedor, utilidade = 1
    if result == X:
        return 1
    # Se O for o vencedor, utilidade = -1
    elif result == O:
        return -1
    # Caso seja empate, utilidade = 0
    return 0

# Maximiza a jogada (Jogador X) 


def max_value(board):
    # Melhor jogada
    optimal_action = None 
    
    # Caso base: Jogo finalizado
    if terminal(board):
        return utility(board), None
    
    v = float('-inf')
    
    # Analisa todas as possiveis jogadas
    for action in actions(board):
        # Escolhe o maior valor, tendo em vista que o oponente ira minimizar o jogo
        maximo, _ = min_value(result(board, action))
        if maximo > v:
            v = maximo
            optimal_action = action  
              
    return v, optimal_action

# Minimiza a jogada (Jogador O)


def min_value(board):
    # Melhor jogada
    optimal_action = None
    
    # Caso base: jogo finalizado
    if terminal(board):
        return utility(board), None
    
    v = float('inf')
    
    # Analisa todas as possiveis jogadas
    for action in actions(board):
        # Escolhe o menor valor, tendo em vista que o oponente ira maximizar o jogo
        minimo, _ = max_value(result(board, action))
        if minimo < v:
            v = minimo
            optimal_action = action
        
    return v, optimal_action
    
    
def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # Caso seja um tabuleiro finalizado, retorna none
    if terminal(board):
        return None
    
    # Caso seja a vez do jogador X
    if player(board) == X:
        return max_value(board)[1]
    
    # Caso seja a vez do jogador O
    elif player(board) == O:
        return min_value(board)[1]