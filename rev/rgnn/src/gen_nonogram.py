#!/usr/bin/env python3

from z3 import *
import random
import string


def print_board(board):
    height, width = len(board), len(board[0])

    for i in range(height):
        s = ""
        for j in range(width):
            s += str(board[i][j]) + " "
        print(s)


def gen_hint(board):
    height, width = len(board), len(board[0])

    row_hint = [ [] for i in range(height) ]
    for i in range(height):
        last_col, count = board[i][0], 0
        for j in range(width):
            if last_col == board[i][j]:
                count += 1
            else:
                if last_col != 0:
                    row_hint[i].append((last_col, count))
                last_col, count = board[i][j], 1
        
        if last_col != 0:
            row_hint[i].append((last_col, count))

    col_hint = [ [] for i in range(width) ]
    for i in range(width):
        last_col, count = board[0][i], 0
        for j in range(height):
            if last_col == board[j][i]:
                count += 1
            else:
                if last_col != 0:
                    col_hint[i].append((last_col, count))
                last_col, count = board[j][i], 1
        
        if last_col != 0:
            col_hint[i].append((last_col, count))

    return row_hint, col_hint


# Gen with 4-color
def gen(height, width, seed=None):
    if seed is not None:
        random.seed(seed)
    
    board = [[ None for j in range(width) ] for i in range(height)]

    for i in range(height):
        for j in range(width):
            pool = [0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3]

            if i > 0 and board[i - 1][j] != 0:
                pool += [board[i - 1][j]] * 2
            if j > 0 and board[i][j - 1] != 0:
                pool += [board[i][j - 1]] * 2
            
            board[i][j] = random.choice(pool)
    
    print_board(board)

    row_hint, col_hint = gen_hint(board)
    return (height, width), row_hint, col_hint


def solve(size, row_hint, col_hint):
    height, width = size

    X = [ [ Int("X_{}_{}".format(i, j)) for j in range(width) ] for i in range(height)]
    R = [ [ ( Int("Rstart_{}_{}".format(i, j)), Int("Rend_{}_{}".format(i, j)) ) for j in range(len(row_hint[i])) ] for i in range(height) ]
    C = [ [ ( Int("Cstart_{}_{}".format(i, j)), Int("Cend_{}_{}".format(i, j)) ) for j in range(len(col_hint[i])) ] for i in range(width) ]
    sol = Solver()

    for i in range(height):
        for j in range(len(row_hint[i])):
            sol.add( And(0 <= R[i][j][0], R[i][j][0] < width) )
            sol.add( And(0 <= R[i][j][1], R[i][j][1] < width) )
            sol.add( R[i][j][1] == R[i][j][0] + row_hint[i][j][1] - 1)
        
        for j in range(len(row_hint[i]) - 1):
            # If color is not same
            if row_hint[i][j][0] != row_hint[i][j + 1][0]:
                sol.add( R[i][j][1] < R[i][j + 1][0] )
            # If color is same
            else:
                sol.add( R[i][j][1] + 1 < R[i][j + 1][0] )
        
        for j in range(width):
            zero_cond = True
            for k in range(len(row_hint[i])):
                sol.add( If( And(R[i][k][0] <= j, j <= R[i][k][1]), X[i][j] == row_hint[i][k][0], True) )
                zero_cond = And(zero_cond, Not(And(R[i][k][0] <= j, j <= R[i][k][1])))
            sol.add( If(zero_cond, X[i][j] == 0, True) )
    
    for i in range(width):
        for j in range(len(col_hint[i])):
            sol.add( And(0 <= C[i][j][0], C[i][j][0] < height) )
            sol.add( And(0 <= C[i][j][1], C[i][j][1] < height) )
            sol.add( C[i][j][1] == C[i][j][0] + col_hint[i][j][1] - 1)
        
        for j in range(len(col_hint[i]) - 1):
            # If color is not same
            if col_hint[i][j][0] != col_hint[i][j + 1][0]:
                sol.add( C[i][j][1] < C[i][j + 1][0] )
            # If color is same
            else:
                sol.add( C[i][j][1] + 1 < C[i][j + 1][0] )
        
        for j in range(height):
            zero_cond = True
            for k in range(len(col_hint[i])):
                sol.add( If( And(C[i][k][0] <= j, j <= C[i][k][1]), X[j][i] == col_hint[i][k][0], True) )
                zero_cond = And(zero_cond, Not(And(C[i][k][0] <= j, j <= C[i][k][1])))
            sol.add( If(zero_cond, X[j][i] == 0, True) )
    
    sol_count = 0
    solutions = []

    print("Checking")

    while sol_count < 4 and sol.check() == sat:
        model = sol.model()
        board = [ [ model[X[i][j]].as_long() for j in range(width) ] for i in range(height) ]

        solutions.append(board)
        sol_count += 1

        print("sol_count=", sol_count)

        cond = True
        for i in range(height):
            for j in range(width):
                cond = And(cond, X[i][j] == board[i][j])
        
        sol.add(Not(cond))
    
    return sol_count, solutions


# 1. Nonogram generation

# while True:
#     size, row_hint, col_hint = gen(50, 50)
#     print(row_hint)
#     print(col_hint)
#     count, sol = solve(size, row_hint, col_hint)

#     print("====")

#     if count <= 2:
#         break

# 2. Testing generated nonogram

with open('resource/nonogram.txt', 'r') as f:
    data = f.read()

board = []
for line in data.split('\n'):
    arr = []
    for value in line.split(' '):
        if len(value) > 0:
            arr.append(int(value))
        if len(arr) == 50:
            break
    board.append(arr)
    if len(board) == 50:
        break
    
row_hint, col_hint = gen_hint(board)

# count, sol = solve((50, 50), row_hint, col_hint)

# print(count)

# 3. Print as C array

# for i in range(50):
#     arr = []
#     for j in range(40):
#         if len(row_hint[i]) <= j:
#             arr.append("{5, 5}")
#         else:
#             arr.append("{{{}, {}}}".format(row_hint[i][j][0], row_hint[i][j][1]))
    
#     print('    {' + ', '.join(arr) + '},')

# print("====================")

# for i in range(50):
#     arr = []
#     for j in range(40):
#         if len(col_hint[i]) <= j:
#             arr.append("{5, 5}")
#         else:
#             arr.append("{{{}, {}}}".format(col_hint[i][j][0], col_hint[i][j][1]))
    
#     print('    {' + ', '.join(arr) + '},')



