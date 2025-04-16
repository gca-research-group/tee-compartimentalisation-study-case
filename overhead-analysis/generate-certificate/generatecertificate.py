import time
import subprocess
import csv
import os

CSV_FILE = "generateCertificate_results.csv"
NUM_ITERATIONS = 100

os.makedirs("temp_certs", exist_ok=True)

with open(CSV_FILE, mode="w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["iteration", "duration_ms"])

    for i in range(1, NUM_ITERATIONS + 1):
        priv_path = f"temp_certs/priv_{i}.pem"
        cert_path = f"temp_certs/cert_{i}.pem"

        start = time.perf_counter()

        subprocess.run([
            "openssl", "genpkey", "-algorithm", "RSA",
            "-out", priv_path,
            "-pkeyopt", "rsa_keygen_bits:2048"
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        subprocess.run([
            "openssl", "req", "-new", "-x509",
            "-key", priv_path,
            "-out", cert_path,
            "-days", "1",
            "-subj", "/C=BR/ST=RS/L=Ijui/O=Unijui/CN=example.com"
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        end = time.perf_counter()
        duration = (end - start) * 1000
        writer.writerow([i, f"{duration:.3f}"])

for file in os.listdir("temp_certs"):
    os.remove(os.path.join("temp_certs", file))
os.rmdir("temp_certs")
