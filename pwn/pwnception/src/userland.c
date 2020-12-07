#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>

size_t do_read(char *buf, size_t size)
{
  return read(0, buf, size);
}

size_t do_write(char *buf, size_t size)
{
  return write(1, buf, size);
}

char banner[] = "Give me some bf (end with a !): ";
char error[] = "Error reading\n";
char done[] = "You said: ";

char program[0x1000] = {0};

size_t get_program(char *program, size_t len)
{
  char c = 0;
  char *p = program;
  size_t size = 0;
  while (c != '!' && size < len)
  {
    size_t ret = do_read(&c, 1);
    if (ret != 1)
    {
      do_write(error, sizeof(error));
      return -1;
    }
    *p++ = c;
    size++;
  }
  program[size - 1] = 0;
  return size;
}

int run()
{
  char stack[0x1000] = {0};
  char data[0x1000] = {0};

  size_t size = get_program(program, sizeof(program) - 1);

  size_t pc = 0;
  size_t sp = 0;
  char *ptr = data;

  size_t ticks = 0;

  while (pc <= size)
  {
    ticks++;
    if (ticks > 0x100000)
    {
      char msg[] = "too many ticks\n";
      do_write(msg, sizeof(msg) - 1);
      return -1;
    }

    // char buf[0x100];
    // int n = sprintf(buf, "running 0x%04lx: '%c' (%ld)\n", pc, program[pc], ticks);
    // do_write(buf, n);

    switch (program[pc])
    {
    case '>':
      ++ptr;
      break;
    case '<':
      --ptr;
      break;
    case '+':
      ++*ptr;
      break;
    case '-':
      --*ptr;
      break;
    case '.':
      do_write(ptr, 1);
      break;
    case ',':
      do_read(ptr, 1);
      break;
    case '[':
      if (*ptr)
      {
        stack[sp++] = pc;
      }
      else
      {
        size_t count = 0;
        while (pc < size)
        {
          pc++;
          if (program[pc] == '[')
          {
            count++;
          }
          else if (program[pc] == ']')
          {
            if (count)
            {
              count--;
            }
            else
            {
              break;
            }
          }
        }
      }
      break;
    case ']':
      pc = stack[--sp] - 1;
      break;
    default:
      break;
    }
    pc++;
  }

  return 0;
}

int main()
{
  do_write(banner, sizeof(banner) - 1);
  return run();
}
