; ModuleID = 'huge_gpt/hugegpt_opt_4096.c'
source_filename = "huge_gpt/hugegpt_opt_4096.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128-Fn32"
target triple = "arm64-apple-macosx15.0.0"

%struct.timespec = type { i64, i64 }

@.str = private unnamed_addr constant [10 x i8] c"Time: %f\0A\00", align 1
@.memset_pattern.6 = private unnamed_addr constant [4 x float] [float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00], align 16

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_0(ptr noalias nocapture noundef %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef readonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %12
  %5 = phi i64 [ 0, %3 ], [ %13, %12 ]
  %6 = shl nuw nsw i64 %5, 12
  %7 = shl i64 %5, 12
  %8 = or disjoint i64 %7, 4096
  br label %10

9:                                                ; preds = %12
  ret void

10:                                               ; preds = %4, %25
  %11 = phi i64 [ 0, %4 ], [ %26, %25 ]
  br label %15

12:                                               ; preds = %25
  %13 = add nuw nsw i64 %5, 2
  %14 = icmp ult i64 %5, 1022
  br i1 %14, label %4, label %9, !llvm.loop !6

15:                                               ; preds = %10, %43
  %16 = phi i64 [ 0, %10 ], [ %44, %43 ]
  %17 = shl nsw i64 %16, 14
  %18 = getelementptr inbounds i8, ptr %2, i64 %17
  %19 = or disjoint i64 %6, %16
  %20 = getelementptr inbounds float, ptr %1, i64 %19
  %21 = load float, ptr %20, align 4, !tbaa !9
  %22 = or disjoint i64 %8, %16
  %23 = getelementptr inbounds float, ptr %1, i64 %22
  %24 = load float, ptr %23, align 4, !tbaa !9
  br label %28

25:                                               ; preds = %43
  %26 = add nuw nsw i64 %11, 256
  %27 = icmp ult i64 %11, 3840
  br i1 %27, label %10, label %12, !llvm.loop !13

28:                                               ; preds = %15, %28
  %29 = phi i64 [ 0, %15 ], [ %41, %28 ]
  %30 = or disjoint i64 %29, %11
  %31 = getelementptr inbounds float, ptr %18, i64 %30
  %32 = load float, ptr %31, align 4, !tbaa !9
  %33 = or disjoint i64 %6, %30
  %34 = getelementptr inbounds float, ptr %0, i64 %33
  %35 = load float, ptr %34, align 4, !tbaa !9
  %36 = tail call float @llvm.fmuladd.f32(float %21, float %32, float %35)
  store float %36, ptr %34, align 4, !tbaa !9
  %37 = or disjoint i64 %8, %30
  %38 = getelementptr inbounds float, ptr %0, i64 %37
  %39 = load float, ptr %38, align 4, !tbaa !9
  %40 = tail call float @llvm.fmuladd.f32(float %24, float %32, float %39)
  store float %40, ptr %38, align 4, !tbaa !9
  %41 = add nuw nsw i64 %29, 1
  %42 = icmp eq i64 %41, 256
  br i1 %42, label %43, label %28, !llvm.loop !14

43:                                               ; preds = %28
  %44 = add nuw nsw i64 %16, 1
  %45 = icmp eq i64 %44, 4096
  br i1 %45, label %25, label %15, !llvm.loop !15
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #1

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fmuladd.f32(float, float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #1

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_1(ptr noalias nocapture noundef %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef readonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %14
  %5 = phi i64 [ 0, %3 ], [ %15, %14 ]
  %6 = shl nsw i64 %5, 14
  %7 = shl nsw i64 %5, 12
  %8 = or disjoint i64 %5, 1
  %9 = shl nsw i64 %8, 14
  %10 = shl nsw i64 %8, 12
  br label %12

11:                                               ; preds = %14
  ret void

12:                                               ; preds = %4, %26
  %13 = phi i64 [ 0, %4 ], [ %27, %26 ]
  br label %17

14:                                               ; preds = %26
  %15 = add nuw nsw i64 %5, 2
  %16 = icmp ult i64 %5, 1022
  br i1 %16, label %4, label %11, !llvm.loop !16

17:                                               ; preds = %12, %45
  %18 = phi i64 [ 0, %12 ], [ %46, %45 ]
  %19 = shl nsw i64 %18, 14
  %20 = getelementptr inbounds i8, ptr %2, i64 %19
  %21 = getelementptr inbounds float, ptr %0, i64 %18
  %22 = getelementptr inbounds i8, ptr %21, i64 %7
  %23 = getelementptr inbounds i8, ptr %21, i64 %10
  %24 = load float, ptr %22, align 4, !tbaa !9
  %25 = load float, ptr %23, align 4, !tbaa !9
  br label %29

26:                                               ; preds = %45
  %27 = add nuw nsw i64 %13, 256
  %28 = icmp ult i64 %13, 3840
  br i1 %28, label %12, label %14, !llvm.loop !17

29:                                               ; preds = %17, %29
  %30 = phi float [ %25, %17 ], [ %42, %29 ]
  %31 = phi float [ %24, %17 ], [ %39, %29 ]
  %32 = phi i64 [ 0, %17 ], [ %43, %29 ]
  %33 = or disjoint i64 %32, %13
  %34 = getelementptr inbounds float, ptr %20, i64 %33
  %35 = load float, ptr %34, align 4, !tbaa !9
  %36 = getelementptr inbounds float, ptr %1, i64 %33
  %37 = getelementptr inbounds i8, ptr %36, i64 %6
  %38 = load float, ptr %37, align 4, !tbaa !9
  %39 = tail call float @llvm.fmuladd.f32(float %38, float %35, float %31)
  %40 = getelementptr inbounds i8, ptr %36, i64 %9
  %41 = load float, ptr %40, align 4, !tbaa !9
  %42 = tail call float @llvm.fmuladd.f32(float %41, float %35, float %30)
  %43 = add nuw nsw i64 %32, 1
  %44 = icmp eq i64 %43, 256
  br i1 %44, label %45, label %29, !llvm.loop !18

45:                                               ; preds = %29
  store float %39, ptr %22, align 4, !tbaa !9
  store float %42, ptr %23, align 4, !tbaa !9
  %46 = add nuw nsw i64 %18, 1
  %47 = icmp eq i64 %46, 1024
  br i1 %47, label %26, label %17, !llvm.loop !19
}

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_2(ptr noalias nocapture noundef readonly %0, ptr noalias nocapture noundef %1, ptr noalias nocapture noundef readonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %20
  %5 = phi i64 [ 0, %3 ], [ %21, %20 ]
  %6 = shl nsw i64 %5, 12
  %7 = shl nsw i64 %5, 14
  %8 = or disjoint i64 %5, 1
  %9 = shl nsw i64 %8, 12
  %10 = shl nsw i64 %8, 14
  br label %12

11:                                               ; preds = %20
  ret void

12:                                               ; preds = %4, %39
  %13 = phi i64 [ 0, %4 ], [ %40, %39 ]
  %14 = getelementptr inbounds float, ptr %2, i64 %13
  %15 = getelementptr inbounds float, ptr %1, i64 %13
  %16 = getelementptr inbounds i8, ptr %15, i64 %7
  %17 = getelementptr inbounds i8, ptr %15, i64 %10
  %18 = load float, ptr %16, align 4, !tbaa !9
  %19 = load float, ptr %17, align 4, !tbaa !9
  br label %23

20:                                               ; preds = %39
  %21 = add nuw nsw i64 %5, 2
  %22 = icmp ult i64 %5, 1022
  br i1 %22, label %4, label %11, !llvm.loop !20

23:                                               ; preds = %12, %23
  %24 = phi float [ %19, %12 ], [ %36, %23 ]
  %25 = phi float [ %18, %12 ], [ %33, %23 ]
  %26 = phi i64 [ 0, %12 ], [ %37, %23 ]
  %27 = shl nsw i64 %26, 14
  %28 = getelementptr inbounds i8, ptr %14, i64 %27
  %29 = load float, ptr %28, align 4, !tbaa !9
  %30 = getelementptr inbounds float, ptr %0, i64 %26
  %31 = getelementptr inbounds i8, ptr %30, i64 %6
  %32 = load float, ptr %31, align 4, !tbaa !9
  %33 = tail call float @llvm.fmuladd.f32(float %32, float %29, float %25)
  %34 = getelementptr inbounds i8, ptr %30, i64 %9
  %35 = load float, ptr %34, align 4, !tbaa !9
  %36 = tail call float @llvm.fmuladd.f32(float %35, float %29, float %24)
  %37 = add nuw nsw i64 %26, 1
  %38 = icmp eq i64 %37, 1024
  br i1 %38, label %39, label %23, !llvm.loop !21

39:                                               ; preds = %23
  store float %33, ptr %16, align 4, !tbaa !9
  store float %36, ptr %17, align 4, !tbaa !9
  %40 = add nuw nsw i64 %13, 1
  %41 = icmp eq i64 %40, 4096
  br i1 %41, label %20, label %12, !llvm.loop !22
}

; Function Attrs: nounwind ssp uwtable(sync)
define noundef i32 @main() local_unnamed_addr #3 {
  %1 = alloca %struct.timespec, align 8
  %2 = alloca %struct.timespec, align 8
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %1) #9
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %2) #9
  %3 = call i32 @clock_gettime(i32 noundef 6, ptr noundef nonnull %1) #9
  %4 = call dereferenceable_or_null(16777216) ptr @malloc(i64 noundef 16777216) #10
  call void @memset_pattern16(ptr %4, ptr nonnull @.memset_pattern.6, i64 16777216), !tbaa !9
  %5 = call dereferenceable_or_null(67108864) ptr @malloc(i64 noundef 67108864) #10
  call void @memset_pattern16(ptr %5, ptr nonnull @.memset_pattern.6, i64 67108864), !tbaa !9
  %6 = call dereferenceable_or_null(16777216) ptr @malloc(i64 noundef 16777216) #10
  call void @memset_pattern16(ptr %6, ptr nonnull @.memset_pattern.6, i64 16777216), !tbaa !9
  %7 = call dereferenceable_or_null(16777216) ptr @malloc(i64 noundef 16777216) #10
  call void @memset_pattern16(ptr %7, ptr nonnull @.memset_pattern.6, i64 16777216), !tbaa !9
  %8 = call dereferenceable_or_null(4194304) ptr @malloc(i64 noundef 4194304) #10
  call void @memset_pattern16(ptr %8, ptr nonnull @.memset_pattern.6, i64 4194304), !tbaa !9
  %9 = call dereferenceable_or_null(16777216) ptr @malloc(i64 noundef 16777216) #10
  call void @memset_pattern16(ptr %9, ptr nonnull @.memset_pattern.6, i64 16777216), !tbaa !9
  %10 = call dereferenceable_or_null(16777216) ptr @malloc(i64 noundef 16777216) #10
  call void @memset_pattern16(ptr %10, ptr nonnull @.memset_pattern.6, i64 16777216), !tbaa !9
  call void @llvm.experimental.noalias.scope.decl(metadata !23)
  call void @llvm.experimental.noalias.scope.decl(metadata !26)
  call void @llvm.experimental.noalias.scope.decl(metadata !28)
  br label %11

11:                                               ; preds = %17, %0
  %12 = phi i64 [ 0, %0 ], [ %18, %17 ]
  %13 = shl nuw nsw i64 %12, 12
  %14 = or disjoint i64 %13, 4096
  br label %15

15:                                               ; preds = %30, %11
  %16 = phi i64 [ 0, %11 ], [ %31, %30 ]
  br label %20

17:                                               ; preds = %30
  %18 = add nuw nsw i64 %12, 2
  %19 = icmp ult i64 %12, 1022
  br i1 %19, label %11, label %51, !llvm.loop !6

20:                                               ; preds = %48, %15
  %21 = phi i64 [ 0, %15 ], [ %49, %48 ]
  %22 = shl nsw i64 %21, 14
  %23 = getelementptr inbounds i8, ptr %5, i64 %22
  %24 = or disjoint i64 %21, %13
  %25 = getelementptr inbounds float, ptr %4, i64 %24
  %26 = load float, ptr %25, align 4, !tbaa !9, !alias.scope !26, !noalias !30
  %27 = or disjoint i64 %21, %14
  %28 = getelementptr inbounds float, ptr %4, i64 %27
  %29 = load float, ptr %28, align 4, !tbaa !9, !alias.scope !26, !noalias !30
  br label %33

30:                                               ; preds = %48
  %31 = add nuw nsw i64 %16, 256
  %32 = icmp ult i64 %16, 3840
  br i1 %32, label %15, label %17, !llvm.loop !13

33:                                               ; preds = %33, %20
  %34 = phi i64 [ 0, %20 ], [ %46, %33 ]
  %35 = or disjoint i64 %34, %16
  %36 = getelementptr inbounds float, ptr %23, i64 %35
  %37 = load float, ptr %36, align 4, !tbaa !9, !alias.scope !28, !noalias !31
  %38 = or disjoint i64 %35, %13
  %39 = getelementptr inbounds float, ptr %6, i64 %38
  %40 = load float, ptr %39, align 4, !tbaa !9, !alias.scope !23, !noalias !32
  %41 = call float @llvm.fmuladd.f32(float %26, float %37, float %40)
  store float %41, ptr %39, align 4, !tbaa !9, !alias.scope !23, !noalias !32
  %42 = or disjoint i64 %35, %14
  %43 = getelementptr inbounds float, ptr %6, i64 %42
  %44 = load float, ptr %43, align 4, !tbaa !9, !alias.scope !23, !noalias !32
  %45 = call float @llvm.fmuladd.f32(float %29, float %37, float %44)
  store float %45, ptr %43, align 4, !tbaa !9, !alias.scope !23, !noalias !32
  %46 = add nuw nsw i64 %34, 1
  %47 = icmp eq i64 %46, 256
  br i1 %47, label %48, label %33, !llvm.loop !14

48:                                               ; preds = %33
  %49 = add nuw nsw i64 %21, 1
  %50 = icmp eq i64 %49, 4096
  br i1 %50, label %30, label %20, !llvm.loop !15

51:                                               ; preds = %17
  call void @llvm.experimental.noalias.scope.decl(metadata !33)
  call void @llvm.experimental.noalias.scope.decl(metadata !36)
  call void @llvm.experimental.noalias.scope.decl(metadata !38)
  br label %52

52:                                               ; preds = %61, %51
  %53 = phi i64 [ 0, %51 ], [ %62, %61 ]
  %54 = shl nuw nsw i64 %53, 14
  %55 = shl nuw nsw i64 %53, 12
  %56 = or disjoint i64 %53, 1
  %57 = shl nuw nsw i64 %56, 14
  %58 = shl nuw nsw i64 %56, 12
  br label %59

59:                                               ; preds = %73, %52
  %60 = phi i64 [ 0, %52 ], [ %74, %73 ]
  br label %64

61:                                               ; preds = %73
  %62 = add nuw nsw i64 %53, 2
  %63 = icmp ult i64 %53, 1022
  br i1 %63, label %52, label %95, !llvm.loop !16

64:                                               ; preds = %92, %59
  %65 = phi i64 [ 0, %59 ], [ %93, %92 ]
  %66 = shl nsw i64 %65, 14
  %67 = getelementptr inbounds i8, ptr %7, i64 %66
  %68 = getelementptr inbounds float, ptr %8, i64 %65
  %69 = getelementptr inbounds i8, ptr %68, i64 %55
  %70 = getelementptr inbounds i8, ptr %68, i64 %58
  %71 = load float, ptr %69, align 4, !tbaa !9, !alias.scope !33, !noalias !40
  %72 = load float, ptr %70, align 4, !tbaa !9, !alias.scope !33, !noalias !40
  br label %76

73:                                               ; preds = %92
  %74 = add nuw nsw i64 %60, 256
  %75 = icmp ult i64 %60, 3840
  br i1 %75, label %59, label %61, !llvm.loop !17

76:                                               ; preds = %76, %64
  %77 = phi float [ %72, %64 ], [ %89, %76 ]
  %78 = phi float [ %71, %64 ], [ %86, %76 ]
  %79 = phi i64 [ 0, %64 ], [ %90, %76 ]
  %80 = or disjoint i64 %79, %60
  %81 = getelementptr inbounds float, ptr %67, i64 %80
  %82 = load float, ptr %81, align 4, !tbaa !9, !alias.scope !38, !noalias !41
  %83 = getelementptr inbounds float, ptr %6, i64 %80
  %84 = getelementptr inbounds i8, ptr %83, i64 %54
  %85 = load float, ptr %84, align 4, !tbaa !9, !alias.scope !36, !noalias !42
  %86 = call float @llvm.fmuladd.f32(float %85, float %82, float %78)
  %87 = getelementptr inbounds i8, ptr %83, i64 %57
  %88 = load float, ptr %87, align 4, !tbaa !9, !alias.scope !36, !noalias !42
  %89 = call float @llvm.fmuladd.f32(float %88, float %82, float %77)
  %90 = add nuw nsw i64 %79, 1
  %91 = icmp eq i64 %90, 256
  br i1 %91, label %92, label %76, !llvm.loop !18

92:                                               ; preds = %76
  store float %86, ptr %69, align 4, !tbaa !9, !alias.scope !33, !noalias !40
  store float %89, ptr %70, align 4, !tbaa !9, !alias.scope !33, !noalias !40
  %93 = add nuw nsw i64 %65, 1
  %94 = icmp eq i64 %93, 1024
  br i1 %94, label %73, label %64, !llvm.loop !19

95:                                               ; preds = %61
  call void @llvm.experimental.noalias.scope.decl(metadata !43)
  call void @llvm.experimental.noalias.scope.decl(metadata !46)
  call void @llvm.experimental.noalias.scope.decl(metadata !48)
  br label %96

96:                                               ; preds = %111, %95
  %97 = phi i64 [ 0, %95 ], [ %112, %111 ]
  %98 = shl nuw nsw i64 %97, 12
  %99 = shl nuw nsw i64 %97, 14
  %100 = or disjoint i64 %97, 1
  %101 = shl nuw nsw i64 %100, 12
  %102 = shl nuw nsw i64 %100, 14
  br label %103

103:                                              ; preds = %130, %96
  %104 = phi i64 [ 0, %96 ], [ %131, %130 ]
  %105 = getelementptr inbounds float, ptr %9, i64 %104
  %106 = getelementptr inbounds float, ptr %10, i64 %104
  %107 = getelementptr inbounds i8, ptr %106, i64 %99
  %108 = getelementptr inbounds i8, ptr %106, i64 %102
  %109 = load float, ptr %107, align 4, !tbaa !9, !alias.scope !46, !noalias !50
  %110 = load float, ptr %108, align 4, !tbaa !9, !alias.scope !46, !noalias !50
  br label %114

111:                                              ; preds = %130
  %112 = add nuw nsw i64 %97, 2
  %113 = icmp ult i64 %97, 1022
  br i1 %113, label %96, label %133, !llvm.loop !20

114:                                              ; preds = %114, %103
  %115 = phi float [ %110, %103 ], [ %127, %114 ]
  %116 = phi float [ %109, %103 ], [ %124, %114 ]
  %117 = phi i64 [ 0, %103 ], [ %128, %114 ]
  %118 = shl nsw i64 %117, 14
  %119 = getelementptr inbounds i8, ptr %105, i64 %118
  %120 = load float, ptr %119, align 4, !tbaa !9, !alias.scope !48, !noalias !51
  %121 = getelementptr inbounds float, ptr %8, i64 %117
  %122 = getelementptr inbounds i8, ptr %121, i64 %98
  %123 = load float, ptr %122, align 4, !tbaa !9, !alias.scope !43, !noalias !52
  %124 = call float @llvm.fmuladd.f32(float %123, float %120, float %116)
  %125 = getelementptr inbounds i8, ptr %121, i64 %101
  %126 = load float, ptr %125, align 4, !tbaa !9, !alias.scope !43, !noalias !52
  %127 = call float @llvm.fmuladd.f32(float %126, float %120, float %115)
  %128 = add nuw nsw i64 %117, 1
  %129 = icmp eq i64 %128, 1024
  br i1 %129, label %130, label %114, !llvm.loop !21

130:                                              ; preds = %114
  store float %124, ptr %107, align 4, !tbaa !9, !alias.scope !46, !noalias !50
  store float %127, ptr %108, align 4, !tbaa !9, !alias.scope !46, !noalias !50
  %131 = add nuw nsw i64 %104, 1
  %132 = icmp eq i64 %131, 4096
  br i1 %132, label %111, label %103, !llvm.loop !22

133:                                              ; preds = %111
  %134 = call i32 @clock_gettime(i32 noundef 6, ptr noundef nonnull %2) #9
  %135 = load i64, ptr %2, align 8, !tbaa !53
  %136 = load i64, ptr %1, align 8, !tbaa !53
  %137 = sub nsw i64 %135, %136
  %138 = sitofp i64 %137 to double
  %139 = getelementptr inbounds i8, ptr %2, i64 8
  %140 = load i64, ptr %139, align 8, !tbaa !56
  %141 = getelementptr inbounds i8, ptr %1, i64 8
  %142 = load i64, ptr %141, align 8, !tbaa !56
  %143 = sub nsw i64 %140, %142
  %144 = sitofp i64 %143 to double
  %145 = call double @llvm.fmuladd.f64(double %144, double 1.000000e-09, double %138)
  %146 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str, double noundef %145)
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %2) #9
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %1) #9
  ret i32 0
}

declare i32 @clock_gettime(i32 noundef, ptr noundef) local_unnamed_addr #4

; Function Attrs: mustprogress nofree nounwind willreturn allockind("alloc,uninitialized") allocsize(0) memory(inaccessiblemem: readwrite)
declare noalias noundef ptr @malloc(i64 noundef) local_unnamed_addr #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.fmuladd.f64(double, double, double) #2

; Function Attrs: nofree nounwind
declare noundef i32 @printf(ptr nocapture noundef readonly, ...) local_unnamed_addr #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: readwrite)
declare void @llvm.experimental.noalias.scope.decl(metadata) #7

; Function Attrs: nofree nounwind willreturn memory(argmem: readwrite)
declare void @memset_pattern16(ptr nocapture writeonly, ptr nocapture readonly, i64) local_unnamed_addr #8

attributes #0 = { nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync) "frame-pointer"="non-leaf" "no-trapping-math"="true" "probe-stack"="__chkstk_darwin" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+altnzcv,+bti,+ccdp,+ccidx,+complxnum,+crc,+dit,+dotprod,+flagm,+fp-armv8,+fp16fml,+fptoint,+fullfp16,+jsconv,+lse,+neon,+pauth,+perfmon,+predres,+ras,+rcpc,+rdm,+sb,+sha2,+sha3,+specrestrict,+ssbs,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }
attributes #1 = { mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { nounwind ssp uwtable(sync) "frame-pointer"="non-leaf" "no-trapping-math"="true" "probe-stack"="__chkstk_darwin" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+altnzcv,+bti,+ccdp,+ccidx,+complxnum,+crc,+dit,+dotprod,+flagm,+fp-armv8,+fp16fml,+fptoint,+fullfp16,+jsconv,+lse,+neon,+pauth,+perfmon,+predres,+ras,+rcpc,+rdm,+sb,+sha2,+sha3,+specrestrict,+ssbs,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }
attributes #4 = { "frame-pointer"="non-leaf" "no-trapping-math"="true" "probe-stack"="__chkstk_darwin" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+altnzcv,+bti,+ccdp,+ccidx,+complxnum,+crc,+dit,+dotprod,+flagm,+fp-armv8,+fp16fml,+fptoint,+fullfp16,+jsconv,+lse,+neon,+pauth,+perfmon,+predres,+ras,+rcpc,+rdm,+sb,+sha2,+sha3,+specrestrict,+ssbs,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }
attributes #5 = { mustprogress nofree nounwind willreturn allockind("alloc,uninitialized") allocsize(0) memory(inaccessiblemem: readwrite) "alloc-family"="malloc" "frame-pointer"="non-leaf" "no-trapping-math"="true" "probe-stack"="__chkstk_darwin" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+altnzcv,+bti,+ccdp,+ccidx,+complxnum,+crc,+dit,+dotprod,+flagm,+fp-armv8,+fp16fml,+fptoint,+fullfp16,+jsconv,+lse,+neon,+pauth,+perfmon,+predres,+ras,+rcpc,+rdm,+sb,+sha2,+sha3,+specrestrict,+ssbs,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }
attributes #6 = { nofree nounwind "frame-pointer"="non-leaf" "no-trapping-math"="true" "probe-stack"="__chkstk_darwin" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+altnzcv,+bti,+ccdp,+ccidx,+complxnum,+crc,+dit,+dotprod,+flagm,+fp-armv8,+fp16fml,+fptoint,+fullfp16,+jsconv,+lse,+neon,+pauth,+perfmon,+predres,+ras,+rcpc,+rdm,+sb,+sha2,+sha3,+specrestrict,+ssbs,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: readwrite) }
attributes #8 = { nofree nounwind willreturn memory(argmem: readwrite) }
attributes #9 = { nounwind }
attributes #10 = { allocsize(0) }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 2, !"SDK Version", [2 x i32] [i32 26, i32 0]}
!1 = !{i32 1, !"wchar_size", i32 4}
!2 = !{i32 8, !"PIC Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 1}
!4 = !{i32 7, !"frame-pointer", i32 1}
!5 = !{!"Apple clang version 17.0.0 (clang-1700.3.19.1)"}
!6 = distinct !{!6, !7, !8}
!7 = !{!"llvm.loop.mustprogress"}
!8 = !{!"llvm.loop.unroll.disable"}
!9 = !{!10, !10, i64 0}
!10 = !{!"float", !11, i64 0}
!11 = !{!"omnipotent char", !12, i64 0}
!12 = !{!"Simple C/C++ TBAA"}
!13 = distinct !{!13, !7, !8}
!14 = distinct !{!14, !7, !8}
!15 = distinct !{!15, !7, !8}
!16 = distinct !{!16, !7, !8}
!17 = distinct !{!17, !7, !8}
!18 = distinct !{!18, !7, !8}
!19 = distinct !{!19, !7, !8}
!20 = distinct !{!20, !7, !8}
!21 = distinct !{!21, !7, !8}
!22 = distinct !{!22, !7, !8}
!23 = !{!24}
!24 = distinct !{!24, !25, !"einsum_0: argument 0"}
!25 = distinct !{!25, !"einsum_0"}
!26 = !{!27}
!27 = distinct !{!27, !25, !"einsum_0: argument 1"}
!28 = !{!29}
!29 = distinct !{!29, !25, !"einsum_0: argument 2"}
!30 = !{!24, !29}
!31 = !{!24, !27}
!32 = !{!27, !29}
!33 = !{!34}
!34 = distinct !{!34, !35, !"einsum_1: argument 0"}
!35 = distinct !{!35, !"einsum_1"}
!36 = !{!37}
!37 = distinct !{!37, !35, !"einsum_1: argument 1"}
!38 = !{!39}
!39 = distinct !{!39, !35, !"einsum_1: argument 2"}
!40 = !{!37, !39}
!41 = !{!34, !37}
!42 = !{!34, !39}
!43 = !{!44}
!44 = distinct !{!44, !45, !"einsum_2: argument 0"}
!45 = distinct !{!45, !"einsum_2"}
!46 = !{!47}
!47 = distinct !{!47, !45, !"einsum_2: argument 1"}
!48 = !{!49}
!49 = distinct !{!49, !45, !"einsum_2: argument 2"}
!50 = !{!44, !49}
!51 = !{!44, !47}
!52 = !{!47, !49}
!53 = !{!54, !55, i64 0}
!54 = !{!"timespec", !55, i64 0, !55, i64 8}
!55 = !{!"long", !11, i64 0}
!56 = !{!54, !55, i64 8}
