#define _GNU_SOURCE
#include <err.h>
#include <stdint.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/ucontext.h>
#include <sys/mman.h>

#include "trap.h"
#include "safeguard.h"
#include "mtwister.h"

#define MAX_STACK 128
static uint64_t prev_faults[MAX_STACK];
static uint64_t nprev_faults = 0;
void seg_handler(siginfo_t *info, void *ucontext) {
  ucontext_t *cunt = ucontext;
  uint64_t rip = cunt->uc_mcontext.gregs[REG_RIP];

  // RESET_PERMS signal?
  if (info->si_addr == NULL) {
    if (memcmp(reset, (void*)rip, sizeof(reset) - 1)) {
      goto segfault;
    }

    for (int i = 0; i < nprev_faults; i++)
      CHK(mprotect, (void*)prev_faults[i], 0x1000, PROT_READ | PROT_EXEC);
    cunt->uc_mcontext.gregs[REG_RIP] += sizeof(reset) - 1; nprev_faults = 0;
  // We need to write/exec something that's not legal
  } else if (info->si_code == SEGV_ACCERR) {
    if (nprev_faults >= MAX_STACK) {
      abort_msg("Past MAX_STACK");
    }

    uint64_t addr = prev_faults[nprev_faults++] = (uint64_t)info->si_addr & ~0xfff; 
    CHK(mprotect, (void*)addr, 0x1000, PROT_READ | PROT_WRITE | PROT_EXEC);
  } else {
segfault:
    signal(SIGSEGV, SIG_DFL);
    kill(getpid(), SIGSEGV);
  }
  return;
}

static uint64_t prev_steps[MAX_STACK];
static uint64_t nprev_steps = 0;
void ill_handler(siginfo_t *info, void *ucontext) {
  ucontext_t *cunt = ucontext;
  uint64_t val;
  if (!cunt->uc_mcontext.gregs[REG_RAX]) {
    val = prev_steps[nprev_steps++] = cunt->uc_mcontext.gregs[REG_RIP];
  } else {
    val = prev_steps[--nprev_steps];
  }

  if (nprev_steps == -1)
    abort_msg("nprev_steps = -1");

  char *mem = (char*)val;
  MTRand r;
  seedRand(&r, val & 0xfff);
  ((int*)(mem + 3))[0] ^= (int)genRandLong(&r);
  ((int*)(mem + 3))[1] ^= (int)genRandLong(&r);

  cunt->uc_mcontext.gregs[REG_RIP] += 3;
  RESET_PERMS;
}

#define ireg(r) (cunt->uc_mcontext.gregs[REG_ ## r])
#define preg(r) ((void*)cunt->uc_mcontext.gregs[REG_ ## r])
#define xreg(r) (*(const void**)&cunt->uc_mcontext.gregs[REG_ ## r])
static const char *prev_str;
void trap_handler(siginfo_t *info, void *ucontext) {
  ucontext_t *cunt = ucontext;
  // ireg(RIP)++;
  switch (ireg(RAX)) {
    case TRP_SETBUF:
      ENTER;
      setbuf(preg(RDI), preg(RSI));
      break;
    case TRP_FGETS: 
    {
      ENTER;
      char *buff = preg(RDI);
      uint64_t i;
      for (i = 0; i < ireg(RSI) - 1; i++) {
        char c = fgetc(preg(RDX));
        if (c == EOF || c == '\n') break;
        else buff[i] = c;
      }
      buff[i] = 0;
      break;
    }
    case TRP_CRYPT: 
    {
      ENTER;
      const char *s = preg(RDI);
      if (!s) {
        s = prev_str;
        if (!s) xreg(RAX) = "";
      } else {
        prev_str = s;
      }

      char *ss = (char*)s;

      ENTER;
      if (memcmp(ss, CMARK, 3))
        abort_msg("Malformed marker.");
      ss += 3;
      LEAVE;
      
      ENTER;
      MTRand r;
      seedRand(&r, (uint64_t)ss & 0xfff);
      LEAVE;
      while (*ss) {
        ENTER;
        *ss ^= genRandLong(&r) | 0x80;
        ss++;
        LEAVE;
      }

      RESET_PERMS;
      xreg(RAX) = s + 3;
      break;
    }
    case TRP_FOPEN:
      ENTER;
      xreg(RAX) = fopen(preg(RDI), preg(RSI));
      break;
    case TRP_FREAD:
      ENTER;
      xreg(RAX) = (void*)fread(preg(RDI), 1, ireg(RSI), preg(RDX));
      break;
    case TRP_FWRITE:
      ENTER;
      xreg(RAX) = (void*)fwrite(preg(RDI), 1, ireg(RSI), preg(RDX));
      break;
    case TRP_FSEEK:
      ENTER;
      xreg(RAX) = (void*)(long)fseek(preg(RDI), ireg(RSI), ireg(RDX));
      break;
    case TRP_RSEED:
      ENTER;
      seedRand((MTRand*)preg(RDI), ireg(RSI));
      break;
    case TRP_RAND:
      ENTER;
      xreg(RAX) = (void*)genRandLong((MTRand*)preg(RDI));
      break;
  }

  LEAVE;
}

void handler(int signum, siginfo_t *info, void* ucontext) {
  switch (signum) {
    case SIGILL: ill_handler(info, ucontext); break;
    case SIGSEGV: seg_handler(info, ucontext); break;
    case SIGTRAP: trap_handler(info, ucontext); break;
    default: return;
  }
}

void init_safeguard() {
  struct sigaction act;
  act.sa_flags = SA_SIGINFO | SA_RESTART | SA_NODEFER;
  sigemptyset(&act.sa_mask);
  act.sa_sigaction = handler;
  CHK(sigaction, SIGILL, &act, NULL);
  CHK(sigaction, SIGTRAP, &act, NULL);

  act.sa_flags = SA_SIGINFO | SA_RESTART;
  sigemptyset(&act.sa_mask);
  sigaddset(&act.sa_mask, SIGSEGV);
  act.sa_sigaction = handler;
  CHK(sigaction, SIGSEGV, &act, NULL);
}
