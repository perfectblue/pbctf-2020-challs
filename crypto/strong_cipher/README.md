# Strong Cipher

**Category**: Crypto

**Author**: rbtree

**Description**: 

Multiplication is better than addition.

**Hints**:
 * None.

**Public files**: 
 * dist/binary
 * dist/ciphertext

## Solution

The given binary uses a `GF2P8MULB` instruction, which multiplies each byte in
the finite field `GF(2^8)`, and the encryption algorithm is similar to the XOR
cipher or the Vigenère cipher.

Therefore, it's possible to solve the challenge by modifying an existing XOR
cipher solver, for example, hellman's xortool (https://github.com/hellman/xortool).

The given gf2p8multool is a modification of the xortool.

