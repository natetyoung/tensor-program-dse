; ModuleID = 'small_gpt/smallgpt.c'
source_filename = "small_gpt/smallgpt.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128-Fn32"
target triple = "arm64-apple-macosx15.0.0"

%struct.timespec = type { i64, i64 }

@.str = private unnamed_addr constant [10 x i8] c"Time: %f\0A\00", align 1
@.str.1 = private unnamed_addr constant [10 x i8] c"Test: %f\0A\00", align 1
@.memset_pattern.7 = private unnamed_addr constant [4 x float] [float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00], align 16

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_0(ptr noalias nocapture noundef readonly %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef writeonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %13
  %5 = phi i64 [ 0, %3 ], [ %14, %13 ]
  %6 = shl nuw nsw i64 %5, 8
  %7 = getelementptr inbounds float, ptr %0, i64 %6
  %8 = getelementptr inbounds float, ptr %2, i64 %6
  br label %10

9:                                                ; preds = %13
  ret void

10:                                               ; preds = %4, %16
  %11 = phi i64 [ 0, %4 ], [ %18, %16 ]
  %12 = getelementptr inbounds float, ptr %1, i64 %11
  br label %20

13:                                               ; preds = %16
  %14 = add nuw nsw i64 %5, 1
  %15 = icmp eq i64 %14, 64
  br i1 %15, label %9, label %4, !llvm.loop !6

16:                                               ; preds = %20
  %17 = getelementptr inbounds float, ptr %8, i64 %11
  store float %28, ptr %17, align 4, !tbaa !9
  %18 = add nuw nsw i64 %11, 1
  %19 = icmp eq i64 %18, 256
  br i1 %19, label %13, label %10, !llvm.loop !13

20:                                               ; preds = %10, %20
  %21 = phi i64 [ 0, %10 ], [ %29, %20 ]
  %22 = phi float [ 0.000000e+00, %10 ], [ %28, %20 ]
  %23 = getelementptr inbounds float, ptr %7, i64 %21
  %24 = load float, ptr %23, align 4, !tbaa !9
  %25 = shl nsw i64 %21, 10
  %26 = getelementptr inbounds i8, ptr %12, i64 %25
  %27 = load float, ptr %26, align 4, !tbaa !9
  %28 = tail call float @llvm.fmuladd.f32(float %24, float %27, float %22)
  %29 = add nuw nsw i64 %21, 1
  %30 = icmp eq i64 %29, 256
  br i1 %30, label %16, label %20, !llvm.loop !14
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #1

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fmuladd.f32(float, float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #1

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_1(ptr noalias nocapture noundef readonly %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef writeonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %15
  %5 = phi i64 [ 0, %3 ], [ %16, %15 ]
  %6 = shl nsw i64 %5, 10
  %7 = getelementptr inbounds i8, ptr %0, i64 %6
  %8 = shl nsw i64 %5, 8
  %9 = getelementptr inbounds i8, ptr %2, i64 %8
  br label %11

10:                                               ; preds = %15
  ret void

11:                                               ; preds = %4, %18
  %12 = phi i64 [ 0, %4 ], [ %20, %18 ]
  %13 = shl nsw i64 %12, 10
  %14 = getelementptr inbounds i8, ptr %1, i64 %13
  br label %22

15:                                               ; preds = %18
  %16 = add nuw nsw i64 %5, 1
  %17 = icmp eq i64 %16, 64
  br i1 %17, label %10, label %4, !llvm.loop !15

18:                                               ; preds = %22
  %19 = getelementptr inbounds float, ptr %9, i64 %12
  store float %29, ptr %19, align 4, !tbaa !9
  %20 = add nuw nsw i64 %12, 1
  %21 = icmp eq i64 %20, 64
  br i1 %21, label %15, label %11, !llvm.loop !16

22:                                               ; preds = %11, %22
  %23 = phi i64 [ 0, %11 ], [ %30, %22 ]
  %24 = phi float [ 0.000000e+00, %11 ], [ %29, %22 ]
  %25 = getelementptr inbounds float, ptr %7, i64 %23
  %26 = load float, ptr %25, align 4, !tbaa !9
  %27 = getelementptr inbounds float, ptr %14, i64 %23
  %28 = load float, ptr %27, align 4, !tbaa !9
  %29 = tail call float @llvm.fmuladd.f32(float %26, float %28, float %24)
  %30 = add nuw nsw i64 %23, 1
  %31 = icmp eq i64 %30, 256
  br i1 %31, label %18, label %22, !llvm.loop !17
}

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_2(ptr noalias nocapture noundef readonly %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef writeonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %14
  %5 = phi i64 [ 0, %3 ], [ %15, %14 ]
  %6 = shl nsw i64 %5, 8
  %7 = getelementptr inbounds i8, ptr %0, i64 %6
  %8 = shl nsw i64 %5, 10
  %9 = getelementptr inbounds i8, ptr %2, i64 %8
  br label %11

10:                                               ; preds = %14
  ret void

11:                                               ; preds = %4, %17
  %12 = phi i64 [ 0, %4 ], [ %19, %17 ]
  %13 = getelementptr inbounds float, ptr %1, i64 %12
  br label %21

14:                                               ; preds = %17
  %15 = add nuw nsw i64 %5, 1
  %16 = icmp eq i64 %15, 64
  br i1 %16, label %10, label %4, !llvm.loop !18

17:                                               ; preds = %21
  %18 = getelementptr inbounds float, ptr %9, i64 %12
  store float %29, ptr %18, align 4, !tbaa !9
  %19 = add nuw nsw i64 %12, 1
  %20 = icmp eq i64 %19, 256
  br i1 %20, label %14, label %11, !llvm.loop !19

21:                                               ; preds = %11, %21
  %22 = phi i64 [ 0, %11 ], [ %30, %21 ]
  %23 = phi float [ 0.000000e+00, %11 ], [ %29, %21 ]
  %24 = getelementptr inbounds float, ptr %7, i64 %22
  %25 = load float, ptr %24, align 4, !tbaa !9
  %26 = shl nsw i64 %22, 10
  %27 = getelementptr inbounds i8, ptr %13, i64 %26
  %28 = load float, ptr %27, align 4, !tbaa !9
  %29 = tail call float @llvm.fmuladd.f32(float %25, float %28, float %23)
  %30 = add nuw nsw i64 %22, 1
  %31 = icmp eq i64 %30, 64
  br i1 %31, label %17, label %21, !llvm.loop !20
}

; Function Attrs: nounwind ssp uwtable(sync)
define noundef i32 @main() local_unnamed_addr #3 {
  %1 = alloca %struct.timespec, align 8
  %2 = alloca %struct.timespec, align 8
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %1) #9
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %2) #9
  %3 = call i32 @clock_gettime(i32 noundef 6, ptr noundef nonnull %1) #9
  %4 = call dereferenceable_or_null(65536) ptr @malloc(i64 noundef 65536) #10
  call void @memset_pattern16(ptr %4, ptr nonnull @.memset_pattern.7, i64 65536), !tbaa !9
  %5 = call dereferenceable_or_null(262144) ptr @malloc(i64 noundef 262144) #10
  call void @memset_pattern16(ptr %5, ptr nonnull @.memset_pattern.7, i64 262144), !tbaa !9
  %6 = call dereferenceable_or_null(65536) ptr @malloc(i64 noundef 65536) #10
  call void @memset_pattern16(ptr %6, ptr nonnull @.memset_pattern.7, i64 65536), !tbaa !9
  %7 = call dereferenceable_or_null(65536) ptr @malloc(i64 noundef 65536) #10
  call void @memset_pattern16(ptr %7, ptr nonnull @.memset_pattern.7, i64 65536), !tbaa !9
  %8 = call dereferenceable_or_null(16384) ptr @malloc(i64 noundef 16384) #10
  call void @memset_pattern16(ptr %8, ptr nonnull @.memset_pattern.7, i64 16384), !tbaa !9
  %9 = call dereferenceable_or_null(65536) ptr @malloc(i64 noundef 65536) #10
  call void @memset_pattern16(ptr %9, ptr nonnull @.memset_pattern.7, i64 65536), !tbaa !9
  %10 = call dereferenceable_or_null(65536) ptr @malloc(i64 noundef 65536) #10
  call void @memset_pattern16(ptr %10, ptr nonnull @.memset_pattern.7, i64 65536), !tbaa !9
  call void @llvm.experimental.noalias.scope.decl(metadata !21)
  call void @llvm.experimental.noalias.scope.decl(metadata !24)
  call void @llvm.experimental.noalias.scope.decl(metadata !26)
  br label %11

11:                                               ; preds = %19, %0
  %12 = phi i64 [ 0, %0 ], [ %20, %19 ]
  %13 = shl nuw nsw i64 %12, 8
  %14 = getelementptr inbounds float, ptr %4, i64 %13
  %15 = getelementptr inbounds float, ptr %6, i64 %13
  br label %16

16:                                               ; preds = %22, %11
  %17 = phi i64 [ 0, %11 ], [ %24, %22 ]
  %18 = getelementptr inbounds float, ptr %5, i64 %17
  br label %26

19:                                               ; preds = %22
  %20 = add nuw nsw i64 %12, 1
  %21 = icmp eq i64 %20, 64
  br i1 %21, label %37, label %11, !llvm.loop !6

22:                                               ; preds = %26
  %23 = getelementptr inbounds float, ptr %15, i64 %17
  store float %34, ptr %23, align 4, !tbaa !9, !alias.scope !26, !noalias !28
  %24 = add nuw nsw i64 %17, 1
  %25 = icmp eq i64 %24, 256
  br i1 %25, label %19, label %16, !llvm.loop !13

26:                                               ; preds = %26, %16
  %27 = phi i64 [ 0, %16 ], [ %35, %26 ]
  %28 = phi float [ 0.000000e+00, %16 ], [ %34, %26 ]
  %29 = getelementptr inbounds float, ptr %14, i64 %27
  %30 = load float, ptr %29, align 4, !tbaa !9, !alias.scope !21, !noalias !29
  %31 = shl nsw i64 %27, 10
  %32 = getelementptr inbounds i8, ptr %18, i64 %31
  %33 = load float, ptr %32, align 4, !tbaa !9, !alias.scope !24, !noalias !30
  %34 = call float @llvm.fmuladd.f32(float %30, float %33, float %28)
  %35 = add nuw nsw i64 %27, 1
  %36 = icmp eq i64 %35, 256
  br i1 %36, label %22, label %26, !llvm.loop !14

37:                                               ; preds = %19
  call void @llvm.experimental.noalias.scope.decl(metadata !31)
  call void @llvm.experimental.noalias.scope.decl(metadata !34)
  call void @llvm.experimental.noalias.scope.decl(metadata !36)
  br label %38

38:                                               ; preds = %48, %37
  %39 = phi i64 [ 0, %37 ], [ %49, %48 ]
  %40 = shl nsw i64 %39, 10
  %41 = getelementptr inbounds i8, ptr %6, i64 %40
  %42 = shl nsw i64 %39, 8
  %43 = getelementptr inbounds i8, ptr %8, i64 %42
  br label %44

44:                                               ; preds = %51, %38
  %45 = phi i64 [ 0, %38 ], [ %53, %51 ]
  %46 = shl nsw i64 %45, 10
  %47 = getelementptr inbounds i8, ptr %7, i64 %46
  br label %55

48:                                               ; preds = %51
  %49 = add nuw nsw i64 %39, 1
  %50 = icmp eq i64 %49, 64
  br i1 %50, label %65, label %38, !llvm.loop !15

51:                                               ; preds = %55
  %52 = getelementptr inbounds float, ptr %43, i64 %45
  store float %62, ptr %52, align 4, !tbaa !9, !alias.scope !36, !noalias !38
  %53 = add nuw nsw i64 %45, 1
  %54 = icmp eq i64 %53, 64
  br i1 %54, label %48, label %44, !llvm.loop !16

55:                                               ; preds = %55, %44
  %56 = phi i64 [ 0, %44 ], [ %63, %55 ]
  %57 = phi float [ 0.000000e+00, %44 ], [ %62, %55 ]
  %58 = getelementptr inbounds float, ptr %41, i64 %56
  %59 = load float, ptr %58, align 4, !tbaa !9, !alias.scope !31, !noalias !39
  %60 = getelementptr inbounds float, ptr %47, i64 %56
  %61 = load float, ptr %60, align 4, !tbaa !9, !alias.scope !34, !noalias !40
  %62 = call float @llvm.fmuladd.f32(float %59, float %61, float %57)
  %63 = add nuw nsw i64 %56, 1
  %64 = icmp eq i64 %63, 256
  br i1 %64, label %51, label %55, !llvm.loop !17

65:                                               ; preds = %48
  call void @llvm.experimental.noalias.scope.decl(metadata !41)
  call void @llvm.experimental.noalias.scope.decl(metadata !44)
  call void @llvm.experimental.noalias.scope.decl(metadata !46)
  br label %66

66:                                               ; preds = %75, %65
  %67 = phi i64 [ 0, %65 ], [ %76, %75 ]
  %68 = shl nsw i64 %67, 8
  %69 = getelementptr inbounds i8, ptr %8, i64 %68
  %70 = shl nsw i64 %67, 10
  %71 = getelementptr inbounds i8, ptr %10, i64 %70
  br label %72

72:                                               ; preds = %78, %66
  %73 = phi i64 [ 0, %66 ], [ %80, %78 ]
  %74 = getelementptr inbounds float, ptr %9, i64 %73
  br label %82

75:                                               ; preds = %78
  %76 = add nuw nsw i64 %67, 1
  %77 = icmp eq i64 %76, 64
  br i1 %77, label %93, label %66, !llvm.loop !18

78:                                               ; preds = %82
  %79 = getelementptr inbounds float, ptr %71, i64 %73
  store float %90, ptr %79, align 4, !tbaa !9, !alias.scope !46, !noalias !48
  %80 = add nuw nsw i64 %73, 1
  %81 = icmp eq i64 %80, 256
  br i1 %81, label %75, label %72, !llvm.loop !19

82:                                               ; preds = %82, %72
  %83 = phi i64 [ 0, %72 ], [ %91, %82 ]
  %84 = phi float [ 0.000000e+00, %72 ], [ %90, %82 ]
  %85 = getelementptr inbounds float, ptr %69, i64 %83
  %86 = load float, ptr %85, align 4, !tbaa !9, !alias.scope !41, !noalias !49
  %87 = shl nsw i64 %83, 10
  %88 = getelementptr inbounds i8, ptr %74, i64 %87
  %89 = load float, ptr %88, align 4, !tbaa !9, !alias.scope !44, !noalias !50
  %90 = call float @llvm.fmuladd.f32(float %86, float %89, float %84)
  %91 = add nuw nsw i64 %83, 1
  %92 = icmp eq i64 %91, 64
  br i1 %92, label %78, label %82, !llvm.loop !20

93:                                               ; preds = %75
  %94 = call i32 @clock_gettime(i32 noundef 6, ptr noundef nonnull %2) #9
  %95 = load i64, ptr %2, align 8, !tbaa !51
  %96 = load i64, ptr %1, align 8, !tbaa !51
  %97 = sub nsw i64 %95, %96
  %98 = sitofp i64 %97 to double
  %99 = getelementptr inbounds i8, ptr %2, i64 8
  %100 = load i64, ptr %99, align 8, !tbaa !54
  %101 = getelementptr inbounds i8, ptr %1, i64 8
  %102 = load i64, ptr %101, align 8, !tbaa !54
  %103 = sub nsw i64 %100, %102
  %104 = sitofp i64 %103 to double
  %105 = call double @llvm.fmuladd.f64(double %104, double 1.000000e-09, double %98)
  %106 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str, double noundef %105)
  %107 = load float, ptr %10, align 4, !tbaa !9
  %108 = fpext float %107 to double
  %109 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str.1, double noundef %108)
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
!21 = !{!22}
!22 = distinct !{!22, !23, !"einsum_0: argument 0"}
!23 = distinct !{!23, !"einsum_0"}
!24 = !{!25}
!25 = distinct !{!25, !23, !"einsum_0: argument 1"}
!26 = !{!27}
!27 = distinct !{!27, !23, !"einsum_0: argument 2"}
!28 = !{!22, !25}
!29 = !{!25, !27}
!30 = !{!22, !27}
!31 = !{!32}
!32 = distinct !{!32, !33, !"einsum_1: argument 0"}
!33 = distinct !{!33, !"einsum_1"}
!34 = !{!35}
!35 = distinct !{!35, !33, !"einsum_1: argument 1"}
!36 = !{!37}
!37 = distinct !{!37, !33, !"einsum_1: argument 2"}
!38 = !{!32, !35}
!39 = !{!35, !37}
!40 = !{!32, !37}
!41 = !{!42}
!42 = distinct !{!42, !43, !"einsum_2: argument 0"}
!43 = distinct !{!43, !"einsum_2"}
!44 = !{!45}
!45 = distinct !{!45, !43, !"einsum_2: argument 1"}
!46 = !{!47}
!47 = distinct !{!47, !43, !"einsum_2: argument 2"}
!48 = !{!42, !45}
!49 = !{!45, !47}
!50 = !{!42, !47}
!51 = !{!52, !53, i64 0}
!52 = !{!"timespec", !53, i64 0, !53, i64 8}
!53 = !{!"long", !11, i64 0}
!54 = !{!52, !53, i64 8}
