bits 64 
org 0xFFFFFFFF81000000

interupt_handlers:
jmp [.table + 0]
jmp [.table + 8]
jmp [.table + 16]
	.table:
	dq handle_boot, handle_syscall, handle_segfault

handle_boot:
	mov rsi, .msg
	mov rcx, .end_msg - .msg
	mov dx, 0x38f
	rep outsb
	pause

	.msg:
	db "Kernel has booted", 0xa
	.end_msg:

handle_segfault:
	mov rsi, .msg
	mov rcx, .end_msg - .msg
	mov dx, 0x38f
	rep outsb
	hlt

	.msg:
	db "Segmentation fault", 0xa
	.end_msg:

kernel_write:
	mov rcx, rsi
	mov rsi, rdi
	mov dx, 0x38f
	rep outsb
	ret

kernel_read:
	mov rcx, rsi
	mov dx, 0x38f
	rep insb
	ret

unimplemented:
	mov rsi, .msg
	mov rcx, .end_msg - .msg
	mov dx, 0x38f
	rep outsb
	ret

	.msg:
	db "Unimplemented", 0xa
	.end_msg:

handle_syscall:
	call [.syscall_table + rax * 8]
	iret

	align 32

	.read:
	mov rax, -1
	cmp rdi, 0
	jne .read_done

	mov r13, 0x800000000000
	cmp r13, rsi
	jbe .read_done

	mov r11, rdx
	mov rcx, rdx
	mov rdi, rsi
	mov dx, 0x38f
	rep insb
	.read_done:
	mov rax, r11
	ret

	.write:
	mov rax, -1
	cmp rdi, 1
	jne .write_done
	mov r13, 0x800000000000
	cmp r13, rsi
	jbe .write_done
	
	mov r11, rdx
	mov rcx, rdx
	mov dx, 0x38f
	rep outsb
	.write_done:
	mov rax, r11
	ret

	.open:
	push rbp
	mov rbp, rsp
	sub rsp, 0x50
	lea r13, [rbp-0x40]
	.loop:
	mov al, [rdi]          
    mov byte [r13], al
	inc rdi
	inc r13
	cmp byte [rdi],0
	jne .loop
	
	lea rdi, [rbp-0x40]
	mov rsi, r13
	sub rsi, rdi
	call kernel_write

	mov rsi, .msg
	mov rcx, .end_msg - .msg
	mov dx, 0x38f
	rep outsb
	mov rsi, rdx
	leave
	ret

	.msg:
	db " cannot be opened", 0xa
	.end_msg:

	.close:
	call unimplemented
	ret

	.stat:
	call unimplemented
	ret

	.fstat:
	call unimplemented
	ret

	.lstat:
	call unimplemented
	ret

	.poll:
	call unimplemented
	ret

	.lseek:
	call unimplemented
	ret

	.mmap:
	call unimplemented
	ret

	.mprotect:
	call unimplemented
	ret

	.munmap:
	call unimplemented
	ret

	.brk:
	call unimplemented
	ret

	.rt_sigaction:
	call unimplemented
	ret

	.rt_sigprocmask:
	call unimplemented
	ret

	.rt_sigreturn:
	int 0x70
	ret

	.ioctl:
	call unimplemented
	ret

	.pread64:
	call unimplemented
	ret

	.pwrite64:
	call unimplemented
	ret

	.readv:
	call unimplemented
	ret

	.writev:
	call unimplemented
	ret

	.access:
	call unimplemented
	ret

	.pipe:
	call unimplemented
	ret

	.select:
	call unimplemented
	ret

	.sched_yield:
	call unimplemented
	ret

	.mremap:
	call unimplemented
	ret

	.msync:
	call unimplemented
	ret

	.mincore:
	call unimplemented
	ret

	.madvise:
	call unimplemented
	ret

	.shmget:
	call unimplemented
	ret

	.shmat:
	call unimplemented
	ret

	.shmctl:
	call unimplemented
	ret

	.dup:
	call unimplemented
	ret

	.dup2:
	call unimplemented
	ret

	.pause:
	call unimplemented
	ret

	.nanosleep:
	call unimplemented
	ret

	.getitimer:
	call unimplemented
	ret

	.alarm:
	call unimplemented
	ret

	.setitimer:
	call unimplemented
	ret

	.getpid:
	call unimplemented
	ret

	.sendfile:
	call unimplemented
	ret

	.socket:
	call unimplemented
	ret

	.connect:
	call unimplemented
	ret

	.accept:
	call unimplemented
	ret

	.sendto:
	call unimplemented
	ret

	.recvfrom:
	call unimplemented
	ret

	.sendmsg:
	call unimplemented
	ret

	.recvmsg:
	call unimplemented
	ret

	.shutdown:
	call unimplemented
	ret

	.bind:
	call unimplemented
	ret

	.listen:
	call unimplemented
	ret

	.getsockname:
	call unimplemented
	ret

	.getpeername:
	call unimplemented
	ret

	.socketpair:
	call unimplemented
	ret

	.setsockopt:
	call unimplemented
	ret

	.getsockopt:
	call unimplemented
	ret

	.clone:
	call unimplemented
	ret

	.fork:
	call unimplemented
	ret

	.vfork:
	call unimplemented
	ret

	.execve:
	call unimplemented
	ret

	.exit:
	hlt

	.wait4:
    call unimplemented
    ret

	.kill:
		call unimplemented
		ret
	.uname:
		call unimplemented
		ret
	.semget:
		call unimplemented
		ret
	.semop:
		call unimplemented
		ret
	.semctl:
		call unimplemented
		ret
	.shmdt:
		call unimplemented
		ret
	.msgget:
		call unimplemented
		ret
	.msgsnd:
		call unimplemented
		ret
	.msgrcv:
		call unimplemented
		ret
	.msgctl:
		call unimplemented
		ret
	.fcntl:
		call unimplemented
		ret
	.flock:
		call unimplemented
		ret
	.fsync:
		call unimplemented
		ret
	.fdatasync:
		call unimplemented
		ret
	.truncate:
		call unimplemented
		ret
	.ftruncate:
		call unimplemented
		ret
	.getdents:
		call unimplemented
		ret
	.getcwd:
		call unimplemented
		ret
	.chdir:
		call unimplemented
		ret
	.fchdir:
		call unimplemented
		ret
	.rename:
		call unimplemented
		ret
	.mkdir:
		call unimplemented
		ret
	.rmdir:
		call unimplemented
		ret
	.creat:
		call unimplemented
		ret
	.link:
		call unimplemented
		ret
	.unlink:
		call unimplemented
		ret
	.symlink:
		call unimplemented
		ret
	.readlink:
		call unimplemented
		ret
	.chmod:
		call unimplemented
		ret
	.fchmod:
		call unimplemented
		ret
	.chown:
		call unimplemented
		ret
	.fchown:
		call unimplemented
		ret
	.lchown:
		call unimplemented
		ret
	.umask:
		call unimplemented
		ret
	.gettimeofday:
		call unimplemented
		ret
	.getrlimit:
		call unimplemented
		ret
	.getrusage:
		call unimplemented
		ret
	.sysinfo:
		call unimplemented
		ret
	.times:
		call unimplemented
		ret
	.ptrace:
		call unimplemented
		ret
	.getuid:
		call unimplemented
		ret
	.syslog:
		call unimplemented
		ret
	.getgid:
		call unimplemented
		ret
	.setuid:
		call unimplemented
		ret
	.setgid:
		call unimplemented
		ret
	.geteuid:
		call unimplemented
		ret
	.getegid:
		call unimplemented
		ret
	.setpgid:
		call unimplemented
		ret
	.getppid:
		call unimplemented
		ret
	.getpgrp:
		call unimplemented
		ret
	.setsid:
		call unimplemented
		ret
	.setreuid:
		call unimplemented
		ret
	.setregid:
		call unimplemented
		ret
	.getgroups:
		call unimplemented
		ret
	.setgroups:
		call unimplemented
		ret
	.setresuid:
		call unimplemented
		ret
	.getresuid:
		call unimplemented
		ret
	.setresgid:
		call unimplemented
		ret
	.getresgid:
		call unimplemented
		ret
	.getpgid:
		call unimplemented
		ret
	.setfsuid:
		call unimplemented
		ret
	.setfsgid:
		call unimplemented
		ret
	.getsid:
		call unimplemented
		ret
	.capget:
		call unimplemented
		ret
	.capset:
		call unimplemented
		ret
	.rt_sigpending:
		call unimplemented
		ret
	.rt_sigtimedwait:
		call unimplemented
		ret
	.rt_sigqueueinfo:
		call unimplemented
		ret
	.rt_sigsuspend:
		call unimplemented
		ret
	.sigaltstack:
		call unimplemented
		ret
	.utime:
		call unimplemented
		ret
	.mknod:
		call unimplemented
		ret
	.uselib:
		call unimplemented
		ret
	.personality:
		call unimplemented
		ret
	.ustat:
		call unimplemented
		ret
	.statfs:
		call unimplemented
		ret
	.fstatfs:
		call unimplemented
		ret
	.sysfs:
		call unimplemented
		ret
	.getpriority:
		call unimplemented
		ret
	.setpriority:
		call unimplemented
		ret
	.sched_setparam:
		call unimplemented
		ret
	.sched_getparam:
		call unimplemented
		ret
	.sched_setscheduler:
		call unimplemented
		ret
	.sched_getscheduler:
		call unimplemented
		ret
	.sched_get_priority_max:
		call unimplemented
		ret
	.sched_get_priority_min:
		call unimplemented
		ret
	.sched_rr_get_interval:
		call unimplemented
		ret
	.mlock:
		call unimplemented
		ret
	.munlock:
		call unimplemented
		ret
	.mlockall:
		call unimplemented
		ret
	.munlockall:
		call unimplemented
		ret
	.vhangup:
		call unimplemented
		ret
	.modify_ldt:
		call unimplemented
		ret
	.pivot_root:
		call unimplemented
		ret
	._sysctl:
		call unimplemented
		ret
	.prctl:
		call unimplemented
		ret
	.arch_prctl:
		int 0x70
		ret
	
	.adjtimex:
		call unimplemented
		ret
	.setrlimit:
		call unimplemented
		ret
	.chroot:
		call unimplemented
		ret
	.sync:
		call unimplemented
		ret
	.acct:
		call unimplemented
		ret
	.settimeofday:
		call unimplemented
		ret
	.mount:
		call unimplemented
		ret
	.umount2:
		call unimplemented
		ret
	.swapon:
		call unimplemented
		ret
	.swapoff:
		call unimplemented
		ret
	.reboot:
		call unimplemented
		ret
	.sethostname:
		call unimplemented
		ret
	.setdomainname:
		call unimplemented
		ret
	.iopl:
		call unimplemented
		ret
	.ioperm:
		call unimplemented
		ret
	.create_module:
		call unimplemented
		ret
	.init_module:
		call unimplemented
		ret
	.delete_module:
		call unimplemented
		ret
	.get_kernel_syms:
		call unimplemented
		ret
	.query_module:
		call unimplemented
		ret
	.quotactl:
		call unimplemented
		ret
	.nfsservctl:
		call unimplemented
		ret
	.getpmsg:
		call unimplemented
		ret
	.putpmsg:
		call unimplemented
		ret
	.afs_syscall:
		call unimplemented
		ret
	.tuxcall:
		call unimplemented
		ret
	.security:
		call unimplemented
		ret
	.gettid:
		call unimplemented
		ret
	.readahead:
		call unimplemented
		ret
	.setxattr:
		call unimplemented
		ret
	.lsetxattr:
		call unimplemented
		ret
	.fsetxattr:
		call unimplemented
		ret
	.getxattr:
		call unimplemented
		ret
	.lgetxattr:
		call unimplemented
		ret
	.fgetxattr:
		call unimplemented
		ret
	.listxattr:
		call unimplemented
		ret
	.llistxattr:
		call unimplemented
		ret
	.flistxattr:
		call unimplemented
		ret
	.removexattr:
		call unimplemented
		ret
	.lremovexattr:
		call unimplemented
		ret
	.fremovexattr:
		call unimplemented
		ret
	.tkill:
		call unimplemented
		ret
	.time:
		call unimplemented
		ret
	.futex:
		call unimplemented
		ret
	.sched_setaffinity:
		call unimplemented
		ret
	.sched_getaffinity:
		call unimplemented
		ret
	.set_thread_area:
		call unimplemented
		ret
	.io_setup:
		call unimplemented
		ret
	.io_destroy:
		call unimplemented
		ret
	.io_getevents:
		call unimplemented
		ret
	.io_submit:
		call unimplemented
		ret
	.io_cancel:
		call unimplemented
		ret
	.get_thread_area:
		call unimplemented
		ret
	.lookup_dcookie:
		call unimplemented
		ret
	.epoll_create:
		call unimplemented
		ret
	.epoll_ctl_old:
		call unimplemented
		ret
	.epoll_wait_old:
		call unimplemented
		ret
	.remap_file_pages:
		call unimplemented
		ret
	.getdents64:
		call unimplemented
		ret
	.set_tid_address:
		; call unimplemented
		ret
	.restart_syscall:
		call unimplemented
		ret
	.semtimedop:
		call unimplemented
		ret
	.fadvise64:
		call unimplemented
		ret
	.timer_create:
		call unimplemented
		ret
	.timer_settime:
		call unimplemented
		ret
	.timer_gettime:
		call unimplemented
		ret
	.timer_getoverrun:
		call unimplemented
		ret
	.timer_delete:
		call unimplemented
		ret
	.clock_settime:
		call unimplemented
		ret
	.clock_gettime:
		call unimplemented
		ret
	.clock_getres:
		call unimplemented
		ret
	.clock_nanosleep:
		call unimplemented
		ret
	.exit_group:
		; call unimplemented
		hlt
	.epoll_wait:
		call unimplemented
		ret
	.epoll_ctl:
		call unimplemented
		ret
	.tgkill:
		call unimplemented
		ret
	.utimes:
		call unimplemented
		ret
	.vserver:
		call unimplemented
		ret
	.mbind:
		call unimplemented
		ret
	.set_mempolicy:
		call unimplemented
		ret
	.get_mempolicy:
		call unimplemented
		ret
	.mq_open:
		call unimplemented
		ret
	.mq_unlink:
		call unimplemented
		ret
	.mq_timedsend:
		call unimplemented
		ret
	.mq_timedreceive:
		call unimplemented
		ret
	.mq_notify:
		call unimplemented
		ret
	.mq_getsetattr:
		call unimplemented
		ret
	.kexec_load:
		call unimplemented
		ret
	.waitid:
		call unimplemented
		ret
	.add_key:
		call unimplemented
		ret
	.request_key:
		call unimplemented
		ret
	.keyctl:
		call unimplemented
		ret
	.ioprio_set:
		call unimplemented
		ret
	.ioprio_get:
		call unimplemented
		ret
	.inotify_init:
		call unimplemented
		ret
	.inotify_add_watch:
		call unimplemented
		ret
	.inotify_rm_watch:
		call unimplemented
		ret
	.migrate_pages:
		call unimplemented
		ret
	.openat:
		call unimplemented
		ret
	.mkdirat:
		call unimplemented
		ret
	.mknodat:
		call unimplemented
		ret
	.fchownat:
		call unimplemented
		ret
	.futimesat:
		call unimplemented
		ret
	.newfstatat:
		call unimplemented
		ret
	.unlinkat:
		call unimplemented
		ret
	.renameat:
		call unimplemented
		ret
	.linkat:
		call unimplemented
		ret
	.symlinkat:
		call unimplemented
		ret
	.readlinkat:
		call unimplemented
		ret
	.fchmodat:
		call unimplemented
		ret
	.faccessat:
		call unimplemented
		ret
	.pselect6:
		call unimplemented
		ret
	.ppoll:
		call unimplemented
		ret
	.unshare:
		call unimplemented
		ret
	.set_robust_list:
		call unimplemented
		ret
	.get_robust_list:
		call unimplemented
		ret
	.splice:
		call unimplemented
		ret
	.tee:
		call unimplemented
		ret
	.sync_file_range:
		call unimplemented
		ret
	.vmsplice:
		call unimplemented
		ret
	.move_pages:
		call unimplemented
		ret
	.utimensat:
		call unimplemented
		ret
	.epoll_pwait:
		call unimplemented
		ret
	.signalfd:
		call unimplemented
		ret
	.timerfd_create:
		call unimplemented
		ret
	.eventfd:
		call unimplemented
		ret
	.fallocate:
		call unimplemented
		ret
	.timerfd_settime:
		call unimplemented
		ret
	.timerfd_gettime:
		call unimplemented
		ret
	.accept4:
		call unimplemented
		ret
	.signalfd4:
		call unimplemented
		ret
	.eventfd2:
		call unimplemented
		ret
	.epoll_create1:
		call unimplemented
		ret
	.dup3:
		call unimplemented
		ret
	.pipe2:
		call unimplemented
		ret
	.inotify_init1:
		call unimplemented
		ret
	.preadv:
		call unimplemented
		ret
	.pwritev:
		call unimplemented
		ret
	.rt_tgsigqueueinfo:
		call unimplemented
		ret
	.perf_event_open:
		call unimplemented
		ret
	.recvmmsg:
		call unimplemented
		ret
	.fanotify_init:
		call unimplemented
		ret
	.fanotify_mark:
		call unimplemented
		ret
	.prlimit64:
		call unimplemented
		ret
	.name_to_handle_at:
		call unimplemented
		ret
	.open_by_handle_at:
		call unimplemented
		ret
	.clock_adjtime:
		call unimplemented
		ret
	.syncfs:
		call unimplemented
		ret
	.sendmmsg:
		call unimplemented
		ret
	.setns:
		call unimplemented
		ret
	.getcpu:
		call unimplemented
		ret
	.process_vm_readv:
		call unimplemented
		ret
	.process_vm_writev:
		call unimplemented
		ret
	.kcmp:
		call unimplemented
		ret
	.finit_module:
		call unimplemented
		ret
	.sched_setattr:
		call unimplemented
		ret
	.sched_getattr:
		call unimplemented
		ret
	.renameat2:
		call unimplemented
		ret
	.seccomp:
		call unimplemented
		ret
	.getrandom:
		call unimplemented
		ret
	.memfd_create:
		call unimplemented
		ret
	.kexec_file_load:
		call unimplemented
		ret
	.bpf:
		call unimplemented
		ret

	align 32
	.syscall_table:
		dq  .read, .write, .open, .close, .stat, .fstat, .lstat, \
			.poll, .lseek, .mmap, .mprotect, .munmap, .brk, .rt_sigaction, \
			.rt_sigprocmask, .rt_sigreturn, .ioctl, .pread64, .pwrite64, \
			.readv, .writev, .access, .pipe, .select, .sched_yield, .mremap, \
			.msync, .mincore, .madvise, .shmget, .shmat, .shmctl, .dup, .dup2, \
			.pause, .nanosleep, .getitimer, .alarm, .setitimer, .getpid, .sendfile, \
			.socket, .connect, .accept, .sendto, .recvfrom, .sendmsg, .recvmsg, \
			.shutdown, .bind, .listen, .getsockname, .getpeername, .socketpair, \
			.setsockopt, .getsockopt, .clone, .fork, .vfork, .execve, .exit, \
			.wait4, .kill, .uname, .semget, .semop, .semctl, .shmdt, .msgget, .msgsnd, .msgrcv, .msgctl, .fcntl, .flock, .fsync, .fdatasync, .truncate, .ftruncate, .getdents, .getcwd, .chdir, .fchdir, .rename, .mkdir, .rmdir, .creat, .link, .unlink, .symlink, .readlink, .chmod, .fchmod, .chown, .fchown, .lchown, .umask, .gettimeofday, .getrlimit, .getrusage, .sysinfo, .times, .ptrace, .getuid, .syslog, .getgid, .setuid, .setgid, .geteuid, .getegid, .setpgid, .getppid, .getpgrp, .setsid, .setreuid, .setregid, .getgroups, .setgroups, .setresuid, .getresuid, .setresgid, .getresgid, .getpgid, .setfsuid, .setfsgid, .getsid, .capget, .capset, .rt_sigpending, .rt_sigtimedwait, .rt_sigqueueinfo, .rt_sigsuspend, .sigaltstack, .utime, .mknod, .uselib, .personality, .ustat, .statfs, .fstatfs, .sysfs, .getpriority, .setpriority, .sched_setparam, .sched_getparam, .sched_setscheduler, .sched_getscheduler, .sched_get_priority_max, .sched_get_priority_min, .sched_rr_get_interval, .mlock, .munlock, .mlockall, .munlockall, .vhangup, .modify_ldt, .pivot_root, ._sysctl, .prctl, .arch_prctl, .adjtimex, .setrlimit, .chroot, .sync, .acct, .settimeofday, .mount, .umount2, .swapon, .swapoff, .reboot, .sethostname, .setdomainname, .iopl, .ioperm, .create_module, .init_module, .delete_module, .get_kernel_syms, .query_module, .quotactl, .nfsservctl, .getpmsg, .putpmsg, .afs_syscall, .tuxcall, .security, .gettid, .readahead, .setxattr, .lsetxattr, .fsetxattr, .getxattr, .lgetxattr, .fgetxattr, .listxattr, .llistxattr, .flistxattr, .removexattr, .lremovexattr, .fremovexattr, .tkill, .time, .futex, .sched_setaffinity, .sched_getaffinity, .set_thread_area, .io_setup, .io_destroy, .io_getevents, .io_submit, .io_cancel, .get_thread_area, .lookup_dcookie, .epoll_create, .epoll_ctl_old, .epoll_wait_old, .remap_file_pages, .getdents64, .set_tid_address, .restart_syscall, .semtimedop, .fadvise64, .timer_create, .timer_settime, .timer_gettime, .timer_getoverrun, .timer_delete, .clock_settime, .clock_gettime, .clock_getres, .clock_nanosleep, .exit_group, .epoll_wait, .epoll_ctl, .tgkill, .utimes, .vserver, .mbind, .set_mempolicy, .get_mempolicy, .mq_open, .mq_unlink, .mq_timedsend, .mq_timedreceive, .mq_notify, .mq_getsetattr, .kexec_load, .waitid, .add_key, .request_key, .keyctl, .ioprio_set, .ioprio_get, .inotify_init, .inotify_add_watch, .inotify_rm_watch, .migrate_pages, .openat, .mkdirat, .mknodat, .fchownat, .futimesat, .newfstatat, .unlinkat, .renameat, .linkat, .symlinkat, .readlinkat, .fchmodat, .faccessat, .pselect6, .ppoll, .unshare, .set_robust_list, .get_robust_list, .splice, .tee, .sync_file_range, .vmsplice, .move_pages, .utimensat, .epoll_pwait, .signalfd, .timerfd_create, .eventfd, .fallocate, .timerfd_settime, .timerfd_gettime, .accept4, .signalfd4, .eventfd2, .epoll_create1, .dup3, .pipe2, .inotify_init1, .preadv, .pwritev, .rt_tgsigqueueinfo, .perf_event_open, .recvmmsg, .fanotify_init, .fanotify_mark, .prlimit64, .name_to_handle_at, .open_by_handle_at, .clock_adjtime, .syncfs, .sendmmsg, .setns, .getcpu, .process_vm_readv, .process_vm_writev, .kcmp, .finit_module, .sched_setattr, .sched_getattr, .renameat2, .seccomp, .getrandom, .memfd_create, .kexec_file_load, .bpf
		dq 0
