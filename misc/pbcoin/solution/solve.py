#cipher = "vw=9<"+chr(0x0002)+"'f\t"+chr(0x0010)+"W|!>'"+chr(0x0015)+chr(0x0018)+"y"+chr(0x001c)+chr(0x0014)
#print "Challenge: "+str(cipher.encode('hex'))
cipher ="76773d393c0227660910577c213e271518791c14".decode('hex')
seed = "rodl"                           # players should recover it by bruting it against hmacsha256
len_cipher = len(cipher)
offset = len_cipher - 2
cipher = list(cipher)
cipher[offset-8] = chr(ord(seed[2]) ^ ord(cipher[offset-8])^ ord(seed[3]) ^ ord(cipher[offset-4]))
cipher[offset-2] = chr(ord(seed[0]) ^ ord(cipher[offset-2]) ^ ord(seed[1]) ^ ord(cipher[offset-6]))
arr_num = [39,13,93,45,59,68,77,5,2,7]    # Must be retrieved carefully from memory array
blk_num = 72
for i in xrange(0, len_cipher):
    cipher[i] = chr((ord(cipher[i])^arr_num[(i+5)%10])^(72))
    print cipher
print "".join(cipher).encode('hex')
dice =  "".join(cipher)

print dice
def decrypt_rotx(ET):
    encrypted_text = ET.lower()
    number = 7
    text = "abcdefghijklmnopqrstuvwxyz"
    final = ""
    finaldecrypted = ''
    rotation = text[number:] + text[:number]

    for i in range(len(encrypted_text)):
        if encrypted_text[i].isalpha():
            final = text[rotation.index(encrypted_text[i])]
            finaldecrypted += final
        else:
            finaldecrypted += encrypted_text[i]
    return finaldecrypted

print "pbctf{"+decrypt_rotx(dice)+"}"

# pbctf{skillfulevmremasterz}