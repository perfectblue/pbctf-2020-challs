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
  defplt bitstream
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

  ; Find length of argv[1]
  mov rdi, [rbp+0x30]
  mov rdi, [rdi + 8]
  mov [rbp-0x8], rdi
  call plt(strlen)

  ; Find first instance of '_' from end.
  mov ecx, eax
  mov al, '_'
  mov rdi, [rbp-0x8]
  lea rdi, [rcx + rdi - 1]
  std
  repne scasb 
  je .found

.bad:
  ; call main
  leave
  pop r12
  pop rbx
  ret

.found:
  inc rdi
  mov byte [rdi], 0
  inc rdi
  mov [rbp-0x8], rdi

  call plt(strlen)

  ; String must be non-zero, even number
  test eax, eax
  jz .bad

  test eax, 1
  jnz .bad

  shr eax, 1
  mov [rbp-0xc], eax

  mov edi, eax
  inc edi
  call plt(alloc)
  mov rdi, rax

  mov rsi, [rbp-0x8]
  mov ecx, [rbp-0xc]
  mov [rbp-0x8], rdi
  
.unhex_loop:
  mov al, [rsi]
  call .tohex
  mov dl, al
  shl dl, 4

  mov al, [rsi+1]
  call .tohex
  or dl, al

  mov [rdi], dl
  
  inc rdi
  add rsi, 2
  dec ecx
  jne .unhex_loop

  ; Obtain sym mod_start
  lea rdi, [thunk(s_modstart)]
  lea rsi, [thunk(got_modstart)]
  call plt(dl_find)

  ; Save old mod_start, set new mod_start
  mov rdx, [rax]
  mov [rbp-0x10], rdx
  lea rdx, [thunk(data)]
  mov [rax], rdx

  mov rdi, [rbp-0x8]
  lea rsi, [thunk(check)]
  call plt(bitstream)
  test byte [thunk(.is_bad)], 0xff
  jne .skip

  ; Obtain sym mod, and decode bitstream
  lea rdi, [thunk(s_mod)]
  lea rsi, [thunk(got_mod)]
  call plt(dl_find)

  mov rdi, [rbp-0x8]
  mov rsi, rax
  call plt(bitstream)
.skip:

  ; Restore mod_start
  mov rax, [thunk(got_modstart)]
  mov rdx, [rbp-0x10]
  mov [rax], rdx
  ;int3

  ; Now compare strings.
  lea rdi, [thunk(data)]
  lea rsi, [thunk(valid)]
  mov edx, len(valid)
  call plt(strncmp)

  ;int3
  db 0x0c ; or al, .is_bad
  .is_bad: db 0

  test eax, eax
  jne .bad

  ; Prepare init section for phase 2 on heap
  mov edi, init2_len
  call plt(alloc)
  mov [rbp-0x8], rax
  mov rdi, rax
  lea rsi, [thunk(init2)]
  mov edx, init2_len
  call plt(memcpy)

  ; Return to bitstream
  mov rdi, [rbp-0x8]
  mov rsi, [thunk(got_mod)]
  leave
  pop r12
  ret


.tohex:
  mov al, al
  cmp al, '0'
  jb .bad2
  cmp al, '9'
  ja .letter

; number
  sub al, '0'
  ret

.letter:
  cmp al, 'a'
  jb .bad2
  cmp al, 'f'
  ja .bad2
  
  sub al, 'a' - 10
  ret

.bad2:
  pop rax
  jmp .bad

check:
  push r12

  prep_thunk

  mov edx, edi
  
  dec byte[thunk(.ct)]

.S_begin:
  ; Jump to current state
  db 0xb0 ; mov al, .state
  .state: db 0x1
  movzx eax, al

  mov rax, [thunk(.check_jmp) + rax * 8]
  lea rax, [rax + thunk(0)]
  jmp rax
.Sxxx:
  db 0x35
.S0_0:
  db 0xb0 ; mov al, .tmp
  .tmp: db 0
  shl al, 1
  add al, dl
  mov byte [thunk(.tmp)], al

  mov dl, 0
  jmp .S_end_ct

.S0_1: ; ct == 0
  mov al, byte [thunk(.tmp)]
  and al, 0xf
  mov byte [thunk(.ct)], al ; ct = tmp + 1
  mov dl, 3
  jmp .S_next_ct

.S0_2: ; tmp == 0
  mov al, 1
  jmp .S_end

.S0_3: ; assert edi == 1
  mov eax, 1
  test edi, edi
  je .fail
  jmp .ret

.S1_0: ; tmp != 0, ct != 0
  test edi, edi
  setne al
  inc al
  jmp .S_next

.S1_1: ; edi == 0
  inc byte [thunk(.zeros)]
  mov byte [thunk(.consec_ones)], 0
  mov al, 2
  jmp .S_next

.S1_2: ; edi != 0
  inc byte [thunk(.consec_ones)]
  ; fall through

.S1_3:
  mov dl, -3 
  jmp .S_end_ct
  
.S1_4: ; ct == 0, assert edi == 0
  mov esi, 0xdeadbeef

  db 0xb0 ; mov al, .zeros
  .zeros: db 0
  cmp al, 8
  cmovne edi, esi

  db 0xb0 ; mov al, .consec_ones
  .consec_ones: db 0
  cmp al, 1
  cmova edi, esi

  mov byte [thunk(.zeros)], 0
  mov byte [thunk(.consec_ones)], 0

  xor eax, eax
  test edi, edi
  jne .fail
  jmp .ret
.fail:
  mov byte [thunk(main.is_bad)], 1
  jmp .ret
  
.check_ct: ; essentially jne_ct
  db 0xb1 ; mov cl, .ct
.ct: db 4
  test cl, cl
  mov al, 1
  cmovne eax, edx
  ret

.S_next_ct:
  call .check_ct

.S_next:
  add byte [thunk(.state)], al
  jmp .S_begin

.S_end_ct:
  call .check_ct

.S_end:
  add byte [thunk(.state)], al

  xor eax, eax
.ret:
  pop r12
  ret
.check_jmp: ptr .Sxxx, .S0_0, .S0_1, .S0_2, .S0_3, .S1_0, .S1_1, .S1_2, .S1_3, .S1_4


s_mod: db "mod", 0
s_modstart: db "mod_start", 0

got_modstart: dq 0
got_mod: dq 0

init2: 
  incbin 'phase2.bit'
init2_len: equ $ - init2

str valid, ":3 awesome"

data:
