import os
import logging
from datetime import datetime
from typing import Optional

import requests
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# ==============================
# CONFIG
# ==============================
STORAGE_ACCOUNT_URL: str = "https://<your-storage-account>.blob.core.windows.net"
CONTAINER_NAME: str = "certificates"
BLOB_NAME: str = "CA_CERT_CA3.pem"

LOCAL_PEM_FILE: str = "CA_CERT_CA3.pem"
DOWNLOADED_PEM_FILE: str = "downloaded_CA_CERT_CA3.pem"

LOG_FILE: str = "blob_pem_app.log"

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
# AUTH CLIENT
# ==============================
def get_blob_service_client() -> BlobServiceClient:
    logger.info("Initializing Azure Blob Service Client")

    try:
        credential = DefaultAzureCredential()
        client = BlobServiceClient(account_url=STORAGE_ACCOUNT_URL, credential=credential)
        logger.info("Blob Service Client initialized successfully")
        return client

    except Exception as e:
        logger.exception("Failed to create Blob Service Client")
        raise


# ==============================
# UPLOAD PEM TO BLOB
# ==============================
def upload_pem_to_blob(file_path: str) -> bool:
    logger.info(f"Uploading PEM file: {file_path}")

    if not os.path.exists(file_path):
        logger.error("PEM file not found")
        raise FileNotFoundError(file_path)

    try:
        client = get_blob_service_client()
        blob_client = client.get_blob_client(container=CONTAINER_NAME, blob=BLOB_NAME)

        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        logger.info("Upload successful ✅")
        return True

    except Exception as e:
        logger.exception("Upload failed ❌")
        return False


# ==============================
# DOWNLOAD PEM FROM BLOB
# ==============================
def download_pem_from_blob(output_file: str) -> Optional[str]:
    logger.info("Downloading PEM from Blob")

    try:
        client = get_blob_service_client()
        blob_client = client.get_blob_client(container=CONTAINER_NAME, blob=BLOB_NAME)

        with open(output_file, "wb") as f:
            download_stream = blob_client.download_blob()
            f.write(download_stream.readall())

        logger.info(f"Downloaded PEM file: {output_file}")
        return output_file

    except Exception as e:
        logger.exception("Download failed ❌")
        return None


# ==============================
# CALL API USING PEM
# ==============================
def call_secure_api(url: str, pem_file: str) -> dict:
    logger.info(f"Calling API: {url}")

    try:
        response = requests.get(url, verify=pem_file, timeout=10)

        logger.info("API call successful")
        return {
            "status_code": response.status_code,
            "response_preview": response.text[:200]
        }

    except requests.exceptions.SSLError as e:
        logger.error(f"SSL Error: {str(e)}")
        return {"error": "SSL Error", "details": str(e)}

    except Exception as e:
        logger.exception("API call failed")
        return {"error": "Request Failed", "details": str(e)}


# ==============================
# FULL WORKFLOW
# ==============================
def full_flow(api_url: str) -> dict:
    start_time = datetime.now()
    logger.info("========== START FULL FLOW ==========")

    try:
        upload_status = upload_pem_to_blob(LOCAL_PEM_FILE)

        if not upload_status:
            return {"error": "Upload failed"}

        downloaded_file = download_pem_from_blob(DOWNLOADED_PEM_FILE)

        if not downloaded_file:
            return {"error": "Download failed"}

        api_result = call_secure_api(api_url, downloaded_file)

        return {
            "upload": "success",
            "download": downloaded_file,
            "api_result": api_result
        }

    except Exception as e:
        logger.exception("Full flow failed ❌")
        return {"error": str(e)}

    finally:
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Execution time: {duration} seconds")
        logger.info("========== END FULL FLOW ==========\n")


# ==============================
# ENTRY POINT
# ==============================
if __name__ == "__main__":
    TEST_URL: str = "https://example.com"

    result = full_flow(TEST_URL)

    print("\n===== FINAL RESULT =====")
    print(result)