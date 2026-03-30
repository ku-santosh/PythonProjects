# convert_to_pem_return_file.py

import os
import re
import logging
from datetime import datetime
from typing import Optional

INPUT_FILE: str = "CA_CERT_CA3.text"
OUTPUT_FILE: str = "CA_CERT_CA3.pem"
LOG_FILE: str = "pem_conversion.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def read_file(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} does not exist")
    with open(file_path, "r") as f:
        content: str = f.read()
    if not content.strip():
        raise ValueError("Input file is empty")
    return content

def normalize_to_pem(content: str) -> str:
    content = content.strip()
    if "BEGIN CERTIFICATE" in content:
        certs = re.findall(
            r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----",
            content,
            re.DOTALL
        )
        if not certs:
            raise ValueError("Invalid PEM format")
        return "\n".join(cert.strip() for cert in certs)
    else:
        base64_data: str = re.sub(r"\s+", "", content)
        lines = [base64_data[i:i+64] for i in range(0, len(base64_data), 64)]
        pem: str = "-----BEGIN CERTIFICATE-----\n"
        pem += "\n".join(lines)
        pem += "\n-----END CERTIFICATE-----\n"
        return pem

def write_pem(file_path: str, content: str) -> None:
    with open(file_path, "w") as f:
        f.write(content)

def convert_to_pem(input_file: str, output_file: str) -> Optional[str]:
    try:
        content: str = read_file(input_file)
        pem_content: str = normalize_to_pem(content)
        write_pem(output_file, pem_content)
        return output_file
    except Exception:
        return None

if __name__ == "__main__":
    result = convert_to_pem(INPUT_FILE, OUTPUT_FILE)
    print(f"Output: {result}")
