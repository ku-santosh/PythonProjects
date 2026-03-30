# SSL Certificate Debug Tool

## Overview
This application converts certificate text files into PEM format and helps debug SSL handshake issues with APIs.

## Features
- Convert .text certificate to .pem
- Validate PEM file
- Debug SSL handshake
- Call APIs with custom certificate

## Setup

### 📦 Install Dependencies
pip install flask requests
pip install azure-identity azure-keyvault-secrets

### Run app
python app.py

## Endpoints
- /full-check/uat
- /full-check/prod

## Usage
1. Place your certificate in CA_CERT_CA3.text
2. Run the app
3. Open browser: http://127.0.0.1:5000/full-check/uat

## Notes
- Ensure certificate chain is complete
- Use correct hostnames

## 📦 How to Run
python convert_to_pem.py

## 🔍 Example Logs
- INFO | Reading input file
- INFO | Detected existing PEM format
- INFO | Found 2 certificates
- INFO | Writing PEM file
- INFO | PEM validation successful

## ⚡ Why This Is Production-Ready

- ✔ Handles all real-world certificate formats
- ✔ Supports certificate chains
- ✔ Includes full logging for debugging
- ✔ Prevents invalid base64 issues
- ✔ Validates certificate after conversion