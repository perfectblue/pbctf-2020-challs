BITS 64

DEFAULT REL

%include 'linux/syscall.inc'
%include 'tricks.inc'

bin_init
plt_sect
  defplt alloc
  defplt dl_find
  defplt memcpy
  defplt strlen
  defplt strncmp
plt_endsect

; Here are the elements that are on the stack:
; [rsp]      <re-linker>
; [rsp+0x08] main
; [rsp+0x10] ret to _start
; [rsp+0x18] argc
; [rsp+0x20] argv

section .text
main: 
  push r12
  push rbp
  mov rbp, rsp
  sub rsp, 0x10

  prep_thunk

  mov edi, [rbp+0x28]
  mov rsi, [rbp+0x30]
  cmp edi, 2
  jne .bad

  ; Determine length of arg[1]
  mov rdi, [rsi+0x8]
  mov [rbp-0x8], rdi
  call plt(strlen)
  cmp rax, flaglen 
  jne .bad2
.restart:
 
  ; Must end with '}'
  mov rdi, [rbp-0x8]
  cmp byte [rax + rdi - 1], '}'
  mov byte [rax + rdi - 1], 0 ; change '}' to null-terminator
  jne .bad

  cmp dword [rax + rdi - 5], '0401'
  je .skip_fudge
  mov dword [rdi + 6], 0xdeadbeef

.skip_fudge:

  ; Must begin with 'pbctf{'
  lea rsi, [thunk(head)]
  mov rdx, len(head)
  call plt(strncmp)
  test eax, eax
  jne .bad


  ; Strip out flag endings and copy into heap.
; mov edi, 0x100
; call plt(alloc)
; mov [rbp-0x10], rax
; mov rdi, rax
; mov rsi, [rbp-0x8]
; add rsi, len(head)
; mov edx, flaglen - len(head)
; call plt(memcpy)

  mov rdx, [rbp+0x30] ; argv
  add qword [rdx+8], len(head)

  ; Prepare init section for phase 1.5 on heap
  mov edi, init2_len
  call plt(alloc)
  mov [rbp-0x8], rax
  mov rdi, rax
  lea rsi, [thunk(init2)]
  mov edx, init2_len
  call plt(memcpy)

  ; Obtain sym mod
  lea rdi, [thunk(s_mod)]
  xor rsi, rsi
  call plt(dl_find)


  ; Return to bitstream
  mov rdi, [rbp-0x8]
  mov rsi, rax
  leave
  pop r12
  ret

.bad2:
  ; let's just continue 
  mov rdi, [rbp-0x8]
  mov dword [rdi + 5], 0xdeadbeef
  jmp .restart

.bad:
  ; call main
  leave
  pop r12
  pop rbx
  ret


flaglen: equ 86; TODO: replace this with actual length of flag
str msg, "Hello world", 0xa
str head, "pbctf{"
s_mod: db "mod", 0
init2: 
  incbin 'phase1_5.bit'
init2_len: equ $ - init2

