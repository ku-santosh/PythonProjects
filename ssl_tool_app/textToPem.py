from flask import Flask, jsonify
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from cryptography.hazmat.primitives import serialization
import os

app = Flask(__name__)

# Config
KEY_VAULT_URL = "https://<your-key-vault-name>.vault.azure.net/"
SECRET_NAME = "my-pem-key"

# Load PEM once at startup (best practice)
def load_private_key():
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)

    secret = client.get_secret(SECRET_NAME)
    pem_data = secret.value

    private_key = serialization.load_pem_private_key(
        pem_data.encode(),
        password=None,
    )
    return private_key

# Initialize key at startup
private_key = load_private_key()

@app.route("/")
def home():
    return "Flask App with Secure PEM Loaded"

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/sign")
def sign_demo():
    # Example: just confirming key is loaded
    return jsonify({"message": "Private key loaded successfully"})

if __name__ == "__main__":
    app.run(debug=True)