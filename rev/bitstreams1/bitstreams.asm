; See if you can RE(ad) me!
; This uses nasmx + nasm

section .text   progbits alloc exec   nowrite align=4096
section .data   progbits alloc noexec write   align=4
section .bss    nobits   alloc noexec write   align=4
section .rodata progbits alloc noexec nowrite align=8
section .dynstr progbits alloc noexec nowrite align=4
section .dyn    progbits alloc noexec nowrite align=8

%include 'nasmx.inc'
%include 'linux/syscall.inc'
%include 'tricks.inc'

sym_sect
  sym __dynStart
  sym _dynlink
  sym abort
  sym alloc
  sym bitstream
  sym collect
  sym dl_find
  sym getData
  sym memcpy
  sym mod
  sym strcmp
  sym strncmp
  sym strlen
  sym mod_start
sym_endsect

section .text
__nonx_begin:

USE_CALLX

section .dyn

section .data
  str fail_msg,  "You failed. The flag is incorrect.", 0xa
  str good_msg,  "Good! This flag is correct!", 0xa
  str usage_msg, "Usage: ", 0
  str usage2_msg, " <flag>", 0xa
  align 0x8
__heap_top: ptr 0
__heap_brk: ptr 0

section .rodata
init:
  ; prints hello world
  incbin 'phase1.bit'
section .text
  ; Some random bytes
  db 0x35, 0x60, 0x01, 0x52, 0x69

__dynStart:
  prep_thunk
  
  mov rdi, init
  mov rsi, mod

  callx __retmain ; push address of main
  jmp __prep
  ralign 0x1000
  db 0xf
  ralign 0x1000
__dynEnd:
  db 0x0f
  
__retprep:
  pop rax
  call __fff
__prep:
  callx __retprep ; push address of this procedure to relink after __dyn

  prep_thunk

  push __dynStart    ; store argument onto stack
  callx __retdynlink ; return to _dynlink after bitstream

  lea rax, [thunk(bitstream)]
  jmp rax

; ******************************************************************
; _dynlink(base): links the codebase at <base> for execution
__retdynlink:
  pop rax
  call __fff
  pop rdi
_dynlink:
  mov ecx, [rdi + BIN_HEADER.bnGotEntries]
  mov eax, [rdi + BIN_HEADER.bnGotOff]
  add rax, rdi

  ; Update .got entries from its pic offsets
  jmp .loopcond
.loop:
  dec rcx
  add [rcx * 8 + rax], rdi
.loopcond:
  test ecx, ecx
  jne .loop
  
  ; Update linker address
  mov qword [rdi + BIN_HEADER.bnLinker], _dl_resolve

  ; Jump to code entry point
  mov eax, [rdi + BIN_HEADER.bnTextOff] 
  add rax, rdi
  jmp rax

; ******************************************************************
; bitstream(BYTE PTR stream, (bool (*)(bool)) acpt): reads from the bitstream 
;   bit by bit, and invokes the acpt PROC for each bit until the acpt 
;   procedure returns false (to terminate the bitstream).
__retbitstream: ; Return to bitstream
  pop rax
  call __fff
PROC bitstream
uses rbx, r12, r13, r14
locals none
  mov rbx, rdi
  mov r12, rsi
  
.outerloop:
  mov al, byte [rbx] ; read in current byte
  movzx eax, al
  mov r13, rax   ; save it to r13
  mov r14, 8     ; we can shift 8 times right

.innerloop:
  
  ; DEBUG
;  mov rax, r13
;  and rax, 1
;  add rax, 0x30
;
;  mov [__xxx], al
;  syscall write, 1, __xxx, 1

  mov rdi, r13
  and rdi, 1
  call r12
  test eax, eax
  jz .end ; Terminiate bitstream

  shr r13, 1
  dec r14 ; decrement counter
  jnz .innerloop ; while r14 != 0

  inc rbx
  jmp .outerloop

.end:
ENDPROC

; ******************************************************************
; mod(bool bit): Modifies a memory section based on a continuous bitstream:
;   size (4 bits): 
;     The size of the modspec
;   modspec ((size + 1) bits):
;     shift left if bit == 0, otherwise, increment if bit == 1
;   preadd (1 bit):
;     determines whether to pre-add 1 to the next index
;   returns true to continue, false to terminate bitstream

section .rodata
  align 8, db 0
  mod_jmp    ptr mod.S0, mod.S1, mod.S2, mod.S3
  mod_jmp2   ptr mod.SS0, mod.SS1, mod.SS2

section .text

mod_start: ptr __dynStart

__xxx: db 0

mod:
  push rbp
  push rbx
  push r12 ; for thunk

  prep_thunk
  mov rbx, qword [thunk(mod_start)]
  sub rbx, 0xc
  mov edx, edi
  xor rbp, rbp

  ; Decrement count
  dec byte [thunk(.ct)]

  db 0xbe ; mov esi, .modind
  .modind: dd 0

  ; Jump to current state
  db 0xb0 ; mov al, .state
  .state: db 0x0
  movzx eax, al
  jmp [rax * 8 + mod_jmp]
.S0:
  ; Shift current bit into tmp.
  db 0xb0 ; mov al, .tmp
  .tmp: db 0x0
  shl al, 1
  add al, dl
  mov byte [thunk(.tmp)], al

  jmp .SX
.S1:
  callx .L2
  test edi, edi
  cmovne eax, ebx ; only move back when edi != 0, i.e. xchg is called
  ret
.L2:
;  test edi, edi
;  sete al
;  add byte [thunk(.zeros)], al

  mov eax, esi
  pop rsi
  
  mov ecx, 3   
  add edx, ecx ; ensure [rdx * 4 + rbx] is a valid address
  inc rbp


  test edi, edi ; test bit

  ; Special section. Runs two ways depending on ZF:
  ; ZF = 1:
  ;     75 01       jnz L0
  ;     d0 64 03 0c shl BYTE [rax + rbx + 0x0c], 1 ; ends up into fallthrough 
  ;                                                ; of 'je'
  ;     eb 01       jmp L1
  ;     ...
  ;   L1:
  ;     03 0c 93    add ecx, [rdx * 4 + rbx]
  ; ZF = 0:
  ;     75 01       jnz L0
  ;     ...
  ;   L0:
  ;     64 03 0c eb add ecx, fs:[rbx + rbp * 8]
  ;     01 7c 03 0c add dword [rbx + rax + 0xc], edi ; edi = 1
  ;     93          xchg ebx, eax
  ;   
  ; There is an additional way if we jump to inc:
  ; inc: 
  ;     01 d0       add eax, edx
  ;   L0:
  ;     64 03 0c eb add ecx, fs:[rbx + rbp * 8]
  ;     01 7c 03 0c add dword [rbx + rax + 0xc], edi ; edi could be 1/0
  ;     93          xchg ebx, eax
  db 0x75
.inc:
  db 0x01, 0xd0, 0x64, 0x03, 0x0c, 0xeb, 0x01, 0x7c, 0x03, 0x0c, 0x93
  
  ; Save new index
  call rsi ; revert modind to eax if needed
  mov dword [thunk(.modind)], eax
  jmp .SX
.S2:
;  test edi, edi
;  jne .bad
  mov edx, 1
  mov byte [rbx + rsi + 0xd], 0
  callx .L3
  xchg eax, ebx ; exchange ebx and eax
  ret
.L3:
  mov eax, esi
  pop rsi
  jmp .inc
.S3:
;  ; edi MUST be non-zero
;  test edi, edi
;  jne .ok
;.bad:
;  ;int3
;  mov rax, [thunk(mod_start)]
;  mov dword [rax], 0xdeadbeef
;.ok:

  ; Reset all states
  mov byte [thunk(.state)], 0
  mov byte [thunk(.ct)], 4
  mov dword [thunk(.modind)], 0
  xor eax, eax ; terminate loop
  pop r12
  pop rbx
  pop rbp
  ret
.SX: ; end switch
  db 0xb0 ; mov al, .ct
  .ct: db 0x4
  test al, al
  jne .SSX ; jump to .SSX if .ct != 0

  ; DEBUG
;  mov byte [thunk(__xxx)], 10
;  lea eax, [thunk(__xxx)]
;  syscall write, 1, __xxx, 1
  
  ; Jump to respective increment state.
  mov al, byte [thunk(.state)]
  inc byte [thunk(.state)] ; increment state
  movzx eax, al
  jmp [rax * 8 + mod_jmp2]
.SS0:
  ; Change state to 1, set the number of bytes to read as tmp
  mov al, byte [thunk(.tmp)]
  and al, 0xf

  ; If tmp == 0, change to state 3 instead.
  jne .nochange
  mov byte [thunk(.state)], 3
.nochange:

  add al, 1
  mov byte [thunk(.ct)], al
  jmp .SSX
.SS1: ; run inc code once only.
;  ; Check for correct number of zeros
;  db 0xb0 ; mov al, .ct
;  .zeros: db 0x0
;  cmp al, 8
;  jne .bad
;
;  mov byte [thunk(.zeros)], 0

  mov byte [thunk(.ct)], 1
  jmp .SSX
.SS2: ; reset state to 0, read 4 bytes
  mov eax, dword [thunk(.modind)]
  mov byte [thunk(.state)], 0
  mov byte [thunk(.ct)], 4
  jmp .SSX
  db 0x0f
.SSX:
  mov eax, 1 ; continue looping
  pop r12
  pop rbx
  pop rbp
  ret

; ******************************************************************
; collect(bool bit, uint32_t size)
PROC collect
locals none
  prep_thunk

  xor edx, edx
  db 0xb0 ; mov al, .bitind
.bitind: db 0x0
  inc al
  mov [thunk(.bitind)], al
  cmp al, sil
  jb .notdone
  mov [thunk(.bitind)], dl
  mov edx, 1
.notdone:

  and rdi, 1
  db 0x48, 0xb8 ; movabs rax, .value
.value: dq 0x0
  shl rax, 1
  or al, dil
  mov [thunk(.value)], rax
ENDPROC

  ralign 0x1000
__nonx_end:

; ******************************************************************
; _start()
global _start
_start:
  pop rdi
  mov rsi, rsp

  push rsi
  push rdi
  callx __unpackRun
  syscall exit, rax

; ******************************************************************
; main()
section .rodata
  
  encoded: incbin 'matB'
  __encoded_len: equ $ - encoded

section .text
  str author, "This challenge was created by theKidOfArcrania.", 0xa
__retmain: ; jump to main on return
  pop rax
  call __fff
  mov edi, [rsp+0x08] ; argc
  mov rsi, [rsp+0x10] ; argv
  lea rdx, [rsi + rdi * 8 + 8] ; envp
PROC main, uint32_t count, intptr_t args
locals none
  ;syscall write, 0x1, author, len(author)

  mov eax, [argv(.count)]
  cmp eax, 2
  jne .usage

  mov rax, [argv(.args)] ; argv
  mov rax, [rax + 8] ; argv[1]
  invoke strncmp, rax, encoded, __encoded_len
  test eax, eax
  jne .failed


  syscall write, 0x1, good_msg, len(good_msg)
  mov eax, 0
  jmp .end
.usage:
  syscall write, 0x1, usage_msg, len(usage_msg)
  
  mov rax, [argv(.args)]
  mov rdx, [rax] ; argv[0]
  invoke strlen, rdx
  mov rsi, rdx
  syscall write, 0x1, rsi, rax

  syscall write, 0x1, usage2_msg, len(usage2_msg)
  mov eax, 1
  jmp .end
.failed:
  syscall write, 0x1, fail_msg, len(fail_msg)
  mov eax, 1
.end:
ENDPROC

_dl_resolve:
  push r12
  mov r12, rsp

  push rdi
  push rsi
  push rdx
  push rcx
  push rax

  mov rax, [r12+0x08] ; bin_header
  mov rcx, [r12+0x10] ; entry index

  ; Get symbol name to search up
  mov edx, [rax + BIN_HEADER.bnDynOff]
  add rdx, rax ; address to dyn table
  mov edi, [rdx + rcx * 4] ; dyn entry
  add edi, [rax + BIN_HEADER.bnDynStrOff] ; str offset
  add rdi, rax ; address

  ; Obtain address of got entry
  mov edx, [rax + BIN_HEADER.bnGotOff]
  add rdx, rax ; address to got table
  lea esi, [rdx + rcx * 8] ; address of got entry

  call dl_find
  mov [r12+0x10], rax

  pop rax
  pop rcx
  pop rdx
  pop rsi
  pop rdi
  pop r12

  add rsp, 0x8 ; pop one argument (other one becomes return address)
  ret

; simple slab allocator
PROC alloc, size_t n
locals none

  mov rax, [__heap_top]
  test rax, rax
  je .init_brk
.back:
  
  mov rsi, [argv(.n)]
  mov rax, [__heap_brk]
  mov rdx, [__heap_top]
  
  lea rsi, [rdx + rsi + 7]
  and rsi, 0xfffffffffffffff8
  cmp rsi, rdx
  jbe .err

  cmp rsi, rax
  ja .brk

.no_brk:
  mov qword [__heap_top], rsi
  mov rax, rdx
  ret

.brk:
  mov rax, rsi
  add rax, 0xfff
  and rax, ~0xfff
  syscall brk, rax

  cmp rax, [__heap_brk]
  je .err

  mov [__heap_brk], rax
  jmp .no_brk

.init_brk:
  syscall brk, 0
  mov [__heap_top], rax
  mov [__heap_brk], rax
  jmp .back

.err:
  mov rax, 0
  ret
ENDPROC

section .rodata
  str dl_find_err, "dl_find: Unable to find function entry. Aborting...", 0xa

section .text
PROC dl_find, intptr_t name, intptr_t got
locals
  local ptr, intptr_t
endlocals
  mov qword [var(.ptr)], sym_start

  jmp .loop_cond
.loop:
  mov rax, [var(.ptr)]

  ; check if string field is equal
  mov rdx, [rax]
  mov rax, [argv(.name)]
  invoke strcmp, rax, rdx
  test eax, eax
  jne .loop_nomatch ; if they are not equal jump over.

  ; return found symbol
  mov rdx, [var(.ptr)]
  mov rax, [rdx + 8] ; get location of symbol
  mov rdx, [argv(.got)]
  test rdx, rdx
  jz .end
  mov [rdx], rax ; update .got entry
  jmp .end
.loop_nomatch:

  ; increment
  add qword [var(.ptr)], 0x10
.loop_cond: ; while str is not null
  mov rax, [var(.ptr)]
  mov rax, [rax]
  test rax, rax
  jne .loop
  syscall write, 2, dl_find_err, len(dl_find_err)
  call abort
.end:
ENDPROC

PROC abort
locals none
  syscall getpid
  syscall kill, rax, 6 ; SIGABRT
  ; If we get here, we need to restore sigaction for SIGABRT... too lazy to do
  ; that. Just exit now
  syscall exit, 12
ENDPROC

section .rodata
data:
  incbin 'matA'

section .text
getData:
  mov rax, data
  ret
  

PROC memcpy ; dst, src, n
locals none
  mov ecx, edx
  cld
  rep movsb
ENDPROC

PROC strlen, intptr_t a
locals none
  cld
  xor al, al
  mov ecx, -1
  repnz scasb
  not ecx
  dec ecx
  mov eax, ecx
ENDPROC

PROC strcmp, intptr_t a, intptr_t b
locals none
  mov rdi, [argv(.a)]
  mov rsi, [argv(.b)]
  xor ecx, ecx

.loop:
  mov al, [rdi + rcx]
  mov dl, al
  sub al, [rsi + rcx]
  movsx eax, al
  jne .end

  inc rcx
  test dl, dl
  jne .loop

  xor eax, eax
.end:
ENDPROC

PROC strncmp, intptr_t a, intptr_t b, size_t n
locals none
  mov rdi, [argv(.a)]
  mov rsi, [argv(.b)]
  mov ecx, [argv(.n)]
  xor eax, eax

  cld
  repz cmpsb
  je .end ; check if last comparison was equals
  mov al, [rdi-1]
  sub al, [rsi-1]
  movsx eax, al
.end:
ENDPROC

NASMX_PRAGMA PROC_FASTCALL_STACK_PRELOAD, DISABLE

; ******************************************************************
; __unpackRun()
PROC __unpackRun
locals none
  mov eax, 0x33
  mov fs, eax

  prep_thunk
  ; Disable NX for a section
  syscall mprotect, __nonx_begin, __nonx_end - __nonx_begin, 7

  pop rax
  lea rax, [thunk(__dynStart)]
  jmp rax
ENDPROC
