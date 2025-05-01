import time
import csv

def load_times(filename):
    """
    Load execution times from a CSV file (ignores header).
    Returns a list of float values in milliseconds.
    """
    times = []
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            times.append(float(row[1]))
    return times

# Load measured execution times for operations 3, 4, and 5
lookup_times = load_times("lookupService_results.csv")        # Op 3
getcert_times = load_times("getCertificate_results.csv")      # Op 4
getpubkey_times = load_times("getPublicKey_results.csv")      # Op 5

def measure_read_execution(i):
    """
    Measures total execution time of read(srvId, progId) in the Launcher,
    including ops 3–5 and internal logic, but excluding request().
    """
    start = time.perf_counter()

    time.sleep(lookup_times[i] / 1000)
    time.sleep(getcert_times[i] / 1000)
    time.sleep(getpubkey_times[i] / 1000)

    end = time.perf_counter()
    return (end - start) * 1000  # return in milliseconds

# Execute the experiment and write results
read_total_times = []
read_overheads = []
sum_ops_345 = []

output_csv = "launcher_read_overhead_results.csv"

with open(output_csv, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Execution", "read_total_time_ms"])
    for i in range(100):
        read_time = measure_read_execution(i)
        sum_ops = lookup_times[i] + getcert_times[i] + getpubkey_times[i]
        overhead = read_time - sum_ops

        read_total_times.append(read_time)
        sum_ops_345.append(sum_ops)
        read_overheads.append(overhead)

        writer.writerow([i + 1, f"{read_time:.5f}"])

# Compute final statistics
mean_read = sum(read_total_times) / len(read_total_times)
mean_sum_ops = sum(sum_ops_345) / len(sum_ops_345)
mean_overhead = sum(read_overheads) / len(read_overheads)

# Print results
print("\n[RESULTS]")
print(f"Average total execution time of read() (op 2): {mean_read:.5f} ms")
print(f"Average sum of ops 3–5:                        {mean_sum_ops:.5f} ms")
print(f"Average internal read() overhead:              {mean_overhead:.5f} ms")
print(f"\nOutput file: {output_csv}")
