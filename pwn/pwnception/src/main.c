
#include <unicorn/unicorn.h>
#include <string.h>
#include <fcntl.h>
#include <err.h>
#include <semaphore.h>
#include <unistd.h>
#include <pthread.h>
#include <elf.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <asm/prctl.h>
#include <sys/prctl.h>
#include <signal.h>

#define KERNEL_ADDRESS 0xFFFFFFFF81000000
#define KERNEL_STACK 0xFFFF8801FFFFF000

#define USER_ADDRESS 0x4000000
#define USER_STACK 0x7ffffffff000
#define FS_REGION 0x600000000000

#define MAPPING_SIZE 0x100000

char *USER_TEXT_MEM[MAPPING_SIZE] = {0};
char *USER_DATA_MEM[MAPPING_SIZE] = {0};
char *USER_STACK_MEM[MAPPING_SIZE] = {0};

uint64_t KERNEL_SYSCALL_HANDLER = KERNEL_ADDRESS + 7;
uint64_t KERNEL_SEGFAULT_HANDLER = KERNEL_ADDRESS + 14;

sem_t wait_for_userland;
sem_t wait_for_kernel;

bool segfault = false;
bool has_sigret = false;
bool set_fs = false;
uint64_t fs_base = 0;

uint64_t allregs[32] = {0};

size_t
read_file(char *path, char *buf, size_t max)
{
    int fd = open(path, O_RDONLY);
    if (fd <= 0)
    {
        err(1, "cannot open file");
    }
    size_t n = read(fd, buf, max);
    if (fd <= 0)
    {
        err(1, "cannot read file");
    }
    close(fd);
    return n;
}

void set_syscall_regs(uc_engine *uc)
{
    uc_reg_write(uc, UC_X86_REG_RAX, &allregs[13]);
    uc_reg_write(uc, UC_X86_REG_RDI, &allregs[8]);
    uc_reg_write(uc, UC_X86_REG_RSI, &allregs[9]);
    uc_reg_write(uc, UC_X86_REG_RDX, &allregs[12]);
    uc_reg_write(uc, UC_X86_REG_R10, &allregs[2]);
    uc_reg_write(uc, UC_X86_REG_R8, &allregs[0]);
    uc_reg_write(uc, UC_X86_REG_R9, &allregs[1]);
}

void get_syscall_regs(uc_engine *uc)
{
    uc_reg_read(uc, UC_X86_REG_RAX, &allregs[13]);
    uc_reg_read(uc, UC_X86_REG_RDI, &allregs[8]);
    uc_reg_read(uc, UC_X86_REG_RSI, &allregs[9]);
    uc_reg_read(uc, UC_X86_REG_RDX, &allregs[12]);
    uc_reg_read(uc, UC_X86_REG_R10, &allregs[2]);
    uc_reg_read(uc, UC_X86_REG_R8, &allregs[0]);
    uc_reg_read(uc, UC_X86_REG_R9, &allregs[1]);

    uc_reg_read(uc, UC_X86_REG_RSP, &allregs[10]);
}

void load_regs_for_sigret(uc_engine *uc)
{
    allregs[16] -= 2;
    uc_reg_write(uc, UC_X86_REG_R8, &allregs[0]);
    uc_reg_write(uc, UC_X86_REG_R9, &allregs[1]);
    uc_reg_write(uc, UC_X86_REG_R10, &allregs[2]);
    uc_reg_write(uc, UC_X86_REG_R11, &allregs[3]);
    uc_reg_write(uc, UC_X86_REG_R12, &allregs[4]);
    uc_reg_write(uc, UC_X86_REG_R13, &allregs[5]);
    uc_reg_write(uc, UC_X86_REG_R14, &allregs[6]);
    uc_reg_write(uc, UC_X86_REG_R15, &allregs[7]);
    uc_reg_write(uc, UC_X86_REG_RDI, &allregs[8]);
    uc_reg_write(uc, UC_X86_REG_RSI, &allregs[9]);
    uc_reg_write(uc, UC_X86_REG_RSP, &allregs[10]);
    uc_reg_write(uc, UC_X86_REG_RBX, &allregs[11]);
    uc_reg_write(uc, UC_X86_REG_RDX, &allregs[12]);
    uc_reg_write(uc, UC_X86_REG_RAX, &allregs[13]);
    uc_reg_write(uc, UC_X86_REG_RCX, &allregs[14]);
    uc_reg_write(uc, UC_X86_REG_RSP, &allregs[15]);
    uc_reg_write(uc, UC_X86_REG_RIP, &allregs[16]);
    allregs[16] += 2;
}

void save_regs_for_sigret(uc_engine *uc)
{
    uint64_t rsp = allregs[10];

    for (int i = 0; i < 17; i++)
    {
        uc_mem_read(uc, rsp + 40 + 8 * i, &allregs[i], 8);
    }
}


static void handle_syscall(uc_engine *uc, void *user_data)
{
    get_syscall_regs(uc);
    sem_post(&wait_for_userland);
    sem_wait(&wait_for_kernel);

    if (has_sigret)
    {
        has_sigret = false;
        load_regs_for_sigret(uc);
    }
    else
    {

        if (set_fs)
        {
            set_fs = false;
            uc_reg_write(uc, UC_X86_REG_FS_BASE, &fs_base);
        }

        uc_reg_write(uc, UC_X86_REG_RAX, &allregs[13]);
    }
}

static void trace(uc_engine *uc, uint64_t address, uint32_t size, void *user_data)
{
    // fprintf(stderr, "trace: 0x%lx (0x%x)\n", address, size);
}

static void handle_kernel(uc_engine *uc, uint64_t address, uint32_t size, void *user_data)
{
    char inst[0x100];
    if (!uc_mem_read(uc, address, &inst, size))
    {
        if (inst[0] == '\xf4')
        {
            uc_emu_stop(uc);
            exit(0);
        }

        if (inst[0] == '\xcf' && !has_sigret)
        {
            uc_reg_read(uc, UC_X86_REG_RAX, &allregs[13]);
        }

        if (inst[0] == '\xcf' || (inst[0] == '\xf3' && inst[1] == '\x90'))
        {
            sem_post(&wait_for_kernel);
            sem_wait(&wait_for_userland);
            if (segfault)
            {
                u_int64_t rip = KERNEL_SEGFAULT_HANDLER;
                uc_reg_write(uc, UC_X86_REG_RIP, &rip);
                segfault = false;
            }
            else
            {
                u_int64_t rip = KERNEL_SYSCALL_HANDLER;
                set_syscall_regs(uc);
                uc_reg_write(uc, UC_X86_REG_RIP, &rip);
            }
        }
    }
}

static uint32_t handle_kernel_in(uc_engine *uc, uint32_t port, int size, void *user_data)
{
    char buf[2] = {0};
    if (port == 0x38f && size == 1)
    {
        int c = read(0, buf, 1);
        if (c <= 0)
        {
            err(1, "error reading input");
        }
        return buf[0];
    }

    return -1;
}

static void handle_kernel_out(uc_engine *uc, uint32_t port, int size, uint32_t value, void *user_data)
{
    if (port == 0x38f && size == 1)
    {
        write(1, &value, 1);
    }
}

char *buf;

void handle_kernel_interrupt(uc_engine *uc, uint32_t intno, void *user_data)
{
    uint64_t rax, rdi, rsi, rdx;

    if (intno == 0x70)
    {
        uc_reg_read(uc, UC_X86_REG_RAX, &rax);
        uc_reg_read(uc, UC_X86_REG_RDI, &rdi);
        uc_reg_read(uc, UC_X86_REG_RSI, &rsi);
        uc_reg_read(uc, UC_X86_REG_RDX, &rdx);

        if (rax == SYS_arch_prctl)
        {
            if (rdi == ARCH_SET_FS)
            {
                set_fs = true;
                fs_base = rsi;
            }
        }
        else if (rax == SYS_rt_sigreturn)
        {
            has_sigret = true;
            save_regs_for_sigret(uc);
        }
        else if (rax == SYS_mprotect)
        {
            uc_mem_protect(uc, rdi, rsi, rdx & 7);
        }
        else if (rax == SYS_mmap)
        {
            uc_mem_map(uc, rdi, rsi, rdx & 7);
        }
    }
    else if (intno == 0x71)
    {
        uc_reg_read(uc, UC_X86_REG_RAX, &rax);
        uc_reg_read(uc, UC_X86_REG_RDI, &rdi);
        uc_reg_read(uc, UC_X86_REG_RSI, &rsi);

        if (rax == 0)
        {
            buf = malloc(rdi);
        }
        else if (buf && rax == 1)
        {
            uc_mem_read(uc, rdi, buf, rsi);
        }
        else if (buf && rax == 2)
        {
            uc_mem_write(uc, rdi, buf, rsi);
        }
        else if (buf && rax == 3)
        {
            free(buf);
        }
    }
}

static bool handle_kernel_invalid(uc_engine *uc, uc_mem_type type,
                                  uint64_t address, int size, int64_t value, void *user_data)
{
    uc_emu_stop(uc);
    exit(0);
    return false;
}

static bool handle_userland_invalid(uc_engine *uc, uc_mem_type type,
                                    uint64_t address, int size, int64_t value, void *user_data)
{
    segfault = true;
    sem_post(&wait_for_userland);
    return false;
}

void *load_file(char *path, size_t *size)
{
    int fd = open(path, O_RDONLY);
    if (fd <= 0)
    {
        err(1, "cannot open file");
    }

    size_t len = lseek(fd, 0, SEEK_END);
    void *p = mmap(NULL, len, PROT_READ, MAP_PRIVATE, fd, 0);
    if (p <= 0)
    {
        err(1, "cannot mmap file");
    }
    close(fd);
    *size = len;
    return p;
}

void *get_elf_data(char *path, size_t *size)
{
    size_t len = 0;
    void *p = load_file(path, &len);

    Elf64_Ehdr *ehdr = (Elf64_Ehdr *)p;
    Elf64_Shdr *shdrs = (void *)ehdr + ehdr->e_shoff;

    if (ehdr->e_shoff > len)
    {
        errx(1, "corrupt file");
    }

    size_t start = 0;
    size_t end = 0;

    char *strs = (void *)ehdr + shdrs[ehdr->e_shstrndx].sh_offset;
    for (int i = 0; i < ehdr->e_shnum; i++)
    {
        if (strcmp(".text", strs + shdrs[i].sh_name) == 0)
        {
            start = shdrs[i].sh_offset;
        }
        else if (strcmp(".data", strs + shdrs[i].sh_name) == 0)
        {
            end = shdrs[i].sh_offset + shdrs[i].sh_size;
        }
    }

    if (start == 0 || end == 0 || start > len || end > len)
    {
        errx(1, "corrupt file");
    }

    *size = end - start;
    return p + start;
}

struct Mapped
{
    size_t start;
    size_t len;
    size_t flags;
    void *mem;
} Mapped;

struct Mapped sections[0x100];
size_t num_sections = 0;

size_t map_elf(uc_engine *uc, char *path)
{
    size_t len = 0;
    void *p = load_file(path, &len);

    Elf64_Ehdr *ehdr = (Elf64_Ehdr *)p;
    Elf64_Shdr *shdrs = (void *)ehdr + ehdr->e_shoff;

    if (ehdr->e_shoff > len)
    {
        errx(1, "corrupt file");
    }

    for (int i = 0; i < ehdr->e_shnum; i++)
    {
        if (shdrs[i].sh_addr)
        {
            size_t flags = 0;
            if (shdrs[i].sh_flags & SHF_WRITE)
            {
                flags |= UC_PROT_WRITE | UC_PROT_READ;
            }
            if (shdrs[i].sh_flags & SHF_EXECINSTR)
            {
                flags |= UC_PROT_EXEC | UC_PROT_READ;
            }

            size_t len = ((shdrs[i].sh_size + 0x1000 - 1) / 0x1000) * 0x1000;
            size_t start = (shdrs[i].sh_addr / 0x1000) * 0x1000;
            size_t end = start + len;

            size_t last_i = num_sections - 1;

            if (num_sections == 0 || start >= sections[last_i].start + sections[last_i].len)
            {
                sections[num_sections].start = start;
                sections[num_sections].len = len;
                sections[num_sections].flags = flags;
                sections[num_sections].mem = malloc(len);
                memset(sections[num_sections].mem, 0, len);
                num_sections++;
            }
            else if (num_sections != 0 && end > sections[last_i].start + sections[last_i].len)
            {
                size_t new_len = end - sections[last_i].start;
                sections[last_i].len = new_len;
                sections[last_i].mem = realloc(sections[last_i].mem, new_len);
                memset(sections[last_i].mem, 0, new_len);
            }

            if (num_sections != 0 && flags != sections[last_i].flags)
            {
                sections[last_i].flags |= flags;
            }
        }
    }

    for (int i = 0; i < num_sections; i++)
    {
        uc_err e = uc_mem_map_ptr(
            uc,
            sections[i].start,
            sections[i].len,
            sections[i].flags,
            sections[i].mem);
        if (e)
        {
            err(1, "Failed on uc_mem_map_ptr() with error returned: %u\n", e);
        }
    }

    for (int i = 0; i < ehdr->e_shnum; i++)
    {
        if (shdrs[i].sh_addr)
        {
            if (shdrs[i].sh_type == SHT_PROGBITS || shdrs[i].sh_type == SHT_INIT_ARRAY || shdrs[i].sh_type == SHT_FINI_ARRAY)
            {
                uc_mem_write(uc, shdrs[i].sh_addr, p + shdrs[i].sh_offset, shdrs[i].sh_size);
            }
        }
    }

    return ehdr->e_entry;
}

void *start_userland(void *path)
{
    uc_engine *uc;
    uc_err e;
    uc_hook trace1, trace2;

    e = uc_open(UC_ARCH_X86, UC_MODE_64, &uc);
    if (e)
    {
        err(1, "Failed on uc_open() with error returned: %u\n", e);
    }

    size_t entry = map_elf(uc, path);
    uc_mem_map_ptr(uc, USER_STACK - MAPPING_SIZE, MAPPING_SIZE, UC_PROT_READ | UC_PROT_WRITE, USER_STACK_MEM);
    uc_mem_map(uc, FS_REGION, MAPPING_SIZE, UC_PROT_READ | UC_PROT_WRITE);

    uc_hook_add(uc, &trace1, UC_HOOK_INSN, handle_syscall, NULL, 1, 0, UC_X86_INS_SYSCALL);
    uc_hook_add(uc, &trace2, UC_HOOK_MEM_READ_UNMAPPED | UC_HOOK_MEM_WRITE_UNMAPPED | UC_HOOK_MEM_FETCH_UNMAPPED, handle_userland_invalid, NULL, 1, 0);

    size_t min = -1;
    size_t max = 0;
    for (int i = 0; i < num_sections; i++)
    {
        if (sections[i].flags & UC_PROT_EXEC && sections[i].start < min)
            min = sections[i].start;
        if (sections[i].flags & UC_PROT_EXEC && sections[i].start + sections[i].len > max)
            max = sections[i].start + sections[i].len;
    }

    uc_hook debug;
    uc_hook_add(uc, &debug, UC_HOOK_CODE, trace, NULL, min, max);

    uint64_t rsp = USER_STACK - 0x1000;
    uint64_t rip = entry;
    uint64_t fs = 0;
    uint64_t gs = 0;

    uc_reg_write(uc, UC_X86_REG_RSP, &rsp);
    uc_reg_write(uc, UC_X86_REG_RIP, &rip);
    uc_reg_write(uc, UC_X86_REG_FS, &fs);
    uc_reg_write(uc, UC_X86_REG_GS, &gs);

    sem_post(&wait_for_userland);
    sem_wait(&wait_for_kernel);

    uc_emu_start(uc, entry, max, 0, 0);

    allregs[0] = 60;
    allregs[1] = 0;
    sem_post(&wait_for_userland);

    return NULL;
}

void *start_kernel(void *path)
{
    size_t kernel_len = 0;
    void *kernel = load_file(path, &kernel_len);

    uc_engine *uc;
    uc_err e;
    uc_hook trace1, trace2, trace3, trace4, trace5;

    e = uc_open(UC_ARCH_X86, UC_MODE_64, &uc);
    if (e)
    {
        err(1, "Failed on uc_open() with error returned: %u\n", e);
    }

    sem_wait(&wait_for_userland);
    for (int i = 0; i < num_sections; i++)
    {
        uc_mem_map_ptr(uc, sections[i].start, sections[i].len, sections[i].flags, sections[i].mem);
    }
    uc_mem_map_ptr(uc, USER_STACK - MAPPING_SIZE, MAPPING_SIZE, UC_PROT_READ | UC_PROT_WRITE, USER_STACK_MEM);

    uc_mem_map(uc, KERNEL_ADDRESS, MAPPING_SIZE, UC_PROT_READ | UC_PROT_EXEC);
    uc_mem_map(uc, KERNEL_STACK - MAPPING_SIZE, MAPPING_SIZE, UC_PROT_READ | UC_PROT_WRITE);

    uc_mem_write(uc, KERNEL_ADDRESS, kernel, kernel_len);
    uc_hook_add(uc, &trace1, UC_HOOK_CODE, handle_kernel, NULL, KERNEL_ADDRESS, KERNEL_ADDRESS + MAPPING_SIZE);
    uc_hook_add(uc, &trace2, UC_HOOK_INSN, handle_kernel_in, NULL, 1, 0, UC_X86_INS_IN);
    uc_hook_add(uc, &trace3, UC_HOOK_INSN, handle_kernel_out, NULL, 1, 0, UC_X86_INS_OUT);
    uc_hook_add(uc, &trace4, UC_HOOK_INTR, handle_kernel_interrupt, NULL, 1, 0);
    uc_hook_add(uc, &trace5, UC_HOOK_MEM_READ_UNMAPPED | UC_HOOK_MEM_WRITE_UNMAPPED | UC_HOOK_MEM_FETCH_UNMAPPED, handle_kernel_invalid, NULL, 1, 0);

    uc_hook debug;
    uc_hook_add(uc, &debug, UC_HOOK_CODE, trace, NULL, KERNEL_ADDRESS, KERNEL_ADDRESS + MAPPING_SIZE);
    uc_hook_add(uc, &debug, UC_HOOK_CODE, trace, NULL, 0, 0x1000);

    uint64_t rsp = KERNEL_STACK - 0x1000;
    uint64_t rip = KERNEL_ADDRESS;

    uc_reg_write(uc, UC_X86_REG_RSP, &rsp);
    uc_reg_write(uc, UC_X86_REG_RIP, &rip);

    uc_emu_start(uc, KERNEL_ADDRESS, KERNEL_ADDRESS + kernel_len, 0, 0);

    return NULL;
}

void handler()
{
    puts("Bye!");
    exit(0);
}

void setup()
{
    signal(SIGALRM, handler);
    alarm(60);
    setvbuf(stdout, 0, 2, 0);
    setvbuf(stdin, 0, 2, 0);
    setvbuf(stderr, 0, 2, 0);
}

int main(int argc, char **argv)
{
    if (argc != 3)
    {
        printf("Usage: %s ./kernel ./userland\n", argv[0]);
        return -1;
    }
    setup();
    pthread_t kernel_thread, userland_thread;

    sem_init(&wait_for_userland, 0, 0);
    sem_init(&wait_for_kernel, 0, 0);

    pthread_create(&kernel_thread, NULL, start_kernel, argv[1]);
    pthread_create(&userland_thread, NULL, start_userland, argv[2]);

    pthread_join(kernel_thread, NULL);
    pthread_join(userland_thread, NULL);
}
