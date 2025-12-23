; ModuleID = 'med_gpt/medgpt_opt_4096.c'
source_filename = "med_gpt/medgpt_opt_4096.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128-Fn32"
target triple = "arm64-apple-macosx15.0.0"

%struct.timespec = type { i64, i64 }

@.str = private unnamed_addr constant [10 x i8] c"Time: %f\0A\00", align 1
@.memset_pattern.6 = private unnamed_addr constant [4 x float] [float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00], align 16

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_0(ptr noalias nocapture noundef %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef readonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %48
  %5 = phi i64 [ 0, %3 ], [ %49, %48 ]
  %6 = icmp ult i64 %5, 108
  %7 = sub nsw i64 128, %5
  %8 = and i64 %7, 4294967295
  %9 = select i1 %6, i64 21, i64 %8
  br label %10

10:                                               ; preds = %4, %44
  %11 = phi i64 [ 0, %4 ], [ %45, %44 ]
  %12 = icmp ult i64 %11, 462
  %13 = sub nsw i64 512, %11
  %14 = and i64 %13, 4294967295
  %15 = select i1 %12, i64 51, i64 %14
  br label %16

16:                                               ; preds = %41, %10
  %17 = phi i64 [ %42, %41 ], [ 0, %10 ]
  %18 = shl nsw i64 %17, 11
  %19 = getelementptr inbounds i8, ptr %2, i64 %18
  br label %20

20:                                               ; preds = %38, %16
  %21 = phi i64 [ %39, %38 ], [ 0, %16 ]
  %22 = add nuw nsw i64 %21, %5
  %23 = shl nsw i64 %22, 9
  %24 = or disjoint i64 %23, %17
  %25 = getelementptr inbounds float, ptr %1, i64 %24
  %26 = load float, ptr %25, align 4, !tbaa !6
  %27 = getelementptr inbounds float, ptr %0, i64 %23
  br label %28

28:                                               ; preds = %28, %20
  %29 = phi i64 [ %36, %28 ], [ 0, %20 ]
  %30 = add nuw nsw i64 %29, %11
  %31 = getelementptr inbounds float, ptr %19, i64 %30
  %32 = load float, ptr %31, align 4, !tbaa !6
  %33 = getelementptr inbounds float, ptr %27, i64 %30
  %34 = load float, ptr %33, align 4, !tbaa !6
  %35 = tail call float @llvm.fmuladd.f32(float %26, float %32, float %34)
  store float %35, ptr %33, align 4, !tbaa !6
  %36 = add nuw nsw i64 %29, 1
  %37 = icmp eq i64 %36, %15
  br i1 %37, label %38, label %28, !llvm.loop !10

38:                                               ; preds = %28
  %39 = add nuw nsw i64 %21, 1
  %40 = icmp eq i64 %39, %9
  br i1 %40, label %41, label %20, !llvm.loop !13

41:                                               ; preds = %38
  %42 = add nuw nsw i64 %17, 1
  %43 = icmp eq i64 %42, 512
  br i1 %43, label %44, label %16, !llvm.loop !14

44:                                               ; preds = %41
  %45 = add nuw nsw i64 %11, 51
  %46 = icmp ult i64 %11, 461
  br i1 %46, label %10, label %48, !llvm.loop !15

47:                                               ; preds = %48
  ret void

48:                                               ; preds = %44
  %49 = add nuw nsw i64 %5, 21
  %50 = icmp ult i64 %5, 107
  br i1 %50, label %4, label %47, !llvm.loop !16
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
  %6 = icmp ult i64 %5, 108
  %7 = sub nsw i64 128, %5
  %8 = and i64 %7, 4294967295
  %9 = select i1 %6, i64 21, i64 %8
  br label %10

10:                                               ; preds = %4, %41
  %11 = phi i64 [ 0, %4 ], [ %42, %41 ]
  br label %12

12:                                               ; preds = %38, %10
  %13 = phi i64 [ %39, %38 ], [ 0, %10 ]
  %14 = shl nsw i64 %13, 11
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
  %26 = shl nsw i64 %25, 11
  %27 = getelementptr inbounds i8, ptr %22, i64 %26
  %28 = load float, ptr %27, align 4, !tbaa !6
  %29 = shl nsw i64 %25, 9
  %30 = getelementptr inbounds i8, ptr %16, i64 %29
  %31 = load float, ptr %30, align 4, !tbaa !6
  %32 = tail call float @llvm.fmuladd.f32(float %28, float %21, float %31)
  store float %32, ptr %30, align 4, !tbaa !6
  %33 = add nuw nsw i64 %24, 1
  %34 = icmp eq i64 %33, %9
  br i1 %34, label %35, label %23, !llvm.loop !17

35:                                               ; preds = %23
  %36 = add nuw nsw i64 %18, 1
  %37 = icmp eq i64 %36, 51
  br i1 %37, label %38, label %17, !llvm.loop !18

38:                                               ; preds = %35
  %39 = add nuw nsw i64 %13, 1
  %40 = icmp eq i64 %39, 128
  br i1 %40, label %41, label %12, !llvm.loop !19

41:                                               ; preds = %38
  %42 = add nuw nsw i64 %11, 51
  %43 = icmp ult i64 %11, 461
  br i1 %43, label %10, label %45, !llvm.loop !20

44:                                               ; preds = %45
  ret void

45:                                               ; preds = %41
  %46 = add nuw nsw i64 %5, 21
  %47 = icmp ult i64 %5, 107
  br i1 %47, label %4, label %44, !llvm.loop !21
}

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_2(ptr noalias nocapture noundef readonly %0, ptr noalias nocapture noundef %1, ptr noalias nocapture noundef readonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %39
  %5 = phi i64 [ 0, %3 ], [ %40, %39 ]
  %6 = icmp ult i64 %5, 108
  %7 = sub nsw i64 128, %5
  %8 = and i64 %7, 4294967295
  %9 = select i1 %6, i64 21, i64 %8
  br label %10

10:                                               ; preds = %4, %35
  %11 = phi i64 [ 0, %4 ], [ %36, %35 ]
  %12 = getelementptr inbounds float, ptr %2, i64 %11
  %13 = getelementptr inbounds float, ptr %1, i64 %11
  br label %14

14:                                               ; preds = %32, %10
  %15 = phi i64 [ %33, %32 ], [ 0, %10 ]
  %16 = shl nsw i64 %15, 11
  %17 = getelementptr inbounds i8, ptr %12, i64 %16
  %18 = load float, ptr %17, align 4, !tbaa !6
  %19 = getelementptr inbounds float, ptr %0, i64 %15
  br label %20

20:                                               ; preds = %20, %14
  %21 = phi i64 [ %30, %20 ], [ 0, %14 ]
  %22 = add nuw nsw i64 %21, %5
  %23 = shl nsw i64 %22, 9
  %24 = getelementptr inbounds i8, ptr %19, i64 %23
  %25 = load float, ptr %24, align 4, !tbaa !6
  %26 = shl nsw i64 %22, 11
  %27 = getelementptr inbounds i8, ptr %13, i64 %26
  %28 = load float, ptr %27, align 4, !tbaa !6
  %29 = tail call float @llvm.fmuladd.f32(float %25, float %18, float %28)
  store float %29, ptr %27, align 4, !tbaa !6
  %30 = add nuw nsw i64 %21, 1
  %31 = icmp eq i64 %30, %9
  br i1 %31, label %32, label %20, !llvm.loop !22

32:                                               ; preds = %20
  %33 = add nuw nsw i64 %15, 1
  %34 = icmp eq i64 %33, 128
  br i1 %34, label %35, label %14, !llvm.loop !23

35:                                               ; preds = %32
  %36 = add nuw nsw i64 %11, 1
  %37 = icmp eq i64 %36, 512
  br i1 %37, label %39, label %10, !llvm.loop !24

38:                                               ; preds = %39
  ret void

39:                                               ; preds = %35
  %40 = add nuw nsw i64 %5, 21
  %41 = icmp ult i64 %5, 107
  br i1 %41, label %4, label %38, !llvm.loop !25
}

; Function Attrs: nounwind ssp uwtable(sync)
define noundef i32 @main() local_unnamed_addr #3 {
  %1 = alloca %struct.timespec, align 8
  %2 = alloca %struct.timespec, align 8
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %1) #9
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %2) #9
  %3 = call i32 @clock_gettime(i32 noundef 6, ptr noundef nonnull %1) #9
  %4 = call dereferenceable_or_null(262144) ptr @malloc(i64 noundef 262144) #10
  call void @memset_pattern16(ptr %4, ptr nonnull @.memset_pattern.6, i64 262144), !tbaa !6
  %5 = call dereferenceable_or_null(1048576) ptr @malloc(i64 noundef 1048576) #10
  call void @memset_pattern16(ptr %5, ptr nonnull @.memset_pattern.6, i64 1048576), !tbaa !6
  %6 = call dereferenceable_or_null(262144) ptr @malloc(i64 noundef 262144) #10
  call void @memset_pattern16(ptr %6, ptr nonnull @.memset_pattern.6, i64 262144), !tbaa !6
  %7 = call dereferenceable_or_null(262144) ptr @malloc(i64 noundef 262144) #10
  call void @memset_pattern16(ptr %7, ptr nonnull @.memset_pattern.6, i64 262144), !tbaa !6
  %8 = call dereferenceable_or_null(65536) ptr @malloc(i64 noundef 65536) #10
  call void @memset_pattern16(ptr %8, ptr nonnull @.memset_pattern.6, i64 65536), !tbaa !6
  %9 = call dereferenceable_or_null(262144) ptr @malloc(i64 noundef 262144) #10
  call void @memset_pattern16(ptr %9, ptr nonnull @.memset_pattern.6, i64 262144), !tbaa !6
  %10 = call dereferenceable_or_null(262144) ptr @malloc(i64 noundef 262144) #10
  call void @memset_pattern16(ptr %10, ptr nonnull @.memset_pattern.6, i64 262144), !tbaa !6
  call void @llvm.experimental.noalias.scope.decl(metadata !26)
  call void @llvm.experimental.noalias.scope.decl(metadata !29)
  call void @llvm.experimental.noalias.scope.decl(metadata !31)
  br label %11

11:                                               ; preds = %52, %0
  %12 = phi i64 [ 0, %0 ], [ %53, %52 ]
  %13 = icmp ult i64 %12, 108
  %14 = sub nuw nsw i64 128, %12
  %15 = select i1 %13, i64 21, i64 %14
  br label %16

16:                                               ; preds = %49, %11
  %17 = phi i64 [ 0, %11 ], [ %50, %49 ]
  %18 = icmp ult i64 %17, 462
  %19 = sub nuw nsw i64 512, %17
  %20 = select i1 %18, i64 51, i64 %19
  br label %21

21:                                               ; preds = %46, %16
  %22 = phi i64 [ %47, %46 ], [ 0, %16 ]
  %23 = shl nsw i64 %22, 11
  %24 = getelementptr inbounds i8, ptr %5, i64 %23
  br label %25

25:                                               ; preds = %43, %21
  %26 = phi i64 [ %44, %43 ], [ 0, %21 ]
  %27 = add nuw nsw i64 %26, %12
  %28 = shl nsw i64 %27, 9
  %29 = or disjoint i64 %28, %22
  %30 = getelementptr inbounds float, ptr %4, i64 %29
  %31 = load float, ptr %30, align 4, !tbaa !6, !alias.scope !29, !noalias !33
  %32 = getelementptr inbounds float, ptr %6, i64 %28
  br label %33

33:                                               ; preds = %33, %25
  %34 = phi i64 [ %41, %33 ], [ 0, %25 ]
  %35 = add nuw nsw i64 %34, %17
  %36 = getelementptr inbounds float, ptr %24, i64 %35
  %37 = load float, ptr %36, align 4, !tbaa !6, !alias.scope !31, !noalias !34
  %38 = getelementptr inbounds float, ptr %32, i64 %35
  %39 = load float, ptr %38, align 4, !tbaa !6, !alias.scope !26, !noalias !35
  %40 = call float @llvm.fmuladd.f32(float %31, float %37, float %39)
  store float %40, ptr %38, align 4, !tbaa !6, !alias.scope !26, !noalias !35
  %41 = add nuw nsw i64 %34, 1
  %42 = icmp eq i64 %41, %20
  br i1 %42, label %43, label %33, !llvm.loop !10

43:                                               ; preds = %33
  %44 = add nuw nsw i64 %26, 1
  %45 = icmp eq i64 %44, %15
  br i1 %45, label %46, label %25, !llvm.loop !13

46:                                               ; preds = %43
  %47 = add nuw nsw i64 %22, 1
  %48 = icmp eq i64 %47, 512
  br i1 %48, label %49, label %21, !llvm.loop !14

49:                                               ; preds = %46
  %50 = add nuw nsw i64 %17, 51
  %51 = icmp ult i64 %17, 461
  br i1 %51, label %16, label %52, !llvm.loop !15

52:                                               ; preds = %49
  %53 = add nuw nsw i64 %12, 21
  %54 = icmp ult i64 %12, 107
  br i1 %54, label %11, label %55, !llvm.loop !16

55:                                               ; preds = %52
  call void @llvm.experimental.noalias.scope.decl(metadata !36)
  call void @llvm.experimental.noalias.scope.decl(metadata !39)
  call void @llvm.experimental.noalias.scope.decl(metadata !41)
  br label %56

56:                                               ; preds = %95, %55
  %57 = phi i64 [ 0, %55 ], [ %96, %95 ]
  %58 = icmp ult i64 %57, 108
  %59 = sub nuw nsw i64 128, %57
  %60 = select i1 %58, i64 21, i64 %59
  br label %61

61:                                               ; preds = %92, %56
  %62 = phi i64 [ 0, %56 ], [ %93, %92 ]
  br label %63

63:                                               ; preds = %89, %61
  %64 = phi i64 [ %90, %89 ], [ 0, %61 ]
  %65 = shl nsw i64 %64, 11
  %66 = getelementptr inbounds i8, ptr %7, i64 %65
  %67 = getelementptr inbounds float, ptr %8, i64 %64
  br label %68

68:                                               ; preds = %86, %63
  %69 = phi i64 [ %87, %86 ], [ 0, %63 ]
  %70 = add nuw nsw i64 %69, %62
  %71 = getelementptr inbounds float, ptr %66, i64 %70
  %72 = load float, ptr %71, align 4, !tbaa !6, !alias.scope !41, !noalias !43
  %73 = getelementptr inbounds float, ptr %6, i64 %70
  br label %74

74:                                               ; preds = %74, %68
  %75 = phi i64 [ %84, %74 ], [ 0, %68 ]
  %76 = add nuw nsw i64 %75, %57
  %77 = shl nsw i64 %76, 11
  %78 = getelementptr inbounds i8, ptr %73, i64 %77
  %79 = load float, ptr %78, align 4, !tbaa !6, !alias.scope !39, !noalias !44
  %80 = shl nsw i64 %76, 9
  %81 = getelementptr inbounds i8, ptr %67, i64 %80
  %82 = load float, ptr %81, align 4, !tbaa !6, !alias.scope !36, !noalias !45
  %83 = call float @llvm.fmuladd.f32(float %79, float %72, float %82)
  store float %83, ptr %81, align 4, !tbaa !6, !alias.scope !36, !noalias !45
  %84 = add nuw nsw i64 %75, 1
  %85 = icmp eq i64 %84, %60
  br i1 %85, label %86, label %74, !llvm.loop !17

86:                                               ; preds = %74
  %87 = add nuw nsw i64 %69, 1
  %88 = icmp eq i64 %87, 51
  br i1 %88, label %89, label %68, !llvm.loop !18

89:                                               ; preds = %86
  %90 = add nuw nsw i64 %64, 1
  %91 = icmp eq i64 %90, 128
  br i1 %91, label %92, label %63, !llvm.loop !19

92:                                               ; preds = %89
  %93 = add nuw nsw i64 %62, 51
  %94 = icmp ult i64 %62, 461
  br i1 %94, label %61, label %95, !llvm.loop !20

95:                                               ; preds = %92
  %96 = add nuw nsw i64 %57, 21
  %97 = icmp ult i64 %57, 107
  br i1 %97, label %56, label %98, !llvm.loop !21

98:                                               ; preds = %95
  call void @llvm.experimental.noalias.scope.decl(metadata !46)
  call void @llvm.experimental.noalias.scope.decl(metadata !49)
  call void @llvm.experimental.noalias.scope.decl(metadata !51)
  br label %99

99:                                               ; preds = %132, %98
  %100 = phi i64 [ 0, %98 ], [ %133, %132 ]
  %101 = icmp ult i64 %100, 108
  %102 = sub nuw nsw i64 128, %100
  %103 = select i1 %101, i64 21, i64 %102
  br label %104

104:                                              ; preds = %129, %99
  %105 = phi i64 [ 0, %99 ], [ %130, %129 ]
  %106 = getelementptr inbounds float, ptr %9, i64 %105
  %107 = getelementptr inbounds float, ptr %10, i64 %105
  br label %108

108:                                              ; preds = %126, %104
  %109 = phi i64 [ %127, %126 ], [ 0, %104 ]
  %110 = shl nsw i64 %109, 11
  %111 = getelementptr inbounds i8, ptr %106, i64 %110
  %112 = load float, ptr %111, align 4, !tbaa !6, !alias.scope !51, !noalias !53
  %113 = getelementptr inbounds float, ptr %8, i64 %109
  br label %114

114:                                              ; preds = %114, %108
  %115 = phi i64 [ %124, %114 ], [ 0, %108 ]
  %116 = add nuw nsw i64 %115, %100
  %117 = shl nsw i64 %116, 9
  %118 = getelementptr inbounds i8, ptr %113, i64 %117
  %119 = load float, ptr %118, align 4, !tbaa !6, !alias.scope !46, !noalias !54
  %120 = shl nsw i64 %116, 11
  %121 = getelementptr inbounds i8, ptr %107, i64 %120
  %122 = load float, ptr %121, align 4, !tbaa !6, !alias.scope !49, !noalias !55
  %123 = call float @llvm.fmuladd.f32(float %119, float %112, float %122)
  store float %123, ptr %121, align 4, !tbaa !6, !alias.scope !49, !noalias !55
  %124 = add nuw nsw i64 %115, 1
  %125 = icmp eq i64 %124, %103
  br i1 %125, label %126, label %114, !llvm.loop !22

126:                                              ; preds = %114
  %127 = add nuw nsw i64 %109, 1
  %128 = icmp eq i64 %127, 128
  br i1 %128, label %129, label %108, !llvm.loop !23

129:                                              ; preds = %126
  %130 = add nuw nsw i64 %105, 1
  %131 = icmp eq i64 %130, 512
  br i1 %131, label %132, label %104, !llvm.loop !24

132:                                              ; preds = %129
  %133 = add nuw nsw i64 %100, 21
  %134 = icmp ult i64 %100, 107
  br i1 %134, label %99, label %135, !llvm.loop !25

135:                                              ; preds = %132
  %136 = call i32 @clock_gettime(i32 noundef 6, ptr noundef nonnull %2) #9
  %137 = load i64, ptr %2, align 8, !tbaa !56
  %138 = load i64, ptr %1, align 8, !tbaa !56
  %139 = sub nsw i64 %137, %138
  %140 = sitofp i64 %139 to double
  %141 = getelementptr inbounds i8, ptr %2, i64 8
  %142 = load i64, ptr %141, align 8, !tbaa !59
  %143 = getelementptr inbounds i8, ptr %1, i64 8
  %144 = load i64, ptr %143, align 8, !tbaa !59
  %145 = sub nsw i64 %142, %144
  %146 = sitofp i64 %145 to double
  %147 = call double @llvm.fmuladd.f64(double %146, double 1.000000e-09, double %140)
  %148 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str, double noundef %147)
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
!33 = !{!27, !32}
!34 = !{!27, !30}
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
