import time
import csv

CERT_PATH = "certificate.pem"
NUM_ITERATIONS = 100
CSV_FILE = "getCertificate_results.csv"

with open(CSV_FILE, mode="w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["iteration", "duration_ms"])

    for i in range(1, NUM_ITERATIONS + 1):
        start = time.perf_counter()
        with open(CERT_PATH, "rb") as cert_file:
            cert = cert_file.read()
        end = time.perf_counter()
        duration = (end - start) * 1000
        writer.writerow([i, f"{duration:.6f}"])
