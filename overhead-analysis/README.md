# Overhead Analysis of Laucher's operations

This repository contains benchmark scripts and results for evaluating the performance overhead of core operations in the Launcher operations, including cryptographic functions, certificate management, and interactions with digital services. Each subdirectory contains self-contained experiments designed to isolate and measure the execution time of specific operations.

---

## Directory Structure

```
overhead-analysis/        
├── exchange-keys/           
├── generate-certificate/    
├── get-certificate/         
├── get-publickey/           
├── lockup-service/         
├── read-write/             
```

---

## System Requirements

- **Hardware**: Research Morello Board (Research Morello SoC r0p0)
- **CPU**: 4 cores
- **RAM**: 16 GB DDR4
- **Operating System**: CheriBSD 22.12 
- **Execution Model**: Conventional environment

---

## Prerequisites

- Python 3.6+
- Flask (`pip install Flask`)
- OpenSSL (for certificate generation)
- For HTTPS tests: self-signed `cert.pem` and `priv.pem`

---

## Experiment Summaries

Each experiment in this repository isolates a specific operation used in the Launcher and measures its execution time across 100 iterations. Below is a summary of each:

- **exchange-keys/**: Simulates the exchange of public keys between a client and a server over HTTPS.
- **generate-certificate/**: Generates an RSA-2048 key pair and an X.509 certificate with custom extensions.
- **get-certificate/**: Measures the time to read a PEM-formatted certificate from disk.
- **get-publickey/**: Simulates retrieving a public key from an in-memory dictionary.
- **lockup-service/**: Benchmarks the DNS resolution time for a remote service (e.g., 'example.com').
- **read-write/**: Performs 100 HTTPS GET and POST requests to a running API (e.g., API1.py).

---

## How to Run Each Experiment

Each folder contains a Python script that runs the test and saves output to a CSV file.

---

### 1. `exchange-keys/`
Start the server:
```bash
cd exchange-keys/server
python3 exchangekeysserver.py
```
Then run the client:
```bash
cd ../client
python3 exchangekeysclient.py
```
Output: `exchangeKeys_results.csv`

---

### 2. `generate-certificate/`
```bash
cd generate-certificate
python3 generatecertificate.py
```
Output: `generateCertificate_results.csv`

---

### 3. `get-certificate/`
```bash
cd get-certificate
python3 getcertificate.py
```
Output: `getCertificate_results.csv`

---

### 4. `get-publickey/`
```bash
cd get-publickey
python3 getpublickey.py
```
Output: `getPublicKey_results.csv`

---

### 5. `lockup-service/`
```bash
cd lockup-service
python3 lockupservice.py
```
Output: `lookupService_results.csv`

---

### 6. `read-write/`
Start the target API (e.g., API1.py) and then:
```bash
cd read-write
python3 read-write.py
```
Outputs:
- `overhead_get.csv`
- `overhead_post.csv`

---
