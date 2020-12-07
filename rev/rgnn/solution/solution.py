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


with open('binary', 'rb') as f:
    f.seek(0x2040)
    row_hint = [ [] for _ in range(50) ]
    for i in range(50):
        for j in range(40):
            color, count = f.read(1)[0], f.read(1)[0]
            if color == 5:
                continue
            row_hint[i].append((color, count))

    f.seek(0x2FE0)
    col_hint = [ [] for _ in range(50) ]
    for i in range(50):
        for j in range(40):
            color, count = f.read(1)[0], f.read(1)[0]
            if color == 5:
                continue
            col_hint[i].append((color, count))

size = (50, 50)

count, sol = solve(size, row_hint, col_hint)
assert count == 1

with open('solution.txt', 'w') as f:
    for i in range(50):
        for j in range(50):
            f.write(str(sol[0][i][j]))
        f.write('\n')