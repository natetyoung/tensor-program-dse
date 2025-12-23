; ModuleID = 'small_gpt/smallgpt.c'
source_filename = "small_gpt/smallgpt.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128-Fn32"
target triple = "arm64-apple-macosx15.0.0"

%struct.timespec = type { i64, i64 }

@.str = private unnamed_addr constant [10 x i8] c"Time: %f\0A\00", align 1
@.str.1 = private unnamed_addr constant [10 x i8] c"Test: %f\0A\00", align 1

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define void @einsum_0(ptr noalias noundef %0, ptr noalias noundef %1, ptr noalias noundef %2) #0 {
  %4 = alloca ptr, align 8
  %5 = alloca ptr, align 8
  %6 = alloca ptr, align 8
  %7 = alloca i32, align 4
  %8 = alloca i32, align 4
  %9 = alloca float, align 4
  %10 = alloca i32, align 4
  store ptr %0, ptr %4, align 8
  store ptr %1, ptr %5, align 8
  store ptr %2, ptr %6, align 8
  store i32 0, ptr %7, align 4
  br label %11

11:                                               ; preds = %60, %3
  %12 = load i32, ptr %7, align 4
  %13 = icmp slt i32 %12, 64
  br i1 %13, label %14, label %63

14:                                               ; preds = %11
  store i32 0, ptr %8, align 4
  br label %15

15:                                               ; preds = %56, %14
  %16 = load i32, ptr %8, align 4
  %17 = icmp slt i32 %16, 256
  br i1 %17, label %18, label %59

18:                                               ; preds = %15
  store float 0.000000e+00, ptr %9, align 4
  store i32 0, ptr %10, align 4
  br label %19

19:                                               ; preds = %43, %18
  %20 = load i32, ptr %10, align 4
  %21 = icmp slt i32 %20, 256
  br i1 %21, label %22, label %46

22:                                               ; preds = %19
  %23 = load ptr, ptr %4, align 8
  %24 = load i32, ptr %7, align 4
  %25 = mul nsw i32 %24, 256
  %26 = load i32, ptr %10, align 4
  %27 = mul nsw i32 %26, 1
  %28 = add nsw i32 %25, %27
  %29 = sext i32 %28 to i64
  %30 = getelementptr inbounds float, ptr %23, i64 %29
  %31 = load float, ptr %30, align 4
  %32 = load ptr, ptr %5, align 8
  %33 = load i32, ptr %10, align 4
  %34 = mul nsw i32 %33, 256
  %35 = load i32, ptr %8, align 4
  %36 = mul nsw i32 %35, 1
  %37 = add nsw i32 %34, %36
  %38 = sext i32 %37 to i64
  %39 = getelementptr inbounds float, ptr %32, i64 %38
  %40 = load float, ptr %39, align 4
  %41 = load float, ptr %9, align 4
  %42 = call float @llvm.fmuladd.f32(float %31, float %40, float %41)
  store float %42, ptr %9, align 4
  br label %43

43:                                               ; preds = %22
  %44 = load i32, ptr %10, align 4
  %45 = add nsw i32 %44, 1
  store i32 %45, ptr %10, align 4
  br label %19, !llvm.loop !6

46:                                               ; preds = %19
  %47 = load float, ptr %9, align 4
  %48 = load ptr, ptr %6, align 8
  %49 = load i32, ptr %7, align 4
  %50 = mul nsw i32 %49, 256
  %51 = load i32, ptr %8, align 4
  %52 = mul nsw i32 %51, 1
  %53 = add nsw i32 %50, %52
  %54 = sext i32 %53 to i64
  %55 = getelementptr inbounds float, ptr %48, i64 %54
  store float %47, ptr %55, align 4
  br label %56

56:                                               ; preds = %46
  %57 = load i32, ptr %8, align 4
  %58 = add nsw i32 %57, 1
  store i32 %58, ptr %8, align 4
  br label %15, !llvm.loop !8

59:                                               ; preds = %15
  br label %60

60:                                               ; preds = %59
  %61 = load i32, ptr %7, align 4
  %62 = add nsw i32 %61, 1
  store i32 %62, ptr %7, align 4
  br label %11, !llvm.loop !9

63:                                               ; preds = %11
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fmuladd.f32(float, float, float) #1

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define void @einsum_1(ptr noalias noundef %0, ptr noalias noundef %1, ptr noalias noundef %2) #0 {
  %4 = alloca ptr, align 8
  %5 = alloca ptr, align 8
  %6 = alloca ptr, align 8
  %7 = alloca i32, align 4
  %8 = alloca i32, align 4
  %9 = alloca float, align 4
  %10 = alloca i32, align 4
  store ptr %0, ptr %4, align 8
  store ptr %1, ptr %5, align 8
  store ptr %2, ptr %6, align 8
  store i32 0, ptr %7, align 4
  br label %11

11:                                               ; preds = %60, %3
  %12 = load i32, ptr %7, align 4
  %13 = icmp slt i32 %12, 64
  br i1 %13, label %14, label %63

14:                                               ; preds = %11
  store i32 0, ptr %8, align 4
  br label %15

15:                                               ; preds = %56, %14
  %16 = load i32, ptr %8, align 4
  %17 = icmp slt i32 %16, 64
  br i1 %17, label %18, label %59

18:                                               ; preds = %15
  store float 0.000000e+00, ptr %9, align 4
  store i32 0, ptr %10, align 4
  br label %19

19:                                               ; preds = %43, %18
  %20 = load i32, ptr %10, align 4
  %21 = icmp slt i32 %20, 256
  br i1 %21, label %22, label %46

22:                                               ; preds = %19
  %23 = load ptr, ptr %4, align 8
  %24 = load i32, ptr %7, align 4
  %25 = mul nsw i32 %24, 256
  %26 = load i32, ptr %10, align 4
  %27 = mul nsw i32 %26, 1
  %28 = add nsw i32 %25, %27
  %29 = sext i32 %28 to i64
  %30 = getelementptr inbounds float, ptr %23, i64 %29
  %31 = load float, ptr %30, align 4
  %32 = load ptr, ptr %5, align 8
  %33 = load i32, ptr %8, align 4
  %34 = mul nsw i32 %33, 256
  %35 = load i32, ptr %10, align 4
  %36 = mul nsw i32 %35, 1
  %37 = add nsw i32 %34, %36
  %38 = sext i32 %37 to i64
  %39 = getelementptr inbounds float, ptr %32, i64 %38
  %40 = load float, ptr %39, align 4
  %41 = load float, ptr %9, align 4
  %42 = call float @llvm.fmuladd.f32(float %31, float %40, float %41)
  store float %42, ptr %9, align 4
  br label %43

43:                                               ; preds = %22
  %44 = load i32, ptr %10, align 4
  %45 = add nsw i32 %44, 1
  store i32 %45, ptr %10, align 4
  br label %19, !llvm.loop !10

46:                                               ; preds = %19
  %47 = load float, ptr %9, align 4
  %48 = load ptr, ptr %6, align 8
  %49 = load i32, ptr %7, align 4
  %50 = mul nsw i32 %49, 64
  %51 = load i32, ptr %8, align 4
  %52 = mul nsw i32 %51, 1
  %53 = add nsw i32 %50, %52
  %54 = sext i32 %53 to i64
  %55 = getelementptr inbounds float, ptr %48, i64 %54
  store float %47, ptr %55, align 4
  br label %56

56:                                               ; preds = %46
  %57 = load i32, ptr %8, align 4
  %58 = add nsw i32 %57, 1
  store i32 %58, ptr %8, align 4
  br label %15, !llvm.loop !11

59:                                               ; preds = %15
  br label %60

60:                                               ; preds = %59
  %61 = load i32, ptr %7, align 4
  %62 = add nsw i32 %61, 1
  store i32 %62, ptr %7, align 4
  br label %11, !llvm.loop !12

63:                                               ; preds = %11
  ret void
}

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define void @einsum_2(ptr noalias noundef %0, ptr noalias noundef %1, ptr noalias noundef %2) #0 {
  %4 = alloca ptr, align 8
  %5 = alloca ptr, align 8
  %6 = alloca ptr, align 8
  %7 = alloca i32, align 4
  %8 = alloca i32, align 4
  %9 = alloca float, align 4
  %10 = alloca i32, align 4
  store ptr %0, ptr %4, align 8
  store ptr %1, ptr %5, align 8
  store ptr %2, ptr %6, align 8
  store i32 0, ptr %7, align 4
  br label %11

11:                                               ; preds = %60, %3
  %12 = load i32, ptr %7, align 4
  %13 = icmp slt i32 %12, 64
  br i1 %13, label %14, label %63

14:                                               ; preds = %11
  store i32 0, ptr %8, align 4
  br label %15

15:                                               ; preds = %56, %14
  %16 = load i32, ptr %8, align 4
  %17 = icmp slt i32 %16, 256
  br i1 %17, label %18, label %59

18:                                               ; preds = %15
  store float 0.000000e+00, ptr %9, align 4
  store i32 0, ptr %10, align 4
  br label %19

19:                                               ; preds = %43, %18
  %20 = load i32, ptr %10, align 4
  %21 = icmp slt i32 %20, 64
  br i1 %21, label %22, label %46

22:                                               ; preds = %19
  %23 = load ptr, ptr %4, align 8
  %24 = load i32, ptr %7, align 4
  %25 = mul nsw i32 %24, 64
  %26 = load i32, ptr %10, align 4
  %27 = mul nsw i32 %26, 1
  %28 = add nsw i32 %25, %27
  %29 = sext i32 %28 to i64
  %30 = getelementptr inbounds float, ptr %23, i64 %29
  %31 = load float, ptr %30, align 4
  %32 = load ptr, ptr %5, align 8
  %33 = load i32, ptr %10, align 4
  %34 = mul nsw i32 %33, 256
  %35 = load i32, ptr %8, align 4
  %36 = mul nsw i32 %35, 1
  %37 = add nsw i32 %34, %36
  %38 = sext i32 %37 to i64
  %39 = getelementptr inbounds float, ptr %32, i64 %38
  %40 = load float, ptr %39, align 4
  %41 = load float, ptr %9, align 4
  %42 = call float @llvm.fmuladd.f32(float %31, float %40, float %41)
  store float %42, ptr %9, align 4
  br label %43

43:                                               ; preds = %22
  %44 = load i32, ptr %10, align 4
  %45 = add nsw i32 %44, 1
  store i32 %45, ptr %10, align 4
  br label %19, !llvm.loop !13

46:                                               ; preds = %19
  %47 = load float, ptr %9, align 4
  %48 = load ptr, ptr %6, align 8
  %49 = load i32, ptr %7, align 4
  %50 = mul nsw i32 %49, 256
  %51 = load i32, ptr %8, align 4
  %52 = mul nsw i32 %51, 1
  %53 = add nsw i32 %50, %52
  %54 = sext i32 %53 to i64
  %55 = getelementptr inbounds float, ptr %48, i64 %54
  store float %47, ptr %55, align 4
  br label %56

56:                                               ; preds = %46
  %57 = load i32, ptr %8, align 4
  %58 = add nsw i32 %57, 1
  store i32 %58, ptr %8, align 4
  br label %15, !llvm.loop !14

59:                                               ; preds = %15
  br label %60

60:                                               ; preds = %59
  %61 = load i32, ptr %7, align 4
  %62 = add nsw i32 %61, 1
  store i32 %62, ptr %7, align 4
  br label %11, !llvm.loop !15

63:                                               ; preds = %11
  ret void
}

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define i32 @main() #0 {
  %1 = alloca i32, align 4
  %2 = alloca %struct.timespec, align 8
  %3 = alloca %struct.timespec, align 8
  %4 = alloca ptr, align 8
  %5 = alloca i32, align 4
  %6 = alloca ptr, align 8
  %7 = alloca i32, align 4
  %8 = alloca ptr, align 8
  %9 = alloca i32, align 4
  %10 = alloca ptr, align 8
  %11 = alloca i32, align 4
  %12 = alloca ptr, align 8
  %13 = alloca i32, align 4
  %14 = alloca ptr, align 8
  %15 = alloca i32, align 4
  %16 = alloca ptr, align 8
  %17 = alloca i32, align 4
  %18 = alloca double, align 8
  store i32 0, ptr %1, align 4
  %19 = call i32 @clock_gettime(i32 noundef 6, ptr noundef %2)
  %20 = call ptr @malloc(i64 noundef 65536) #4
  store ptr %20, ptr %4, align 8
  store i32 0, ptr %5, align 4
  br label %21

21:                                               ; preds = %29, %0
  %22 = load i32, ptr %5, align 4
  %23 = icmp slt i32 %22, 16384
  br i1 %23, label %24, label %32

24:                                               ; preds = %21
  %25 = load ptr, ptr %4, align 8
  %26 = load i32, ptr %5, align 4
  %27 = sext i32 %26 to i64
  %28 = getelementptr inbounds float, ptr %25, i64 %27
  store float 1.000000e+00, ptr %28, align 4
  br label %29

29:                                               ; preds = %24
  %30 = load i32, ptr %5, align 4
  %31 = add nsw i32 %30, 1
  store i32 %31, ptr %5, align 4
  br label %21, !llvm.loop !16

32:                                               ; preds = %21
  %33 = call ptr @malloc(i64 noundef 262144) #4
  store ptr %33, ptr %6, align 8
  store i32 0, ptr %7, align 4
  br label %34

34:                                               ; preds = %42, %32
  %35 = load i32, ptr %7, align 4
  %36 = icmp slt i32 %35, 65536
  br i1 %36, label %37, label %45

37:                                               ; preds = %34
  %38 = load ptr, ptr %6, align 8
  %39 = load i32, ptr %7, align 4
  %40 = sext i32 %39 to i64
  %41 = getelementptr inbounds float, ptr %38, i64 %40
  store float 1.000000e+00, ptr %41, align 4
  br label %42

42:                                               ; preds = %37
  %43 = load i32, ptr %7, align 4
  %44 = add nsw i32 %43, 1
  store i32 %44, ptr %7, align 4
  br label %34, !llvm.loop !17

45:                                               ; preds = %34
  %46 = call ptr @malloc(i64 noundef 65536) #4
  store ptr %46, ptr %8, align 8
  store i32 0, ptr %9, align 4
  br label %47

47:                                               ; preds = %55, %45
  %48 = load i32, ptr %9, align 4
  %49 = icmp slt i32 %48, 16384
  br i1 %49, label %50, label %58

50:                                               ; preds = %47
  %51 = load ptr, ptr %8, align 8
  %52 = load i32, ptr %9, align 4
  %53 = sext i32 %52 to i64
  %54 = getelementptr inbounds float, ptr %51, i64 %53
  store float 1.000000e+00, ptr %54, align 4
  br label %55

55:                                               ; preds = %50
  %56 = load i32, ptr %9, align 4
  %57 = add nsw i32 %56, 1
  store i32 %57, ptr %9, align 4
  br label %47, !llvm.loop !18

58:                                               ; preds = %47
  %59 = call ptr @malloc(i64 noundef 65536) #4
  store ptr %59, ptr %10, align 8
  store i32 0, ptr %11, align 4
  br label %60

60:                                               ; preds = %68, %58
  %61 = load i32, ptr %11, align 4
  %62 = icmp slt i32 %61, 16384
  br i1 %62, label %63, label %71

63:                                               ; preds = %60
  %64 = load ptr, ptr %10, align 8
  %65 = load i32, ptr %11, align 4
  %66 = sext i32 %65 to i64
  %67 = getelementptr inbounds float, ptr %64, i64 %66
  store float 1.000000e+00, ptr %67, align 4
  br label %68

68:                                               ; preds = %63
  %69 = load i32, ptr %11, align 4
  %70 = add nsw i32 %69, 1
  store i32 %70, ptr %11, align 4
  br label %60, !llvm.loop !19

71:                                               ; preds = %60
  %72 = call ptr @malloc(i64 noundef 16384) #4
  store ptr %72, ptr %12, align 8
  store i32 0, ptr %13, align 4
  br label %73

73:                                               ; preds = %81, %71
  %74 = load i32, ptr %13, align 4
  %75 = icmp slt i32 %74, 4096
  br i1 %75, label %76, label %84

76:                                               ; preds = %73
  %77 = load ptr, ptr %12, align 8
  %78 = load i32, ptr %13, align 4
  %79 = sext i32 %78 to i64
  %80 = getelementptr inbounds float, ptr %77, i64 %79
  store float 1.000000e+00, ptr %80, align 4
  br label %81

81:                                               ; preds = %76
  %82 = load i32, ptr %13, align 4
  %83 = add nsw i32 %82, 1
  store i32 %83, ptr %13, align 4
  br label %73, !llvm.loop !20

84:                                               ; preds = %73
  %85 = call ptr @malloc(i64 noundef 65536) #4
  store ptr %85, ptr %14, align 8
  store i32 0, ptr %15, align 4
  br label %86

86:                                               ; preds = %94, %84
  %87 = load i32, ptr %15, align 4
  %88 = icmp slt i32 %87, 16384
  br i1 %88, label %89, label %97

89:                                               ; preds = %86
  %90 = load ptr, ptr %14, align 8
  %91 = load i32, ptr %15, align 4
  %92 = sext i32 %91 to i64
  %93 = getelementptr inbounds float, ptr %90, i64 %92
  store float 1.000000e+00, ptr %93, align 4
  br label %94

94:                                               ; preds = %89
  %95 = load i32, ptr %15, align 4
  %96 = add nsw i32 %95, 1
  store i32 %96, ptr %15, align 4
  br label %86, !llvm.loop !21

97:                                               ; preds = %86
  %98 = call ptr @malloc(i64 noundef 65536) #4
  store ptr %98, ptr %16, align 8
  store i32 0, ptr %17, align 4
  br label %99

99:                                               ; preds = %107, %97
  %100 = load i32, ptr %17, align 4
  %101 = icmp slt i32 %100, 16384
  br i1 %101, label %102, label %110

102:                                              ; preds = %99
  %103 = load ptr, ptr %16, align 8
  %104 = load i32, ptr %17, align 4
  %105 = sext i32 %104 to i64
  %106 = getelementptr inbounds float, ptr %103, i64 %105
  store float 1.000000e+00, ptr %106, align 4
  br label %107

107:                                              ; preds = %102
  %108 = load i32, ptr %17, align 4
  %109 = add nsw i32 %108, 1
  store i32 %109, ptr %17, align 4
  br label %99, !llvm.loop !22

110:                                              ; preds = %99
  %111 = load ptr, ptr %4, align 8
  %112 = load ptr, ptr %6, align 8
  %113 = load ptr, ptr %8, align 8
  call void @einsum_0(ptr noundef %111, ptr noundef %112, ptr noundef %113)
  %114 = load ptr, ptr %8, align 8
  %115 = load ptr, ptr %10, align 8
  %116 = load ptr, ptr %12, align 8
  call void @einsum_1(ptr noundef %114, ptr noundef %115, ptr noundef %116)
  %117 = load ptr, ptr %12, align 8
  %118 = load ptr, ptr %14, align 8
  %119 = load ptr, ptr %16, align 8
  call void @einsum_2(ptr noundef %117, ptr noundef %118, ptr noundef %119)
  %120 = call i32 @clock_gettime(i32 noundef 6, ptr noundef %3)
  %121 = getelementptr inbounds %struct.timespec, ptr %3, i32 0, i32 0
  %122 = load i64, ptr %121, align 8
  %123 = getelementptr inbounds %struct.timespec, ptr %2, i32 0, i32 0
  %124 = load i64, ptr %123, align 8
  %125 = sub nsw i64 %122, %124
  %126 = sitofp i64 %125 to double
  %127 = getelementptr inbounds %struct.timespec, ptr %3, i32 0, i32 1
  %128 = load i64, ptr %127, align 8
  %129 = getelementptr inbounds %struct.timespec, ptr %2, i32 0, i32 1
  %130 = load i64, ptr %129, align 8
  %131 = sub nsw i64 %128, %130
  %132 = sitofp i64 %131 to double
  %133 = call double @llvm.fmuladd.f64(double %132, double 1.000000e-09, double %126)
  store double %133, ptr %18, align 8
  %134 = load double, ptr %18, align 8
  %135 = call i32 (ptr, ...) @printf(ptr noundef @.str, double noundef %134)
  %136 = load ptr, ptr %16, align 8
  %137 = getelementptr inbounds float, ptr %136, i64 0
  %138 = load float, ptr %137, align 4
  %139 = fpext float %138 to double
  %140 = call i32 (ptr, ...) @printf(ptr noundef @.str.1, double noundef %139)
  ret i32 0
}

declare i32 @clock_gettime(i32 noundef, ptr noundef) #2

; Function Attrs: allocsize(0)
declare ptr @malloc(i64 noundef) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.fmuladd.f64(double, double, double) #1

declare i32 @printf(ptr noundef, ...) #2

attributes #0 = { noinline nounwind optnone ssp uwtable(sync) "frame-pointer"="non-leaf" "no-trapping-math"="true" "probe-stack"="__chkstk_darwin" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+altnzcv,+bti,+ccdp,+ccidx,+complxnum,+crc,+dit,+dotprod,+flagm,+fp-armv8,+fp16fml,+fptoint,+fullfp16,+jsconv,+lse,+neon,+pauth,+perfmon,+predres,+ras,+rcpc,+rdm,+sb,+sha2,+sha3,+specrestrict,+ssbs,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }
attributes #1 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #2 = { "frame-pointer"="non-leaf" "no-trapping-math"="true" "probe-stack"="__chkstk_darwin" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+altnzcv,+bti,+ccdp,+ccidx,+complxnum,+crc,+dit,+dotprod,+flagm,+fp-armv8,+fp16fml,+fptoint,+fullfp16,+jsconv,+lse,+neon,+pauth,+perfmon,+predres,+ras,+rcpc,+rdm,+sb,+sha2,+sha3,+specrestrict,+ssbs,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }
attributes #3 = { allocsize(0) "frame-pointer"="non-leaf" "no-trapping-math"="true" "probe-stack"="__chkstk_darwin" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+altnzcv,+bti,+ccdp,+ccidx,+complxnum,+crc,+dit,+dotprod,+flagm,+fp-armv8,+fp16fml,+fptoint,+fullfp16,+jsconv,+lse,+neon,+pauth,+perfmon,+predres,+ras,+rcpc,+rdm,+sb,+sha2,+sha3,+specrestrict,+ssbs,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }
attributes #4 = { allocsize(0) }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 2, !"SDK Version", [2 x i32] [i32 26, i32 0]}
!1 = !{i32 1, !"wchar_size", i32 4}
!2 = !{i32 8, !"PIC Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 1}
!4 = !{i32 7, !"frame-pointer", i32 1}
!5 = !{!"Apple clang version 17.0.0 (clang-1700.3.19.1)"}
!6 = distinct !{!6, !7}
!7 = !{!"llvm.loop.mustprogress"}
!8 = distinct !{!8, !7}
!9 = distinct !{!9, !7}
!10 = distinct !{!10, !7}
!11 = distinct !{!11, !7}
!12 = distinct !{!12, !7}
!13 = distinct !{!13, !7}
!14 = distinct !{!14, !7}
!15 = distinct !{!15, !7}
!16 = distinct !{!16, !7}
!17 = distinct !{!17, !7}
!18 = distinct !{!18, !7}
!19 = distinct !{!19, !7}
!20 = distinct !{!20, !7}
!21 = distinct !{!21, !7}
!22 = distinct !{!22, !7}
