; ModuleID = 'tiny_gpt/tinygpt_opt_16384.c'
source_filename = "tiny_gpt/tinygpt_opt_16384.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128-Fn32"
target triple = "arm64-apple-macosx15.0.0"

%struct.timespec = type { i64, i64 }

@.str = private unnamed_addr constant [10 x i8] c"Time: %f\0A\00", align 1
@.memset_pattern.6 = private unnamed_addr constant [4 x float] [float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00], align 16

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_0(ptr noalias nocapture noundef readonly %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %14
  %5 = phi i64 [ 0, %3 ], [ %15, %14 ]
  %6 = getelementptr inbounds float, ptr %1, i64 %5
  br label %8

7:                                                ; preds = %14
  ret void

8:                                                ; preds = %4, %17
  %9 = phi i64 [ 0, %4 ], [ %18, %17 ]
  %10 = shl nuw nsw i64 %9, 7
  %11 = or disjoint i64 %10, %5
  %12 = getelementptr inbounds float, ptr %2, i64 %11
  %13 = load float, ptr %12, align 4, !tbaa !6
  br label %20

14:                                               ; preds = %17
  %15 = add nuw nsw i64 %5, 1
  %16 = icmp eq i64 %15, 128
  br i1 %16, label %7, label %4, !llvm.loop !10

17:                                               ; preds = %20
  store float %29, ptr %12, align 4, !tbaa !6
  %18 = add nuw nsw i64 %9, 1
  %19 = icmp eq i64 %18, 32
  br i1 %19, label %14, label %8, !llvm.loop !13

20:                                               ; preds = %8, %20
  %21 = phi i64 [ 0, %8 ], [ %30, %20 ]
  %22 = phi float [ %13, %8 ], [ %29, %20 ]
  %23 = or disjoint i64 %21, %10
  %24 = getelementptr inbounds float, ptr %0, i64 %23
  %25 = load float, ptr %24, align 4, !tbaa !6
  %26 = shl nsw i64 %21, 9
  %27 = getelementptr inbounds i8, ptr %6, i64 %26
  %28 = load float, ptr %27, align 4, !tbaa !6
  %29 = tail call float @llvm.fmuladd.f32(float %25, float %28, float %22)
  %30 = add nuw nsw i64 %21, 1
  %31 = icmp eq i64 %30, 128
  br i1 %31, label %17, label %20, !llvm.loop !14
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

4:                                                ; preds = %3, %16
  %5 = phi i64 [ 0, %3 ], [ %17, %16 ]
  %6 = getelementptr inbounds float, ptr %2, i64 %5
  %7 = getelementptr inbounds float, ptr %1, i64 %5
  br label %9

8:                                                ; preds = %16
  ret void

9:                                                ; preds = %4, %19
  %10 = phi i64 [ 0, %4 ], [ %20, %19 ]
  %11 = shl nsw i64 %10, 9
  %12 = getelementptr inbounds i8, ptr %6, i64 %11
  %13 = load float, ptr %12, align 4, !tbaa !6
  %14 = shl nsw i64 %10, 7
  %15 = getelementptr inbounds i8, ptr %0, i64 %14
  br label %22

16:                                               ; preds = %19
  %17 = add nuw nsw i64 %5, 1
  %18 = icmp eq i64 %17, 128
  br i1 %18, label %8, label %4, !llvm.loop !15

19:                                               ; preds = %22
  %20 = add nuw nsw i64 %10, 1
  %21 = icmp eq i64 %20, 32
  br i1 %21, label %16, label %9, !llvm.loop !16

22:                                               ; preds = %9, %22
  %23 = phi i64 [ 0, %9 ], [ %30, %22 ]
  %24 = shl nsw i64 %23, 9
  %25 = getelementptr inbounds i8, ptr %7, i64 %24
  %26 = load float, ptr %25, align 4, !tbaa !6
  %27 = getelementptr inbounds float, ptr %15, i64 %23
  %28 = load float, ptr %27, align 4, !tbaa !6
  %29 = tail call float @llvm.fmuladd.f32(float %26, float %13, float %28)
  store float %29, ptr %27, align 4, !tbaa !6
  %30 = add nuw nsw i64 %23, 1
  %31 = icmp eq i64 %30, 32
  br i1 %31, label %19, label %22, !llvm.loop !17
}

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_2(ptr noalias nocapture noundef readonly %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %16
  %5 = phi i64 [ 0, %3 ], [ %17, %16 ]
  %6 = getelementptr inbounds float, ptr %2, i64 %5
  %7 = getelementptr inbounds float, ptr %0, i64 %5
  br label %9

8:                                                ; preds = %16
  ret void

9:                                                ; preds = %4, %19
  %10 = phi i64 [ 0, %4 ], [ %20, %19 ]
  %11 = shl nsw i64 %10, 9
  %12 = getelementptr inbounds i8, ptr %6, i64 %11
  %13 = load float, ptr %12, align 4, !tbaa !6
  %14 = shl nsw i64 %10, 7
  %15 = getelementptr inbounds i8, ptr %1, i64 %14
  br label %22

16:                                               ; preds = %19
  %17 = add nuw nsw i64 %5, 1
  %18 = icmp eq i64 %17, 128
  br i1 %18, label %8, label %4, !llvm.loop !18

19:                                               ; preds = %22
  store float %30, ptr %12, align 4, !tbaa !6
  %20 = add nuw nsw i64 %10, 1
  %21 = icmp eq i64 %20, 32
  br i1 %21, label %16, label %9, !llvm.loop !19

22:                                               ; preds = %9, %22
  %23 = phi i64 [ 0, %9 ], [ %31, %22 ]
  %24 = phi float [ %13, %9 ], [ %30, %22 ]
  %25 = shl nsw i64 %23, 9
  %26 = getelementptr inbounds i8, ptr %7, i64 %25
  %27 = load float, ptr %26, align 4, !tbaa !6
  %28 = getelementptr inbounds float, ptr %15, i64 %23
  %29 = load float, ptr %28, align 4, !tbaa !6
  %30 = tail call float @llvm.fmuladd.f32(float %27, float %29, float %24)
  %31 = add nuw nsw i64 %23, 1
  %32 = icmp eq i64 %31, 32
  br i1 %32, label %19, label %22, !llvm.loop !20
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
  call void @llvm.experimental.noalias.scope.decl(metadata !21)
  call void @llvm.experimental.noalias.scope.decl(metadata !24)
  call void @llvm.experimental.noalias.scope.decl(metadata !26)
  br label %11

11:                                               ; preds = %20, %0
  %12 = phi i64 [ 0, %0 ], [ %21, %20 ]
  %13 = getelementptr inbounds float, ptr %5, i64 %12
  br label %14

14:                                               ; preds = %23, %11
  %15 = phi i64 [ 0, %11 ], [ %24, %23 ]
  %16 = shl nuw nsw i64 %15, 7
  %17 = or disjoint i64 %16, %12
  %18 = getelementptr inbounds float, ptr %6, i64 %17
  %19 = load float, ptr %18, align 4, !tbaa !6, !alias.scope !26, !noalias !28
  br label %26

20:                                               ; preds = %23
  %21 = add nuw nsw i64 %12, 1
  %22 = icmp eq i64 %21, 128
  br i1 %22, label %38, label %11, !llvm.loop !10

23:                                               ; preds = %26
  store float %35, ptr %18, align 4, !tbaa !6, !alias.scope !26, !noalias !28
  %24 = add nuw nsw i64 %15, 1
  %25 = icmp eq i64 %24, 32
  br i1 %25, label %20, label %14, !llvm.loop !13

26:                                               ; preds = %26, %14
  %27 = phi i64 [ 0, %14 ], [ %36, %26 ]
  %28 = phi float [ %19, %14 ], [ %35, %26 ]
  %29 = or disjoint i64 %27, %16
  %30 = getelementptr inbounds float, ptr %4, i64 %29
  %31 = load float, ptr %30, align 4, !tbaa !6, !alias.scope !21, !noalias !29
  %32 = shl nsw i64 %27, 9
  %33 = getelementptr inbounds i8, ptr %13, i64 %32
  %34 = load float, ptr %33, align 4, !tbaa !6, !alias.scope !24, !noalias !30
  %35 = call float @llvm.fmuladd.f32(float %31, float %34, float %28)
  %36 = add nuw nsw i64 %27, 1
  %37 = icmp eq i64 %36, 128
  br i1 %37, label %23, label %26, !llvm.loop !14

38:                                               ; preds = %20
  call void @llvm.experimental.noalias.scope.decl(metadata !31)
  call void @llvm.experimental.noalias.scope.decl(metadata !34)
  call void @llvm.experimental.noalias.scope.decl(metadata !36)
  br label %39

39:                                               ; preds = %50, %38
  %40 = phi i64 [ 0, %38 ], [ %51, %50 ]
  %41 = getelementptr inbounds float, ptr %6, i64 %40
  %42 = getelementptr inbounds float, ptr %7, i64 %40
  br label %43

43:                                               ; preds = %53, %39
  %44 = phi i64 [ 0, %39 ], [ %54, %53 ]
  %45 = shl nsw i64 %44, 9
  %46 = getelementptr inbounds i8, ptr %41, i64 %45
  %47 = load float, ptr %46, align 4, !tbaa !6, !alias.scope !36, !noalias !38
  %48 = shl nsw i64 %44, 7
  %49 = getelementptr inbounds i8, ptr %8, i64 %48
  br label %56

50:                                               ; preds = %53
  %51 = add nuw nsw i64 %40, 1
  %52 = icmp eq i64 %51, 128
  br i1 %52, label %66, label %39, !llvm.loop !15

53:                                               ; preds = %56
  %54 = add nuw nsw i64 %44, 1
  %55 = icmp eq i64 %54, 32
  br i1 %55, label %50, label %43, !llvm.loop !16

56:                                               ; preds = %56, %43
  %57 = phi i64 [ 0, %43 ], [ %64, %56 ]
  %58 = shl nsw i64 %57, 9
  %59 = getelementptr inbounds i8, ptr %42, i64 %58
  %60 = load float, ptr %59, align 4, !tbaa !6, !alias.scope !34, !noalias !39
  %61 = getelementptr inbounds float, ptr %49, i64 %57
  %62 = load float, ptr %61, align 4, !tbaa !6, !alias.scope !31, !noalias !40
  %63 = call float @llvm.fmuladd.f32(float %60, float %47, float %62)
  store float %63, ptr %61, align 4, !tbaa !6, !alias.scope !31, !noalias !40
  %64 = add nuw nsw i64 %57, 1
  %65 = icmp eq i64 %64, 32
  br i1 %65, label %53, label %56, !llvm.loop !17

66:                                               ; preds = %50
  call void @llvm.experimental.noalias.scope.decl(metadata !41)
  call void @llvm.experimental.noalias.scope.decl(metadata !44)
  call void @llvm.experimental.noalias.scope.decl(metadata !46)
  br label %67

67:                                               ; preds = %78, %66
  %68 = phi i64 [ 0, %66 ], [ %79, %78 ]
  %69 = getelementptr inbounds float, ptr %10, i64 %68
  %70 = getelementptr inbounds float, ptr %9, i64 %68
  br label %71

71:                                               ; preds = %81, %67
  %72 = phi i64 [ 0, %67 ], [ %82, %81 ]
  %73 = shl nsw i64 %72, 9
  %74 = getelementptr inbounds i8, ptr %69, i64 %73
  %75 = load float, ptr %74, align 4, !tbaa !6, !alias.scope !46, !noalias !48
  %76 = shl nsw i64 %72, 7
  %77 = getelementptr inbounds i8, ptr %8, i64 %76
  br label %84

78:                                               ; preds = %81
  %79 = add nuw nsw i64 %68, 1
  %80 = icmp eq i64 %79, 128
  br i1 %80, label %95, label %67, !llvm.loop !18

81:                                               ; preds = %84
  store float %92, ptr %74, align 4, !tbaa !6, !alias.scope !46, !noalias !48
  %82 = add nuw nsw i64 %72, 1
  %83 = icmp eq i64 %82, 32
  br i1 %83, label %78, label %71, !llvm.loop !19

84:                                               ; preds = %84, %71
  %85 = phi i64 [ 0, %71 ], [ %93, %84 ]
  %86 = phi float [ %75, %71 ], [ %92, %84 ]
  %87 = shl nsw i64 %85, 9
  %88 = getelementptr inbounds i8, ptr %70, i64 %87
  %89 = load float, ptr %88, align 4, !tbaa !6, !alias.scope !41, !noalias !49
  %90 = getelementptr inbounds float, ptr %77, i64 %85
  %91 = load float, ptr %90, align 4, !tbaa !6, !alias.scope !44, !noalias !50
  %92 = call float @llvm.fmuladd.f32(float %89, float %91, float %86)
  %93 = add nuw nsw i64 %85, 1
  %94 = icmp eq i64 %93, 32
  br i1 %94, label %81, label %84, !llvm.loop !20

95:                                               ; preds = %78
  %96 = call i32 @clock_gettime(i32 noundef 6, ptr noundef nonnull %2) #9
  %97 = load i64, ptr %2, align 8, !tbaa !51
  %98 = load i64, ptr %1, align 8, !tbaa !51
  %99 = sub nsw i64 %97, %98
  %100 = sitofp i64 %99 to double
  %101 = getelementptr inbounds i8, ptr %2, i64 8
  %102 = load i64, ptr %101, align 8, !tbaa !54
  %103 = getelementptr inbounds i8, ptr %1, i64 8
  %104 = load i64, ptr %103, align 8, !tbaa !54
  %105 = sub nsw i64 %102, %104
  %106 = sitofp i64 %105 to double
  %107 = call double @llvm.fmuladd.f64(double %106, double 1.000000e-09, double %100)
  %108 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str, double noundef %107)
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
!39 = !{!32, !37}
!40 = !{!35, !37}
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
!53 = !{!"long", !8, i64 0}
!54 = !{!52, !53, i64 8}
