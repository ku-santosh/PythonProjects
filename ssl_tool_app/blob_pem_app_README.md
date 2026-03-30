# 📦 Azure Blob PEM Storage & Access Application

## 🚀 Overview

This application demonstrates how to:

* Upload a `.pem` certificate file to Azure Blob Storage
* Download the `.pem` file securely
* Use the certificate for SSL verification while calling external/internal APIs
* Provide detailed logging for debugging and traceability

⚠️ **Important Note:**
While Azure Blob Storage supports storing `.pem` files, it is **not recommended for sensitive private keys**. For secure storage, consider using Azure Key Vault.

---

## 🏗️ Architecture Flow

```
Local PEM File
      ↓
Upload to Azure Blob Storage
      ↓
Download PEM from Blob
      ↓
Use in HTTPS Request (SSL Verification)
      ↓
Secure API Communication
```

---

## 📁 Project Structure

```
project/
│
├── blob_pem_app.py        # Main application file
├── CA_CERT_CA3.pem        # Input certificate file
├── downloaded_CA_CERT_CA3.pem  # Downloaded certificate (generated)
├── blob_pem_app.log       # Log file (generated)
└── README.md              # Documentation
```

---

## ⚙️ Features

* ✅ Upload `.pem` file to Azure Blob Storage
* ✅ Download `.pem` securely
* ✅ Perform SSL handshake using the certificate
* ✅ Detailed logging (INFO, DEBUG, ERROR)
* ✅ Error handling for:

  * File issues
  * Azure connection errors
  * SSL handshake failures
  * API request failures

---

## 🔧 Prerequisites

* Python 3.8+
* Azure Subscription
* Azure Storage Account

---

## 📦 Install Dependencies

```bash
pip install azure-identity azure-storage-blob requests
```

---

## 🔐 Azure Setup

### 1. Create Storage Account

* Go to Azure Portal
* Create a Storage Account

### 2. Create Container

* Name: `certificates` (or your choice)

### 3. Authentication

#### Option A: Local Development

```bash
az login
```

#### Option B: Azure (Recommended)

* Enable **Managed Identity**
* Assign Role:

  * `Storage Blob Data Contributor`

---

## ⚙️ Configuration

Update these values in `blob_pem_app.py`:

```python
STORAGE_ACCOUNT_URL = "https://<your-storage-account>.blob.core.windows.net"
CONTAINER_NAME = "certificates"
BLOB_NAME = "CA_CERT_CA3.pem"
```

---

## ▶️ How to Run

```bash
python blob_pem_app.py
```

---

## 🧪 Example Output

```text
INFO  | Uploading PEM file
INFO  | Downloading PEM from Blob
INFO  | Calling API
INFO  | API call successful
```

---

## 🔍 Logging

Logs are stored in:

```
blob_pem_app.log
```

### Log Levels:

* INFO → General process flow
* DEBUG → Detailed internal steps
* ERROR → Failures and issues

---

## ❌ Common Errors & Fixes

### 1. File Not Found

```
Error: PEM file not found
```

✔ Ensure file exists in correct path

---

### 2. Authentication Failure

```
DefaultAzureCredential failed
```

✔ Run:

```bash
az login
```

---

### 3. SSL Verification Failed

```
CERTIFICATE_VERIFY_FAILED
```

✔ Check:

* Certificate validity
* Full certificate chain
* Correct server hostname

---

### 4. Blob Access Error

```
AuthorizationPermissionMismatch
```

✔ Ensure role assigned:

* Storage Blob Data Contributor

---

## 🔐 Security Considerations

| Scenario                     | Recommendation         |
| ---------------------------- | ---------------------- |
| Public certificate           | ✅ Blob Storage OK      |
| Private key / sensitive cert | ❌ Use Azure Key Vault  |
| Production environment       | ✅ Use Managed Identity |

---

## 🚀 Best Practices

* Do not store secrets in code
* Use Managed Identity instead of keys
* Rotate certificates regularly
* Use full certificate chain for SSL validation
* Restrict Blob container access

---

## 🔄 Future Enhancements

* 🔐 Integration with Azure Key Vault
* 🌐 Flask API wrapper
* 📊 Monitoring dashboard
* 🔁 Auto certificate rotation
* 🧪 Unit testing support

---

## 📌 Summary

✔ Azure Blob can store `.pem` files
✔ Secure access is possible via Managed Identity
✔ Useful for non-sensitive certificates
✔ Not ideal for private keys → use Azure Key Vault

---

## 👨‍💻 Author

Developed for secure certificate handling and SSL debugging use cases.

---
