BITS 64
DEFAULT REL

%include 'nasmx.inc'
%include 'tricks.inc'

bin_init
plt_sect
  defplt collect ; bit, size
plt_endsect

; Here are the elements that are on the stack:
; [rsp]      <return to phase2>
; [rsp+0x08] xor-key
; [rsp+0x10] rounds
; [rsp+0x18] addrStart

section .text
main:
  pop rdx
  pop rax
  mov [newmod.xorkey], rax
  pop rax
  mov [newmod.rounds], eax
  pop rax
  mov [newmod.modaddr], rax

  call rdx

PROC newmod
uses r12
locals none
  prep_thunk
  
  mov esi, 64 ; size
  call plt(collect)
  test edx, edx ; check if fully collected...
  je .end_true ; not done

  ; Reverse the bits
  mov rdx, rax
  mov ecx, 64
.revloop:
  shl rax, 1
  test dl, 1
  je .noadd
  inc rax
.noadd:
  shr rdx, 1
  dec ecx
  jne .revloop
  db 0x48, 0xb9 ; movabs rcx, .xorKey
.xorkey: dq 0
  xor rax, rcx

  db 0x48, 0xb9 ; movabs rcx, .modaddr
.modaddr: dq 0
  mov [rcx], rax
  add qword [.modaddr], 8
  dec dword [.rounds]
  jne .end_true
  mov eax, 0
  jmp .end
.end_true:
  mov eax, 1
  jmp .end
.rounds:
  dd 0
.end:
ENDPROC


