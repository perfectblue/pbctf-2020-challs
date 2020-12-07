#define _GNU_SOURCE

#include <err.h>
#include <errno.h>
#include <fcntl.h>
#include <stdarg.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/reg.h>
#include <sys/ucontext.h>
#include <openssl/md5.h>
#include <openssl/sha.h>

#include "flag1.h"
#include "safeguard.h"
#include "mtwister.h"
#include "trap.h"

char hash[50];

#define CSTR "!!!"

static inline const char *crypt_str(const char *s) {
  return (const char*)TRP(TRP_CRYPT, (uint64_t)s);
}

#define setbuf _setbuf
static inline void setbuf(FILE *stream, char *buf) {
  TRP(TRP_SETBUF, (uint64_t)stream, (uint64_t)buf);
}

#define fopen _fopen
static inline FILE *fopen(const char *name, char *opts) {
  return (FILE*)TRP(TRP_FOPEN, (uint64_t)name, (uint64_t)opts);
}

#define fgets _fgets
static inline char *fgets(char *buff, uint64_t size, FILE *f) {
  return (char*)TRP(TRP_FGETS, (uint64_t)buff, size, (uint64_t)f);
}

#define fread _fread
static inline char *fread(void *buff, uint64_t size, FILE *f) {
  return (char*)TRP(TRP_FREAD, (uint64_t)buff, size, (uint64_t)f);
}

#define fseek _fseek
static inline char *fseek(FILE *f, long offset, int whence) {
  return (char*)TRP(TRP_FSEEK, (uint64_t)f, offset, whence);
}

#define fwrite _fwrite
static inline char *fwrite(void *buff, uint64_t size, FILE *f) {
  return (char*)TRP(TRP_FWRITE, (uint64_t)buff, size, (uint64_t)f);
}

static inline void seedRand0(MTRand* r, unsigned long seed) {
  TRP(TRP_RSEED, (uint64_t)r, seed);
}

unsigned long genRandLong0(MTRand* rand) {
  return TRP(TRP_RAND, (uint64_t)rand);
}

static inline int c_printf(const char *msg, ...) {
  va_list args;

  ENTER;
  va_start(args, msg);
  int ret = vprintf(crypt_str(msg), args);
  ENTER;
  crypt_str(msg);
  va_end(args);
  LEAVE;
  LEAVE;

  return ret;
}

#define PASS_SIZE 100
char easy[PASS_SIZE];

__attribute__((constructor)) static void init() {
  char buff[0xf00];
  memset(buff, 0xcc, sizeof(buff));
  sprintf(buff, "TMP_%d", getpid());
  getenv(buff);
}


int main(int argc, char **argv) {
  unlink(argv[0]);

#define pass (_pass + 3)
  char _pass[PASS_SIZE + 3];
  char flag[32];
  char chksum[16];
  char chksum2[33];
  unsigned long seed;

  init_safeguard();
  setbuf(stdin, NULL);
  setbuf(stdout, NULL);
  setbuf(stderr, NULL);

  ENTER;
  c_printf(CSTR "First password: ");
  memcpy(_pass, CMARK, 3);

  ENTER;
  fgets(pass, PASS_SIZE, stdin);

  LEAVE;
  LEAVE;

  ENTER;
  MD5((unsigned char*)pass, strlen(pass), (unsigned char*)chksum);
  for (int i = 0; i < sizeof(chksum); i++) {
    sprintf(chksum2 + i * 2, crypt_str(CSTR"%02hhx"), chksum[i]);
    crypt_str(NULL);
  }
  const char *hash = CSTR FLAG1_HASH;
  if (strcmp(chksum2, crypt_str(hash))) {
    c_printf(CSTR"Failed\n");
    return 1;
  }
  ENTER;
  crypt_str(hash);
  LEAVE;
  ENTER;
  memset(chksum, 0, sizeof(chksum));
  memset(chksum2, 0, sizeof(chksum2));
  LEAVE;

  strcpy(easy, pass);

  ENTER;
  FILE *frd = fopen(crypt_str(CSTR "/dev/urandom"), "r");
  fread(&seed, sizeof(seed), frd);
  crypt_str(NULL);

  ENTER;
  c_printf(CSTR"Second password: ");
  LEAVE;

  ENTER;
  fgets(pass, PASS_SIZE, stdin);
  LEAVE;

  ENTER;
  FILE *tmp = fopen(crypt_str(CSTR"/tmp/secure"), "w+");
  crypt_str(NULL);
  setbuf(tmp, NULL); // Make sure we don't leak password
  LEAVE;

  ENTER;
  fwrite(pass, PASS_SIZE, tmp);
  LEAVE;

  LEAVE;

  ENTER;
  crypt_str(_pass);

  for (int i = 0; i < PASS_SIZE; i++)
    pass[i] ^= easy[i];

  // You can recover mersenne twister right??
  ENTER;
  MTRand r;
  seedRand0(&r, seed);
  seed = 0;
  int v = genRandLong0(&r) & 0xfff;
  for (int x = 0; x < v; x++) {
    ENTER;
    for (int i = 0; i < PASS_SIZE; i++) {
      pass[i] ^= (char)genRandLong0(&r);
    }
    LEAVE;
  }
  LEAVE;
  
  ENTER;
  // Might return NULL!!!
  FILE *flag_file = fopen(crypt_str(CSTR"flag.enc"), "r"); // DECRYPT IT using second password.
  crypt_str(NULL);
  LEAVE;

  fseek(tmp, 0, SEEK_SET);
  fread(flag, sizeof(flag), flag_file);
  LEAVE;
  fread(pass, PASS_SIZE, tmp);
  SHA256((unsigned char *)pass, PASS_SIZE, (unsigned char *)chksum2);
  for (int i = 0; i < sizeof(flag); i++) {
    flag[i] ^= chksum2[i];
  }

  c_printf(CSTR"The flag is: %s.\n", flag);
}
