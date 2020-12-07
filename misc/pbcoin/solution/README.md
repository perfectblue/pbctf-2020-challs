# Solution

My intention is that the players use static analysis using existing available decompilers (I won't point out the names), or opcode tools or plugins for well known disassemblers like Ethersplay.

The next step players should look is at the ABI to conclude where to look for functions. There are some filler functions like SHA-1 which increases the byte-code size but is never called during the encrypt function.

PUSH32 strings are important as it gives away information about certain constants. For example: Players can notice HMAC-SHA256 and SHA1 is implemented in the code. The hash is also pushed on the stack. Players can check that the seed size is 4 which is easily brute-forceable locally from 0000-ffff while using that against the hardcoded message to brute the HMAC-SHA256 Hash.

Once, the seed is recovered, players should understand that XOR encryption is used. Players can reverse the commutative property of the XOR (and abuse it) to retrive certain bits and pieces of the ciphertext. 

There is an array defined in `assembly` purely which should be trivial to spot in the byte code and player can see it performs xor on each byte. 

Once, Player clears all the XOR specific portion. They will get an ASCII text. Thereafter, they can choose to reverse the ROT-7 function or just guessgod it (as it's trivial and not even require reversing).