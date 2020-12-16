# Author's writeup

[Author's writeup](https://gist.github.com/stong/1198111d5051391fd0b2447411737058)

# Remote deployment notes.

Basically, you need to solve a jigsaw puzzle over an X forwarded window.

Copy contents of `dist/remote` to `/opt/kokoro`. So there should be `/opt/kokoro/run.sh`

Untar `captcha/lcaptcha.tar` to `/etc/lcaptcha`. So there should be `/etc/lcaptcha/tally`

Install pam module in `pam/` with install.sh

```
apt install openjdk-8-jre-headless
apt install mesa-utils # required for GLX
java -version # make sure it's 1.8

adduser kokoro --home /opt/kokoro --shell /opt/kokoro/run.sh
passwd -d kokoro # no password
chown kokoro:kokoro /opt/kokoro
```

Edit /etc/ssh/sshd_config

```
PermitEmptyPasswords yes
PermitRootLogin prohibit-password
UsePAM yes
ChallengeResponseAuthentication yes
PrintMotd no
Compression delayed

Match Group kokoro
        ForceCommand /opt/kokoro/run.sh
        AllowTcpForwarding no
        PermitTunnel no
        AllowAgentForwarding no
        X11Forwarding yes
        PasswordAuthentication no # defer to PAM
        PermitTTY no
```

Edit /etc/pam.d/sshd. Add to the top:

```
# Captcha meme
auth       requisite     pam_ratelimit.so kokoro
auth       requisite     pam_captcha.so kokoro
```

**Add rate-limiting**

```
modprobe xt_hashlimit
modprobe xt_conntrack # idk if this is needed
iptables -t mangle -F # careful!
iptables -t mangle -A OUTPUT -p tcp -d 127.0.0.0/8 -j RETURN # don't ratelimit X11 localhost socket
iptables -t mangle -A OUTPUT -m tcp -p tcp -m hashlimit --hashlimit-above 4mb/s --hashlimit-burst 20000000b --hashlimit-htable-expire 30000 --hashlimit-mode dstip --hashlimit-name perdst -j DROP
```

Now when you ssh to kokoro@chal you should be greeted with the captcha.

**This challenge is compute heavy. It does the rendering on the server. That's why we are using a heavy rate-limit and captcha**

**The remote and the public one have different code. To save cpu, the remote one has the non-obfuscated version**

To access the challenge, `DISPLAY=localhost:0:0 ssh -X kokoro@remote`

You may need to start an x server, i.e. `XWin_MobaX.exe -nowgl -multiwindow`

# Solution

All of the puzzle pieces are stacked on top of each other at the start. The colors of the points, in order, reveal the state of the xorshift RNG. Each color gives you roughly 24 bits of the RNG state. (The rng is very simple and just copied off the wikipedia implementation). Since the RNG is only 32-bits and not very non-linear you can easily rewind the state all the way to the initial state using z3. Based on that you can find out where the pieces should go and how they should be rotated. To automate it, you can use some script with AutoHotKey or xdotool

See `solve.py`
