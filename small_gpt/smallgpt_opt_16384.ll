; ModuleID = 'small_gpt/smallgpt_opt_16384.c'
source_filename = "small_gpt/smallgpt_opt_16384.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128-Fn32"
target triple = "arm64-apple-macosx15.0.0"

%struct.timespec = type { i64, i64 }

@.str = private unnamed_addr constant [10 x i8] c"Time: %f\0A\00", align 1
@.memset_pattern.6 = private unnamed_addr constant [4 x float] [float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00], align 16

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_0(ptr noalias nocapture noundef %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef readonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %12
  %5 = phi i1 [ true, %3 ], [ false, %12 ]
  %6 = phi i64 [ 0, %3 ], [ 128, %12 ]
  br label %8

7:                                                ; preds = %12
  ret void

8:                                                ; preds = %4, %13
  %9 = phi i64 [ 0, %4 ], [ %14, %13 ]
  %10 = shl nsw i64 %9, 10
  %11 = getelementptr inbounds i8, ptr %2, i64 %10
  br label %16

12:                                               ; preds = %13
  br i1 %5, label %4, label %7, !llvm.loop !6

13:                                               ; preds = %21
  %14 = add nuw nsw i64 %9, 1
  %15 = icmp eq i64 %14, 256
  br i1 %15, label %12, label %8, !llvm.loop !9

16:                                               ; preds = %8, %21
  %17 = phi i64 [ 0, %8 ], [ %22, %21 ]
  %18 = or disjoint i64 %17, %6
  %19 = getelementptr inbounds float, ptr %11, i64 %18
  %20 = load float, ptr %19, align 4, !tbaa !10
  br label %24

21:                                               ; preds = %24
  %22 = add nuw nsw i64 %17, 1
  %23 = icmp eq i64 %22, 128
  br i1 %23, label %13, label %16, !llvm.loop !14

24:                                               ; preds = %16, %24
  %25 = phi i64 [ 0, %16 ], [ %34, %24 ]
  %26 = shl nuw nsw i64 %25, 8
  %27 = or disjoint i64 %26, %9
  %28 = getelementptr inbounds float, ptr %1, i64 %27
  %29 = load float, ptr %28, align 4, !tbaa !10
  %30 = or disjoint i64 %26, %18
  %31 = getelementptr inbounds float, ptr %0, i64 %30
  %32 = load float, ptr %31, align 4, !tbaa !10
  %33 = tail call float @llvm.fmuladd.f32(float %29, float %20, float %32)
  store float %33, ptr %31, align 4, !tbaa !10
  %34 = add nuw nsw i64 %25, 1
  %35 = icmp eq i64 %34, 64
  br i1 %35, label %21, label %24, !llvm.loop !15
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

4:                                                ; preds = %3, %8
  %5 = phi i1 [ true, %3 ], [ false, %8 ]
  %6 = phi i64 [ 0, %3 ], [ 128, %8 ]
  br label %9

7:                                                ; preds = %8
  ret void

8:                                                ; preds = %21
  br i1 %5, label %4, label %7, !llvm.loop !16

9:                                                ; preds = %4, %21
  %10 = phi i64 [ 0, %4 ], [ %22, %21 ]
  %11 = or disjoint i64 %10, %6
  %12 = getelementptr inbounds float, ptr %1, i64 %11
  %13 = getelementptr inbounds float, ptr %2, i64 %11
  br label %14

14:                                               ; preds = %9, %24
  %15 = phi i64 [ 0, %9 ], [ %25, %24 ]
  %16 = shl nsw i64 %15, 10
  %17 = getelementptr inbounds i8, ptr %12, i64 %16
  %18 = load float, ptr %17, align 4, !tbaa !10
  %19 = shl nsw i64 %15, 8
  %20 = getelementptr inbounds i8, ptr %0, i64 %19
  br label %27

21:                                               ; preds = %24
  %22 = add nuw nsw i64 %10, 1
  %23 = icmp eq i64 %22, 128
  br i1 %23, label %8, label %9, !llvm.loop !17

24:                                               ; preds = %27
  %25 = add nuw nsw i64 %15, 1
  %26 = icmp eq i64 %25, 64
  br i1 %26, label %21, label %14, !llvm.loop !18

27:                                               ; preds = %14, %27
  %28 = phi i64 [ 0, %14 ], [ %35, %27 ]
  %29 = shl nsw i64 %28, 10
  %30 = getelementptr inbounds i8, ptr %13, i64 %29
  %31 = load float, ptr %30, align 4, !tbaa !10
  %32 = getelementptr inbounds float, ptr %20, i64 %28
  %33 = load float, ptr %32, align 4, !tbaa !10
  %34 = tail call float @llvm.fmuladd.f32(float %18, float %31, float %33)
  store float %34, ptr %32, align 4, !tbaa !10
  %35 = add nuw nsw i64 %28, 1
  %36 = icmp eq i64 %35, 64
  br i1 %36, label %24, label %27, !llvm.loop !19
}

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_2(ptr noalias nocapture noundef readonly %0, ptr noalias nocapture noundef %1, ptr noalias nocapture noundef readonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %13
  %5 = phi i1 [ true, %3 ], [ false, %13 ]
  %6 = phi i64 [ 0, %3 ], [ 128, %13 ]
  br label %8

7:                                                ; preds = %13
  ret void

8:                                                ; preds = %4, %14
  %9 = phi i64 [ 0, %4 ], [ %15, %14 ]
  %10 = or disjoint i64 %9, %6
  %11 = getelementptr inbounds float, ptr %2, i64 %10
  %12 = getelementptr inbounds float, ptr %1, i64 %10
  br label %17

13:                                               ; preds = %14
  br i1 %5, label %4, label %7, !llvm.loop !20

14:                                               ; preds = %23
  %15 = add nuw nsw i64 %9, 1
  %16 = icmp eq i64 %15, 128
  br i1 %16, label %13, label %8, !llvm.loop !21

17:                                               ; preds = %8, %23
  %18 = phi i64 [ 0, %8 ], [ %24, %23 ]
  %19 = shl nsw i64 %18, 10
  %20 = getelementptr inbounds i8, ptr %11, i64 %19
  %21 = load float, ptr %20, align 4, !tbaa !10
  %22 = getelementptr inbounds float, ptr %0, i64 %18
  br label %26

23:                                               ; preds = %26
  %24 = add nuw nsw i64 %18, 1
  %25 = icmp eq i64 %24, 64
  br i1 %25, label %14, label %17, !llvm.loop !22

26:                                               ; preds = %17, %26
  %27 = phi i64 [ 0, %17 ], [ %35, %26 ]
  %28 = shl nsw i64 %27, 8
  %29 = getelementptr inbounds i8, ptr %22, i64 %28
  %30 = load float, ptr %29, align 4, !tbaa !10
  %31 = shl nsw i64 %27, 10
  %32 = getelementptr inbounds i8, ptr %12, i64 %31
  %33 = load float, ptr %32, align 4, !tbaa !10
  %34 = tail call float @llvm.fmuladd.f32(float %30, float %21, float %33)
  store float %34, ptr %32, align 4, !tbaa !10
  %35 = add nuw nsw i64 %27, 1
  %36 = icmp eq i64 %35, 64
  br i1 %36, label %23, label %26, !llvm.loop !23
}

; Function Attrs: nounwind ssp uwtable(sync)
define noundef i32 @main() local_unnamed_addr #3 {
  %1 = alloca %struct.timespec, align 8
  %2 = alloca %struct.timespec, align 8
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %1) #9
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %2) #9
  %3 = call i32 @clock_gettime(i32 noundef 6, ptr noundef nonnull %1) #9
  %4 = call dereferenceable_or_null(65536) ptr @malloc(i64 noundef 65536) #10
  call void @memset_pattern16(ptr %4, ptr nonnull @.memset_pattern.6, i64 65536), !tbaa !10
  %5 = call dereferenceable_or_null(262144) ptr @malloc(i64 noundef 262144) #10
  call void @memset_pattern16(ptr %5, ptr nonnull @.memset_pattern.6, i64 262144), !tbaa !10
  %6 = call dereferenceable_or_null(65536) ptr @malloc(i64 noundef 65536) #10
  call void @memset_pattern16(ptr %6, ptr nonnull @.memset_pattern.6, i64 65536), !tbaa !10
  %7 = call dereferenceable_or_null(65536) ptr @malloc(i64 noundef 65536) #10
  call void @memset_pattern16(ptr %7, ptr nonnull @.memset_pattern.6, i64 65536), !tbaa !10
  %8 = call dereferenceable_or_null(16384) ptr @malloc(i64 noundef 16384) #10
  call void @memset_pattern16(ptr %8, ptr nonnull @.memset_pattern.6, i64 16384), !tbaa !10
  %9 = call dereferenceable_or_null(65536) ptr @malloc(i64 noundef 65536) #10
  call void @memset_pattern16(ptr %9, ptr nonnull @.memset_pattern.6, i64 65536), !tbaa !10
  %10 = call dereferenceable_or_null(65536) ptr @malloc(i64 noundef 65536) #10
  call void @memset_pattern16(ptr %10, ptr nonnull @.memset_pattern.6, i64 65536), !tbaa !10
  call void @llvm.experimental.noalias.scope.decl(metadata !24)
  call void @llvm.experimental.noalias.scope.decl(metadata !27)
  call void @llvm.experimental.noalias.scope.decl(metadata !29)
  br label %11

11:                                               ; preds = %18, %0
  %12 = phi i1 [ true, %0 ], [ false, %18 ]
  %13 = phi i64 [ 0, %0 ], [ 128, %18 ]
  br label %14

14:                                               ; preds = %19, %11
  %15 = phi i64 [ 0, %11 ], [ %20, %19 ]
  %16 = shl nsw i64 %15, 10
  %17 = getelementptr inbounds i8, ptr %5, i64 %16
  br label %22

18:                                               ; preds = %19
  br i1 %12, label %11, label %42, !llvm.loop !6

19:                                               ; preds = %27
  %20 = add nuw nsw i64 %15, 1
  %21 = icmp eq i64 %20, 256
  br i1 %21, label %18, label %14, !llvm.loop !9

22:                                               ; preds = %27, %14
  %23 = phi i64 [ 0, %14 ], [ %28, %27 ]
  %24 = or disjoint i64 %23, %13
  %25 = getelementptr inbounds float, ptr %17, i64 %24
  %26 = load float, ptr %25, align 4, !tbaa !10, !alias.scope !29, !noalias !31
  br label %30

27:                                               ; preds = %30
  %28 = add nuw nsw i64 %23, 1
  %29 = icmp eq i64 %28, 128
  br i1 %29, label %19, label %22, !llvm.loop !14

30:                                               ; preds = %30, %22
  %31 = phi i64 [ 0, %22 ], [ %40, %30 ]
  %32 = shl nuw nsw i64 %31, 8
  %33 = or disjoint i64 %32, %15
  %34 = getelementptr inbounds float, ptr %4, i64 %33
  %35 = load float, ptr %34, align 4, !tbaa !10, !alias.scope !27, !noalias !32
  %36 = or disjoint i64 %32, %24
  %37 = getelementptr inbounds float, ptr %6, i64 %36
  %38 = load float, ptr %37, align 4, !tbaa !10, !alias.scope !24, !noalias !33
  %39 = call float @llvm.fmuladd.f32(float %35, float %26, float %38)
  store float %39, ptr %37, align 4, !tbaa !10, !alias.scope !24, !noalias !33
  %40 = add nuw nsw i64 %31, 1
  %41 = icmp eq i64 %40, 64
  br i1 %41, label %27, label %30, !llvm.loop !15

42:                                               ; preds = %18
  call void @llvm.experimental.noalias.scope.decl(metadata !34)
  call void @llvm.experimental.noalias.scope.decl(metadata !37)
  call void @llvm.experimental.noalias.scope.decl(metadata !39)
  br label %43

43:                                               ; preds = %46, %42
  %44 = phi i1 [ true, %42 ], [ false, %46 ]
  %45 = phi i64 [ 0, %42 ], [ 128, %46 ]
  br label %47

46:                                               ; preds = %59
  br i1 %44, label %43, label %75, !llvm.loop !16

47:                                               ; preds = %59, %43
  %48 = phi i64 [ 0, %43 ], [ %60, %59 ]
  %49 = or disjoint i64 %48, %45
  %50 = getelementptr inbounds float, ptr %6, i64 %49
  %51 = getelementptr inbounds float, ptr %7, i64 %49
  br label %52

52:                                               ; preds = %62, %47
  %53 = phi i64 [ 0, %47 ], [ %63, %62 ]
  %54 = shl nsw i64 %53, 10
  %55 = getelementptr inbounds i8, ptr %50, i64 %54
  %56 = load float, ptr %55, align 4, !tbaa !10, !alias.scope !37, !noalias !41
  %57 = shl nsw i64 %53, 8
  %58 = getelementptr inbounds i8, ptr %8, i64 %57
  br label %65

59:                                               ; preds = %62
  %60 = add nuw nsw i64 %48, 1
  %61 = icmp eq i64 %60, 128
  br i1 %61, label %46, label %47, !llvm.loop !17

62:                                               ; preds = %65
  %63 = add nuw nsw i64 %53, 1
  %64 = icmp eq i64 %63, 64
  br i1 %64, label %59, label %52, !llvm.loop !18

65:                                               ; preds = %65, %52
  %66 = phi i64 [ 0, %52 ], [ %73, %65 ]
  %67 = shl nsw i64 %66, 10
  %68 = getelementptr inbounds i8, ptr %51, i64 %67
  %69 = load float, ptr %68, align 4, !tbaa !10, !alias.scope !39, !noalias !42
  %70 = getelementptr inbounds float, ptr %58, i64 %66
  %71 = load float, ptr %70, align 4, !tbaa !10, !alias.scope !34, !noalias !43
  %72 = call float @llvm.fmuladd.f32(float %56, float %69, float %71)
  store float %72, ptr %70, align 4, !tbaa !10, !alias.scope !34, !noalias !43
  %73 = add nuw nsw i64 %66, 1
  %74 = icmp eq i64 %73, 64
  br i1 %74, label %62, label %65, !llvm.loop !19

75:                                               ; preds = %46
  call void @llvm.experimental.noalias.scope.decl(metadata !44)
  call void @llvm.experimental.noalias.scope.decl(metadata !47)
  call void @llvm.experimental.noalias.scope.decl(metadata !49)
  br label %76

76:                                               ; preds = %84, %75
  %77 = phi i1 [ true, %75 ], [ false, %84 ]
  %78 = phi i64 [ 0, %75 ], [ 128, %84 ]
  br label %79

79:                                               ; preds = %85, %76
  %80 = phi i64 [ 0, %76 ], [ %86, %85 ]
  %81 = or disjoint i64 %80, %78
  %82 = getelementptr inbounds float, ptr %9, i64 %81
  %83 = getelementptr inbounds float, ptr %10, i64 %81
  br label %88

84:                                               ; preds = %85
  br i1 %77, label %76, label %108, !llvm.loop !20

85:                                               ; preds = %94
  %86 = add nuw nsw i64 %80, 1
  %87 = icmp eq i64 %86, 128
  br i1 %87, label %84, label %79, !llvm.loop !21

88:                                               ; preds = %94, %79
  %89 = phi i64 [ 0, %79 ], [ %95, %94 ]
  %90 = shl nsw i64 %89, 10
  %91 = getelementptr inbounds i8, ptr %82, i64 %90
  %92 = load float, ptr %91, align 4, !tbaa !10, !alias.scope !49, !noalias !51
  %93 = getelementptr inbounds float, ptr %8, i64 %89
  br label %97

94:                                               ; preds = %97
  %95 = add nuw nsw i64 %89, 1
  %96 = icmp eq i64 %95, 64
  br i1 %96, label %85, label %88, !llvm.loop !22

97:                                               ; preds = %97, %88
  %98 = phi i64 [ 0, %88 ], [ %106, %97 ]
  %99 = shl nsw i64 %98, 8
  %100 = getelementptr inbounds i8, ptr %93, i64 %99
  %101 = load float, ptr %100, align 4, !tbaa !10, !alias.scope !44, !noalias !52
  %102 = shl nsw i64 %98, 10
  %103 = getelementptr inbounds i8, ptr %83, i64 %102
  %104 = load float, ptr %103, align 4, !tbaa !10, !alias.scope !47, !noalias !53
  %105 = call float @llvm.fmuladd.f32(float %101, float %92, float %104)
  store float %105, ptr %103, align 4, !tbaa !10, !alias.scope !47, !noalias !53
  %106 = add nuw nsw i64 %98, 1
  %107 = icmp eq i64 %106, 64
  br i1 %107, label %94, label %97, !llvm.loop !23

108:                                              ; preds = %84
  %109 = call i32 @clock_gettime(i32 noundef 6, ptr noundef nonnull %2) #9
  %110 = load i64, ptr %2, align 8, !tbaa !54
  %111 = load i64, ptr %1, align 8, !tbaa !54
  %112 = sub nsw i64 %110, %111
  %113 = sitofp i64 %112 to double
  %114 = getelementptr inbounds i8, ptr %2, i64 8
  %115 = load i64, ptr %114, align 8, !tbaa !57
  %116 = getelementptr inbounds i8, ptr %1, i64 8
  %117 = load i64, ptr %116, align 8, !tbaa !57
  %118 = sub nsw i64 %115, %117
  %119 = sitofp i64 %118 to double
  %120 = call double @llvm.fmuladd.f64(double %119, double 1.000000e-09, double %113)
  %121 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str, double noundef %120)
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
!9 = distinct !{!9, !7, !8}
!10 = !{!11, !11, i64 0}
!11 = !{!"float", !12, i64 0}
!12 = !{!"omnipotent char", !13, i64 0}
!13 = !{!"Simple C/C++ TBAA"}
!14 = distinct !{!14, !7, !8}
!15 = distinct !{!15, !7, !8}
!16 = distinct !{!16, !7, !8}
!17 = distinct !{!17, !7, !8}
!18 = distinct !{!18, !7, !8}
!19 = distinct !{!19, !7, !8}
!20 = distinct !{!20, !7, !8}
!21 = distinct !{!21, !7, !8}
!22 = distinct !{!22, !7, !8}
!23 = distinct !{!23, !7, !8}
!24 = !{!25}
!25 = distinct !{!25, !26, !"einsum_0: argument 0"}
!26 = distinct !{!26, !"einsum_0"}
!27 = !{!28}
!28 = distinct !{!28, !26, !"einsum_0: argument 1"}
!29 = !{!30}
!30 = distinct !{!30, !26, !"einsum_0: argument 2"}
!31 = !{!25, !28}
!32 = !{!25, !30}
!33 = !{!28, !30}
!34 = !{!35}
!35 = distinct !{!35, !36, !"einsum_1: argument 0"}
!36 = distinct !{!36, !"einsum_1"}
!37 = !{!38}
!38 = distinct !{!38, !36, !"einsum_1: argument 1"}
!39 = !{!40}
!40 = distinct !{!40, !36, !"einsum_1: argument 2"}
!41 = !{!35, !40}
!42 = !{!35, !38}
!43 = !{!38, !40}
!44 = !{!45}
!45 = distinct !{!45, !46, !"einsum_2: argument 0"}
!46 = distinct !{!46, !"einsum_2"}
!47 = !{!48}
!48 = distinct !{!48, !46, !"einsum_2: argument 1"}
!49 = !{!50}
!50 = distinct !{!50, !46, !"einsum_2: argument 2"}
!51 = !{!45, !48}
!52 = !{!48, !50}
!53 = !{!45, !50}
!54 = !{!55, !56, i64 0}
!55 = !{!"timespec", !56, i64 0, !56, i64 8}
!56 = !{!"long", !12, i64 0}
!57 = !{!55, !56, i64 8}
