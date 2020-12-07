#define _TRP(regs...) ({ \
    int64_t ret; \
    asm volatile("int3" : "=a"(ret) : regs : "memory"); \
    ret; \
  })

#define TRP0(trapnum) _TRP("a"(trapnum)) 
#define TRP1(trapnum, a1) _TRP("a"(trapnum), "D"(a1)) 
#define TRP2(trapnum, a1, a2) _TRP("a"(trapnum), "D"(a1), "S"(a2)) 
#define TRP3(trapnum, a1, a2, a3) _TRP("a"(trapnum), "D"(a1), "S"(a2), "d"(a3)) 

#define _TRPTYPE(a, b, c, d, e, ...) e
#define TRP(...) _TRPTYPE(__VA_ARGS__, TRP3, TRP2, TRP1, TRP0)(__VA_ARGS__)

#define TRP_SETBUF 0
#define TRP_FGETS  1
#define TRP_CRYPT  2
#define TRP_FOPEN  3
#define TRP_FREAD  4
#define TRP_FWRITE 5
#define TRP_FSEEK  6
#define TRP_RSEED  7
#define TRP_RAND   8
