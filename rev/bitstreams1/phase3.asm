BITS 64
DEFAULT REL

%include 'tricks.inc'

STRUC MATRIX
  .rows resd 1
  .cols resd 1
  .eles resd 0
ENDSTRUC

; Here are the elements that are on the stack:
; [rsp]      <re-linker>
; [rsp+0x08] main
; [rsp+0x10] ret to _start
; [rsp+0x18] argc
; [rsp+0x20] argv

%define __OUTPUT_FORMAT__ bin
bin_init

plt_sect
  defplt alloc
  defplt getData
plt_endsect

section .text
main:
  push r12
  push rbp
  mov rbp, rsp
  sub rsp, 0x10

  ; Allocate an matrix for flag
  mov rdi, MATRIX_size + 4 * flaglen
  call plt(alloc)

  ; Initialize matrix
  mov [rbp-0x8], rax ; flag src matrix
  mov dword [rax+MATRIX.rows], flaglen
  mov dword [rax+MATRIX.cols], 1
  add rax, MATRIX.eles
  
  mov rdx, [rbp+0x30] ; argv
  mov rdi, [rdx+0x8]  ; argv[1], flag dst
  mov [rbp-0x10], rdi

  ; compute f(i) = f(i) + f(i+1)
  mov byte [rdi + rcx + flaglen], 0
  mov ecx, 0
.addloop:
  mov dl, [rdi + rcx]
  add dl, [rdi + rcx + 1]
  movsx edx, dl
  mov [rax + rcx * 4], edx ; src[i] = argv[1][i] + argv[1][i+1]
  inc ecx
  cmp ecx, flaglen
  jne .addloop
  
  call plt(getData)
  mov rdi, rax
  mov eax, [rdi+MATRIX.rows]

  ; Turn argv[1] into a matrix
  mov rdx, [rbp-0x10]
  mov [rdx+MATRIX.rows], eax
  mov dword [rdx+MATRIX.cols], 1
  
  mov rsi, [rbp-0x08]
  call multiply
  
  leave
  pop r12
  pop rax ; go out to main
  ret

flaglen: equ 24

%define __OUTPUT_FORMAT__ elf64
%include 'nasmx.inc'
%include 'linux/syscall.inc'

;****************************************************
; multiply(MATRIX* a, MATRIX* b, MATRIX* out)
PROC multiply, uint64_t a, uint64_t b, uint64_t out
  uses rbx
  locals
    local rows, uint32_t
    local cols, uint32_t
    local inners, uint32_t
  endlocals

  ; assume rdi, rsi, rdx are not cleared
  ; Do some checks
  mov eax, [rdi+MATRIX.rows]
  mov [var(.rows)], eax
  cmp eax, [rdx+MATRIX.rows] ; a.rows == out.rows
  jne .fail
  mov eax, [rdi+MATRIX.cols]
  mov [var(.inners)], eax
  cmp eax, [rsi+MATRIX.rows] ; a.cols == b.rows
  jne .fail
  mov eax, [rsi+MATRIX.cols]
  mov [var(.cols)], eax
  cmp eax, [rdx+MATRIX.cols] ; b.cols == out.cols
  jne .fail

  mov rsi, rdx ; free up rdx register

  ; for each outer row
  mov r8d, 0 
  jmp .rowcond
.rowloop:
  ; for each outer column
  mov ecx, 0
  jmp .colcond
.colloop:
  ; for each inner element
  mov r9d, 0
  mov edi, 0 ; result of the inner product sums
.mult:
  mov eax, r8d
  mul dword [var(.inners)]
  add eax, r9d ; r * innerCols + inner
  mov esi, eax

  mov eax, r9d
  mul dword [var(.cols)]
  add eax, ecx ; inner * cols + c

  mov edx, [argv(.a)]
  mov esi, [edx + esi * 4 + MATRIX.eles] ; A[...]
  mov edx, [argv(.b)]
  mov eax, [edx + eax * 4 + MATRIX.eles] ; B[...]

  mul esi ; A[...] * B[...]
  add edi, eax ; add to sum
  inc r9d
.multcond:
  cmp r9d, [var(.inners)]
  jb .mult ; while r9d < inner

  ; Assign to out
  mov eax, r8d
  mul dword [var(.cols)]
  add eax, ecx ; r * cols + inner

  mov rdx, [argv(.out)]
  mov [rdx + rax * 4 + MATRIX.eles], edi ; Out[...] = edi

  inc ecx
.colcond:
  cmp ecx, [var(.cols)]
  jb .colloop ; while ecx < cols
  inc r8d
.rowcond:
  cmp r8d, [var(.rows)]
  jb .rowloop ; while r8d < rows

  mov rax, 1
  jmp .end
.fail:
  mov rax, 0
.end:
  leave
  ret
ENDPROC
