; ModuleID = 'small_gpt/smallgpt_opt_4096.c'
source_filename = "small_gpt/smallgpt_opt_4096.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128-Fn32"
target triple = "arm64-apple-macosx15.0.0"

%struct.timespec = type { i64, i64 }

@.str = private unnamed_addr constant [10 x i8] c"Time: %f\0A\00", align 1

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define void @einsum_0(ptr noalias noundef %0, ptr noalias noundef %1, ptr noalias noundef %2) #0 {
  %4 = alloca ptr, align 8
  %5 = alloca ptr, align 8
  %6 = alloca ptr, align 8
  %7 = alloca i32, align 4
  %8 = alloca i32, align 4
  %9 = alloca i32, align 4
  %10 = alloca i32, align 4
  %11 = alloca i32, align 4
  %12 = alloca i32, align 4
  %13 = alloca i32, align 4
  %14 = alloca i32, align 4
  %15 = alloca i32, align 4
  store ptr %0, ptr %4, align 8
  store ptr %1, ptr %5, align 8
  store ptr %2, ptr %6, align 8
  store i32 0, ptr %7, align 4
  br label %16

16:                                               ; preds = %124, %3
  %17 = load i32, ptr %7, align 4
  %18 = icmp slt i32 %17, 64
  br i1 %18, label %19, label %127

19:                                               ; preds = %16
  store i32 0, ptr %8, align 4
  br label %20

20:                                               ; preds = %120, %19
  %21 = load i32, ptr %8, align 4
  %22 = icmp slt i32 %21, 256
  br i1 %22, label %23, label %123

23:                                               ; preds = %20
  store i32 0, ptr %9, align 4
  br label %24

24:                                               ; preds = %116, %23
  %25 = load i32, ptr %9, align 4
  %26 = icmp slt i32 %25, 256
  br i1 %26, label %27, label %119

27:                                               ; preds = %24
  store i32 0, ptr %10, align 4
  br label %28

28:                                               ; preds = %112, %27
  %29 = load i32, ptr %10, align 4
  %30 = load i32, ptr %7, align 4
  %31 = add nsw i32 %30, 32
  %32 = icmp sle i32 %31, 64
  br i1 %32, label %33, label %34

33:                                               ; preds = %28
  br label %37

34:                                               ; preds = %28
  %35 = load i32, ptr %7, align 4
  %36 = sub nsw i32 64, %35
  br label %37

37:                                               ; preds = %34, %33
  %38 = phi i32 [ 32, %33 ], [ %36, %34 ]
  %39 = icmp slt i32 %29, %38
  br i1 %39, label %40, label %115

40:                                               ; preds = %37
  %41 = load i32, ptr %7, align 4
  %42 = load i32, ptr %10, align 4
  %43 = add nsw i32 %41, %42
  store i32 %43, ptr %11, align 4
  store i32 0, ptr %12, align 4
  br label %44

44:                                               ; preds = %108, %40
  %45 = load i32, ptr %12, align 4
  %46 = load i32, ptr %8, align 4
  %47 = add nsw i32 %46, 51
  %48 = icmp sle i32 %47, 256
  br i1 %48, label %49, label %50

49:                                               ; preds = %44
  br label %53

50:                                               ; preds = %44
  %51 = load i32, ptr %8, align 4
  %52 = sub nsw i32 256, %51
  br label %53

53:                                               ; preds = %50, %49
  %54 = phi i32 [ 51, %49 ], [ %52, %50 ]
  %55 = icmp slt i32 %45, %54
  br i1 %55, label %56, label %111

56:                                               ; preds = %53
  %57 = load i32, ptr %8, align 4
  %58 = load i32, ptr %12, align 4
  %59 = add nsw i32 %57, %58
  store i32 %59, ptr %13, align 4
  store i32 0, ptr %14, align 4
  br label %60

60:                                               ; preds = %104, %56
  %61 = load i32, ptr %14, align 4
  %62 = load i32, ptr %9, align 4
  %63 = add nsw i32 %62, 1
  %64 = icmp sle i32 %63, 256
  br i1 %64, label %65, label %66

65:                                               ; preds = %60
  br label %69

66:                                               ; preds = %60
  %67 = load i32, ptr %9, align 4
  %68 = sub nsw i32 256, %67
  br label %69

69:                                               ; preds = %66, %65
  %70 = phi i32 [ 1, %65 ], [ %68, %66 ]
  %71 = icmp slt i32 %61, %70
  br i1 %71, label %72, label %107

72:                                               ; preds = %69
  %73 = load i32, ptr %9, align 4
  %74 = load i32, ptr %14, align 4
  %75 = add nsw i32 %73, %74
  store i32 %75, ptr %15, align 4
  %76 = load ptr, ptr %5, align 8
  %77 = load i32, ptr %11, align 4
  %78 = mul nsw i32 %77, 256
  %79 = load i32, ptr %15, align 4
  %80 = mul nsw i32 %79, 1
  %81 = add nsw i32 %78, %80
  %82 = sext i32 %81 to i64
  %83 = getelementptr inbounds float, ptr %76, i64 %82
  %84 = load float, ptr %83, align 4
  %85 = load ptr, ptr %6, align 8
  %86 = load i32, ptr %15, align 4
  %87 = mul nsw i32 %86, 256
  %88 = load i32, ptr %13, align 4
  %89 = mul nsw i32 %88, 1
  %90 = add nsw i32 %87, %89
  %91 = sext i32 %90 to i64
  %92 = getelementptr inbounds float, ptr %85, i64 %91
  %93 = load float, ptr %92, align 4
  %94 = load ptr, ptr %4, align 8
  %95 = load i32, ptr %11, align 4
  %96 = mul nsw i32 %95, 256
  %97 = load i32, ptr %13, align 4
  %98 = mul nsw i32 %97, 1
  %99 = add nsw i32 %96, %98
  %100 = sext i32 %99 to i64
  %101 = getelementptr inbounds float, ptr %94, i64 %100
  %102 = load float, ptr %101, align 4
  %103 = call float @llvm.fmuladd.f32(float %84, float %93, float %102)
  store float %103, ptr %101, align 4
  br label %104

104:                                              ; preds = %72
  %105 = load i32, ptr %14, align 4
  %106 = add nsw i32 %105, 1
  store i32 %106, ptr %14, align 4
  br label %60, !llvm.loop !6

107:                                              ; preds = %69
  br label %108

108:                                              ; preds = %107
  %109 = load i32, ptr %12, align 4
  %110 = add nsw i32 %109, 1
  store i32 %110, ptr %12, align 4
  br label %44, !llvm.loop !8

111:                                              ; preds = %53
  br label %112

112:                                              ; preds = %111
  %113 = load i32, ptr %10, align 4
  %114 = add nsw i32 %113, 1
  store i32 %114, ptr %10, align 4
  br label %28, !llvm.loop !9

115:                                              ; preds = %37
  br label %116

116:                                              ; preds = %115
  %117 = load i32, ptr %9, align 4
  %118 = add nsw i32 %117, 1
  store i32 %118, ptr %9, align 4
  br label %24, !llvm.loop !10

119:                                              ; preds = %24
  br label %120

120:                                              ; preds = %119
  %121 = load i32, ptr %8, align 4
  %122 = add nsw i32 %121, 51
  store i32 %122, ptr %8, align 4
  br label %20, !llvm.loop !11

123:                                              ; preds = %20
  br label %124

124:                                              ; preds = %123
  %125 = load i32, ptr %7, align 4
  %126 = add nsw i32 %125, 32
  store i32 %126, ptr %7, align 4
  br label %16, !llvm.loop !12

127:                                              ; preds = %16
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
  %9 = alloca i32, align 4
  %10 = alloca i32, align 4
  %11 = alloca i32, align 4
  %12 = alloca i32, align 4
  %13 = alloca i32, align 4
  %14 = alloca i32, align 4
  %15 = alloca i32, align 4
  %16 = alloca i32, align 4
  store ptr %0, ptr %4, align 8
  store ptr %1, ptr %5, align 8
  store ptr %2, ptr %6, align 8
  store i32 0, ptr %7, align 4
  br label %17

17:                                               ; preds = %135, %3
  %18 = load i32, ptr %7, align 4
  %19 = icmp slt i32 %18, 64
  br i1 %19, label %20, label %138

20:                                               ; preds = %17
  store i32 0, ptr %8, align 4
  br label %21

21:                                               ; preds = %131, %20
  %22 = load i32, ptr %8, align 4
  %23 = icmp slt i32 %22, 256
  br i1 %23, label %24, label %134

24:                                               ; preds = %21
  store i32 0, ptr %9, align 4
  br label %25

25:                                               ; preds = %127, %24
  %26 = load i32, ptr %9, align 4
  %27 = icmp slt i32 %26, 64
  br i1 %27, label %28, label %130

28:                                               ; preds = %25
  store i32 0, ptr %10, align 4
  br label %29

29:                                               ; preds = %123, %28
  %30 = load i32, ptr %10, align 4
  %31 = icmp slt i32 %30, 51
  br i1 %31, label %32, label %126

32:                                               ; preds = %29
  store i32 0, ptr %11, align 4
  br label %33

33:                                               ; preds = %119, %32
  %34 = load i32, ptr %11, align 4
  %35 = load i32, ptr %7, align 4
  %36 = add nsw i32 %35, 32
  %37 = icmp sle i32 %36, 64
  br i1 %37, label %38, label %39

38:                                               ; preds = %33
  br label %42

39:                                               ; preds = %33
  %40 = load i32, ptr %7, align 4
  %41 = sub nsw i32 64, %40
  br label %42

42:                                               ; preds = %39, %38
  %43 = phi i32 [ 32, %38 ], [ %41, %39 ]
  %44 = icmp slt i32 %34, %43
  br i1 %44, label %45, label %122

45:                                               ; preds = %42
  %46 = load i32, ptr %7, align 4
  %47 = load i32, ptr %11, align 4
  %48 = add nsw i32 %46, %47
  store i32 %48, ptr %12, align 4
  store i32 0, ptr %13, align 4
  br label %49

49:                                               ; preds = %115, %45
  %50 = load i32, ptr %13, align 4
  %51 = load i32, ptr %10, align 4
  %52 = add nsw i32 %51, 1
  %53 = icmp sle i32 %52, 256
  br i1 %53, label %54, label %55

54:                                               ; preds = %49
  br label %58

55:                                               ; preds = %49
  %56 = load i32, ptr %10, align 4
  %57 = sub nsw i32 256, %56
  br label %58

58:                                               ; preds = %55, %54
  %59 = phi i32 [ 1, %54 ], [ %57, %55 ]
  %60 = icmp slt i32 %50, %59
  br i1 %60, label %61, label %118

61:                                               ; preds = %58
  %62 = load i32, ptr %10, align 4
  %63 = load i32, ptr %8, align 4
  %64 = add nsw i32 %62, %63
  %65 = load i32, ptr %13, align 4
  %66 = add nsw i32 %64, %65
  store i32 %66, ptr %14, align 4
  store i32 0, ptr %15, align 4
  br label %67

67:                                               ; preds = %111, %61
  %68 = load i32, ptr %15, align 4
  %69 = load i32, ptr %9, align 4
  %70 = add nsw i32 %69, 1
  %71 = icmp sle i32 %70, 64
  br i1 %71, label %72, label %73

72:                                               ; preds = %67
  br label %76

73:                                               ; preds = %67
  %74 = load i32, ptr %9, align 4
  %75 = sub nsw i32 64, %74
  br label %76

76:                                               ; preds = %73, %72
  %77 = phi i32 [ 1, %72 ], [ %75, %73 ]
  %78 = icmp slt i32 %68, %77
  br i1 %78, label %79, label %114

79:                                               ; preds = %76
  %80 = load i32, ptr %9, align 4
  %81 = load i32, ptr %15, align 4
  %82 = add nsw i32 %80, %81
  store i32 %82, ptr %16, align 4
  %83 = load ptr, ptr %5, align 8
  %84 = load i32, ptr %12, align 4
  %85 = mul nsw i32 %84, 256
  %86 = load i32, ptr %14, align 4
  %87 = mul nsw i32 %86, 1
  %88 = add nsw i32 %85, %87
  %89 = sext i32 %88 to i64
  %90 = getelementptr inbounds float, ptr %83, i64 %89
  %91 = load float, ptr %90, align 4
  %92 = load ptr, ptr %6, align 8
  %93 = load i32, ptr %16, align 4
  %94 = mul nsw i32 %93, 256
  %95 = load i32, ptr %14, align 4
  %96 = mul nsw i32 %95, 1
  %97 = add nsw i32 %94, %96
  %98 = sext i32 %97 to i64
  %99 = getelementptr inbounds float, ptr %92, i64 %98
  %100 = load float, ptr %99, align 4
  %101 = load ptr, ptr %4, align 8
  %102 = load i32, ptr %12, align 4
  %103 = mul nsw i32 %102, 64
  %104 = load i32, ptr %16, align 4
  %105 = mul nsw i32 %104, 1
  %106 = add nsw i32 %103, %105
  %107 = sext i32 %106 to i64
  %108 = getelementptr inbounds float, ptr %101, i64 %107
  %109 = load float, ptr %108, align 4
  %110 = call float @llvm.fmuladd.f32(float %91, float %100, float %109)
  store float %110, ptr %108, align 4
  br label %111

111:                                              ; preds = %79
  %112 = load i32, ptr %15, align 4
  %113 = add nsw i32 %112, 1
  store i32 %113, ptr %15, align 4
  br label %67, !llvm.loop !13

114:                                              ; preds = %76
  br label %115

115:                                              ; preds = %114
  %116 = load i32, ptr %13, align 4
  %117 = add nsw i32 %116, 1
  store i32 %117, ptr %13, align 4
  br label %49, !llvm.loop !14

118:                                              ; preds = %58
  br label %119

119:                                              ; preds = %118
  %120 = load i32, ptr %11, align 4
  %121 = add nsw i32 %120, 1
  store i32 %121, ptr %11, align 4
  br label %33, !llvm.loop !15

122:                                              ; preds = %42
  br label %123

123:                                              ; preds = %122
  %124 = load i32, ptr %10, align 4
  %125 = add nsw i32 %124, 1
  store i32 %125, ptr %10, align 4
  br label %29, !llvm.loop !16

126:                                              ; preds = %29
  br label %127

127:                                              ; preds = %126
  %128 = load i32, ptr %9, align 4
  %129 = add nsw i32 %128, 1
  store i32 %129, ptr %9, align 4
  br label %25, !llvm.loop !17

130:                                              ; preds = %25
  br label %131

131:                                              ; preds = %130
  %132 = load i32, ptr %8, align 4
  %133 = add nsw i32 %132, 51
  store i32 %133, ptr %8, align 4
  br label %21, !llvm.loop !18

134:                                              ; preds = %21
  br label %135

135:                                              ; preds = %134
  %136 = load i32, ptr %7, align 4
  %137 = add nsw i32 %136, 32
  store i32 %137, ptr %7, align 4
  br label %17, !llvm.loop !19

138:                                              ; preds = %17
  ret void
}

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define void @einsum_2(ptr noalias noundef %0, ptr noalias noundef %1, ptr noalias noundef %2) #0 {
  %4 = alloca ptr, align 8
  %5 = alloca ptr, align 8
  %6 = alloca ptr, align 8
  %7 = alloca i32, align 4
  %8 = alloca i32, align 4
  %9 = alloca i32, align 4
  %10 = alloca i32, align 4
  %11 = alloca i32, align 4
  %12 = alloca i32, align 4
  %13 = alloca i32, align 4
  %14 = alloca i32, align 4
  %15 = alloca i32, align 4
  store ptr %0, ptr %4, align 8
  store ptr %1, ptr %5, align 8
  store ptr %2, ptr %6, align 8
  store i32 0, ptr %7, align 4
  br label %16

16:                                               ; preds = %124, %3
  %17 = load i32, ptr %7, align 4
  %18 = icmp slt i32 %17, 64
  br i1 %18, label %19, label %127

19:                                               ; preds = %16
  store i32 0, ptr %8, align 4
  br label %20

20:                                               ; preds = %120, %19
  %21 = load i32, ptr %8, align 4
  %22 = icmp slt i32 %21, 256
  br i1 %22, label %23, label %123

23:                                               ; preds = %20
  store i32 0, ptr %9, align 4
  br label %24

24:                                               ; preds = %116, %23
  %25 = load i32, ptr %9, align 4
  %26 = icmp slt i32 %25, 64
  br i1 %26, label %27, label %119

27:                                               ; preds = %24
  store i32 0, ptr %10, align 4
  br label %28

28:                                               ; preds = %112, %27
  %29 = load i32, ptr %10, align 4
  %30 = load i32, ptr %7, align 4
  %31 = add nsw i32 %30, 32
  %32 = icmp sle i32 %31, 64
  br i1 %32, label %33, label %34

33:                                               ; preds = %28
  br label %37

34:                                               ; preds = %28
  %35 = load i32, ptr %7, align 4
  %36 = sub nsw i32 64, %35
  br label %37

37:                                               ; preds = %34, %33
  %38 = phi i32 [ 32, %33 ], [ %36, %34 ]
  %39 = icmp slt i32 %29, %38
  br i1 %39, label %40, label %115

40:                                               ; preds = %37
  %41 = load i32, ptr %7, align 4
  %42 = load i32, ptr %10, align 4
  %43 = add nsw i32 %41, %42
  store i32 %43, ptr %11, align 4
  store i32 0, ptr %12, align 4
  br label %44

44:                                               ; preds = %108, %40
  %45 = load i32, ptr %12, align 4
  %46 = load i32, ptr %8, align 4
  %47 = add nsw i32 %46, 1
  %48 = icmp sle i32 %47, 256
  br i1 %48, label %49, label %50

49:                                               ; preds = %44
  br label %53

50:                                               ; preds = %44
  %51 = load i32, ptr %8, align 4
  %52 = sub nsw i32 256, %51
  br label %53

53:                                               ; preds = %50, %49
  %54 = phi i32 [ 1, %49 ], [ %52, %50 ]
  %55 = icmp slt i32 %45, %54
  br i1 %55, label %56, label %111

56:                                               ; preds = %53
  %57 = load i32, ptr %8, align 4
  %58 = load i32, ptr %12, align 4
  %59 = add nsw i32 %57, %58
  store i32 %59, ptr %13, align 4
  store i32 0, ptr %14, align 4
  br label %60

60:                                               ; preds = %104, %56
  %61 = load i32, ptr %14, align 4
  %62 = load i32, ptr %9, align 4
  %63 = add nsw i32 %62, 1
  %64 = icmp sle i32 %63, 64
  br i1 %64, label %65, label %66

65:                                               ; preds = %60
  br label %69

66:                                               ; preds = %60
  %67 = load i32, ptr %9, align 4
  %68 = sub nsw i32 64, %67
  br label %69

69:                                               ; preds = %66, %65
  %70 = phi i32 [ 1, %65 ], [ %68, %66 ]
  %71 = icmp slt i32 %61, %70
  br i1 %71, label %72, label %107

72:                                               ; preds = %69
  %73 = load i32, ptr %9, align 4
  %74 = load i32, ptr %14, align 4
  %75 = add nsw i32 %73, %74
  store i32 %75, ptr %15, align 4
  %76 = load ptr, ptr %4, align 8
  %77 = load i32, ptr %11, align 4
  %78 = mul nsw i32 %77, 64
  %79 = load i32, ptr %15, align 4
  %80 = mul nsw i32 %79, 1
  %81 = add nsw i32 %78, %80
  %82 = sext i32 %81 to i64
  %83 = getelementptr inbounds float, ptr %76, i64 %82
  %84 = load float, ptr %83, align 4
  %85 = load ptr, ptr %6, align 8
  %86 = load i32, ptr %15, align 4
  %87 = mul nsw i32 %86, 256
  %88 = load i32, ptr %13, align 4
  %89 = mul nsw i32 %88, 1
  %90 = add nsw i32 %87, %89
  %91 = sext i32 %90 to i64
  %92 = getelementptr inbounds float, ptr %85, i64 %91
  %93 = load float, ptr %92, align 4
  %94 = load ptr, ptr %5, align 8
  %95 = load i32, ptr %11, align 4
  %96 = mul nsw i32 %95, 256
  %97 = load i32, ptr %13, align 4
  %98 = mul nsw i32 %97, 1
  %99 = add nsw i32 %96, %98
  %100 = sext i32 %99 to i64
  %101 = getelementptr inbounds float, ptr %94, i64 %100
  %102 = load float, ptr %101, align 4
  %103 = call float @llvm.fmuladd.f32(float %84, float %93, float %102)
  store float %103, ptr %101, align 4
  br label %104

104:                                              ; preds = %72
  %105 = load i32, ptr %14, align 4
  %106 = add nsw i32 %105, 1
  store i32 %106, ptr %14, align 4
  br label %60, !llvm.loop !20

107:                                              ; preds = %69
  br label %108

108:                                              ; preds = %107
  %109 = load i32, ptr %12, align 4
  %110 = add nsw i32 %109, 1
  store i32 %110, ptr %12, align 4
  br label %44, !llvm.loop !21

111:                                              ; preds = %53
  br label %112

112:                                              ; preds = %111
  %113 = load i32, ptr %10, align 4
  %114 = add nsw i32 %113, 1
  store i32 %114, ptr %10, align 4
  br label %28, !llvm.loop !22

115:                                              ; preds = %37
  br label %116

116:                                              ; preds = %115
  %117 = load i32, ptr %9, align 4
  %118 = add nsw i32 %117, 1
  store i32 %118, ptr %9, align 4
  br label %24, !llvm.loop !23

119:                                              ; preds = %24
  br label %120

120:                                              ; preds = %119
  %121 = load i32, ptr %8, align 4
  %122 = add nsw i32 %121, 1
  store i32 %122, ptr %8, align 4
  br label %20, !llvm.loop !24

123:                                              ; preds = %20
  br label %124

124:                                              ; preds = %123
  %125 = load i32, ptr %7, align 4
  %126 = add nsw i32 %125, 32
  store i32 %126, ptr %7, align 4
  br label %16, !llvm.loop !25

127:                                              ; preds = %16
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
  br label %21, !llvm.loop !26

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
  br label %34, !llvm.loop !27

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
  br label %47, !llvm.loop !28

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
  br label %60, !llvm.loop !29

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
  br label %73, !llvm.loop !30

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
  br label %86, !llvm.loop !31

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
  br label %99, !llvm.loop !32

110:                                              ; preds = %99
  %111 = load ptr, ptr %8, align 8
  %112 = load ptr, ptr %4, align 8
  %113 = load ptr, ptr %6, align 8
  call void @einsum_0(ptr noundef %111, ptr noundef %112, ptr noundef %113)
  %114 = load ptr, ptr %12, align 8
  %115 = load ptr, ptr %8, align 8
  %116 = load ptr, ptr %10, align 8
  call void @einsum_1(ptr noundef %114, ptr noundef %115, ptr noundef %116)
  %117 = load ptr, ptr %12, align 8
  %118 = load ptr, ptr %16, align 8
  %119 = load ptr, ptr %14, align 8
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
!23 = distinct !{!23, !7}
!24 = distinct !{!24, !7}
!25 = distinct !{!25, !7}
!26 = distinct !{!26, !7}
!27 = distinct !{!27, !7}
!28 = distinct !{!28, !7}
!29 = distinct !{!29, !7}
!30 = distinct !{!30, !7}
!31 = distinct !{!31, !7}
!32 = distinct !{!32, !7}
