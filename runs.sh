#!/bin/bash

# List of sizes
sizes=("tiny" "small" "med" "huge")

# List of capacities
caps=("4096 8192 16384" "4096 8192 16384" "4096 8192 16384" "4096 8192 16384")

# Directory where the C files are located
src_dir="../../"

for i in "${!sizes[@]}"; do
    size="${sizes[$i]}"
    cap_list=(${caps[$i]})
    
    # Directory to store logs
    log_dir="${src_dir}${size}_gpt_logs-O3-O3/"
    file_dir="${src_dir}${size}_gpt/"
    mkdir -p "$log_dir"
    mkdir -p "$file_dir"
    
    src_file="${file_dir}${size}gpt.c"
    exe_file="${file_dir}${size}gpt.out"
    echo $file_dir
    echo $exe_file
    
    echo "Compiling $src_file with clang ..."
    clang -O3 -fno-vectorize -fno-slp-vectorize -fno-unroll-loops -o "$exe_file" "$src_file"
    
    for run in {1..5}; do
        log_file="${log_dir}${size}gpt_run${run}.log"
        echo "Running $exe_file (run $run) ... logging to $log_file"
        "$exe_file" > "$log_file" 2>&1
        echo "Finished unopt run $run."
        echo "-------------------------------------"
    done
    
    for cap in "${cap_list[@]}"; do
        src_file="${file_dir}${size}gpt_opt_${cap}.c"
        exe_file="${file_dir}${size}gpt_opt_${cap}.out"
        echo $exe_file
    
        echo "Compiling $src_file with clang ..."
        clang -O3 -fno-vectorize -fno-slp-vectorize -fno-unroll-loops -o "$exe_file" "$src_file"
    
        for run in {1..5}; do
            log_file="${log_dir}${size}gpt_opt_${cap}_run${run}.log"
            echo "Running $exe_file (run $run) ... logging to $log_file"
            "$exe_file" > "$log_file" 2>&1
            echo "Finished run $run for capacity $cap."
            echo "-------------------------------------"
        done
    done
done