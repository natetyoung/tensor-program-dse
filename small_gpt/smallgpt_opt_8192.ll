; ModuleID = 'small_gpt/smallgpt_opt_8192.c'
source_filename = "small_gpt/smallgpt_opt_8192.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128-Fn32"
target triple = "arm64-apple-macosx15.0.0"

%struct.timespec = type { i64, i64 }

@.str = private unnamed_addr constant [10 x i8] c"Time: %f\0A\00", align 1
@.memset_pattern.6 = private unnamed_addr constant [4 x float] [float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00], align 16

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_0(ptr noalias nocapture noundef %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef readonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %38
  %5 = phi i64 [ 0, %3 ], [ %39, %38 ]
  %6 = icmp ult i64 %5, 206
  %7 = sub nsw i64 256, %5
  %8 = and i64 %7, 4294967295
  %9 = select i1 %6, i64 51, i64 %8
  br label %10

10:                                               ; preds = %4, %34
  %11 = phi i64 [ 0, %4 ], [ %35, %34 ]
  %12 = shl nsw i64 %11, 10
  %13 = getelementptr inbounds i8, ptr %1, i64 %12
  br label %14

14:                                               ; preds = %31, %10
  %15 = phi i64 [ %32, %31 ], [ 0, %10 ]
  %16 = shl nuw nsw i64 %15, 8
  %17 = or disjoint i64 %16, %11
  %18 = getelementptr inbounds float, ptr %2, i64 %17
  %19 = load float, ptr %18, align 4, !tbaa !6
  %20 = getelementptr inbounds float, ptr %0, i64 %16
  br label %21

21:                                               ; preds = %21, %14
  %22 = phi i64 [ %29, %21 ], [ 0, %14 ]
  %23 = add nuw nsw i64 %22, %5
  %24 = getelementptr inbounds float, ptr %13, i64 %23
  %25 = load float, ptr %24, align 4, !tbaa !6
  %26 = getelementptr inbounds float, ptr %20, i64 %23
  %27 = load float, ptr %26, align 4, !tbaa !6
  %28 = tail call float @llvm.fmuladd.f32(float %25, float %19, float %27)
  store float %28, ptr %26, align 4, !tbaa !6
  %29 = add nuw nsw i64 %22, 1
  %30 = icmp eq i64 %29, %9
  br i1 %30, label %31, label %21, !llvm.loop !10

31:                                               ; preds = %21
  %32 = add nuw nsw i64 %15, 1
  %33 = icmp eq i64 %32, 64
  br i1 %33, label %34, label %14, !llvm.loop !13

34:                                               ; preds = %31
  %35 = add nuw nsw i64 %11, 1
  %36 = icmp eq i64 %35, 256
  br i1 %36, label %38, label %10, !llvm.loop !14

37:                                               ; preds = %38
  ret void

38:                                               ; preds = %34
  %39 = add nuw nsw i64 %5, 51
  %40 = icmp ult i64 %5, 205
  br i1 %40, label %4, label %37, !llvm.loop !15
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

4:                                                ; preds = %3, %12
  %5 = phi i64 [ 0, %3 ], [ %13, %12 ]
  br label %7

6:                                                ; preds = %12
  ret void

7:                                                ; preds = %4, %15
  %8 = phi i64 [ 0, %4 ], [ %16, %15 ]
  %9 = shl nsw i64 %8, 10
  %10 = getelementptr inbounds i8, ptr %2, i64 %9
  %11 = getelementptr inbounds float, ptr %0, i64 %8
  br label %18

12:                                               ; preds = %15
  %13 = add nuw nsw i64 %5, 51
  %14 = icmp ult i64 %5, 205
  br i1 %14, label %4, label %6, !llvm.loop !16

15:                                               ; preds = %24
  %16 = add nuw nsw i64 %8, 1
  %17 = icmp eq i64 %16, 64
  br i1 %17, label %12, label %7, !llvm.loop !17

18:                                               ; preds = %7, %24
  %19 = phi i64 [ 0, %7 ], [ %25, %24 ]
  %20 = add nuw nsw i64 %19, %5
  %21 = getelementptr inbounds float, ptr %10, i64 %20
  %22 = load float, ptr %21, align 4, !tbaa !6
  %23 = getelementptr inbounds float, ptr %1, i64 %20
  br label %27

24:                                               ; preds = %27
  %25 = add nuw nsw i64 %19, 1
  %26 = icmp eq i64 %25, 51
  br i1 %26, label %15, label %18, !llvm.loop !18

27:                                               ; preds = %18, %27
  %28 = phi i64 [ 0, %18 ], [ %36, %27 ]
  %29 = shl nsw i64 %28, 10
  %30 = getelementptr inbounds i8, ptr %23, i64 %29
  %31 = load float, ptr %30, align 4, !tbaa !6
  %32 = shl nsw i64 %28, 8
  %33 = getelementptr inbounds i8, ptr %11, i64 %32
  %34 = load float, ptr %33, align 4, !tbaa !6
  %35 = tail call float @llvm.fmuladd.f32(float %31, float %22, float %34)
  store float %35, ptr %33, align 4, !tbaa !6
  %36 = add nuw nsw i64 %28, 1
  %37 = icmp eq i64 %36, 64
  br i1 %37, label %24, label %27, !llvm.loop !19
}

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_2(ptr noalias nocapture noundef readonly %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef %2) local_unnamed_addr #0 {
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
  %11 = shl nsw i64 %10, 10
  %12 = getelementptr inbounds i8, ptr %6, i64 %11
  %13 = load float, ptr %12, align 4, !tbaa !6
  %14 = shl nsw i64 %10, 8
  %15 = getelementptr inbounds i8, ptr %0, i64 %14
  br label %22

16:                                               ; preds = %19
  %17 = add nuw nsw i64 %5, 1
  %18 = icmp eq i64 %17, 256
  br i1 %18, label %8, label %4, !llvm.loop !20

19:                                               ; preds = %22
  store float %30, ptr %12, align 4, !tbaa !6
  %20 = add nuw nsw i64 %10, 1
  %21 = icmp eq i64 %20, 64
  br i1 %21, label %16, label %9, !llvm.loop !21

22:                                               ; preds = %9, %22
  %23 = phi i64 [ 0, %9 ], [ %31, %22 ]
  %24 = phi float [ %13, %9 ], [ %30, %22 ]
  %25 = getelementptr inbounds float, ptr %15, i64 %23
  %26 = load float, ptr %25, align 4, !tbaa !6
  %27 = shl nsw i64 %23, 10
  %28 = getelementptr inbounds i8, ptr %7, i64 %27
  %29 = load float, ptr %28, align 4, !tbaa !6
  %30 = tail call float @llvm.fmuladd.f32(float %26, float %29, float %24)
  %31 = add nuw nsw i64 %23, 1
  %32 = icmp eq i64 %31, 64
  br i1 %32, label %19, label %22, !llvm.loop !22
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
  call void @llvm.experimental.noalias.scope.decl(metadata !23)
  call void @llvm.experimental.noalias.scope.decl(metadata !26)
  call void @llvm.experimental.noalias.scope.decl(metadata !28)
  br label %11

11:                                               ; preds = %43, %0
  %12 = phi i64 [ 0, %0 ], [ %44, %43 ]
  %13 = icmp ult i64 %12, 206
  %14 = sub nuw nsw i64 256, %12
  %15 = select i1 %13, i64 51, i64 %14
  br label %16

16:                                               ; preds = %40, %11
  %17 = phi i64 [ 0, %11 ], [ %41, %40 ]
  %18 = shl nsw i64 %17, 10
  %19 = getelementptr inbounds i8, ptr %5, i64 %18
  br label %20

20:                                               ; preds = %37, %16
  %21 = phi i64 [ %38, %37 ], [ 0, %16 ]
  %22 = shl nuw nsw i64 %21, 8
  %23 = or disjoint i64 %22, %17
  %24 = getelementptr inbounds float, ptr %4, i64 %23
  %25 = load float, ptr %24, align 4, !tbaa !6, !alias.scope !28, !noalias !30
  %26 = getelementptr inbounds float, ptr %6, i64 %22
  br label %27

27:                                               ; preds = %27, %20
  %28 = phi i64 [ %35, %27 ], [ 0, %20 ]
  %29 = add nuw nsw i64 %28, %12
  %30 = getelementptr inbounds float, ptr %19, i64 %29
  %31 = load float, ptr %30, align 4, !tbaa !6, !alias.scope !26, !noalias !31
  %32 = getelementptr inbounds float, ptr %26, i64 %29
  %33 = load float, ptr %32, align 4, !tbaa !6, !alias.scope !23, !noalias !32
  %34 = call float @llvm.fmuladd.f32(float %31, float %25, float %33)
  store float %34, ptr %32, align 4, !tbaa !6, !alias.scope !23, !noalias !32
  %35 = add nuw nsw i64 %28, 1
  %36 = icmp eq i64 %35, %15
  br i1 %36, label %37, label %27, !llvm.loop !10

37:                                               ; preds = %27
  %38 = add nuw nsw i64 %21, 1
  %39 = icmp eq i64 %38, 64
  br i1 %39, label %40, label %20, !llvm.loop !13

40:                                               ; preds = %37
  %41 = add nuw nsw i64 %17, 1
  %42 = icmp eq i64 %41, 256
  br i1 %42, label %43, label %16, !llvm.loop !14

43:                                               ; preds = %40
  %44 = add nuw nsw i64 %12, 51
  %45 = icmp ult i64 %12, 205
  br i1 %45, label %11, label %46, !llvm.loop !15

46:                                               ; preds = %43
  call void @llvm.experimental.noalias.scope.decl(metadata !33)
  call void @llvm.experimental.noalias.scope.decl(metadata !36)
  call void @llvm.experimental.noalias.scope.decl(metadata !38)
  br label %47

47:                                               ; preds = %54, %46
  %48 = phi i64 [ 0, %46 ], [ %55, %54 ]
  br label %49

49:                                               ; preds = %57, %47
  %50 = phi i64 [ 0, %47 ], [ %58, %57 ]
  %51 = shl nsw i64 %50, 10
  %52 = getelementptr inbounds i8, ptr %7, i64 %51
  %53 = getelementptr inbounds float, ptr %8, i64 %50
  br label %60

54:                                               ; preds = %57
  %55 = add nuw nsw i64 %48, 51
  %56 = icmp ult i64 %48, 205
  br i1 %56, label %47, label %80, !llvm.loop !16

57:                                               ; preds = %66
  %58 = add nuw nsw i64 %50, 1
  %59 = icmp eq i64 %58, 64
  br i1 %59, label %54, label %49, !llvm.loop !17

60:                                               ; preds = %66, %49
  %61 = phi i64 [ 0, %49 ], [ %67, %66 ]
  %62 = add nuw nsw i64 %61, %48
  %63 = getelementptr inbounds float, ptr %52, i64 %62
  %64 = load float, ptr %63, align 4, !tbaa !6, !alias.scope !38, !noalias !40
  %65 = getelementptr inbounds float, ptr %6, i64 %62
  br label %69

66:                                               ; preds = %69
  %67 = add nuw nsw i64 %61, 1
  %68 = icmp eq i64 %67, 51
  br i1 %68, label %57, label %60, !llvm.loop !18

69:                                               ; preds = %69, %60
  %70 = phi i64 [ 0, %60 ], [ %78, %69 ]
  %71 = shl nsw i64 %70, 10
  %72 = getelementptr inbounds i8, ptr %65, i64 %71
  %73 = load float, ptr %72, align 4, !tbaa !6, !alias.scope !36, !noalias !41
  %74 = shl nsw i64 %70, 8
  %75 = getelementptr inbounds i8, ptr %53, i64 %74
  %76 = load float, ptr %75, align 4, !tbaa !6, !alias.scope !33, !noalias !42
  %77 = call float @llvm.fmuladd.f32(float %73, float %64, float %76)
  store float %77, ptr %75, align 4, !tbaa !6, !alias.scope !33, !noalias !42
  %78 = add nuw nsw i64 %70, 1
  %79 = icmp eq i64 %78, 64
  br i1 %79, label %66, label %69, !llvm.loop !19

80:                                               ; preds = %54
  call void @llvm.experimental.noalias.scope.decl(metadata !43)
  call void @llvm.experimental.noalias.scope.decl(metadata !46)
  call void @llvm.experimental.noalias.scope.decl(metadata !48)
  br label %81

81:                                               ; preds = %92, %80
  %82 = phi i64 [ 0, %80 ], [ %93, %92 ]
  %83 = getelementptr inbounds float, ptr %10, i64 %82
  %84 = getelementptr inbounds float, ptr %9, i64 %82
  br label %85

85:                                               ; preds = %95, %81
  %86 = phi i64 [ 0, %81 ], [ %96, %95 ]
  %87 = shl nsw i64 %86, 10
  %88 = getelementptr inbounds i8, ptr %83, i64 %87
  %89 = load float, ptr %88, align 4, !tbaa !6, !alias.scope !48, !noalias !50
  %90 = shl nsw i64 %86, 8
  %91 = getelementptr inbounds i8, ptr %8, i64 %90
  br label %98

92:                                               ; preds = %95
  %93 = add nuw nsw i64 %82, 1
  %94 = icmp eq i64 %93, 256
  br i1 %94, label %109, label %81, !llvm.loop !20

95:                                               ; preds = %98
  store float %106, ptr %88, align 4, !tbaa !6, !alias.scope !48, !noalias !50
  %96 = add nuw nsw i64 %86, 1
  %97 = icmp eq i64 %96, 64
  br i1 %97, label %92, label %85, !llvm.loop !21

98:                                               ; preds = %98, %85
  %99 = phi i64 [ 0, %85 ], [ %107, %98 ]
  %100 = phi float [ %89, %85 ], [ %106, %98 ]
  %101 = getelementptr inbounds float, ptr %91, i64 %99
  %102 = load float, ptr %101, align 4, !tbaa !6, !alias.scope !43, !noalias !51
  %103 = shl nsw i64 %99, 10
  %104 = getelementptr inbounds i8, ptr %84, i64 %103
  %105 = load float, ptr %104, align 4, !tbaa !6, !alias.scope !46, !noalias !52
  %106 = call float @llvm.fmuladd.f32(float %102, float %105, float %100)
  %107 = add nuw nsw i64 %99, 1
  %108 = icmp eq i64 %107, 64
  br i1 %108, label %95, label %98, !llvm.loop !22

109:                                              ; preds = %92
  %110 = call i32 @clock_gettime(i32 noundef 6, ptr noundef nonnull %2) #9
  %111 = load i64, ptr %2, align 8, !tbaa !53
  %112 = load i64, ptr %1, align 8, !tbaa !53
  %113 = sub nsw i64 %111, %112
  %114 = sitofp i64 %113 to double
  %115 = getelementptr inbounds i8, ptr %2, i64 8
  %116 = load i64, ptr %115, align 8, !tbaa !56
  %117 = getelementptr inbounds i8, ptr %1, i64 8
  %118 = load i64, ptr %117, align 8, !tbaa !56
  %119 = sub nsw i64 %116, %118
  %120 = sitofp i64 %119 to double
  %121 = call double @llvm.fmuladd.f64(double %120, double 1.000000e-09, double %114)
  %122 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str, double noundef %121)
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
!23 = !{!24}
!24 = distinct !{!24, !25, !"einsum_0: argument 0"}
!25 = distinct !{!25, !"einsum_0"}
!26 = !{!27}
!27 = distinct !{!27, !25, !"einsum_0: argument 1"}
!28 = !{!29}
!29 = distinct !{!29, !25, !"einsum_0: argument 2"}
!30 = !{!24, !27}
!31 = !{!24, !29}
!32 = !{!27, !29}
!33 = !{!34}
!34 = distinct !{!34, !35, !"einsum_1: argument 0"}
!35 = distinct !{!35, !"einsum_1"}
!36 = !{!37}
!37 = distinct !{!37, !35, !"einsum_1: argument 1"}
!38 = !{!39}
!39 = distinct !{!39, !35, !"einsum_1: argument 2"}
!40 = !{!34, !37}
!41 = !{!34, !39}
!42 = !{!37, !39}
!43 = !{!44}
!44 = distinct !{!44, !45, !"einsum_2: argument 0"}
!45 = distinct !{!45, !"einsum_2"}
!46 = !{!47}
!47 = distinct !{!47, !45, !"einsum_2: argument 1"}
!48 = !{!49}
!49 = distinct !{!49, !45, !"einsum_2: argument 2"}
!50 = !{!44, !47}
!51 = !{!47, !49}
!52 = !{!44, !49}
!53 = !{!54, !55, i64 0}
!54 = !{!"timespec", !55, i64 0, !55, i64 8}
!55 = !{!"long", !8, i64 0}
!56 = !{!54, !55, i64 8}
