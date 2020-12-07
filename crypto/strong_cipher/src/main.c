#include <stdio.h>
#include <emmintrin.h>
#include <immintrin.h>
// #include <gfniintrin.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>

char key[32] = {0};
int key_len = 0;
char *plaintext;
int plaintext_len = 0;

void encrypt(char *plaintext, char *key) {
    __m128i pt = _mm_loadu_si128((__m128i *) plaintext);
    __m128i k = _mm_loadu_si128((__m128i *) key);
    __m128i res = _mm_gf2p8mul_epi8(k, pt);
    _mm_store_si128( (__m128i *) plaintext, res );
}

int main(int argc, char *argv[])
{
    if (argc != 4) {
        printf("./binary <key file> <plaintext file> <ciphertext file>");
        return 0;
    }

    // Read files

    int fd = open(argv[1], O_RDONLY);
    key_len = read(fd, key, 16);
    if (key_len <= 0) 
        return 0;
    close(fd);

    fd = open(argv[2], O_RDONLY);
    plaintext_len = lseek(fd, 0, SEEK_END);
    if (plaintext_len < 0)
        return 0;
    
    plaintext = (char *) malloc( (plaintext_len + 15) / 16 * 16 );
    lseek(fd, 0, SEEK_SET);

    int idx = 0;
    while (idx < plaintext_len) {
        int len = read(fd, plaintext + idx, 4096);
        idx += len;
    }
    close(fd);

    // Copy key for gf2p8mul instruction

    for (idx = key_len; idx < 32; idx++) {
        key[idx] = key[idx % key_len];
    }

    // Encrypt

    for (idx = 0; idx < plaintext_len; idx += 16) {
        encrypt(plaintext + idx, key + (idx % key_len));
    }
    
    // Save

    fd = open(argv[3], O_WRONLY | O_CREAT);
    idx = 0;
    while (idx < plaintext_len) {
        int len = write(fd, plaintext + idx, 1);
        idx += len;
    }
    close(fd);

    free(plaintext);

    return 0;
}