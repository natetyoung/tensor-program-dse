clang ../../gpt.c \               
  -O3 \   
  -Xclang -disable-O0-optnone \
  -fno-vectorize -fno-slp-vectorize -emit-llvm -S \
  -o ../../gpt_before-polly.ll

/Users/arw274/llvm-polly/bin/opt \
  -polly \
  -polly-detect \
  -polly-print-scops \
  -disable-output \
  ../../gpt_before-polly.ll