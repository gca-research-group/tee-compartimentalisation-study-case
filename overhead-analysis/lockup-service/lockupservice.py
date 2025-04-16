import socket
import time
import csv

HOSTNAME = "example.com"
NUM_ITERATIONS = 100
CSV_FILE = "lookupService_results.csv"

with open(CSV_FILE, mode="w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["iteration", "duration_ms"])

    for i in range(1, NUM_ITERATIONS + 1):
        start = time.perf_counter()
        ip = socket.gethostbyname(HOSTNAME)
        end = time.perf_counter()
        duration = (end - start) * 1000
        writer.writerow([i, f"{duration:.3f}"])
