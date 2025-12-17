#!/bin/bash

# List of sizes
sizes=("tiny" "small" "med" "large")

# List of capacities
caps=("8192 16384 32768" "32768 65536 131072" "65536 131072 262144" "262144 524288 1048576")

# Directory where the C files are located
src_dir="../../"

for i in "${!sizes[@]}"; do
    size="${sizes[$i]}"
    cap_list=(${caps[$i]})
    
    # Directory to store logs
    log_dir="${src_dir}${size}_gpt_logs/"
    mkdir -p "$log_dir"
    
    src_file="${src_dir}${size}gpt.c"
    exe_file="${src_dir}${size}gpt.out"
    
    echo "Compiling $src_file with clang ..."
    clang -O3 -fno-vectorize -fno-slp-vectorize -fno-unroll-loops -o "$exe_file" "$src_file"
    
    for run in {1..10}; do
        log_file="${log_dir}${size}gpt_run${run}.log"
        echo "Running $exe_file (run $run) ... logging to $log_file"
        "$exe_file" > "$log_file" 2>&1
        echo "Finished unopt run $run."
        echo "-------------------------------------"
    done
    
    for cap in "${cap_list[@]}"; do
        src_file="${src_dir}${size}gpt_opt_${cap}.c"
        exe_file="${src_dir}${size}gpt_opt_${cap}.out"
    
        echo "Compiling $src_file with clang ..."
        clang -O0 -o "$exe_file" "$src_file"
    
        for run in {1..10}; do
            log_file="${log_dir}${size}gpt_opt_${cap}_run${run}.log"
            echo "Running $exe_file (run $run) ... logging to $log_file"
            "$exe_file" > "$log_file" 2>&1
            echo "Finished run $run for capacity $cap."
            echo "-------------------------------------"
        done
    done
done