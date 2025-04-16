import time
import csv

keys = {"svc": b"pubkey"}
NUM_ITERATIONS = 100
CSV_FILE = "getPublicKey_results.csv"

with open(CSV_FILE, mode="w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["iteration", "duration_ms"])

    for i in range(1, NUM_ITERATIONS + 1):
        start = time.perf_counter()
        key = keys["svc"]
        end = time.perf_counter()
        duration = (end - start) * 1000
        writer.writerow([i, f"{duration:.6f}"])
