# Overhead Analysis of Laucher's operations

This repository contains benchmark scripts and results for evaluating the performance overhead of core operations in the Launcher operations, including cryptographic functions, certificate management, and interactions with digital services. Each subdirectory contains self-contained experiments designed to isolate and measure the execution time of specific operations.

## Directory Structure

```
overhead-analysis/
├── encrypt-decrypt/         # AES encryption/decryption benchmarking
├── exchange-keys/           # Public key exchange benchmarking
├── generate-certificate/    # Certificate generation (RSA + X.509)
├── get-certificate/         # File read (load certificate)
├── get-publickey/           # In-memory dictionary read
├── lockup-service/          # DNS name resolution benchmark
├── read-write/              # HTTP GET/POST benchmark to API1.py
```

## Prerequisites

- Python 3.6+
- Flask (`pip install Flask`)
- Flask-Talisman (`pip install Flask-Talisman`)
- OpenSSL (for certificate generation)
- SQLite3 (`sudo apt install sqlite3 libsqlite3-dev`)
- For HTTPS tests: self-signed `cert.pem` and `priv.pem`

## Experiment Summaries

Each experiment in this repository isolates a specific operation used in the Launcher and measures its execution time across 100 iterations. Below is a summary of each:

- **encrypt-decrypt/**: Measures the time to encrypt and decrypt a 128-byte plaintext using AES-CBC mode. Useful to assess the cost of symmetric cryptographic operations used in secure communications.
- **exchange-keys/**: Simulates the exchange of public keys between a client and a server over HTTPS. Evaluates the time to transmit and store a public key in the integration context.
- **generate-certificate/**: Generates an RSA-2048 key pair and an X.509 certificate with custom extensions. Measures the overhead of certificate creation, a crucial step in trusted environments.
- **get-certificate/**: Measures the time to read a PEM-formatted certificate from disk. Simulates the retrieval of stored certificates for validation.
- **get-publickey/**: Simulates retrieving a public key from an in-memory dictionary. Useful to quantify the minimal overhead of key access operations.
- **lockup-service/**: Benchmarks the DNS resolution time for a remote service (e.g., 'example.com'). Evaluates the delay introduced by service discovery in integration processes.
- **read-write/**: Performs 100 HTTPS GET and POST requests to a running API (e.g., API1.py). Measures the overhead of sending and retrieving data in a secure channel.

## How to Run Each Experiment

Each folder contains a Python script that runs the test and saves output to a CSV file.

### 1. `encrypt-decrypt/`
```bash
cd encrypt-decrypt
python3 encrypt-decrypt.py
```
Outputs:
- `encrypt_results.csv`
- `decrypt_results.csv`

### 2. `exchange-keys/`
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

### 3. `generate-certificate/`
```bash
cd generate-certificate
python3 generatecertificate.py
```
Output: `generateCertificate_results.csv`

### 4. `get-certificate/`
```bash
cd get-certificate
python3 getcertificate.py
```
Output: `getCertificate_results.csv`

### 5. `get-publickey/`
```bash
cd get-publickey
python3 getpublickey.py
```
Output: `getPublicKey_results.csv`

### 6. `lockup-service/`
```bash
cd lockup-service
python3 lockupservice.py
```
Output: `lookupService_results.csv`

### 7. `read-write/`
Start the target API (e.g., API1.py) and then:
```bash
cd read-write
python3 read-write.py
```
Outputs:
- `overhead_get.csv`
- `overhead_post.csv`

## Output Format

All results are saved as CSV with the following columns:

```
iteration,duration_ms
1,12.401
2,13.005
...
```
