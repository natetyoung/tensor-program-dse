; ModuleID = 'small_gpt/smallgpt_opt_4096.c'
source_filename = "small_gpt/smallgpt_opt_4096.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128-Fn32"
target triple = "arm64-apple-macosx15.0.0"

%struct.timespec = type { i64, i64 }

@.str = private unnamed_addr constant [10 x i8] c"Time: %f\0A\00", align 1
@.memset_pattern.6 = private unnamed_addr constant [4 x float] [float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00], align 16

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_0(ptr noalias nocapture noundef %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef readonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %45, %3
  %5 = phi i1 [ true, %3 ], [ false, %45 ]
  %6 = phi i64 [ 0, %3 ], [ 32, %45 ]
  br label %7

7:                                                ; preds = %4, %41
  %8 = phi i64 [ 0, %4 ], [ %42, %41 ]
  %9 = icmp ult i64 %8, 206
  %10 = sub nsw i64 256, %8
  %11 = and i64 %10, 4294967295
  %12 = select i1 %9, i64 51, i64 %11
  br label %13

13:                                               ; preds = %38, %7
  %14 = phi i64 [ %39, %38 ], [ 0, %7 ]
  %15 = shl nsw i64 %14, 10
  %16 = getelementptr inbounds i8, ptr %2, i64 %15
  br label %17

17:                                               ; preds = %35, %13
  %18 = phi i64 [ %36, %35 ], [ 0, %13 ]
  %19 = add nuw nsw i64 %18, %6
  %20 = shl nsw i64 %19, 8
  %21 = or disjoint i64 %20, %14
  %22 = getelementptr inbounds float, ptr %1, i64 %21
  %23 = load float, ptr %22, align 4, !tbaa !6
  %24 = getelementptr inbounds float, ptr %0, i64 %20
  br label %25

25:                                               ; preds = %25, %17
  %26 = phi i64 [ %33, %25 ], [ 0, %17 ]
  %27 = add nuw nsw i64 %26, %8
  %28 = getelementptr inbounds float, ptr %16, i64 %27
  %29 = load float, ptr %28, align 4, !tbaa !6
  %30 = getelementptr inbounds float, ptr %24, i64 %27
  %31 = load float, ptr %30, align 4, !tbaa !6
  %32 = tail call float @llvm.fmuladd.f32(float %23, float %29, float %31)
  store float %32, ptr %30, align 4, !tbaa !6
  %33 = add nuw nsw i64 %26, 1
  %34 = icmp eq i64 %33, %12
  br i1 %34, label %35, label %25, !llvm.loop !10

35:                                               ; preds = %25
  %36 = add nuw nsw i64 %18, 1
  %37 = icmp eq i64 %36, 32
  br i1 %37, label %38, label %17, !llvm.loop !13

38:                                               ; preds = %35
  %39 = add nuw nsw i64 %14, 1
  %40 = icmp eq i64 %39, 256
  br i1 %40, label %41, label %13, !llvm.loop !14

41:                                               ; preds = %38
  %42 = add nuw nsw i64 %8, 51
  %43 = icmp ult i64 %8, 205
  br i1 %43, label %7, label %45, !llvm.loop !15

44:                                               ; preds = %45
  ret void

45:                                               ; preds = %41
  br i1 %5, label %4, label %44, !llvm.loop !16
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

4:                                                ; preds = %42, %3
  %5 = phi i1 [ true, %3 ], [ false, %42 ]
  %6 = phi i64 [ 0, %3 ], [ 32, %42 ]
  br label %7

7:                                                ; preds = %4, %38
  %8 = phi i64 [ 0, %4 ], [ %39, %38 ]
  br label %9

9:                                                ; preds = %35, %7
  %10 = phi i64 [ %36, %35 ], [ 0, %7 ]
  %11 = shl nsw i64 %10, 10
  %12 = getelementptr inbounds i8, ptr %2, i64 %11
  %13 = getelementptr inbounds float, ptr %0, i64 %10
  br label %14

14:                                               ; preds = %32, %9
  %15 = phi i64 [ %33, %32 ], [ 0, %9 ]
  %16 = add nuw nsw i64 %15, %8
  %17 = getelementptr inbounds float, ptr %12, i64 %16
  %18 = load float, ptr %17, align 4, !tbaa !6
  %19 = getelementptr inbounds float, ptr %1, i64 %16
  br label %20

20:                                               ; preds = %20, %14
  %21 = phi i64 [ %30, %20 ], [ 0, %14 ]
  %22 = add nuw nsw i64 %21, %6
  %23 = shl nsw i64 %22, 10
  %24 = getelementptr inbounds i8, ptr %19, i64 %23
  %25 = load float, ptr %24, align 4, !tbaa !6
  %26 = shl nsw i64 %22, 8
  %27 = getelementptr inbounds i8, ptr %13, i64 %26
  %28 = load float, ptr %27, align 4, !tbaa !6
  %29 = tail call float @llvm.fmuladd.f32(float %25, float %18, float %28)
  store float %29, ptr %27, align 4, !tbaa !6
  %30 = add nuw nsw i64 %21, 1
  %31 = icmp eq i64 %30, 32
  br i1 %31, label %32, label %20, !llvm.loop !17

32:                                               ; preds = %20
  %33 = add nuw nsw i64 %15, 1
  %34 = icmp eq i64 %33, 51
  br i1 %34, label %35, label %14, !llvm.loop !18

35:                                               ; preds = %32
  %36 = add nuw nsw i64 %10, 1
  %37 = icmp eq i64 %36, 64
  br i1 %37, label %38, label %9, !llvm.loop !19

38:                                               ; preds = %35
  %39 = add nuw nsw i64 %8, 51
  %40 = icmp ult i64 %8, 205
  br i1 %40, label %7, label %42, !llvm.loop !20

41:                                               ; preds = %42
  ret void

42:                                               ; preds = %38
  br i1 %5, label %4, label %41, !llvm.loop !21
}

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_2(ptr noalias nocapture noundef readonly %0, ptr noalias nocapture noundef %1, ptr noalias nocapture noundef readonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %36, %3
  %5 = phi i1 [ true, %3 ], [ false, %36 ]
  %6 = phi i64 [ 0, %3 ], [ 32, %36 ]
  br label %7

7:                                                ; preds = %4, %32
  %8 = phi i64 [ 0, %4 ], [ %33, %32 ]
  %9 = getelementptr inbounds float, ptr %2, i64 %8
  %10 = getelementptr inbounds float, ptr %1, i64 %8
  br label %11

11:                                               ; preds = %29, %7
  %12 = phi i64 [ %30, %29 ], [ 0, %7 ]
  %13 = shl nsw i64 %12, 10
  %14 = getelementptr inbounds i8, ptr %9, i64 %13
  %15 = load float, ptr %14, align 4, !tbaa !6
  %16 = getelementptr inbounds float, ptr %0, i64 %12
  br label %17

17:                                               ; preds = %17, %11
  %18 = phi i64 [ %27, %17 ], [ 0, %11 ]
  %19 = add nuw nsw i64 %18, %6
  %20 = shl nsw i64 %19, 8
  %21 = getelementptr inbounds i8, ptr %16, i64 %20
  %22 = load float, ptr %21, align 4, !tbaa !6
  %23 = shl nsw i64 %19, 10
  %24 = getelementptr inbounds i8, ptr %10, i64 %23
  %25 = load float, ptr %24, align 4, !tbaa !6
  %26 = tail call float @llvm.fmuladd.f32(float %22, float %15, float %25)
  store float %26, ptr %24, align 4, !tbaa !6
  %27 = add nuw nsw i64 %18, 1
  %28 = icmp eq i64 %27, 32
  br i1 %28, label %29, label %17, !llvm.loop !22

29:                                               ; preds = %17
  %30 = add nuw nsw i64 %12, 1
  %31 = icmp eq i64 %30, 64
  br i1 %31, label %32, label %11, !llvm.loop !23

32:                                               ; preds = %29
  %33 = add nuw nsw i64 %8, 1
  %34 = icmp eq i64 %33, 256
  br i1 %34, label %36, label %7, !llvm.loop !24

35:                                               ; preds = %36
  ret void

36:                                               ; preds = %32
  br i1 %5, label %4, label %35, !llvm.loop !25
}

; Function Attrs: nounwind ssp uwtable(sync)
define noundef i32 @main() local_unnamed_addr #3 {
  %1 = alloca %struct.timespec, align 8
  %2 = alloca %struct.timespec, align 8
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %1) #9
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %2) #9
  %3 = call i32 @clock_gettime(i32 noundef 6, ptr noundef nonnull %1) #9
  %4 = call dereferenceable_or_null(65536) ptr @malloc(i64 noundef 65536) #10
  call void @memset_pattern16(ptr %4, ptr nonnull @.memset_pattern.6, i64 65536), !tbaa !6
  %5 = call dereferenceable_or_null(262144) ptr @malloc(i64 noundef 262144) #10
  call void @memset_pattern16(ptr %5, ptr nonnull @.memset_pattern.6, i64 262144), !tbaa !6
  %6 = call dereferenceable_or_null(65536) ptr @malloc(i64 noundef 65536) #10
  call void @memset_pattern16(ptr %6, ptr nonnull @.memset_pattern.6, i64 65536), !tbaa !6
  %7 = call dereferenceable_or_null(65536) ptr @malloc(i64 noundef 65536) #10
  call void @memset_pattern16(ptr %7, ptr nonnull @.memset_pattern.6, i64 65536), !tbaa !6
  %8 = call dereferenceable_or_null(16384) ptr @malloc(i64 noundef 16384) #10
  call void @memset_pattern16(ptr %8, ptr nonnull @.memset_pattern.6, i64 16384), !tbaa !6
  %9 = call dereferenceable_or_null(65536) ptr @malloc(i64 noundef 65536) #10
  call void @memset_pattern16(ptr %9, ptr nonnull @.memset_pattern.6, i64 65536), !tbaa !6
  %10 = call dereferenceable_or_null(65536) ptr @malloc(i64 noundef 65536) #10
  call void @memset_pattern16(ptr %10, ptr nonnull @.memset_pattern.6, i64 65536), !tbaa !6
  call void @llvm.experimental.noalias.scope.decl(metadata !26)
  call void @llvm.experimental.noalias.scope.decl(metadata !29)
  call void @llvm.experimental.noalias.scope.decl(metadata !31)
  br label %11

11:                                               ; preds = %50, %0
  %12 = phi i1 [ true, %0 ], [ false, %50 ]
  %13 = phi i64 [ 0, %0 ], [ 32, %50 ]
  br label %14

14:                                               ; preds = %47, %11
  %15 = phi i64 [ 0, %11 ], [ %48, %47 ]
  %16 = icmp ult i64 %15, 206
  %17 = sub nuw nsw i64 256, %15
  %18 = select i1 %16, i64 51, i64 %17
  br label %19

19:                                               ; preds = %44, %14
  %20 = phi i64 [ %45, %44 ], [ 0, %14 ]
  %21 = shl nsw i64 %20, 10
  %22 = getelementptr inbounds i8, ptr %5, i64 %21
  br label %23

23:                                               ; preds = %41, %19
  %24 = phi i64 [ %42, %41 ], [ 0, %19 ]
  %25 = add nuw nsw i64 %24, %13
  %26 = shl nsw i64 %25, 8
  %27 = or disjoint i64 %26, %20
  %28 = getelementptr inbounds float, ptr %4, i64 %27
  %29 = load float, ptr %28, align 4, !tbaa !6, !alias.scope !29, !noalias !33
  %30 = getelementptr inbounds float, ptr %6, i64 %26
  br label %31

31:                                               ; preds = %31, %23
  %32 = phi i64 [ %39, %31 ], [ 0, %23 ]
  %33 = add nuw nsw i64 %32, %15
  %34 = getelementptr inbounds float, ptr %22, i64 %33
  %35 = load float, ptr %34, align 4, !tbaa !6, !alias.scope !31, !noalias !34
  %36 = getelementptr inbounds float, ptr %30, i64 %33
  %37 = load float, ptr %36, align 4, !tbaa !6, !alias.scope !26, !noalias !35
  %38 = call float @llvm.fmuladd.f32(float %29, float %35, float %37)
  store float %38, ptr %36, align 4, !tbaa !6, !alias.scope !26, !noalias !35
  %39 = add nuw nsw i64 %32, 1
  %40 = icmp eq i64 %39, %18
  br i1 %40, label %41, label %31, !llvm.loop !10

41:                                               ; preds = %31
  %42 = add nuw nsw i64 %24, 1
  %43 = icmp eq i64 %42, 32
  br i1 %43, label %44, label %23, !llvm.loop !13

44:                                               ; preds = %41
  %45 = add nuw nsw i64 %20, 1
  %46 = icmp eq i64 %45, 256
  br i1 %46, label %47, label %19, !llvm.loop !14

47:                                               ; preds = %44
  %48 = add nuw nsw i64 %15, 51
  %49 = icmp ult i64 %15, 205
  br i1 %49, label %14, label %50, !llvm.loop !15

50:                                               ; preds = %47
  br i1 %12, label %11, label %51, !llvm.loop !16

51:                                               ; preds = %50
  call void @llvm.experimental.noalias.scope.decl(metadata !36)
  call void @llvm.experimental.noalias.scope.decl(metadata !39)
  call void @llvm.experimental.noalias.scope.decl(metadata !41)
  br label %52

52:                                               ; preds = %89, %51
  %53 = phi i1 [ true, %51 ], [ false, %89 ]
  %54 = phi i64 [ 0, %51 ], [ 32, %89 ]
  br label %55

55:                                               ; preds = %86, %52
  %56 = phi i64 [ 0, %52 ], [ %87, %86 ]
  br label %57

57:                                               ; preds = %83, %55
  %58 = phi i64 [ %84, %83 ], [ 0, %55 ]
  %59 = shl nsw i64 %58, 10
  %60 = getelementptr inbounds i8, ptr %7, i64 %59
  %61 = getelementptr inbounds float, ptr %8, i64 %58
  br label %62

62:                                               ; preds = %80, %57
  %63 = phi i64 [ %81, %80 ], [ 0, %57 ]
  %64 = add nuw nsw i64 %63, %56
  %65 = getelementptr inbounds float, ptr %60, i64 %64
  %66 = load float, ptr %65, align 4, !tbaa !6, !alias.scope !41, !noalias !43
  %67 = getelementptr inbounds float, ptr %6, i64 %64
  br label %68

68:                                               ; preds = %68, %62
  %69 = phi i64 [ %78, %68 ], [ 0, %62 ]
  %70 = add nuw nsw i64 %69, %54
  %71 = shl nsw i64 %70, 10
  %72 = getelementptr inbounds i8, ptr %67, i64 %71
  %73 = load float, ptr %72, align 4, !tbaa !6, !alias.scope !39, !noalias !44
  %74 = shl nsw i64 %70, 8
  %75 = getelementptr inbounds i8, ptr %61, i64 %74
  %76 = load float, ptr %75, align 4, !tbaa !6, !alias.scope !36, !noalias !45
  %77 = call float @llvm.fmuladd.f32(float %73, float %66, float %76)
  store float %77, ptr %75, align 4, !tbaa !6, !alias.scope !36, !noalias !45
  %78 = add nuw nsw i64 %69, 1
  %79 = icmp eq i64 %78, 32
  br i1 %79, label %80, label %68, !llvm.loop !17

80:                                               ; preds = %68
  %81 = add nuw nsw i64 %63, 1
  %82 = icmp eq i64 %81, 51
  br i1 %82, label %83, label %62, !llvm.loop !18

83:                                               ; preds = %80
  %84 = add nuw nsw i64 %58, 1
  %85 = icmp eq i64 %84, 64
  br i1 %85, label %86, label %57, !llvm.loop !19

86:                                               ; preds = %83
  %87 = add nuw nsw i64 %56, 51
  %88 = icmp ult i64 %56, 205
  br i1 %88, label %55, label %89, !llvm.loop !20

89:                                               ; preds = %86
  br i1 %53, label %52, label %90, !llvm.loop !21

90:                                               ; preds = %89
  call void @llvm.experimental.noalias.scope.decl(metadata !46)
  call void @llvm.experimental.noalias.scope.decl(metadata !49)
  call void @llvm.experimental.noalias.scope.decl(metadata !51)
  br label %91

91:                                               ; preds = %122, %90
  %92 = phi i1 [ true, %90 ], [ false, %122 ]
  %93 = phi i64 [ 0, %90 ], [ 32, %122 ]
  br label %94

94:                                               ; preds = %119, %91
  %95 = phi i64 [ 0, %91 ], [ %120, %119 ]
  %96 = getelementptr inbounds float, ptr %9, i64 %95
  %97 = getelementptr inbounds float, ptr %10, i64 %95
  br label %98

98:                                               ; preds = %116, %94
  %99 = phi i64 [ %117, %116 ], [ 0, %94 ]
  %100 = shl nsw i64 %99, 10
  %101 = getelementptr inbounds i8, ptr %96, i64 %100
  %102 = load float, ptr %101, align 4, !tbaa !6, !alias.scope !51, !noalias !53
  %103 = getelementptr inbounds float, ptr %8, i64 %99
  br label %104

104:                                              ; preds = %104, %98
  %105 = phi i64 [ %114, %104 ], [ 0, %98 ]
  %106 = add nuw nsw i64 %105, %93
  %107 = shl nsw i64 %106, 8
  %108 = getelementptr inbounds i8, ptr %103, i64 %107
  %109 = load float, ptr %108, align 4, !tbaa !6, !alias.scope !46, !noalias !54
  %110 = shl nsw i64 %106, 10
  %111 = getelementptr inbounds i8, ptr %97, i64 %110
  %112 = load float, ptr %111, align 4, !tbaa !6, !alias.scope !49, !noalias !55
  %113 = call float @llvm.fmuladd.f32(float %109, float %102, float %112)
  store float %113, ptr %111, align 4, !tbaa !6, !alias.scope !49, !noalias !55
  %114 = add nuw nsw i64 %105, 1
  %115 = icmp eq i64 %114, 32
  br i1 %115, label %116, label %104, !llvm.loop !22

116:                                              ; preds = %104
  %117 = add nuw nsw i64 %99, 1
  %118 = icmp eq i64 %117, 64
  br i1 %118, label %119, label %98, !llvm.loop !23

119:                                              ; preds = %116
  %120 = add nuw nsw i64 %95, 1
  %121 = icmp eq i64 %120, 256
  br i1 %121, label %122, label %94, !llvm.loop !24

122:                                              ; preds = %119
  br i1 %92, label %91, label %123, !llvm.loop !25

123:                                              ; preds = %122
  %124 = call i32 @clock_gettime(i32 noundef 6, ptr noundef nonnull %2) #9
  %125 = load i64, ptr %2, align 8, !tbaa !56
  %126 = load i64, ptr %1, align 8, !tbaa !56
  %127 = sub nsw i64 %125, %126
  %128 = sitofp i64 %127 to double
  %129 = getelementptr inbounds i8, ptr %2, i64 8
  %130 = load i64, ptr %129, align 8, !tbaa !59
  %131 = getelementptr inbounds i8, ptr %1, i64 8
  %132 = load i64, ptr %131, align 8, !tbaa !59
  %133 = sub nsw i64 %130, %132
  %134 = sitofp i64 %133 to double
  %135 = call double @llvm.fmuladd.f64(double %134, double 1.000000e-09, double %128)
  %136 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str, double noundef %135)
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
