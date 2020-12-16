#define _GNU_SOURCE // lmao asprintf

#include <sys/types.h>
#include <sys/param.h>
#include <sys/stat.h>

#include <time.h>
#include <sys/uio.h>
#include <fcntl.h>
#include <pwd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <unistd.h>
#include <syslog.h>
#include <stdarg.h>
#include <dirent.h> 

#include <security/pam_modules.h>
#include <security/pam_appl.h>
#include <security/pam_ext.h>

#include <zlib.h>

#ifndef PAM_EXTERN
#define PAM_EXTERN
#endif

static char* readgzip(const char* filename) {
  gzFile f = gzopen(filename, "rb");
  unsigned int cap = 1024;
  char* buf = malloc(cap);
  char* ptr = buf;
  while (!gzeof(f)) {
    assert(cap - (ptr-buf) - 1 >= 0);
    int n = gzread(f, ptr, cap - (ptr-buf) - 1); // -1 for nullterm
    ptr += n;
    *ptr = '\0';
    if (n <= 0) break;
    if (ptr-buf+1 == cap) {
      buf = realloc(buf, cap*2);
      ptr = buf + cap - 1;
      cap *= 2;
    }
  }
  gzclose(f);
  return buf;
}

// reservoir sampling algorithm
// https://florian.github.io/reservoir-sampling/
static char* choose_file(const char* dirname) {
  DIR *d;
  struct dirent *dir;
  d = opendir(dirname);
  char* result = NULL;
  int n = 0;
  if (d) {
    while ((dir = readdir(d)) != NULL) {
      if (!dir->d_name[0] || dir->d_name[0] == '.') { // skip . .. etc
        continue;
      }
      n++;
      if (rand() % n == 0) { // probability 1/n for nth element
        free(result);
        result = strdup(dir->d_name);
      }
    }
    closedir(d);
  }
  return result;
}

static void display_captcha(pam_handle_t *pamh, char* captcha_dir) {
  char* file = choose_file(captcha_dir);
  char* full_path;
  asprintf(&full_path, "%s/%s", captcha_dir, file);
  free(file);
  // pam_prompt(pamh, PAM_TEXT_INFO, NULL, "%s", full_path);
  char* contents = readgzip(full_path);
  free(full_path);
  pam_prompt(pamh, PAM_TEXT_INFO, NULL, "%s", contents);
  free(contents);
}

char* captcha_base_dir = "/etc/lcaptcha";
char* captcha_types[2] = { "cat", "dog" };
int captchas_required = 3; // how many captchas the user must pass before we accept them
int max_retries = 3; // max retries

#define CAPTCHA_SUCCESS 0
#define CAPTCHA_FAIL 1
#define CAPTCHA_RETRY 2

static int do_captcha(pam_handle_t *pamh, int flags, int argc, const char *argv[]) {
  char *resp;
  int ret = CAPTCHA_SUCCESS;

  int category = rand() % (sizeof(captcha_types) / sizeof(*captcha_types));
  char* captcha_type = captcha_types[category];

  char* captcha_dir;
  asprintf(&captcha_dir, "%s/%s", captcha_base_dir, captcha_type);
  display_captcha(pamh, captcha_dir);
  free(captcha_dir);

  pam_prompt(pamh, PAM_PROMPT_ECHO_ON, &resp, "CAPTCHA: What is this? [cat/dog/skip] ");

  if (!strcmp(resp, "skip")) {
    return CAPTCHA_RETRY;
  }

  if (strcmp(resp, captcha_type)) { // wrong answer. stop authentication flow.
    ret = CAPTCHA_FAIL;
  }

  free(resp);
  return ret;
}

void do_srand() {
  int seed;
  
  int fd = open("/dev/urandom", 0, 0);
  read(fd, &seed, 4);
  close(fd);

  seed ^= time(NULL);
  srand(seed);
}

PAM_EXTERN int
pam_sm_authenticate(pam_handle_t *pamh, int flags,
    int argc, const char *argv[])
{
  char *user, *host;
  pam_get_item(pamh, PAM_USER, (const void **)&user);
  pam_get_item(pamh, PAM_RHOST, (const void **)&host);

  if (argc && strcmp(user, argv[0])) { // don't harass other users
    return PAM_SUCCESS;
  }

  int ret = PAM_SUCCESS;

  do_srand();
  openlog("pam_captcha", 0, LOG_AUTHPRIV);

  pam_prompt(pamh, PAM_TEXT_INFO, NULL, "Are you a robot?");

  int retries = 0;
  for (int n_passed = 0; n_passed < captchas_required;) {
    int captcha_result = do_captcha(pamh, flags, argc, argv);

    if (captcha_result == CAPTCHA_RETRY) {
      retries++;
      if (retries == max_retries) {
        pam_prompt(pamh, PAM_TEXT_INFO, NULL, "Sorry, you can't retry that many times.");
        ret = PAM_MAXTRIES;
        break;
      }
      continue;
    } else if (captcha_result == CAPTCHA_FAIL) {
      syslog(LOG_INFO, "User %s failed to pass captcha (from %s)", user, host);
      // sleep(3);
      pam_prompt(pamh, PAM_TEXT_INFO, NULL, "Sorry, wrong answer.");
      ret = PAM_MAXTRIES;
      break;
    } else if (captcha_result == CAPTCHA_SUCCESS) {
      syslog(LOG_INFO, "User %s passed captcha (from %s)", user, host);
      n_passed++;
      pam_prompt(pamh, PAM_TEXT_INFO, NULL, "Correct! %d/%d solved", n_passed, captchas_required);
    } else {
      abort();
    }
  }

  // if (ret == PAM_SUCCESS) {
  //  pam_prompt(pamh, PAM_TEXT_INFO, NULL, "[2J[0;0H"); // Clear screen
  // }

  closelog();
  return ret;
}

PAM_EXTERN int
pam_sm_setcred(pam_handle_t *pamh, int flags,
    int argc, const char *argv[])
{
  return (PAM_SUCCESS);
}

PAM_EXTERN int
pam_sm_acct_mgmt(pam_handle_t *pamh, int flags,
    int argc, const char *argv[])
{
  return (PAM_SUCCESS);
}

PAM_EXTERN int
pam_sm_open_session(pam_handle_t *pamh, int flags,
    int argc, const char *argv[])
{
  return (PAM_SUCCESS);
}

PAM_EXTERN int
pam_sm_close_session(pam_handle_t *pamh, int flags,
    int argc, const char *argv[])
{
  return (PAM_SUCCESS);
}

PAM_EXTERN int
pam_sm_chauthtok(pam_handle_t *pamh, int flags,
    int argc, const char *argv[])
{
  return (PAM_SERVICE_ERR);
}

#ifdef PAM_MODULE_ENTRY
PAM_MODULE_ENTRY("pam_captcha");
#endif
