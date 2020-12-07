#!/bin/env python3
from string import ascii_uppercase as UC

# break.txt is a file that contains ~300 outputs or so, even from different sessions
lines = [e.strip() for e in open("break.txt").readlines()]

# Initially, all letters are possible candiates
candidates = [set(UC) for _ in range(len(lines[0]))]

# Remove seen letters
for line in lines:
    for i, e in enumerate(line):
        candidates[i] -= set(e)

# What's left is the flag
print("flag{" + ''.join(list(e)[0] for e in candidates) + "}")