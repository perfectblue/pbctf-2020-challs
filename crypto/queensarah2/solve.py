from challenge import S_box, encrypt, ALPHABET
from math import ceil, log, floor
from itertools import chain, product
from secretstuff import FLAG

ENC_FLAG = encrypt(FLAG)
BLOCK_LEN = 8

def decrypt(message, sbox):
    S_box_inv = {v: k for k, v in sbox.items()}
    message = list(message)
    rounds = int(2 * ceil(log(len(message), 2)))

    for round in range(rounds):
        # Decrypt
        for i in range(0, len(message), 2):
            message[i:i+2] = S_box_inv[''.join(message[i:i+2])]

        # Unshuffle, but not in the last round
        if round < (rounds-1):
            message = list(chain(*zip(message[:len(message)//2],message[len(message)//2:])))

    return ''.join(message)


# Method 2: encrypt all 4-"letter pair" messages and store them
A = {} # A['ab'] contains encryption of "abababab", permuted an extra time
B = {} # B['ab'] contains encryption of "aaaabbbb"
S_box_recovered = {}

def recover_sbox(key, value):
    S_box_recovered[key] = value
    assert S_box_recovered[key] == S_box[key]

for combo in product(ALPHABET, repeat=2):
    comb = ''.join(combo)

    # First "abababab"
    enc = encrypt(comb*BLOCK_LEN)
    # Permute an extra time
    enc = [enc[i] for i in range(len(enc)) if i%2 == 0] + [enc[i] for i in range(len(enc)) if i%2 == 1]
    A[comb] = ''.join(enc)

    # Then "aaaabbbb"
    message = comb[0]*BLOCK_LEN + comb[1]*BLOCK_LEN
    enc = encrypt(message)
    B[comb] = ''.join(enc)

# Look for pairs in a very specific place. Any pair is good enough, but here we just try until we get this exact one
A_uniq = [(k,e) for k,e in A.items() if (e[0:2]==e[2:4] and e[2:4]!=e[4:6] and e[2:4]!=e[6:8] and e[4:6]!=e[6:8])]
B_uniq = [(k,e) for k,e in B.items() if (e[0:2]==e[2:4] and e[2:4]!=e[4:6] and e[2:4]!=e[6:8] and e[4:6]!=e[6:8])]

check_queue = []

if len(A_uniq) == len(B_uniq) == 1:
    recover_sbox(A_uniq[0][0], B_uniq[0][0])
    for i in range(0, BLOCK_LEN*2, 2):
        a = A_uniq[0][1][i:i+2]
        b = B_uniq[0][1][i:i+2]
        check_queue.append((a, b))
        recover_sbox(a, b)

    while check_queue:
        cur_a, cur_b = check_queue.pop()
        for i in range(0, BLOCK_LEN*2, 2):
            if cur_b not in B: continue
            a = A[cur_a][i:i+2]
            b = B[cur_b][i:i+2]
            if a not in S_box_recovered:
                check_queue.append((a, b))
            recover_sbox(a, b)

    # Now we've recovered most of the Sbox, but there's ~16 orphaned values left.
    # Manually search for matching encryptions (slow)
    while len(S_box_recovered) < len(S_box):
        for a_v in A.values():
            a_segments = [a_v[i:i+2] for i in range(0, BLOCK_LEN*2, 2)]
            lookfor = [S_box_recovered.get(segment, "AA") for segment in a_segments]
            if "AA" in lookfor and lookfor.count("AA") == 1:
                print(f"Looking for a match for {a_segments[lookfor.index('AA')]}")
                b_cands = []
                for b_v in B.values():
                    equal = True
                    b_segments = [b_v[i:i+2] for i in range(0, BLOCK_LEN*2, 2)]
                    for a,b in zip(lookfor, b_segments):
                        if a!=b and a!="AA":
                            equal = False
                    if equal:
                        b_cands.append(b_segments[lookfor.index("AA")])
                print("cands", b_cands)
                if len(b_cands) == 1:
                    recover_sbox(a_segments[lookfor.index('AA')], b_cands[0])
                    break
        else:
            print("Nothing more to recover")
            break

    print(f"Flag: {decrypt(ENC_FLAG, S_box_recovered)}")


else:
    print("Could not find specific pattern, try again or try another one")