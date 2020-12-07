%use smartalign


; ******************************************************************
; cxor macro: takes two strings and computes the xor of them
%imacro cxor 2
  %ifnstr %1
    %error "Argument must be a string."
  %elifnstr %2
    %error "Argument must be a string."
  %else
    %strlen __a__ %1
    %strlen __b__ %2

    %if __a__ != __b__
      %error "Strings are not same length."
    %else
      %assign __ind__ 1
      %rep __a__
        %substr __ac__ %1 __ind__
        %substr __bc__ %2 __ind__
        db __ac__ ^ __bc__
        %assign __ind__ __ind__ + 1
      %endrep
    %endif
  %endif
%endmacro

; ******************************************************************
; callx macro: makes an eXtended call; just like a regular call but 
;              more convoluted
%imacro callx 1
  %ifndef __has_callx__
    %fatal "Must declare USE_CALLX to use callx macro"
  %endif
  mov rax, %1
  call __fff
%endmacro
%imacro use_callx 0
  [section .text]
  %define __has_callx__
  %if $$ - $ != 0
    %error "USE_CALLX must come before any other instructions"
  %endif
    db 0x35
  __fff:
    jmp rax

  __SECT__
%endmacro

; ******************************************************************
; thunk macro: creates positional-independent code
%define thunk(sym) r12 + sym - .thunk 
%imacro prep_thunk 0
  
  %ifndef __has_callx__
    call .ggg
  %else
    callx .ggg
  %endif
  .thunk:
    db 0x0f
  .ggg:
    pop r12
%endmacro

; ******************************************************************
; str macro: declares a string
%idefine len(sym) __l %+ sym
%imacro str 2+
  %1: db %2
  __l %+ %1: equ $ - %1
%endmacro

; ******************************************************************
; random byte macro: creates a random byte value
%assign __seed__ 0x31a4624d ; make this seed random
%imacro randbyte 0
  %assign __seed__ (__seed__ * 1103515245 + 12345) & 0xffffffff
  %assign __tmp__ __seed__ & 0xff
  db __tmp__
%endmacro
%imacro ralign 1
  ; check argument is a multiple of 2
  %assign __tmp__ %1
  %assign __sum__ 0
  %rep 64
    %assign __sum__ __sum__ + (__tmp__ & 1)
    %assign __tmp__ __tmp__ >> 1
  %endrep
  %if __sum__ != 1
    %error "Alignment not a power of 2."
  %endif

  ; compute alignment
  %assign __tmp__ %1 - 1
  %assign __align__ (($ - $$) + __tmp__) & ~__tmp__

  %rep __align__ - ($ - $$)
    randbyte
  %endrep
%endmacro

%imacro ptr 1+:
  %if __BITS__ == 32
    dd %1
  %elif __BITS__ == 64
    dq %1
  %else 
    %error "Invalid bit-mode"
  %endif 
%endmacro
  

; ******************************************************************
; symbol/linking macros
; This is a special plt linker. Note that our linker address is located
; physically before

%imacro linker_addr 1
  %ifdef __linker_addr
    %warning "Multiple linker definitions, ignoring second one."
  %else
    %define __linker_addr %1
  %endif
%endmacro

; Begin sym section
%imacro sym_sect 0
  %ifdef __has_sym__
    %error "Cannot declare multiple sym sections."
  %else
    %define __has_sym__
    %define __in_sym__
    %define sym_start __link_start
    [section .dyn]
__link_start: 
  %endif
%endmacro

; Defines a symbol
%imacro sym 1
  %ifndef __in_sym__
    %error "sym entries must be defined within SYM_SECT directive."
  %else
    %defstr __name__ %1

    [section .dynstr]
__str_exp_%1:
    db __name__, 0

    [section .dyn]
    ptr __str_exp_%1, %1

    __SECT__
  %endif
%endmacro

; End sym section
%imacro sym_endsect 0 
  %ifndef __in_sym__
    %error "Missing paired SYM_SECT directive."
  %else
    %undef __in_sym__

    [section .dyn]
    %if ($ - $$ & 0x3) != 0 
      %error "Misaligned dyn section."
    %endif
    ptr 0, 0

    __SECT__
  %endif
%endmacro

; binary header
STRUC BIN_HEADER
  .bnTextOff:    resd 1
  .bnDynOff:     resd 1
  .bnDynStrOff:  resd 1
  .bnGotOff:     resd 1
  .bnGotEntries: resd 1
  .__align__:    resd 1
  .bnLinker:     resq 1
ENDSTRUC

%imacro bin_init 0 
  section .text
  %ifdef __bin_inited__
    %warning "Binary has already been initialized."
  %elif $ - $$ != 0
    %error "Must declare bin_init at the top of the file."
  %else
    %define __bin_inited__
    %ifnidn __OUTPUT_FORMAT__, bin
      %fatal "Must be a binary format file."
    %endif
    org 0
    section .head start=0
    section .dyn
    section .dynstr
    section .got align=8
    section .text align=16 follows=.plt 
    section .plt align=16

    ; Header data
    [section .head]
    __head: ISTRUC BIN_HEADER
      AT BIN_HEADER.bnTextOff,    dd section..text.start
      AT BIN_HEADER.bnDynOff,     dd section..dyn.start
      AT BIN_HEADER.bnDynStrOff,  dd section..dynstr.start
      AT BIN_HEADER.bnGotOff,     dd section..got.start
      AT BIN_HEADER.bnGotEntries, dd __dyn_ent__
    IEND
  
    ; Create got entry for header
    section .got
__gott_head:
    dq 0

    section .dyn
    dd 0

    section .plt
__pltentry__:
    push qword [rel __gott_head ]
    jmp [rel __head + BIN_HEADER.bnLinker] ; FIXME: cannot be RIP-relative
    align 16
  %endif
  section .text
%endmacro

; Begin plt section
%imacro plt_sect 0
  %ifndef __bin_inited__
    %fatal "Binary format must be initialized already; use BIN_INIT directive."
  %endif

  %idefine plt(sym) __plt_ %+ sym
  %assign __plt_id__ 1
  %ifdef __has_plt__
    %error "Cannot declare multiple plt sections."
  %else
    %define __has_plt__
    %define __in_plt__
  %endif
%endmacro

; Defines a plt entry
%imacro defplt 1
  %ifndef __in_plt__
    %error "plt entries must be defined within PLT_SECT directive."
  %else
    %defstr __name__ %1

    [section .dynstr]
__stroff_imp_ %+ %1: equ $ - $$
    db __name__, 0

    [section .got]
__got_ %+ %1:
    dq __pltl_ %+ %1

    [section .dyn]
    dd __stroff_imp_ %+ %1

    [section .plt]
__plt_ %+ %1:
    jmp [rel __got_ %+ %1]
__pltl_ %+ %1:
    db 0x68
    dd __plt_id__ ; push __plt_id__
    jmp near __pltentry__
    
    %assign __plt_id__ __plt_id__ + 1
    __SECT__
  %endif
%endmacro

; End plt section
%imacro plt_endsect 0 
  %ifndef __in_plt__
    %error "Missing paired PLT directive."
  %else
    %undef __in_plt__

    [section .dyn]
    %if ($ - $$ & 0x3) != 0 
      %error "Misaligned dyn section."
    %endif
    __dyn_ent__: equ ($ - $$) >> 2

    __SECT__
  %endif
%endmacro



