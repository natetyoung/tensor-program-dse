; ModuleID = 'tiny_gpt/tinygpt_opt_4096.c'
source_filename = "tiny_gpt/tinygpt_opt_4096.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128-Fn32"
target triple = "arm64-apple-macosx15.0.0"

%struct.timespec = type { i64, i64 }

@.str = private unnamed_addr constant [10 x i8] c"Time: %f\0A\00", align 1
@.memset_pattern.6 = private unnamed_addr constant [4 x float] [float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00], align 16

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_0(ptr noalias nocapture noundef %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef readonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %35, %3
  %5 = phi i1 [ true, %3 ], [ false, %35 ]
  %6 = phi i64 [ 0, %3 ], [ 64, %35 ]
  br label %7

7:                                                ; preds = %4, %31
  %8 = phi i64 [ 0, %4 ], [ %32, %31 ]
  %9 = shl nsw i64 %8, 9
  %10 = getelementptr inbounds i8, ptr %1, i64 %9
  br label %11

11:                                               ; preds = %28, %7
  %12 = phi i64 [ %29, %28 ], [ 0, %7 ]
  %13 = shl nuw nsw i64 %12, 7
  %14 = or disjoint i64 %13, %8
  %15 = getelementptr inbounds float, ptr %2, i64 %14
  %16 = load float, ptr %15, align 4, !tbaa !6
  %17 = getelementptr inbounds float, ptr %0, i64 %13
  br label %18

18:                                               ; preds = %18, %11
  %19 = phi i64 [ %26, %18 ], [ 0, %11 ]
  %20 = add nuw nsw i64 %19, %6
  %21 = getelementptr inbounds float, ptr %10, i64 %20
  %22 = load float, ptr %21, align 4, !tbaa !6
  %23 = getelementptr inbounds float, ptr %17, i64 %20
  %24 = load float, ptr %23, align 4, !tbaa !6
  %25 = tail call float @llvm.fmuladd.f32(float %22, float %16, float %24)
  store float %25, ptr %23, align 4, !tbaa !6
  %26 = add nuw nsw i64 %19, 1
  %27 = icmp eq i64 %26, 64
  br i1 %27, label %28, label %18, !llvm.loop !10

28:                                               ; preds = %18
  %29 = add nuw nsw i64 %12, 1
  %30 = icmp eq i64 %29, 32
  br i1 %30, label %31, label %11, !llvm.loop !13

31:                                               ; preds = %28
  %32 = add nuw nsw i64 %8, 1
  %33 = icmp eq i64 %32, 128
  br i1 %33, label %35, label %7, !llvm.loop !14

34:                                               ; preds = %35
  ret void

35:                                               ; preds = %31
  br i1 %5, label %4, label %34, !llvm.loop !15
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

4:                                                ; preds = %3, %13
  %5 = phi i1 [ true, %3 ], [ false, %13 ]
  %6 = phi i64 [ 0, %3 ], [ 64, %13 ]
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
  br i1 %5, label %4, label %7, !llvm.loop !16

14:                                               ; preds = %23
  %15 = add nuw nsw i64 %9, 1
  %16 = icmp eq i64 %15, 64
  br i1 %16, label %13, label %8, !llvm.loop !17

17:                                               ; preds = %8, %23
  %18 = phi i64 [ 0, %8 ], [ %24, %23 ]
  %19 = shl nsw i64 %18, 9
  %20 = getelementptr inbounds i8, ptr %11, i64 %19
  %21 = load float, ptr %20, align 4, !tbaa !6
  %22 = getelementptr inbounds float, ptr %0, i64 %18
  br label %26

23:                                               ; preds = %26
  %24 = add nuw nsw i64 %18, 1
  %25 = icmp eq i64 %24, 32
  br i1 %25, label %14, label %17, !llvm.loop !18

26:                                               ; preds = %17, %26
  %27 = phi i64 [ 0, %17 ], [ %35, %26 ]
  %28 = shl nsw i64 %27, 9
  %29 = getelementptr inbounds i8, ptr %12, i64 %28
  %30 = load float, ptr %29, align 4, !tbaa !6
  %31 = shl nsw i64 %27, 7
  %32 = getelementptr inbounds i8, ptr %22, i64 %31
  %33 = load float, ptr %32, align 4, !tbaa !6
  %34 = tail call float @llvm.fmuladd.f32(float %30, float %21, float %33)
  store float %34, ptr %32, align 4, !tbaa !6
  %35 = add nuw nsw i64 %27, 1
  %36 = icmp eq i64 %35, 32
  br i1 %36, label %23, label %26, !llvm.loop !19
}

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_2(ptr noalias nocapture noundef readonly %0, ptr noalias nocapture noundef %1, ptr noalias nocapture noundef readonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %13
  %5 = phi i1 [ true, %3 ], [ false, %13 ]
  %6 = phi i64 [ 0, %3 ], [ 64, %13 ]
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
  %16 = icmp eq i64 %15, 64
  br i1 %16, label %13, label %8, !llvm.loop !21

17:                                               ; preds = %8, %23
  %18 = phi i64 [ 0, %8 ], [ %24, %23 ]
  %19 = shl nsw i64 %18, 9
  %20 = getelementptr inbounds i8, ptr %11, i64 %19
  %21 = load float, ptr %20, align 4, !tbaa !6
  %22 = getelementptr inbounds float, ptr %0, i64 %18
  br label %26

23:                                               ; preds = %26
  %24 = add nuw nsw i64 %18, 1
  %25 = icmp eq i64 %24, 32
  br i1 %25, label %14, label %17, !llvm.loop !22

26:                                               ; preds = %17, %26
  %27 = phi i64 [ 0, %17 ], [ %35, %26 ]
  %28 = shl nsw i64 %27, 7
  %29 = getelementptr inbounds i8, ptr %22, i64 %28
  %30 = load float, ptr %29, align 4, !tbaa !6
  %31 = shl nsw i64 %27, 9
  %32 = getelementptr inbounds i8, ptr %12, i64 %31
  %33 = load float, ptr %32, align 4, !tbaa !6
  %34 = tail call float @llvm.fmuladd.f32(float %30, float %21, float %33)
  store float %34, ptr %32, align 4, !tbaa !6
  %35 = add nuw nsw i64 %27, 1
  %36 = icmp eq i64 %35, 32
  br i1 %36, label %23, label %26, !llvm.loop !23
}

; Function Attrs: nounwind ssp uwtable(sync)
define noundef i32 @main() local_unnamed_addr #3 {
  %1 = alloca %struct.timespec, align 8
  %2 = alloca %struct.timespec, align 8
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %1) #9
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %2) #9
  %3 = call i32 @clock_gettime(i32 noundef 6, ptr noundef nonnull %1) #9
  %4 = call dereferenceable_or_null(16384) ptr @malloc(i64 noundef 16384) #10
  call void @memset_pattern16(ptr %4, ptr nonnull @.memset_pattern.6, i64 16384), !tbaa !6
  %5 = call dereferenceable_or_null(65536) ptr @malloc(i64 noundef 65536) #10
  call void @memset_pattern16(ptr %5, ptr nonnull @.memset_pattern.6, i64 65536), !tbaa !6
  %6 = call dereferenceable_or_null(16384) ptr @malloc(i64 noundef 16384) #10
  call void @memset_pattern16(ptr %6, ptr nonnull @.memset_pattern.6, i64 16384), !tbaa !6
  %7 = call dereferenceable_or_null(16384) ptr @malloc(i64 noundef 16384) #10
  call void @memset_pattern16(ptr %7, ptr nonnull @.memset_pattern.6, i64 16384), !tbaa !6
  %8 = call dereferenceable_or_null(4096) ptr @malloc(i64 noundef 4096) #10
  call void @memset_pattern16(ptr %8, ptr nonnull @.memset_pattern.6, i64 4096), !tbaa !6
  %9 = call dereferenceable_or_null(16384) ptr @malloc(i64 noundef 16384) #10
  call void @memset_pattern16(ptr %9, ptr nonnull @.memset_pattern.6, i64 16384), !tbaa !6
  %10 = call dereferenceable_or_null(16384) ptr @malloc(i64 noundef 16384) #10
  call void @memset_pattern16(ptr %10, ptr nonnull @.memset_pattern.6, i64 16384), !tbaa !6
  call void @llvm.experimental.noalias.scope.decl(metadata !24)
  call void @llvm.experimental.noalias.scope.decl(metadata !27)
  call void @llvm.experimental.noalias.scope.decl(metadata !29)
  br label %11

11:                                               ; preds = %41, %0
  %12 = phi i1 [ true, %0 ], [ false, %41 ]
  %13 = phi i64 [ 0, %0 ], [ 64, %41 ]
  br label %14

14:                                               ; preds = %38, %11
  %15 = phi i64 [ 0, %11 ], [ %39, %38 ]
  %16 = shl nsw i64 %15, 9
  %17 = getelementptr inbounds i8, ptr %5, i64 %16
  br label %18

18:                                               ; preds = %35, %14
  %19 = phi i64 [ %36, %35 ], [ 0, %14 ]
  %20 = shl nuw nsw i64 %19, 7
  %21 = or disjoint i64 %20, %15
  %22 = getelementptr inbounds float, ptr %4, i64 %21
  %23 = load float, ptr %22, align 4, !tbaa !6, !alias.scope !29, !noalias !31
  %24 = getelementptr inbounds float, ptr %6, i64 %20
  br label %25

25:                                               ; preds = %25, %18
  %26 = phi i64 [ %33, %25 ], [ 0, %18 ]
  %27 = add nuw nsw i64 %26, %13
  %28 = getelementptr inbounds float, ptr %17, i64 %27
  %29 = load float, ptr %28, align 4, !tbaa !6, !alias.scope !27, !noalias !32
  %30 = getelementptr inbounds float, ptr %24, i64 %27
  %31 = load float, ptr %30, align 4, !tbaa !6, !alias.scope !24, !noalias !33
  %32 = call float @llvm.fmuladd.f32(float %29, float %23, float %31)
  store float %32, ptr %30, align 4, !tbaa !6, !alias.scope !24, !noalias !33
  %33 = add nuw nsw i64 %26, 1
  %34 = icmp eq i64 %33, 64
  br i1 %34, label %35, label %25, !llvm.loop !10

35:                                               ; preds = %25
  %36 = add nuw nsw i64 %19, 1
  %37 = icmp eq i64 %36, 32
  br i1 %37, label %38, label %18, !llvm.loop !13

38:                                               ; preds = %35
  %39 = add nuw nsw i64 %15, 1
  %40 = icmp eq i64 %39, 128
  br i1 %40, label %41, label %14, !llvm.loop !14

41:                                               ; preds = %38
  br i1 %12, label %11, label %42, !llvm.loop !15

42:                                               ; preds = %41
  call void @llvm.experimental.noalias.scope.decl(metadata !34)
  call void @llvm.experimental.noalias.scope.decl(metadata !37)
  call void @llvm.experimental.noalias.scope.decl(metadata !39)
  br label %43

43:                                               ; preds = %51, %42
  %44 = phi i1 [ true, %42 ], [ false, %51 ]
  %45 = phi i64 [ 0, %42 ], [ 64, %51 ]
  br label %46

46:                                               ; preds = %52, %43
  %47 = phi i64 [ 0, %43 ], [ %53, %52 ]
  %48 = or disjoint i64 %47, %45
  %49 = getelementptr inbounds float, ptr %7, i64 %48
  %50 = getelementptr inbounds float, ptr %6, i64 %48
  br label %55

51:                                               ; preds = %52
  br i1 %44, label %43, label %75, !llvm.loop !16

52:                                               ; preds = %61
  %53 = add nuw nsw i64 %47, 1
  %54 = icmp eq i64 %53, 64
  br i1 %54, label %51, label %46, !llvm.loop !17

55:                                               ; preds = %61, %46
  %56 = phi i64 [ 0, %46 ], [ %62, %61 ]
  %57 = shl nsw i64 %56, 9
  %58 = getelementptr inbounds i8, ptr %49, i64 %57
  %59 = load float, ptr %58, align 4, !tbaa !6, !alias.scope !39, !noalias !41
  %60 = getelementptr inbounds float, ptr %8, i64 %56
  br label %64

61:                                               ; preds = %64
  %62 = add nuw nsw i64 %56, 1
  %63 = icmp eq i64 %62, 32
  br i1 %63, label %52, label %55, !llvm.loop !18

64:                                               ; preds = %64, %55
  %65 = phi i64 [ 0, %55 ], [ %73, %64 ]
  %66 = shl nsw i64 %65, 9
  %67 = getelementptr inbounds i8, ptr %50, i64 %66
  %68 = load float, ptr %67, align 4, !tbaa !6, !alias.scope !37, !noalias !42
  %69 = shl nsw i64 %65, 7
  %70 = getelementptr inbounds i8, ptr %60, i64 %69
  %71 = load float, ptr %70, align 4, !tbaa !6, !alias.scope !34, !noalias !43
  %72 = call float @llvm.fmuladd.f32(float %68, float %59, float %71)
  store float %72, ptr %70, align 4, !tbaa !6, !alias.scope !34, !noalias !43
  %73 = add nuw nsw i64 %65, 1
  %74 = icmp eq i64 %73, 32
  br i1 %74, label %61, label %64, !llvm.loop !19

75:                                               ; preds = %51
  call void @llvm.experimental.noalias.scope.decl(metadata !44)
  call void @llvm.experimental.noalias.scope.decl(metadata !47)
  call void @llvm.experimental.noalias.scope.decl(metadata !49)
  br label %76

76:                                               ; preds = %84, %75
  %77 = phi i1 [ true, %75 ], [ false, %84 ]
  %78 = phi i64 [ 0, %75 ], [ 64, %84 ]
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
  %87 = icmp eq i64 %86, 64
  br i1 %87, label %84, label %79, !llvm.loop !21

88:                                               ; preds = %94, %79
  %89 = phi i64 [ 0, %79 ], [ %95, %94 ]
  %90 = shl nsw i64 %89, 9
  %91 = getelementptr inbounds i8, ptr %82, i64 %90
  %92 = load float, ptr %91, align 4, !tbaa !6, !alias.scope !49, !noalias !51
  %93 = getelementptr inbounds float, ptr %8, i64 %89
  br label %97

94:                                               ; preds = %97
  %95 = add nuw nsw i64 %89, 1
  %96 = icmp eq i64 %95, 32
  br i1 %96, label %85, label %88, !llvm.loop !22

97:                                               ; preds = %97, %88
  %98 = phi i64 [ 0, %88 ], [ %106, %97 ]
  %99 = shl nsw i64 %98, 7
  %100 = getelementptr inbounds i8, ptr %93, i64 %99
  %101 = load float, ptr %100, align 4, !tbaa !6, !alias.scope !44, !noalias !52
  %102 = shl nsw i64 %98, 9
  %103 = getelementptr inbounds i8, ptr %83, i64 %102
  %104 = load float, ptr %103, align 4, !tbaa !6, !alias.scope !47, !noalias !53
  %105 = call float @llvm.fmuladd.f32(float %101, float %92, float %104)
  store float %105, ptr %103, align 4, !tbaa !6, !alias.scope !47, !noalias !53
  %106 = add nuw nsw i64 %98, 1
  %107 = icmp eq i64 %106, 32
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
!41 = !{!35, !38}
!42 = !{!35, !40}
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
!56 = !{!"long", !8, i64 0}
!57 = !{!55, !56, i64 8}
