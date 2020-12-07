#include <err.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/mman.h>

#include "mtwister.h"

#define CHK(fn, args...) ({        \
  int64_t val = (int64_t)fn(args); \
  if (val == -1)                   \
    err(1, "%s:%d: %s()", __FILE__, __LINE__, #fn); \
  val;                             \
})

char cmp[] = { 0x0f, 0x0b, 0xff };

int main(int argc, char **argv) {
  if (argc < 2) {
    printf("%s FILE", argv[0]);
    return 1;
  }

  int fd = CHK(open, argv[1], O_RDWR);
  uint64_t fsize = CHK(lseek, fd, 0, SEEK_END);
  CHK(lseek, fd, 0, SEEK_SET);
  char *file = (void*)CHK(mmap, 0, fsize, PROT_READ | PROT_WRITE, 
      MAP_SHARED, fd, 0);
  if (file == NULL)
    err(1, "mmap");

  for (uint64_t i = 0; i < fsize - sizeof(cmp); i++) {
    MTRand r;
    if (!memcmp(cmp, file + i, sizeof(cmp))) {
      printf("Found marker at EXE+0x%lx\n", i);
      seedRand(&r, i & 0xfff);
      ((int*)(file + i + 3))[0] ^= genRandLong(&r);
      ((int*)(file + i + 3))[1] ^= genRandLong(&r);
      i += 8 + sizeof(cmp);
    } else if (!memcmp("!!!", file + i, 3)) {
      file[i] = 0;
      file[i + 1] = 5;
      file[i + 2] = 0;
      i += 3;
      printf("Found string at EXE+0x%lx\n", i);
      seedRand(&r, i & 0xfff);
      char *s = file + i;
      while (*s) {
        *s ^= genRandLong(&r) | 0x80;
        //*s ^= rand() | 0x80;
        s++;
      }
    }
  }
}
