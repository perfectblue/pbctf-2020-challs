#ifndef _SAFEGUARD_H
#define _SAFEGUARD_H

#include <stdlib.h>
#include <stdio.h>

#define ENTER asm("xor %%eax, %%eax; ud2; .byte 0xff" ::: "eax");
#define LEAVE asm("mov $1, %%eax; ud2; .byte 0xfe" ::: "eax");

#define RESET_PERMS_  "\xc7\x04\x25\x00\x00\x00\x00\xef\xbe\xad\xde"
#define RESET_PERMS__ "0xc7,0x04,0x25,0x00,0x00,0x00,0x00,0xef,0xbe,0xad,0xde"
#define RESET_PERMS asm volatile(".byte " RESET_PERMS__ ::: "memory")
static char reset[] = RESET_PERMS_;


#define CMARK "\0\x05\0"


#define CHK(fn, args...) ({        \
  int64_t val = (int64_t)fn(args); \
  if (val == -1)                   \
    err(1, "%s:%d: %s()", __FILE__, __LINE__, #fn); \
  val;                             \
})

#define CHK2(fn, args...) ({       \
  int64_t val = (int64_t)fn(args); \
  if (val == -1)                   \
    warn("%s:%d: %s()", __FILE__, __LINE__, #fn); \
  val;                             \
})

static inline void abort_msg(char *msg) {
  puts(msg);
  abort();
}

void init_safeguard();

#endif
