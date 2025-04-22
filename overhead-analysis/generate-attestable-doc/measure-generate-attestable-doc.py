import time
import csv
import os

# Number of simulated executions
iterations = 100
output_csv = "generate_attestable_doc_times.csv"
times_ms = []

# Simulated generateAttestableDoc() operation
def generate_attestable_doc():
    # Simulates: file reading, signing, JSON serialization, and disk writing
    data = {
        "program_name": "integration_process",
        "cpu_model": "Morello SoC",
        "capabilities": ["read", "write", "encrypt"],
        "timestamp": time.time()
    }
    serialized = str(data).encode('utf-8')  # simulate serialization
    with open("mock_attestable_doc.txt", "wb") as f:
        f.write(serialized)

# Run the simulation 100 times and measure execution time
for _ in range(iterations):
    start = time.time()
    generate_attestable_doc()
    end = time.time()
    elapsed_ms = (end - start) * 1000
    times_ms.append(elapsed_ms)

# Write execution times to CSV
with open(output_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["execution_time_ms"])
    for t in times_ms:
        writer.writerow([round(t, 4)])

print(f"Execution times saved to: {output_csv}")
