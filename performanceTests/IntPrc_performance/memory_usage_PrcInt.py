import subprocess
import psutil
import time
import csv

def main():
    process_list = []
    max_memory_usage = psutil.virtual_memory().total
    csv_file = 'memory_usage_PrcInt.csv'
    start_time = time.time()

    with open(csv_file, 'w', newline='') as csvfile:
        fieldnames = ['Number of Processes', 'Memory Used (MB)', 'Time Elapsed (ms)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        while True:
            # Start a new process
            process = subprocess.Popen(['env', 'LD_C18N_LIBRARY_PATH=.', './integration_process'])
            process_list.append(process)

            # Give some time for the process to start and allocate memory
            time.sleep(0.5)

            # Check memory usage
            memory_used = psutil.virtual_memory().used
            time_elapsed = (time.time() - start_time) * 1000  # Convert to milliseconds
            num_processes = len(process_list)
            
            writer.writerow({
                'Number of Processes': num_processes,
                'Memory Used (MB)': memory_used / (1024 * 1024),
                'Time Elapsed (ms)': time_elapsed
            })

            print(f'Processes: {num_processes}, Memory Used: {memory_used / (1024 * 1024):.2f} MB, Time Elapsed: {time_elapsed:.2f} ms')

            # Check if memory usage exceeds 90% of total memory
            if memory_used > max_memory_usage * 0.9:
                print("Memory usage exceeded 90% of total memory. Stopping...")
                break

            # Wait for 2 seconds before starting the next process
            time.sleep(2)

        # Terminate all started processes
        for process in process_list:
            process.terminate()
            process.wait()

    print(f'Report saved to {csv_file}')

if __name__ == '__main__':
    main()
