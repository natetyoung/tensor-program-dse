../llvm-project/build/bin/mlir-opt example.mlir \
  -pass-pipeline='
    builtin.module(
      linalg-morph-ops{named-to-generic},
      one-shot-bufferize{bufferize-function-boundaries},
      func.func(
        convert-linalg-to-affine-loops,
        lower-affine,
        convert-scf-to-cf,
        convert-arith-to-llvm
      ),
      finalize-memref-to-llvm,
      convert-func-to-llvm,
      convert-cf-to-llvm,
      llvm.func(
        reconcile-unrealized-casts
      )
    )' \
  -o lowered.mlir
