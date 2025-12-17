import os
import re
import csv

# Sizes and capacities (should match your bash script)
sizes = ["tiny", "small", "med", "large"]
caps = [
    [8192, 16384, 32768],
    [32768, 65536, 131072],
    [65536, 131072, 262144],
    [262144, 524288, 1048576]
]

# Regex to match the timing line in the logs
time_pattern = re.compile(r"Time:\s*([0-9.e+-]+)")

# Output file
output_file = "averaged_times.csv"

results = []

for i, size in enumerate(sizes):
    log_dir = f"{size}_gpt_logs"
    
    # --- Unoptimized runs ---
    times = []
    for run in range(1, 11):
        log_file = os.path.join(log_dir, f"{size}gpt_run{run}.log")
        if not os.path.exists(log_file):
            continue
        with open(log_file, "r") as f:
            content = f.read()
            match = time_pattern.search(content)
            if match:
                times.append(float(match.group(1)))
    if times:
        avg_time = sum(times) / len(times)
        results.append([size, "unopt", "N/A", avg_time])
    
    # --- Optimized runs ---
    for cap in caps[i]:
        times = []
        for run in range(1, 11):
            log_file = os.path.join(log_dir, f"{size}gpt_opt_{cap}_run{run}.log")
            if not os.path.exists(log_file):
                continue
            with open(log_file, "r") as f:
                content = f.read()
                match = time_pattern.search(content)
                if match:
                    times.append(float(match.group(1)))
  
        if times:
            print(f"{size} {cap if cap != 'N/A' else 'unopt'}: {len(times)} runs -> {times}")
            avg_time = sum(times) / len(times)
            results.append([size, "opt", cap, avg_time])

# Write results to CSV
with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["size", "option", "capacity", "avg_time_sec"])
    writer.writerows(results)

print(f"Averages written to {output_file}")
