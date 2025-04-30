# Overhead Analysis of Launcher Operations

This repository contains benchmark scripts and results for evaluating the performance overhead of the read and write actions supported by the Launcher. These actions are composed of the following operations: lookupService(), getCertificate(), and getProgramPublicKey(). Each subdirectory contains self-contained experiments that isolate and measure the execution time of these operations individually.

---

## Directory Structure

```
overhead-analysis/
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

- **lockup-service/**: Benchmarks the DNS resolution time for a remote service (e.g., 'example.com').
- **get-certificate/**: Measures the time to read a PEM-formatted certificate from disk.
- **get-publickey/**: Simulates retrieving a public key from an in-memory dictionary.

---

## How to Run Each Experiment

Each folder contains a Python script that runs the test and saves output to a CSV file.

---

### 1. `lockup-service/`
```bash
cd lockup-service
python3 lockupservice.py
```
Output: `lookupService_results.csv`

---

### 2. `get-certificate/`
```bash
cd get-certificate
python3 getcertificate.py
```
Output: `getCertificate_results.csv`

---

### 3. `get-publickey/`
```bash
cd get-publickey
python3 getpublickey.py
```
Output: `getPublicKey_results.csv`

---
