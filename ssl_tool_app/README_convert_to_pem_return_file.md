# PEM Converter Project

## Overview
This project converts a `.text` certificate file into a `.pem` file.

## Files Included

### 1. convert_to_pem_return_file.py
- Reads certificate file
- Converts to PEM format
- Saves output file
- Returns file name

## Setup

### Install Python
Python 3.8+

### Run
python convert_to_pem_return_file.py

## Input
Place your certificate in:
CA_CERT_CA3.text

## Output
CA_CERT_CA3.pem

## Logs
pem_conversion.log

## Notes
- Supports raw base64 and PEM formats
- Handles multiple certificates
