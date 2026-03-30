import os
import re
import ssl
import logging
from datetime import datetime

# Azure imports
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# ==============================
# CONFIG
# ==============================
INPUT_FILE = "CA_CERT_CA3.text"
OUTPUT_FILE = "CA_CERT_CA3.pem"

KEY_VAULT_URL = "https://<your-key-vault-name>.vault.azure.net/"
SECRET_NAME = "ca-cert-ca3"

LOG_FILE = "pem_upload.log"

# ==============================
# LOGGING SETUP
# ==============================
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ==============================
# READ FILE
# ==============================
def read_input(file_path):
    logger.info(f"Reading file: {file_path}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found")

    with open(file_path, "r") as f:
        content = f.read()

    if not content.strip():
        raise ValueError("File is empty")

    return content


# ==============================
# NORMALIZE PEM
# ==============================
def normalize_pem(content):
    logger.info("Normalizing certificate")

    content = content.strip()

    if "BEGIN CERTIFICATE" in content:
        logger.info("PEM format detected")

        certs = re.findall(
            r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----",
            content,
            re.DOTALL
        )

        if not certs:
            raise ValueError("Invalid PEM format")

        logger.info(f"Certificates found: {len(certs)}")
        return "\n".join(cert.strip() for cert in certs)

    else:
        logger.warning("Raw base64 detected, converting")

        base64_data = re.sub(r"\s+", "", content)

        if not re.match(r"^[A-Za-z0-9+/=]+$", base64_data):
            raise ValueError("Invalid base64 certificate")

        lines = [base64_data[i:i+64] for i in range(0, len(base64_data), 64)]

        pem = "-----BEGIN CERTIFICATE-----\n"
        pem += "\n".join(lines)
        pem += "\n-----END CERTIFICATE-----\n"

        return pem


# ==============================
# WRITE FILE
# ==============================
def write_pem(file_path, content):
    logger.info(f"Writing PEM file: {file_path}")

    with open(file_path, "w") as f:
        f.write(content)


# ==============================
# VALIDATE PEM
# ==============================
def validate_pem(file_path):
    logger.info("Validating PEM")

    try:
        ssl.create_default_context(cafile=file_path)
        logger.info("PEM is valid ✅")
        return True
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        return False


# ==============================
# UPLOAD TO AZURE KEY VAULT
# ==============================
def upload_to_key_vault(secret_name, pem_content):
    logger.info("Uploading PEM to Azure Key Vault")

    try:
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)

        client.set_secret(secret_name, pem_content)

        logger.info(f"Successfully uploaded secret: {secret_name}")

    except Exception as e:
        logger.error(f"Key Vault upload failed: {str(e)}")
        raise


# ==============================
# MAIN PROCESS
# ==============================
def process():
    start_time = datetime.now()
    logger.info("====== START PROCESS ======")

    try:
        content = read_input(INPUT_FILE)

        pem_content = normalize_pem(content)

        write_pem(OUTPUT_FILE, pem_content)

        if validate_pem(OUTPUT_FILE):
            upload_to_key_vault(SECRET_NAME, pem_content)
            logger.info("Process completed successfully 🚀")
        else:
            logger.warning("Skipping upload due to invalid PEM")

    except Exception as e:
        logger.exception(f"Process failed ❌: {str(e)}")

    finally:
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Execution time: {duration} seconds")
        logger.info("====== END PROCESS ======\n")


# ==============================
# ENTRY POINT
# ==============================
if __name__ == "__main__":
    process()