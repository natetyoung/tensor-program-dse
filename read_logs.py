import os
import re
import csv
import argparse

# Sizes and capacities (should match your bash script)
sizes = ["tiny", "small", "med", "huge"]
caps = [
    [4096, 8192, 16384],
    [4096, 8192, 16384],
    [4096, 8192, 16384],
    [4096, 8192, 16384],
]

# Regex to match the timing line in the logs
time_pattern = re.compile(r"Time:\s*([0-9.e+-]+)")

parser = argparse.ArgumentParser()
parser.add_argument("--flags", type=str, help="compile flags")
args = parser.parse_args()
flags = args.flags

# Output file
output_file = f"averaged_times{flags}.csv"

results = []

for i, size in enumerate(sizes):
    log_dir = f"{size}_gpt_logs{flags}"
    
    # --- Unoptimized runs ---
    times = []
    for run in range(1, 6):
        log_file = os.path.join(log_dir, f"{size}gpt_run{run}.log")
        if not os.path.exists(log_file):
            print("missing", log_file)
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
        for run in range(1, 6):
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
