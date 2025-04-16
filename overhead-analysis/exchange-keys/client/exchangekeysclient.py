import requests
import time
import csv
import os

SERVER_URL = "https://localhost:8443/exchange-key"
MY_ID = "integration_process"
MY_PUBLIC_KEY_FILE = "public_key.pem"
CSV_FILE = "exchangeKeys_results.csv"

# Carregar chave pública
with open(MY_PUBLIC_KEY_FILE, "r") as f:
    pubkey_pem = f.read()

# Payload base
payload = {
    "id": MY_ID,
    "public_key": pubkey_pem
}

# Desabilitar TLS apenas para testes locais
verify_tls = False

# Criar arquivo CSV
with open(CSV_FILE, mode="w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["iteration", "duration_ms", "status"])

    for i in range(1, 101):
        start = time.perf_counter()
        try:
            response = requests.post(SERVER_URL, json=payload, verify=verify_tls)
            status = response.status_code
        except Exception as e:
            status = f"error: {str(e)}"
        end = time.perf_counter()
        duration = (end - start) * 1000
        writer.writerow([i, f"{duration:.3f}", status])
