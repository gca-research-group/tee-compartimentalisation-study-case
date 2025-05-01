# Overhead Analysis of Launcher Operations

This repository contains benchmark scripts and results for evaluating the performance overhead of the read and write actions supported by the Launcher. These actions are composed of the following operations: read(), write(), lookupService(), getCertificate(), and getProgramPublicKey(). Each subdirectory contains self-contained experiments that isolate and measure the execution time of these operations individually.

---

## Directory Structure

```
overhead-analysis/
├── read/
├── write/
├── lockup-service/    
├── get-certificate/         
├── get-publickey/           

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
---

## Experiment Summaries

Each experiment in this repository isolates a specific operation used in the Launcher and measures its execution time across 100 iterations. Below is a summary of each:

- **read/**: Measures the total execution time of the `read()` function, including internal Launcher overhead and the operations `lookupService()`, `getCertificate()`, and `getProgramPublicKey()`. It calculates the internal overhead by subtracting the time of the individual operations from the full function time.
- **write/**: Measures the total execution time of the `write()` function, including internal Launcher overhead and the operations `lookupService()` and `getCertificate()`. It similarly calculates the internal overhead from measured data.
- **lockup-service/**: Benchmarks the DNS resolution time for a remote service (e.g., 'example.com').
- **get-certificate/**: Measures the time to read a PEM-formatted certificate from disk.
- **get-publickey/**: Simulates retrieving a public key from an in-memory dictionary.

---

## How to Run Each Experiment

Each folder contains a Python script that runs the test and saves output to a CSV file.

---
### 1. `read/`
```bash
cd read
python3 read.py
```
Output: `launcher_read_overhead_results.csv`

---

### 2. `write/`
```bash
cd write
python3 write.py
```
Output: `launcher_write_overhead_results.csv`

---

### 3. `lockup-service/`
```bash
cd lockup-service
python3 lockupservice.py
```
Output: `lookupService_results.csv`

---

### 4. `get-certificate/`
```bash
cd get-certificate
python3 getcertificate.py
```
Output: `getCertificate_results.csv`

---

### 5. `get-publickey/`
```bash
cd get-publickey
python3 getpublickey.py
```
Output: `getPublicKey_results.csv`

---
