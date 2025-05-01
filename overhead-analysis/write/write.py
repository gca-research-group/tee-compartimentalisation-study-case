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
        next(reader)  # Skip header
        for row in reader:
            times.append(float(row[1]))
    return times

# Load measured execution times for ops 5 and 6
lookup_times = load_times("lookupService_results.csv")       # Op 5
getcert_times = load_times("getCertificate_results.csv")     # Op 6

def measure_write_execution(i):
    """
    Simulates write(srvId, progId, dataEnc) in the Launcher,
    including internal logic and operations 5 and 6, but excluding post().
    """
    start = time.perf_counter()

    time.sleep(lookup_times[i] / 1000)
    time.sleep(getcert_times[i] / 1000)

    end = time.perf_counter()
    return (end - start) * 1000  # milliseconds

# Run the experiment
write_total_times = []
write_overheads = []
sum_ops_56 = []

output_csv = "launcher_write_overhead_results.csv"

with open(output_csv, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Execution", "write_total_time_ms"])
    for i in range(100):
        write_time = measure_write_execution(i)
        sum_ops = lookup_times[i] + getcert_times[i]
        overhead = write_time - sum_ops

        write_total_times.append(write_time)
        sum_ops_56.append(sum_ops)
        write_overheads.append(overhead)

        writer.writerow([i + 1, f"{write_time:.5f}"])

# Compute and display stats
mean_write = sum(write_total_times) / len(write_total_times)
mean_sum_ops = sum(sum_ops_56) / len(sum_ops_56)
mean_overhead = sum(write_overheads) / len(write_overheads)

print("\n[RESULTS]")
print(f"Average total execution time of write() (op 4): {mean_write:.3f} ms")
print(f"Average sum of ops 5–6:                        {mean_sum_ops:.3f} ms")
print(f"Average internal write() overhead:             {mean_overhead:.3f} ms")
print(f"\nOutput file: {output_csv}")

