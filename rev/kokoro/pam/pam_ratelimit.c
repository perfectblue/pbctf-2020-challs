#define _GNU_SOURCE // lmao asprintf

#include <sys/stat.h>
#include <utime.h>
#include <unistd.h>
#include <fcntl.h>

#include <time.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <assert.h>
#include <syslog.h>

#include <security/pam_modules.h>
#include <security/pam_appl.h>
#include <security/pam_ext.h>

#ifndef PAM_EXTERN
#define PAM_EXTERN
#endif

char* captcha_base_dir = "/etc/lcaptcha/tally";

static void update_time(char* hostname) {
  char* filename;
  asprintf(&filename, "%s/%s", captcha_base_dir, hostname);
  int fd = open(filename, O_RDWR | O_CREAT, 0644);
  close(fd);
  utime(filename, NULL);
  free(filename);
}

static int query_time(char* hostname) {
  char* filename;
  asprintf(&filename, "%s/%s", captcha_base_dir, hostname);
  struct stat attrib;
  memset(&attrib, 0, sizeof(attrib));
  stat(filename, &attrib);
  free(filename);
  return attrib.st_mtim.tv_sec;
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

  // pam_prompt(pamh, PAM_TEXT_INFO, NULL, "Hi %s, your hostname is %s", user, host);

  int now = time(NULL);
  int last_time = query_time(host);
  if (last_time) {
    pam_prompt(pamh, PAM_TEXT_INFO, NULL, "Your last login was %d seconds ago.", now - last_time);
  }

  if (last_time && now - last_time < 60) {
    pam_prompt(pamh, PAM_TEXT_INFO, NULL, "Sorry, you are being ratelimited");
    ret = PAM_MAXTRIES;
  }

  update_time(host);

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
