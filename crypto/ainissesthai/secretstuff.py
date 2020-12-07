from string import ascii_uppercase

# The only reason these are secret, is that it was painful to generate
# random, valid plugboard settings without confusing code.
PLUGBOARD_SETTINGS = 'BQ CR DI EJ KW MT OS PX UZ GH'
FLAG = open("flag.txt").read()
FLAG = FLAG[FLAG.index("{")+1:FLAG.index("}")]
assert all(e in ascii_uppercase for e in FLAG)

