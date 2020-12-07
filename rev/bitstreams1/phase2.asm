BITS 64
DEFAULT REL

%define __OUTPUT_FORMAT__ elf64
%include 'nasmx.inc'
%define __OUTPUT_FORMAT__ bin
%include 'linux/syscall.inc'
%include 'tricks.inc'

bin_init

plt_sect
  defplt _dynlink ; base
  defplt bitstream
  defplt collect ; bit, size
  defplt dl_find
  defplt memcpy
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
  sub rsp, 8

  prep_thunk
  
  ; Prepare the mod function to xor the flag
  mov rdi, [key]
  mov rax, [rbp+0x30] ; argv
  mov rax, [rax+0x08]; argv[1]
  xchg [rax], rdi
  mov [key], rdi ; swap first 8 bytes of flag with a checker
  mov esi, flag_rounds
  mov rdx, rax
  call prepMod

  ; Xor the flag
  mov rdx, [rbp+0x30] ; argv
  mov rdi, [rdx+0x08] ; argv[1]
  mov rsi, rax
  call plt(bitstream)

  ; Check the first 8 bytes are correct
  mov rax, [rbp+0x30] ; argv
  mov rdx, [rax+0x08] ; argv[1]
  add qword [rax+0x8], 8 ; no need to check this part again.
  mov rax, [rdx]
  mov rdx, 'I_<3_Asm'
  cmp rax, rdx
  je .nobad
  add rbp, 8 ; pop something so that we return to main instead
.nobad:

  ; Prepare the mod function to decrypt phase3
  lea rdi, [s_dynStart]
  xor esi, esi
  call plt(dl_find)

  mov rdi, [thunk(key)]
  mov esi, init3_rounds
  mov rdx, rax
  call prepMod

  ; Return to re-linker and bitstream
  lea rdi, [thunk(init3)]
  mov rsi, rax

  db 0xc9 ; leave
  pop r12
  ret

s_dynStart: db "__dynStart", 0
flag_rounds: equ 4
align 8, db 0
key: cxor 'H0w_l0w_', 'I_<3_Asm'

PROC prepMod, uint64_t xorKey, uint32_t rounds, uint64_t addrStart
  uses r12
  locals
    local modAddr, uint64_t
  endlocals

  prep_thunk

  ; Find address of mod function
  lea rdi, [thunk(s_mod)]
  xor rsi, rsi
  call plt(dl_find)
  mov [var(.modAddr)], rax
  
  ; Copy mod binary into place
  mov rdi, rax
  lea rsi, [thunk(newmod)]
  mov edx, modlen
  call plt(memcpy)

  ; Push arguments to phase2_1
  push qword [argv(.addrStart)]
  mov eax, [argv(.rounds)]
  push rax
  push qword [argv(.xorKey)]
  
  mov rdi, [var(.modAddr)]
  call plt(_dynlink)
  pop rax ; address to newmod
ENDPROC

align 8
newmod: 
  incbin "phase2_1.bin"
  align 8
modlen: equ $ - newmod

init3:
  incbin "phase3.xor"
  align 8
init3_rounds: equ ($ - init3) >> 3

s_mod: db "mod", 0
