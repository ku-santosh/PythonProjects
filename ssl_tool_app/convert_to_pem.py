import os
import re
import ssl
import logging
from datetime import datetime

# ==============================
# LOGGING CONFIGURATION
# ==============================
LOG_FILE = "pem_conversion.log"

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
# CONFIG
# ==============================
INPUT_FILE = "CA_CERT_CA3.text"
OUTPUT_FILE = "CA_CERT_CA3.pem"

# ==============================
# HELPER FUNCTIONS
# ==============================
def read_input_file(file_path):
    logger.info(f"Reading input file: {file_path}")

    if not os.path.exists(file_path):
        logger.error("Input file not found")
        raise FileNotFoundError(f"{file_path} does not exist")

    with open(file_path, "r") as f:
        content = f.read()

    if not content.strip():
        logger.error("Input file is empty")
        raise ValueError("Input file is empty")

    logger.debug(f"Input file size: {len(content)} characters")
    return content


def normalize_pem(content):
    logger.info("Normalizing certificate content")

    content = content.strip()

    # Case 1: Already PEM format
    if "BEGIN CERTIFICATE" in content:
        logger.info("Detected existing PEM format")

        certs = re.findall(
            r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----",
            content,
            re.DOTALL
        )

        if not certs:
            logger.error("Invalid PEM structure found")
            raise ValueError("Invalid PEM format")

        logger.info(f"Found {len(certs)} certificate(s) in file")

        cleaned_certs = []
        for i, cert in enumerate(certs, start=1):
            logger.debug(f"Processing certificate #{i}")

            # Normalize spacing
            cert = cert.strip()
            cert = re.sub(r"\r\n", "\n", cert)

            cleaned_certs.append(cert)

        return "\n".join(cleaned_certs)

    # Case 2: Raw Base64
    else:
        logger.warning("No PEM headers found, assuming raw base64 content")

        base64_data = re.sub(r"\s+", "", content)

        if not re.match(r"^[A-Za-z0-9+/=]+$", base64_data):
            logger.error("Invalid base64 content detected")
            raise ValueError("Input is not valid base64 certificate data")

        logger.info("Formatting base64 content into PEM structure")

        lines = [base64_data[i:i+64] for i in range(0, len(base64_data), 64)]

        pem = "-----BEGIN CERTIFICATE-----\n"
        pem += "\n".join(lines)
        pem += "\n-----END CERTIFICATE-----\n"

        return pem


def write_output_file(file_path, content):
    logger.info(f"Writing PEM file: {file_path}")

    with open(file_path, "w") as f:
        f.write(content)

    logger.info("PEM file written successfully")


def validate_pem(file_path):
    logger.info("Validating PEM file using SSL context")

    try:
        ssl.create_default_context(cafile=file_path)
        logger.info("PEM validation successful")
        return True
    except Exception as e:
        logger.error(f"PEM validation failed: {str(e)}")
        return False


# ==============================
# MAIN PROCESS
# ==============================
def convert_text_to_pem(input_file, output_file):
    start_time = datetime.now()
    logger.info("========== START PEM CONVERSION ==========")

    try:
        content = read_input_file(input_file)

        pem_content = normalize_pem(content)

        write_output_file(output_file, pem_content)

        is_valid = validate_pem(output_file)

        if is_valid:
            logger.info("Conversion completed successfully ✅")
        else:
            logger.warning("Conversion completed but validation failed ⚠️")

    except Exception as e:
        logger.exception(f"Conversion failed ❌: {str(e)}")

    finally:
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Execution time: {duration} seconds")
        logger.info("========== END PEM CONVERSION ==========\n")


# ==============================
# ENTRY POINT
# ==============================
if __name__ == "__main__":
    convert_text_to_pem(INPUT_FILE, OUTPUT_FILE)