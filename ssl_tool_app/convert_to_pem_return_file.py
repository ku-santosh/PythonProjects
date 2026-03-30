import os
import re
import logging
from datetime import datetime
from typing import Optional

# ==============================
# CONFIG
# ==============================
INPUT_FILE: str = "CA_CERT_CA3.text"
OUTPUT_FILE: str = "CA_CERT_CA3.pem"
LOG_FILE: str = "pem_conversion.log"

# ==============================
# LOGGING SETUP
# ==============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ==============================
# FUNCTIONS
# ==============================
def read_file(file_path: str) -> str:
    logger.info(f"Reading file: {file_path}")

    if not os.path.exists(file_path):
        logger.error("Input file not found")
        raise FileNotFoundError(f"{file_path} does not exist")

    with open(file_path, "r") as f:
        content: str = f.read()

    if not content.strip():
        logger.error("File is empty")
        raise ValueError("Input file is empty")

    return content


def normalize_to_pem(content: str) -> str:
    logger.info("Normalizing certificate content")

    content = content.strip()

    # Case 1: Already PEM format
    if "BEGIN CERTIFICATE" in content:
        logger.info("Detected PEM format")

        certs = re.findall(
            r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----",
            content,
            re.DOTALL
        )

        if not certs:
            logger.error("Invalid PEM structure")
            raise ValueError("Invalid PEM format")

        logger.info(f"Certificates found: {len(certs)}")
        return "\n".join(cert.strip() for cert in certs)

    # Case 2: Raw base64
    else:
        logger.warning("No PEM header found, converting from base64")

        base64_data: str = re.sub(r"\s+", "", content)

        if not re.match(r"^[A-Za-z0-9+/=]+$", base64_data):
            logger.error("Invalid base64 content")
            raise ValueError("Invalid certificate data")

        lines: list[str] = [
            base64_data[i:i+64] for i in range(0, len(base64_data), 64)
        ]

        pem: str = "-----BEGIN CERTIFICATE-----\n"
        pem += "\n".join(lines)
        pem += "\n-----END CERTIFICATE-----\n"

        return pem


def write_pem(file_path: str, content: str) -> None:
    logger.info(f"Writing PEM file: {file_path}")

    with open(file_path, "w") as f:
        f.write(content)

    logger.info("PEM file created successfully")


# ==============================
# MAIN FUNCTION
# ==============================
def convert_to_pem(input_file: str, output_file: str) -> Optional[str]:
    start_time: datetime = datetime.now()
    logger.info("===== START CONVERSION =====")

    try:
        content: str = read_file(input_file)

        pem_content: str = normalize_to_pem(content)

        write_pem(output_file, pem_content)

        logger.info("Conversion successful ✅")

        return output_file

    except Exception as e:
        logger.exception(f"Conversion failed ❌: {str(e)}")
        return None

    finally:
        duration: float = (datetime.now() - start_time).total_seconds()
        logger.info(f"Execution time: {duration} seconds")
        logger.info("===== END CONVERSION =====\n")


# ==============================
# ENTRY POINT
# ==============================
if __name__ == "__main__":
    result: Optional[str] = convert_to_pem(INPUT_FILE, OUTPUT_FILE)

    if result:
        print(f"\n✅ PEM file created: {result}")
    else:
        print("\n❌ Conversion failed. Check logs.")