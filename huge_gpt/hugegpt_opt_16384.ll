; ModuleID = 'huge_gpt/hugegpt_opt_16384.c'
source_filename = "huge_gpt/hugegpt_opt_16384.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128-Fn32"
target triple = "arm64-apple-macosx15.0.0"

%struct.timespec = type { i64, i64 }

@.str = private unnamed_addr constant [10 x i8] c"Time: %f\0A\00", align 1
@.memset_pattern.6 = private unnamed_addr constant [4 x float] [float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00], align 16

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_0(ptr noalias nocapture noundef %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef readonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %44
  %5 = phi i64 [ 0, %3 ], [ %45, %44 ]
  %6 = icmp ult i64 %5, 1012
  %7 = sub nsw i64 1024, %5
  %8 = and i64 %7, 4294967295
  %9 = select i1 %6, i64 13, i64 %8
  br label %10

10:                                               ; preds = %4, %40
  %11 = phi i64 [ 0, %4 ], [ %41, %40 ]
  br label %12

12:                                               ; preds = %37, %10
  %13 = phi i64 [ %38, %37 ], [ 0, %10 ]
  %14 = shl nsw i64 %13, 14
  %15 = getelementptr inbounds i8, ptr %2, i64 %14
  br label %16

16:                                               ; preds = %34, %12
  %17 = phi i64 [ %35, %34 ], [ 0, %12 ]
  %18 = add nuw nsw i64 %17, %11
  %19 = getelementptr inbounds float, ptr %15, i64 %18
  %20 = load float, ptr %19, align 4, !tbaa !6
  %21 = getelementptr inbounds float, ptr %0, i64 %18
  br label %22

22:                                               ; preds = %22, %16
  %23 = phi i64 [ %32, %22 ], [ 0, %16 ]
  %24 = add nuw nsw i64 %23, %5
  %25 = shl nsw i64 %24, 12
  %26 = or disjoint i64 %25, %13
  %27 = getelementptr inbounds float, ptr %1, i64 %26
  %28 = load float, ptr %27, align 4, !tbaa !6
  %29 = getelementptr inbounds float, ptr %21, i64 %25
  %30 = load float, ptr %29, align 4, !tbaa !6
  %31 = tail call float @llvm.fmuladd.f32(float %28, float %20, float %30)
  store float %31, ptr %29, align 4, !tbaa !6
  %32 = add nuw nsw i64 %23, 1
  %33 = icmp eq i64 %32, %9
  br i1 %33, label %34, label %22, !llvm.loop !10

34:                                               ; preds = %22
  %35 = add nuw nsw i64 %17, 1
  %36 = icmp eq i64 %35, 141
  br i1 %36, label %37, label %16, !llvm.loop !13

37:                                               ; preds = %34
  %38 = add nuw nsw i64 %13, 1
  %39 = icmp eq i64 %38, 4096
  br i1 %39, label %40, label %12, !llvm.loop !14

40:                                               ; preds = %37
  %41 = add nuw nsw i64 %11, 141
  %42 = icmp ult i64 %11, 3955
  br i1 %42, label %10, label %44, !llvm.loop !15

43:                                               ; preds = %44
  ret void

44:                                               ; preds = %40
  %45 = add nuw nsw i64 %5, 13
  %46 = icmp ult i64 %5, 1011
  br i1 %46, label %4, label %43, !llvm.loop !16
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

4:                                                ; preds = %3, %45
  %5 = phi i64 [ 0, %3 ], [ %46, %45 ]
  %6 = icmp ult i64 %5, 1012
  %7 = sub nsw i64 1024, %5
  %8 = and i64 %7, 4294967295
  %9 = select i1 %6, i64 13, i64 %8
  br label %10

10:                                               ; preds = %4, %41
  %11 = phi i64 [ 0, %4 ], [ %42, %41 ]
  br label %12

12:                                               ; preds = %38, %10
  %13 = phi i64 [ %39, %38 ], [ 0, %10 ]
  %14 = shl nsw i64 %13, 14
  %15 = getelementptr inbounds i8, ptr %2, i64 %14
  %16 = getelementptr inbounds float, ptr %0, i64 %13
  br label %17

17:                                               ; preds = %35, %12
  %18 = phi i64 [ %36, %35 ], [ 0, %12 ]
  %19 = add nuw nsw i64 %18, %11
  %20 = getelementptr inbounds float, ptr %15, i64 %19
  %21 = load float, ptr %20, align 4, !tbaa !6
  %22 = getelementptr inbounds float, ptr %1, i64 %19
  br label %23

23:                                               ; preds = %23, %17
  %24 = phi i64 [ %33, %23 ], [ 0, %17 ]
  %25 = add nuw nsw i64 %24, %5
  %26 = shl nsw i64 %25, 14
  %27 = getelementptr inbounds i8, ptr %22, i64 %26
  %28 = load float, ptr %27, align 4, !tbaa !6
  %29 = shl nsw i64 %25, 12
  %30 = getelementptr inbounds i8, ptr %16, i64 %29
  %31 = load float, ptr %30, align 4, !tbaa !6
  %32 = tail call float @llvm.fmuladd.f32(float %28, float %21, float %31)
  store float %32, ptr %30, align 4, !tbaa !6
  %33 = add nuw nsw i64 %24, 1
  %34 = icmp eq i64 %33, %9
  br i1 %34, label %35, label %23, !llvm.loop !17

35:                                               ; preds = %23
  %36 = add nuw nsw i64 %18, 1
  %37 = icmp eq i64 %36, 141
  br i1 %37, label %38, label %17, !llvm.loop !18

38:                                               ; preds = %35
  %39 = add nuw nsw i64 %13, 1
  %40 = icmp eq i64 %39, 1024
  br i1 %40, label %41, label %12, !llvm.loop !19

41:                                               ; preds = %38
  %42 = add nuw nsw i64 %11, 141
  %43 = icmp ult i64 %11, 3955
  br i1 %43, label %10, label %45, !llvm.loop !20

44:                                               ; preds = %45
  ret void

45:                                               ; preds = %41
  %46 = add nuw nsw i64 %5, 13
  %47 = icmp ult i64 %5, 1011
  br i1 %47, label %4, label %44, !llvm.loop !21
}

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_2(ptr noalias nocapture noundef readonly %0, ptr noalias nocapture noundef %1, ptr noalias nocapture noundef readonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %39
  %5 = phi i64 [ 0, %3 ], [ %40, %39 ]
  %6 = icmp ult i64 %5, 1012
  %7 = sub nsw i64 1024, %5
  %8 = and i64 %7, 4294967295
  %9 = select i1 %6, i64 13, i64 %8
  br label %10

10:                                               ; preds = %4, %35
  %11 = phi i64 [ 0, %4 ], [ %36, %35 ]
  %12 = getelementptr inbounds float, ptr %2, i64 %11
  %13 = getelementptr inbounds float, ptr %1, i64 %11
  br label %14

14:                                               ; preds = %32, %10
  %15 = phi i64 [ %33, %32 ], [ 0, %10 ]
  %16 = shl nsw i64 %15, 14
  %17 = getelementptr inbounds i8, ptr %12, i64 %16
  %18 = load float, ptr %17, align 4, !tbaa !6
  %19 = getelementptr inbounds float, ptr %0, i64 %15
  br label %20

20:                                               ; preds = %20, %14
  %21 = phi i64 [ %30, %20 ], [ 0, %14 ]
  %22 = add nuw nsw i64 %21, %5
  %23 = shl nsw i64 %22, 12
  %24 = getelementptr inbounds i8, ptr %19, i64 %23
  %25 = load float, ptr %24, align 4, !tbaa !6
  %26 = shl nsw i64 %22, 14
  %27 = getelementptr inbounds i8, ptr %13, i64 %26
  %28 = load float, ptr %27, align 4, !tbaa !6
  %29 = tail call float @llvm.fmuladd.f32(float %25, float %18, float %28)
  store float %29, ptr %27, align 4, !tbaa !6
  %30 = add nuw nsw i64 %21, 1
  %31 = icmp eq i64 %30, %9
  br i1 %31, label %32, label %20, !llvm.loop !22

32:                                               ; preds = %20
  %33 = add nuw nsw i64 %15, 1
  %34 = icmp eq i64 %33, 1024
  br i1 %34, label %35, label %14, !llvm.loop !23

35:                                               ; preds = %32
  %36 = add nuw nsw i64 %11, 1
  %37 = icmp eq i64 %36, 4096
  br i1 %37, label %39, label %10, !llvm.loop !24

38:                                               ; preds = %39
  ret void

39:                                               ; preds = %35
  %40 = add nuw nsw i64 %5, 13
  %41 = icmp ult i64 %5, 1011
  br i1 %41, label %4, label %38, !llvm.loop !25
}

; Function Attrs: nounwind ssp uwtable(sync)
define noundef i32 @main() local_unnamed_addr #3 {
  %1 = alloca %struct.timespec, align 8
  %2 = alloca %struct.timespec, align 8
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %1) #9
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %2) #9
  %3 = call i32 @clock_gettime(i32 noundef 6, ptr noundef nonnull %1) #9
  %4 = call dereferenceable_or_null(16777216) ptr @malloc(i64 noundef 16777216) #10
  call void @memset_pattern16(ptr %4, ptr nonnull @.memset_pattern.6, i64 16777216), !tbaa !6
  %5 = call dereferenceable_or_null(67108864) ptr @malloc(i64 noundef 67108864) #10
  call void @memset_pattern16(ptr %5, ptr nonnull @.memset_pattern.6, i64 67108864), !tbaa !6
  %6 = call dereferenceable_or_null(16777216) ptr @malloc(i64 noundef 16777216) #10
  call void @memset_pattern16(ptr %6, ptr nonnull @.memset_pattern.6, i64 16777216), !tbaa !6
  %7 = call dereferenceable_or_null(16777216) ptr @malloc(i64 noundef 16777216) #10
  call void @memset_pattern16(ptr %7, ptr nonnull @.memset_pattern.6, i64 16777216), !tbaa !6
  %8 = call dereferenceable_or_null(4194304) ptr @malloc(i64 noundef 4194304) #10
  call void @memset_pattern16(ptr %8, ptr nonnull @.memset_pattern.6, i64 4194304), !tbaa !6
  %9 = call dereferenceable_or_null(16777216) ptr @malloc(i64 noundef 16777216) #10
  call void @memset_pattern16(ptr %9, ptr nonnull @.memset_pattern.6, i64 16777216), !tbaa !6
  %10 = call dereferenceable_or_null(16777216) ptr @malloc(i64 noundef 16777216) #10
  call void @memset_pattern16(ptr %10, ptr nonnull @.memset_pattern.6, i64 16777216), !tbaa !6
  call void @llvm.experimental.noalias.scope.decl(metadata !26)
  call void @llvm.experimental.noalias.scope.decl(metadata !29)
  call void @llvm.experimental.noalias.scope.decl(metadata !31)
  br label %11

11:                                               ; preds = %49, %0
  %12 = phi i64 [ 0, %0 ], [ %50, %49 ]
  %13 = icmp ult i64 %12, 1012
  %14 = sub nuw nsw i64 1024, %12
  %15 = select i1 %13, i64 13, i64 %14
  br label %16

16:                                               ; preds = %46, %11
  %17 = phi i64 [ 0, %11 ], [ %47, %46 ]
  br label %18

18:                                               ; preds = %43, %16
  %19 = phi i64 [ %44, %43 ], [ 0, %16 ]
  %20 = shl nsw i64 %19, 14
  %21 = getelementptr inbounds i8, ptr %5, i64 %20
  br label %22

22:                                               ; preds = %40, %18
  %23 = phi i64 [ %41, %40 ], [ 0, %18 ]
  %24 = add nuw nsw i64 %23, %17
  %25 = getelementptr inbounds float, ptr %21, i64 %24
  %26 = load float, ptr %25, align 4, !tbaa !6, !alias.scope !31, !noalias !33
  %27 = getelementptr inbounds float, ptr %6, i64 %24
  br label %28

28:                                               ; preds = %28, %22
  %29 = phi i64 [ %38, %28 ], [ 0, %22 ]
  %30 = add nuw nsw i64 %29, %12
  %31 = shl nsw i64 %30, 12
  %32 = or disjoint i64 %31, %19
  %33 = getelementptr inbounds float, ptr %4, i64 %32
  %34 = load float, ptr %33, align 4, !tbaa !6, !alias.scope !29, !noalias !34
  %35 = getelementptr inbounds float, ptr %27, i64 %31
  %36 = load float, ptr %35, align 4, !tbaa !6, !alias.scope !26, !noalias !35
  %37 = call float @llvm.fmuladd.f32(float %34, float %26, float %36)
  store float %37, ptr %35, align 4, !tbaa !6, !alias.scope !26, !noalias !35
  %38 = add nuw nsw i64 %29, 1
  %39 = icmp eq i64 %38, %15
  br i1 %39, label %40, label %28, !llvm.loop !10

40:                                               ; preds = %28
  %41 = add nuw nsw i64 %23, 1
  %42 = icmp eq i64 %41, 141
  br i1 %42, label %43, label %22, !llvm.loop !13

43:                                               ; preds = %40
  %44 = add nuw nsw i64 %19, 1
  %45 = icmp eq i64 %44, 4096
  br i1 %45, label %46, label %18, !llvm.loop !14

46:                                               ; preds = %43
  %47 = add nuw nsw i64 %17, 141
  %48 = icmp ult i64 %17, 3955
  br i1 %48, label %16, label %49, !llvm.loop !15

49:                                               ; preds = %46
  %50 = add nuw nsw i64 %12, 13
  %51 = icmp ult i64 %12, 1011
  br i1 %51, label %11, label %52, !llvm.loop !16

52:                                               ; preds = %49
  call void @llvm.experimental.noalias.scope.decl(metadata !36)
  call void @llvm.experimental.noalias.scope.decl(metadata !39)
  call void @llvm.experimental.noalias.scope.decl(metadata !41)
  br label %53

53:                                               ; preds = %92, %52
  %54 = phi i64 [ 0, %52 ], [ %93, %92 ]
  %55 = icmp ult i64 %54, 1012
  %56 = sub nuw nsw i64 1024, %54
  %57 = select i1 %55, i64 13, i64 %56
  br label %58

58:                                               ; preds = %89, %53
  %59 = phi i64 [ 0, %53 ], [ %90, %89 ]
  br label %60

60:                                               ; preds = %86, %58
  %61 = phi i64 [ %87, %86 ], [ 0, %58 ]
  %62 = shl nsw i64 %61, 14
  %63 = getelementptr inbounds i8, ptr %7, i64 %62
  %64 = getelementptr inbounds float, ptr %8, i64 %61
  br label %65

65:                                               ; preds = %83, %60
  %66 = phi i64 [ %84, %83 ], [ 0, %60 ]
  %67 = add nuw nsw i64 %66, %59
  %68 = getelementptr inbounds float, ptr %63, i64 %67
  %69 = load float, ptr %68, align 4, !tbaa !6, !alias.scope !41, !noalias !43
  %70 = getelementptr inbounds float, ptr %6, i64 %67
  br label %71

71:                                               ; preds = %71, %65
  %72 = phi i64 [ %81, %71 ], [ 0, %65 ]
  %73 = add nuw nsw i64 %72, %54
  %74 = shl nsw i64 %73, 14
  %75 = getelementptr inbounds i8, ptr %70, i64 %74
  %76 = load float, ptr %75, align 4, !tbaa !6, !alias.scope !39, !noalias !44
  %77 = shl nsw i64 %73, 12
  %78 = getelementptr inbounds i8, ptr %64, i64 %77
  %79 = load float, ptr %78, align 4, !tbaa !6, !alias.scope !36, !noalias !45
  %80 = call float @llvm.fmuladd.f32(float %76, float %69, float %79)
  store float %80, ptr %78, align 4, !tbaa !6, !alias.scope !36, !noalias !45
  %81 = add nuw nsw i64 %72, 1
  %82 = icmp eq i64 %81, %57
  br i1 %82, label %83, label %71, !llvm.loop !17

83:                                               ; preds = %71
  %84 = add nuw nsw i64 %66, 1
  %85 = icmp eq i64 %84, 141
  br i1 %85, label %86, label %65, !llvm.loop !18

86:                                               ; preds = %83
  %87 = add nuw nsw i64 %61, 1
  %88 = icmp eq i64 %87, 1024
  br i1 %88, label %89, label %60, !llvm.loop !19

89:                                               ; preds = %86
  %90 = add nuw nsw i64 %59, 141
  %91 = icmp ult i64 %59, 3955
  br i1 %91, label %58, label %92, !llvm.loop !20

92:                                               ; preds = %89
  %93 = add nuw nsw i64 %54, 13
  %94 = icmp ult i64 %54, 1011
  br i1 %94, label %53, label %95, !llvm.loop !21

95:                                               ; preds = %92
  call void @llvm.experimental.noalias.scope.decl(metadata !46)
  call void @llvm.experimental.noalias.scope.decl(metadata !49)
  call void @llvm.experimental.noalias.scope.decl(metadata !51)
  br label %96

96:                                               ; preds = %129, %95
  %97 = phi i64 [ 0, %95 ], [ %130, %129 ]
  %98 = icmp ult i64 %97, 1012
  %99 = sub nuw nsw i64 1024, %97
  %100 = select i1 %98, i64 13, i64 %99
  br label %101

101:                                              ; preds = %126, %96
  %102 = phi i64 [ 0, %96 ], [ %127, %126 ]
  %103 = getelementptr inbounds float, ptr %9, i64 %102
  %104 = getelementptr inbounds float, ptr %10, i64 %102
  br label %105

105:                                              ; preds = %123, %101
  %106 = phi i64 [ %124, %123 ], [ 0, %101 ]
  %107 = shl nsw i64 %106, 14
  %108 = getelementptr inbounds i8, ptr %103, i64 %107
  %109 = load float, ptr %108, align 4, !tbaa !6, !alias.scope !51, !noalias !53
  %110 = getelementptr inbounds float, ptr %8, i64 %106
  br label %111

111:                                              ; preds = %111, %105
  %112 = phi i64 [ %121, %111 ], [ 0, %105 ]
  %113 = add nuw nsw i64 %112, %97
  %114 = shl nsw i64 %113, 12
  %115 = getelementptr inbounds i8, ptr %110, i64 %114
  %116 = load float, ptr %115, align 4, !tbaa !6, !alias.scope !46, !noalias !54
  %117 = shl nsw i64 %113, 14
  %118 = getelementptr inbounds i8, ptr %104, i64 %117
  %119 = load float, ptr %118, align 4, !tbaa !6, !alias.scope !49, !noalias !55
  %120 = call float @llvm.fmuladd.f32(float %116, float %109, float %119)
  store float %120, ptr %118, align 4, !tbaa !6, !alias.scope !49, !noalias !55
  %121 = add nuw nsw i64 %112, 1
  %122 = icmp eq i64 %121, %100
  br i1 %122, label %123, label %111, !llvm.loop !22

123:                                              ; preds = %111
  %124 = add nuw nsw i64 %106, 1
  %125 = icmp eq i64 %124, 1024
  br i1 %125, label %126, label %105, !llvm.loop !23

126:                                              ; preds = %123
  %127 = add nuw nsw i64 %102, 1
  %128 = icmp eq i64 %127, 4096
  br i1 %128, label %129, label %101, !llvm.loop !24

129:                                              ; preds = %126
  %130 = add nuw nsw i64 %97, 13
  %131 = icmp ult i64 %97, 1011
  br i1 %131, label %96, label %132, !llvm.loop !25

132:                                              ; preds = %129
  %133 = call i32 @clock_gettime(i32 noundef 6, ptr noundef nonnull %2) #9
  %134 = load i64, ptr %2, align 8, !tbaa !56
  %135 = load i64, ptr %1, align 8, !tbaa !56
  %136 = sub nsw i64 %134, %135
  %137 = sitofp i64 %136 to double
  %138 = getelementptr inbounds i8, ptr %2, i64 8
  %139 = load i64, ptr %138, align 8, !tbaa !59
  %140 = getelementptr inbounds i8, ptr %1, i64 8
  %141 = load i64, ptr %140, align 8, !tbaa !59
  %142 = sub nsw i64 %139, %141
  %143 = sitofp i64 %142 to double
  %144 = call double @llvm.fmuladd.f64(double %143, double 1.000000e-09, double %137)
  %145 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str, double noundef %144)
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
!6 = !{!7, !7, i64 0}
!7 = !{!"float", !8, i64 0}
!8 = !{!"omnipotent char", !9, i64 0}
!9 = !{!"Simple C/C++ TBAA"}
!10 = distinct !{!10, !11, !12}
!11 = !{!"llvm.loop.mustprogress"}
!12 = !{!"llvm.loop.unroll.disable"}
!13 = distinct !{!13, !11, !12}
!14 = distinct !{!14, !11, !12}
!15 = distinct !{!15, !11, !12}
!16 = distinct !{!16, !11, !12}
!17 = distinct !{!17, !11, !12}
!18 = distinct !{!18, !11, !12}
!19 = distinct !{!19, !11, !12}
!20 = distinct !{!20, !11, !12}
!21 = distinct !{!21, !11, !12}
!22 = distinct !{!22, !11, !12}
!23 = distinct !{!23, !11, !12}
!24 = distinct !{!24, !11, !12}
!25 = distinct !{!25, !11, !12}
!26 = !{!27}
!27 = distinct !{!27, !28, !"einsum_0: argument 0"}
!28 = distinct !{!28, !"einsum_0"}
!29 = !{!30}
!30 = distinct !{!30, !28, !"einsum_0: argument 1"}
!31 = !{!32}
!32 = distinct !{!32, !28, !"einsum_0: argument 2"}
!33 = !{!27, !30}
!34 = !{!27, !32}
!35 = !{!30, !32}
!36 = !{!37}
!37 = distinct !{!37, !38, !"einsum_1: argument 0"}
!38 = distinct !{!38, !"einsum_1"}
!39 = !{!40}
!40 = distinct !{!40, !38, !"einsum_1: argument 1"}
!41 = !{!42}
!42 = distinct !{!42, !38, !"einsum_1: argument 2"}
!43 = !{!37, !40}
!44 = !{!37, !42}
!45 = !{!40, !42}
!46 = !{!47}
!47 = distinct !{!47, !48, !"einsum_2: argument 0"}
!48 = distinct !{!48, !"einsum_2"}
!49 = !{!50}
!50 = distinct !{!50, !48, !"einsum_2: argument 1"}
!51 = !{!52}
!52 = distinct !{!52, !48, !"einsum_2: argument 2"}
!53 = !{!47, !50}
!54 = !{!50, !52}
!55 = !{!47, !52}
!56 = !{!57, !58, i64 0}
!57 = !{!"timespec", !58, i64 0, !58, i64 8}
!58 = !{!"long", !8, i64 0}
!59 = !{!57, !58, i64 8}
