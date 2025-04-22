import os
import time
import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "programs-data-base")
PROGRAM_PATH = os.path.join(DATA_DIR, "example.txt")
CSV_PATH = os.path.join(BASE_DIR, "retrieve_times.csv")

os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(PROGRAM_PATH):
    with open(PROGRAM_PATH, "w") as f:
        f.write("This is an example program.\n" * 1000)

def retrieve_program():
    with open(PROGRAM_PATH, "r") as f:
        return f.read()

def main():
    times = []

    for _ in range(100):
        start = time.perf_counter()
        _ = retrieve_program()
        end = time.perf_counter()
        elapsed_ms = (end - start) * 1000
        times.append(elapsed_ms)

    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["run", "retrieve_time_ms"])
        for i, t in enumerate(times, 1):
            writer.writerow([i, f"{t:.3f}"])

    print(f"Done. Results saved to: {CSV_PATH}")

if __name__ == "__main__":
    main()
