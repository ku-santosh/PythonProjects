import os
import re
import ssl
import socket
import requests
from flask import Flask, jsonify

INPUT_FILE = "CA_CERT_CA3.text"
PEM_FILE = "CA_CERT_CA3.pem"

SERVERS = {
    "uat": {"host": "example.com", "url": "https://example.com"},
    "prod": {"host": "example.org", "url": "https://example.org"}
}

app = Flask(__name__)

def normalize_pem(content: str) -> str:
    content = content.strip()
    if "BEGIN CERTIFICATE" in content:
        certs = re.findall(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", content, re.DOTALL)
        return "\n".join(cert.strip() for cert in certs)
    else:
        base64_data = re.sub(r"\s+", "", content)
        lines = [base64_data[i:i+64] for i in range(0, len(base64_data), 64)]
        return "-----BEGIN CERTIFICATE-----\n" + "\n".join(lines) + "\n-----END CERTIFICATE-----\n"

def convert_to_pem():
    with open(INPUT_FILE, "r") as f:
        content = f.read()
    pem_content = normalize_pem(content)
    with open(PEM_FILE, "w") as f:
        f.write(pem_content)
    return "PEM created"

def validate_pem():
    try:
        ssl.create_default_context(cafile=PEM_FILE)
        return {"status": "valid"}
    except Exception as e:
        return {"status": "invalid", "error": str(e)}

def ssl_debug(host, port=443):
    context = ssl.create_default_context(cafile=PEM_FILE)
    try:
        with socket.create_connection((host, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                return {
                    "status": "success",
                    "tls_version": ssock.version(),
                    "cipher": ssock.cipher(),
                    "issuer": cert.get("issuer")
                }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def call_api(url):
    try:
        r = requests.get(url, verify=PEM_FILE, timeout=10)
        return {"status": r.status_code, "data": r.text[:100]}
    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def home():
    return "SSL Tool Running"

@app.route("/full-check/<env>")
def full_check(env):
    config = SERVERS.get(env)
    return jsonify({
        "convert": convert_to_pem(),
        "validate": validate_pem(),
        "ssl": ssl_debug(config["host"]),
        "api": call_api(config["url"])
    })

if __name__ == "__main__":
    app.run(debug=True)
