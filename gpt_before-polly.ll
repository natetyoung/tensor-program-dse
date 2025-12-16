; ModuleID = '../../gpt.c'
source_filename = "../../gpt.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128"
target triple = "arm64-apple-macosx15.5.0"

%struct.timespec = type { i64, i64 }

@.str = private unnamed_addr constant [10 x i8] c"Time: %f\0A\00", align 1
@.memset_pattern.7 = private unnamed_addr constant [4 x float] [float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00], align 16

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_0(ptr noalias nocapture noundef readonly %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef writeonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %13
  %5 = phi i64 [ 0, %3 ], [ %14, %13 ]
  %6 = shl nuw nsw i64 %5, 12
  %7 = getelementptr float, ptr %0, i64 %6
  %8 = getelementptr float, ptr %2, i64 %6
  br label %10

9:                                                ; preds = %13
  ret void

10:                                               ; preds = %4, %16
  %11 = phi i64 [ 0, %4 ], [ %18, %16 ]
  %12 = getelementptr float, ptr %1, i64 %11
  br label %20

13:                                               ; preds = %16
  %14 = add nuw nsw i64 %5, 1
  %15 = icmp eq i64 %14, 2048
  br i1 %15, label %9, label %4, !llvm.loop !6

16:                                               ; preds = %20
  %17 = getelementptr float, ptr %8, i64 %11
  store float %28, ptr %17, align 4, !tbaa !8
  %18 = add nuw nsw i64 %11, 1
  %19 = icmp eq i64 %18, 4096
  br i1 %19, label %13, label %10, !llvm.loop !12

20:                                               ; preds = %10, %20
  %21 = phi i64 [ 0, %10 ], [ %29, %20 ]
  %22 = phi float [ 0.000000e+00, %10 ], [ %28, %20 ]
  %23 = getelementptr float, ptr %7, i64 %21
  %24 = load float, ptr %23, align 4, !tbaa !8
  %25 = shl nuw nsw i64 %21, 12
  %26 = getelementptr float, ptr %12, i64 %25
  %27 = load float, ptr %26, align 4, !tbaa !8
  %28 = tail call float @llvm.fmuladd.f32(float %24, float %27, float %22)
  %29 = add nuw nsw i64 %21, 1
  %30 = icmp eq i64 %29, 4096
  br i1 %30, label %16, label %20, !llvm.loop !13
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

4:                                                ; preds = %3, %13
  %5 = phi i64 [ 0, %3 ], [ %14, %13 ]
  %6 = shl nuw nsw i64 %5, 12
  %7 = getelementptr float, ptr %0, i64 %6
  %8 = getelementptr float, ptr %2, i64 %6
  br label %10

9:                                                ; preds = %13
  ret void

10:                                               ; preds = %4, %16
  %11 = phi i64 [ 0, %4 ], [ %18, %16 ]
  %12 = getelementptr float, ptr %1, i64 %11
  br label %20

13:                                               ; preds = %16
  %14 = add nuw nsw i64 %5, 1
  %15 = icmp eq i64 %14, 2048
  br i1 %15, label %9, label %4, !llvm.loop !14

16:                                               ; preds = %20
  %17 = getelementptr float, ptr %8, i64 %11
  store float %28, ptr %17, align 4, !tbaa !8
  %18 = add nuw nsw i64 %11, 1
  %19 = icmp eq i64 %18, 4096
  br i1 %19, label %13, label %10, !llvm.loop !15

20:                                               ; preds = %10, %20
  %21 = phi i64 [ 0, %10 ], [ %29, %20 ]
  %22 = phi float [ 0.000000e+00, %10 ], [ %28, %20 ]
  %23 = getelementptr float, ptr %7, i64 %21
  %24 = load float, ptr %23, align 4, !tbaa !8
  %25 = shl nuw nsw i64 %21, 12
  %26 = getelementptr float, ptr %12, i64 %25
  %27 = load float, ptr %26, align 4, !tbaa !8
  %28 = tail call float @llvm.fmuladd.f32(float %24, float %27, float %22)
  %29 = add nuw nsw i64 %21, 1
  %30 = icmp eq i64 %29, 4096
  br i1 %30, label %16, label %20, !llvm.loop !16
}

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_2(ptr noalias nocapture noundef readonly %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef writeonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %13
  %5 = phi i64 [ 0, %3 ], [ %14, %13 ]
  %6 = shl nuw nsw i64 %5, 12
  %7 = getelementptr float, ptr %0, i64 %6
  %8 = getelementptr float, ptr %2, i64 %6
  br label %10

9:                                                ; preds = %13
  ret void

10:                                               ; preds = %4, %16
  %11 = phi i64 [ 0, %4 ], [ %18, %16 ]
  %12 = getelementptr float, ptr %1, i64 %11
  br label %20

13:                                               ; preds = %16
  %14 = add nuw nsw i64 %5, 1
  %15 = icmp eq i64 %14, 2048
  br i1 %15, label %9, label %4, !llvm.loop !17

16:                                               ; preds = %20
  %17 = getelementptr float, ptr %8, i64 %11
  store float %28, ptr %17, align 4, !tbaa !8
  %18 = add nuw nsw i64 %11, 1
  %19 = icmp eq i64 %18, 4096
  br i1 %19, label %13, label %10, !llvm.loop !18

20:                                               ; preds = %10, %20
  %21 = phi i64 [ 0, %10 ], [ %29, %20 ]
  %22 = phi float [ 0.000000e+00, %10 ], [ %28, %20 ]
  %23 = getelementptr float, ptr %7, i64 %21
  %24 = load float, ptr %23, align 4, !tbaa !8
  %25 = shl nuw nsw i64 %21, 12
  %26 = getelementptr float, ptr %12, i64 %25
  %27 = load float, ptr %26, align 4, !tbaa !8
  %28 = tail call float @llvm.fmuladd.f32(float %24, float %27, float %22)
  %29 = add nuw nsw i64 %21, 1
  %30 = icmp eq i64 %29, 4096
  br i1 %30, label %16, label %20, !llvm.loop !19
}

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_3(ptr noalias nocapture noundef readonly %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef writeonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %15
  %5 = phi i64 [ 0, %3 ], [ %16, %15 ]
  %6 = shl nuw nsw i64 %5, 12
  %7 = shl nuw nsw i64 %5, 11
  %8 = getelementptr float, ptr %0, i64 %6
  %9 = getelementptr float, ptr %2, i64 %7
  br label %11

10:                                               ; preds = %15
  ret void

11:                                               ; preds = %4, %18
  %12 = phi i64 [ 0, %4 ], [ %20, %18 ]
  %13 = shl nuw nsw i64 %12, 12
  %14 = getelementptr float, ptr %1, i64 %13
  br label %22

15:                                               ; preds = %18
  %16 = add nuw nsw i64 %5, 1
  %17 = icmp eq i64 %16, 2048
  br i1 %17, label %10, label %4, !llvm.loop !20

18:                                               ; preds = %22
  %19 = getelementptr float, ptr %9, i64 %12
  store float %29, ptr %19, align 4, !tbaa !8
  %20 = add nuw nsw i64 %12, 1
  %21 = icmp eq i64 %20, 2048
  br i1 %21, label %15, label %11, !llvm.loop !21

22:                                               ; preds = %11, %22
  %23 = phi i64 [ 0, %11 ], [ %30, %22 ]
  %24 = phi float [ 0.000000e+00, %11 ], [ %29, %22 ]
  %25 = getelementptr float, ptr %8, i64 %23
  %26 = load float, ptr %25, align 4, !tbaa !8
  %27 = getelementptr float, ptr %14, i64 %23
  %28 = load float, ptr %27, align 4, !tbaa !8
  %29 = tail call float @llvm.fmuladd.f32(float %26, float %28, float %24)
  %30 = add nuw nsw i64 %23, 1
  %31 = icmp eq i64 %30, 4096
  br i1 %31, label %18, label %22, !llvm.loop !22
}

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_4(ptr noalias nocapture noundef readonly %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef writeonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %14
  %5 = phi i64 [ 0, %3 ], [ %15, %14 ]
  %6 = shl nuw nsw i64 %5, 11
  %7 = shl nuw nsw i64 %5, 12
  %8 = getelementptr float, ptr %0, i64 %6
  %9 = getelementptr float, ptr %2, i64 %7
  br label %11

10:                                               ; preds = %14
  ret void

11:                                               ; preds = %4, %17
  %12 = phi i64 [ 0, %4 ], [ %19, %17 ]
  %13 = getelementptr float, ptr %1, i64 %12
  br label %21

14:                                               ; preds = %17
  %15 = add nuw nsw i64 %5, 1
  %16 = icmp eq i64 %15, 2048
  br i1 %16, label %10, label %4, !llvm.loop !23

17:                                               ; preds = %21
  %18 = getelementptr float, ptr %9, i64 %12
  store float %29, ptr %18, align 4, !tbaa !8
  %19 = add nuw nsw i64 %12, 1
  %20 = icmp eq i64 %19, 4096
  br i1 %20, label %14, label %11, !llvm.loop !24

21:                                               ; preds = %11, %21
  %22 = phi i64 [ 0, %11 ], [ %30, %21 ]
  %23 = phi float [ 0.000000e+00, %11 ], [ %29, %21 ]
  %24 = getelementptr float, ptr %8, i64 %22
  %25 = load float, ptr %24, align 4, !tbaa !8
  %26 = shl nuw nsw i64 %22, 12
  %27 = getelementptr float, ptr %13, i64 %26
  %28 = load float, ptr %27, align 4, !tbaa !8
  %29 = tail call float @llvm.fmuladd.f32(float %25, float %28, float %23)
  %30 = add nuw nsw i64 %22, 1
  %31 = icmp eq i64 %30, 2048
  br i1 %31, label %17, label %21, !llvm.loop !25
}

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_5(ptr noalias nocapture noundef readonly %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef writeonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %13
  %5 = phi i64 [ 0, %3 ], [ %14, %13 ]
  %6 = shl nuw nsw i64 %5, 12
  %7 = getelementptr float, ptr %0, i64 %6
  %8 = getelementptr float, ptr %2, i64 %6
  br label %10

9:                                                ; preds = %13
  ret void

10:                                               ; preds = %4, %16
  %11 = phi i64 [ 0, %4 ], [ %18, %16 ]
  %12 = getelementptr float, ptr %1, i64 %11
  br label %20

13:                                               ; preds = %16
  %14 = add nuw nsw i64 %5, 1
  %15 = icmp eq i64 %14, 2048
  br i1 %15, label %9, label %4, !llvm.loop !26

16:                                               ; preds = %20
  %17 = getelementptr float, ptr %8, i64 %11
  store float %28, ptr %17, align 4, !tbaa !8
  %18 = add nuw nsw i64 %11, 1
  %19 = icmp eq i64 %18, 4096
  br i1 %19, label %13, label %10, !llvm.loop !27

20:                                               ; preds = %10, %20
  %21 = phi i64 [ 0, %10 ], [ %29, %20 ]
  %22 = phi float [ 0.000000e+00, %10 ], [ %28, %20 ]
  %23 = getelementptr float, ptr %7, i64 %21
  %24 = load float, ptr %23, align 4, !tbaa !8
  %25 = shl nuw nsw i64 %21, 12
  %26 = getelementptr float, ptr %12, i64 %25
  %27 = load float, ptr %26, align 4, !tbaa !8
  %28 = tail call float @llvm.fmuladd.f32(float %24, float %27, float %22)
  %29 = add nuw nsw i64 %21, 1
  %30 = icmp eq i64 %29, 4096
  br i1 %30, label %16, label %20, !llvm.loop !28
}

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_6(ptr noalias nocapture noundef readonly %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef writeonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %14
  %5 = phi i64 [ 0, %3 ], [ %15, %14 ]
  %6 = shl nuw nsw i64 %5, 12
  %7 = shl nuw nsw i64 %5, 14
  %8 = getelementptr float, ptr %0, i64 %6
  %9 = getelementptr float, ptr %2, i64 %7
  br label %11

10:                                               ; preds = %14
  ret void

11:                                               ; preds = %4, %17
  %12 = phi i64 [ 0, %4 ], [ %19, %17 ]
  %13 = getelementptr float, ptr %1, i64 %12
  br label %21

14:                                               ; preds = %17
  %15 = add nuw nsw i64 %5, 1
  %16 = icmp eq i64 %15, 2048
  br i1 %16, label %10, label %4, !llvm.loop !29

17:                                               ; preds = %21
  %18 = getelementptr float, ptr %9, i64 %12
  store float %29, ptr %18, align 4, !tbaa !8
  %19 = add nuw nsw i64 %12, 1
  %20 = icmp eq i64 %19, 16384
  br i1 %20, label %14, label %11, !llvm.loop !30

21:                                               ; preds = %11, %21
  %22 = phi i64 [ 0, %11 ], [ %30, %21 ]
  %23 = phi float [ 0.000000e+00, %11 ], [ %29, %21 ]
  %24 = getelementptr float, ptr %8, i64 %22
  %25 = load float, ptr %24, align 4, !tbaa !8
  %26 = shl nuw nsw i64 %22, 14
  %27 = getelementptr float, ptr %13, i64 %26
  %28 = load float, ptr %27, align 4, !tbaa !8
  %29 = tail call float @llvm.fmuladd.f32(float %25, float %28, float %23)
  %30 = add nuw nsw i64 %22, 1
  %31 = icmp eq i64 %30, 4096
  br i1 %31, label %17, label %21, !llvm.loop !31
}

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_7(ptr noalias nocapture noundef readonly %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef writeonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %14
  %5 = phi i64 [ 0, %3 ], [ %15, %14 ]
  %6 = shl nuw nsw i64 %5, 14
  %7 = shl nuw nsw i64 %5, 12
  %8 = getelementptr float, ptr %0, i64 %6
  %9 = getelementptr float, ptr %2, i64 %7
  br label %11

10:                                               ; preds = %14
  ret void

11:                                               ; preds = %4, %17
  %12 = phi i64 [ 0, %4 ], [ %19, %17 ]
  %13 = getelementptr float, ptr %1, i64 %12
  br label %21

14:                                               ; preds = %17
  %15 = add nuw nsw i64 %5, 1
  %16 = icmp eq i64 %15, 2048
  br i1 %16, label %10, label %4, !llvm.loop !32

17:                                               ; preds = %21
  %18 = getelementptr float, ptr %9, i64 %12
  store float %29, ptr %18, align 4, !tbaa !8
  %19 = add nuw nsw i64 %12, 1
  %20 = icmp eq i64 %19, 4096
  br i1 %20, label %14, label %11, !llvm.loop !33

21:                                               ; preds = %11, %21
  %22 = phi i64 [ 0, %11 ], [ %30, %21 ]
  %23 = phi float [ 0.000000e+00, %11 ], [ %29, %21 ]
  %24 = getelementptr float, ptr %8, i64 %22
  %25 = load float, ptr %24, align 4, !tbaa !8
  %26 = shl nuw nsw i64 %22, 12
  %27 = getelementptr float, ptr %13, i64 %26
  %28 = load float, ptr %27, align 4, !tbaa !8
  %29 = tail call float @llvm.fmuladd.f32(float %25, float %28, float %23)
  %30 = add nuw nsw i64 %22, 1
  %31 = icmp eq i64 %30, 16384
  br i1 %31, label %17, label %21, !llvm.loop !34
}

; Function Attrs: nounwind ssp uwtable(sync)
define noundef i32 @main() local_unnamed_addr #3 {
  %1 = alloca %struct.timespec, align 8
  %2 = alloca %struct.timespec, align 8
  %3 = tail call dereferenceable_or_null(33554432) ptr @malloc(i64 noundef 33554432) #9
  tail call void @memset_pattern16(ptr %3, ptr nonnull @.memset_pattern.7, i64 33554432), !tbaa !8
  %4 = tail call dereferenceable_or_null(67108864) ptr @malloc(i64 noundef 67108864) #9
  tail call void @memset_pattern16(ptr %4, ptr nonnull @.memset_pattern.7, i64 67108864), !tbaa !8
  %5 = tail call dereferenceable_or_null(33554432) ptr @malloc(i64 noundef 33554432) #9
  tail call void @memset_pattern16(ptr %5, ptr nonnull @.memset_pattern.7, i64 33554432), !tbaa !8
  %6 = tail call dereferenceable_or_null(67108864) ptr @malloc(i64 noundef 67108864) #9
  tail call void @memset_pattern16(ptr %6, ptr nonnull @.memset_pattern.7, i64 67108864), !tbaa !8
  %7 = tail call dereferenceable_or_null(33554432) ptr @malloc(i64 noundef 33554432) #9
  tail call void @memset_pattern16(ptr %7, ptr nonnull @.memset_pattern.7, i64 33554432), !tbaa !8
  %8 = tail call dereferenceable_or_null(67108864) ptr @malloc(i64 noundef 67108864) #9
  tail call void @memset_pattern16(ptr %8, ptr nonnull @.memset_pattern.7, i64 67108864), !tbaa !8
  %9 = tail call dereferenceable_or_null(33554432) ptr @malloc(i64 noundef 33554432) #9
  tail call void @memset_pattern16(ptr %9, ptr nonnull @.memset_pattern.7, i64 33554432), !tbaa !8
  %10 = tail call dereferenceable_or_null(16777216) ptr @malloc(i64 noundef 16777216) #9
  tail call void @memset_pattern16(ptr %10, ptr nonnull @.memset_pattern.7, i64 16777216), !tbaa !8
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %1) #10
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %2) #10
  %11 = call i32 @clock_gettime(i32 noundef 6, ptr noundef nonnull %1) #10
  call void @llvm.experimental.noalias.scope.decl(metadata !35)
  call void @llvm.experimental.noalias.scope.decl(metadata !38)
  call void @llvm.experimental.noalias.scope.decl(metadata !40)
  br label %12

12:                                               ; preds = %20, %0
  %13 = phi i64 [ 0, %0 ], [ %21, %20 ]
  %14 = shl nuw nsw i64 %13, 12
  %15 = getelementptr float, ptr %3, i64 %14
  %16 = getelementptr float, ptr %5, i64 %14
  br label %17

17:                                               ; preds = %23, %12
  %18 = phi i64 [ 0, %12 ], [ %25, %23 ]
  %19 = getelementptr float, ptr %4, i64 %18
  br label %27

20:                                               ; preds = %23
  %21 = add nuw nsw i64 %13, 1
  %22 = icmp eq i64 %21, 2048
  br i1 %22, label %38, label %12, !llvm.loop !6

23:                                               ; preds = %27
  %24 = getelementptr float, ptr %16, i64 %18
  store float %35, ptr %24, align 4, !tbaa !8, !alias.scope !40, !noalias !42
  %25 = add nuw nsw i64 %18, 1
  %26 = icmp eq i64 %25, 4096
  br i1 %26, label %20, label %17, !llvm.loop !12

27:                                               ; preds = %27, %17
  %28 = phi i64 [ 0, %17 ], [ %36, %27 ]
  %29 = phi float [ 0.000000e+00, %17 ], [ %35, %27 ]
  %30 = getelementptr float, ptr %15, i64 %28
  %31 = load float, ptr %30, align 4, !tbaa !8, !alias.scope !35, !noalias !43
  %32 = shl nuw nsw i64 %28, 12
  %33 = getelementptr float, ptr %19, i64 %32
  %34 = load float, ptr %33, align 4, !tbaa !8, !alias.scope !38, !noalias !44
  %35 = call float @llvm.fmuladd.f32(float %31, float %34, float %29)
  %36 = add nuw nsw i64 %28, 1
  %37 = icmp eq i64 %36, 4096
  br i1 %37, label %23, label %27, !llvm.loop !13

38:                                               ; preds = %20
  call void @llvm.experimental.noalias.scope.decl(metadata !45)
  call void @llvm.experimental.noalias.scope.decl(metadata !48)
  call void @llvm.experimental.noalias.scope.decl(metadata !50)
  br label %39

39:                                               ; preds = %47, %38
  %40 = phi i64 [ 0, %38 ], [ %48, %47 ]
  %41 = shl nuw nsw i64 %40, 12
  %42 = getelementptr float, ptr %3, i64 %41
  %43 = getelementptr float, ptr %7, i64 %41
  br label %44

44:                                               ; preds = %50, %39
  %45 = phi i64 [ 0, %39 ], [ %52, %50 ]
  %46 = getelementptr float, ptr %6, i64 %45
  br label %54

47:                                               ; preds = %50
  %48 = add nuw nsw i64 %40, 1
  %49 = icmp eq i64 %48, 2048
  br i1 %49, label %65, label %39, !llvm.loop !14

50:                                               ; preds = %54
  %51 = getelementptr float, ptr %43, i64 %45
  store float %62, ptr %51, align 4, !tbaa !8, !alias.scope !50, !noalias !52
  %52 = add nuw nsw i64 %45, 1
  %53 = icmp eq i64 %52, 4096
  br i1 %53, label %47, label %44, !llvm.loop !15

54:                                               ; preds = %54, %44
  %55 = phi i64 [ 0, %44 ], [ %63, %54 ]
  %56 = phi float [ 0.000000e+00, %44 ], [ %62, %54 ]
  %57 = getelementptr float, ptr %42, i64 %55
  %58 = load float, ptr %57, align 4, !tbaa !8, !alias.scope !45, !noalias !53
  %59 = shl nuw nsw i64 %55, 12
  %60 = getelementptr float, ptr %46, i64 %59
  %61 = load float, ptr %60, align 4, !tbaa !8, !alias.scope !48, !noalias !54
  %62 = call float @llvm.fmuladd.f32(float %58, float %61, float %56)
  %63 = add nuw nsw i64 %55, 1
  %64 = icmp eq i64 %63, 4096
  br i1 %64, label %50, label %54, !llvm.loop !16

65:                                               ; preds = %47
  call void @llvm.experimental.noalias.scope.decl(metadata !55)
  call void @llvm.experimental.noalias.scope.decl(metadata !58)
  call void @llvm.experimental.noalias.scope.decl(metadata !60)
  br label %66

66:                                               ; preds = %74, %65
  %67 = phi i64 [ 0, %65 ], [ %75, %74 ]
  %68 = shl nuw nsw i64 %67, 12
  %69 = getelementptr float, ptr %3, i64 %68
  %70 = getelementptr float, ptr %9, i64 %68
  br label %71

71:                                               ; preds = %77, %66
  %72 = phi i64 [ 0, %66 ], [ %79, %77 ]
  %73 = getelementptr float, ptr %8, i64 %72
  br label %81

74:                                               ; preds = %77
  %75 = add nuw nsw i64 %67, 1
  %76 = icmp eq i64 %75, 2048
  br i1 %76, label %92, label %66, !llvm.loop !17

77:                                               ; preds = %81
  %78 = getelementptr float, ptr %70, i64 %72
  store float %89, ptr %78, align 4, !tbaa !8, !alias.scope !60, !noalias !62
  %79 = add nuw nsw i64 %72, 1
  %80 = icmp eq i64 %79, 4096
  br i1 %80, label %74, label %71, !llvm.loop !18

81:                                               ; preds = %81, %71
  %82 = phi i64 [ 0, %71 ], [ %90, %81 ]
  %83 = phi float [ 0.000000e+00, %71 ], [ %89, %81 ]
  %84 = getelementptr float, ptr %69, i64 %82
  %85 = load float, ptr %84, align 4, !tbaa !8, !alias.scope !55, !noalias !63
  %86 = shl nuw nsw i64 %82, 12
  %87 = getelementptr float, ptr %73, i64 %86
  %88 = load float, ptr %87, align 4, !tbaa !8, !alias.scope !58, !noalias !64
  %89 = call float @llvm.fmuladd.f32(float %85, float %88, float %83)
  %90 = add nuw nsw i64 %82, 1
  %91 = icmp eq i64 %90, 4096
  br i1 %91, label %77, label %81, !llvm.loop !19

92:                                               ; preds = %74
  call void @llvm.experimental.noalias.scope.decl(metadata !65)
  call void @llvm.experimental.noalias.scope.decl(metadata !68)
  call void @llvm.experimental.noalias.scope.decl(metadata !70)
  br label %93

93:                                               ; preds = %103, %92
  %94 = phi i64 [ 0, %92 ], [ %104, %103 ]
  %95 = shl nuw nsw i64 %94, 12
  %96 = shl nuw nsw i64 %94, 11
  %97 = getelementptr float, ptr %5, i64 %95
  %98 = getelementptr float, ptr %10, i64 %96
  br label %99

99:                                               ; preds = %106, %93
  %100 = phi i64 [ 0, %93 ], [ %108, %106 ]
  %101 = shl nuw nsw i64 %100, 12
  %102 = getelementptr float, ptr %7, i64 %101
  br label %110

103:                                              ; preds = %106
  %104 = add nuw nsw i64 %94, 1
  %105 = icmp eq i64 %104, 2048
  br i1 %105, label %120, label %93, !llvm.loop !20

106:                                              ; preds = %110
  %107 = getelementptr float, ptr %98, i64 %100
  store float %117, ptr %107, align 4, !tbaa !8, !alias.scope !70, !noalias !72
  %108 = add nuw nsw i64 %100, 1
  %109 = icmp eq i64 %108, 2048
  br i1 %109, label %103, label %99, !llvm.loop !21

110:                                              ; preds = %110, %99
  %111 = phi i64 [ 0, %99 ], [ %118, %110 ]
  %112 = phi float [ 0.000000e+00, %99 ], [ %117, %110 ]
  %113 = getelementptr float, ptr %97, i64 %111
  %114 = load float, ptr %113, align 4, !tbaa !8, !alias.scope !65, !noalias !73
  %115 = getelementptr float, ptr %102, i64 %111
  %116 = load float, ptr %115, align 4, !tbaa !8, !alias.scope !68, !noalias !74
  %117 = call float @llvm.fmuladd.f32(float %114, float %116, float %112)
  %118 = add nuw nsw i64 %111, 1
  %119 = icmp eq i64 %118, 4096
  br i1 %119, label %106, label %110, !llvm.loop !22

120:                                              ; preds = %103
  call void @llvm.experimental.noalias.scope.decl(metadata !75)
  call void @llvm.experimental.noalias.scope.decl(metadata !78)
  br label %121

121:                                              ; preds = %128, %120
  %122 = phi i64 [ 0, %120 ], [ %129, %128 ]
  %123 = shl nuw nsw i64 %122, 11
  %124 = getelementptr float, ptr %10, i64 %123
  br label %125

125:                                              ; preds = %131, %121
  %126 = phi i64 [ 0, %121 ], [ %132, %131 ]
  %127 = getelementptr float, ptr %9, i64 %126
  br label %134

128:                                              ; preds = %131
  %129 = add nuw nsw i64 %122, 1
  %130 = icmp eq i64 %129, 2048
  br i1 %130, label %145, label %121, !llvm.loop !23

131:                                              ; preds = %134
  %132 = add nuw nsw i64 %126, 1
  %133 = icmp eq i64 %132, 4096
  br i1 %133, label %128, label %125, !llvm.loop !24

134:                                              ; preds = %134, %125
  %135 = phi i64 [ 0, %125 ], [ %143, %134 ]
  %136 = phi float [ 0.000000e+00, %125 ], [ %142, %134 ]
  %137 = getelementptr float, ptr %124, i64 %135
  %138 = load float, ptr %137, align 4, !tbaa !8, !alias.scope !75, !noalias !80
  %139 = shl nuw nsw i64 %135, 12
  %140 = getelementptr float, ptr %127, i64 %139
  %141 = load float, ptr %140, align 4, !tbaa !8, !alias.scope !78, !noalias !82
  %142 = call float @llvm.fmuladd.f32(float %138, float %141, float %136)
  %143 = add nuw nsw i64 %135, 1
  %144 = icmp eq i64 %143, 2048
  br i1 %144, label %131, label %134, !llvm.loop !25

145:                                              ; preds = %128
  %146 = call i32 @clock_gettime(i32 noundef 6, ptr noundef nonnull %2) #10
  %147 = load i64, ptr %2, align 8, !tbaa !83
  %148 = load i64, ptr %1, align 8, !tbaa !83
  %149 = sub nsw i64 %147, %148
  %150 = sitofp i64 %149 to double
  %151 = getelementptr inbounds %struct.timespec, ptr %2, i64 0, i32 1
  %152 = load i64, ptr %151, align 8, !tbaa !86
  %153 = getelementptr inbounds %struct.timespec, ptr %1, i64 0, i32 1
  %154 = load i64, ptr %153, align 8, !tbaa !86
  %155 = sub nsw i64 %152, %154
  %156 = sitofp i64 %155 to double
  %157 = call double @llvm.fmuladd.f64(double %156, double 1.000000e-09, double %150)
  %158 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str, double noundef %157)
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %2) #10
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %1) #10
  ret i32 0
}

; Function Attrs: mustprogress nofree nounwind willreturn allockind("alloc,uninitialized") allocsize(0) memory(inaccessiblemem: readwrite)
declare noalias noundef ptr @malloc(i64 noundef) local_unnamed_addr #4

declare i32 @clock_gettime(i32 noundef, ptr noundef) local_unnamed_addr #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.fmuladd.f64(double, double, double) #2

; Function Attrs: nofree nounwind
declare noundef i32 @printf(ptr nocapture noundef readonly, ...) local_unnamed_addr #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: readwrite)
declare void @llvm.experimental.noalias.scope.decl(metadata) #7

; Function Attrs: nofree nounwind willreturn memory(argmem: readwrite)
declare void @memset_pattern16(ptr nocapture writeonly, ptr nocapture readonly, i64) local_unnamed_addr #8

attributes #0 = { nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync) "frame-pointer"="non-leaf" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+complxnum,+crc,+dotprod,+fp-armv8,+fp16fml,+fullfp16,+jsconv,+lse,+neon,+pauth,+ras,+rcpc,+rdm,+sha2,+sha3,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }
attributes #1 = { mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { nounwind ssp uwtable(sync) "frame-pointer"="non-leaf" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+complxnum,+crc,+dotprod,+fp-armv8,+fp16fml,+fullfp16,+jsconv,+lse,+neon,+pauth,+ras,+rcpc,+rdm,+sha2,+sha3,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }
attributes #4 = { mustprogress nofree nounwind willreturn allockind("alloc,uninitialized") allocsize(0) memory(inaccessiblemem: readwrite) "alloc-family"="malloc" "frame-pointer"="non-leaf" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+complxnum,+crc,+dotprod,+fp-armv8,+fp16fml,+fullfp16,+jsconv,+lse,+neon,+pauth,+ras,+rcpc,+rdm,+sha2,+sha3,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }
attributes #5 = { "frame-pointer"="non-leaf" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+complxnum,+crc,+dotprod,+fp-armv8,+fp16fml,+fullfp16,+jsconv,+lse,+neon,+pauth,+ras,+rcpc,+rdm,+sha2,+sha3,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }
attributes #6 = { nofree nounwind "frame-pointer"="non-leaf" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+complxnum,+crc,+dotprod,+fp-armv8,+fp16fml,+fullfp16,+jsconv,+lse,+neon,+pauth,+ras,+rcpc,+rdm,+sha2,+sha3,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: readwrite) }
attributes #8 = { nofree nounwind willreturn memory(argmem: readwrite) }
attributes #9 = { allocsize(0) }
attributes #10 = { nounwind }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 2, !"SDK Version", [2 x i32] [i32 15, i32 5]}
!1 = !{i32 1, !"wchar_size", i32 4}
!2 = !{i32 8, !"PIC Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 1}
!4 = !{i32 7, !"frame-pointer", i32 1}
!5 = !{!"Homebrew clang version 18.1.8"}
!6 = distinct !{!6, !7}
!7 = !{!"llvm.loop.mustprogress"}
!8 = !{!9, !9, i64 0}
!9 = !{!"float", !10, i64 0}
!10 = !{!"omnipotent char", !11, i64 0}
!11 = !{!"Simple C/C++ TBAA"}
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
!33 = distinct !{!33, !7}
!34 = distinct !{!34, !7}
!35 = !{!36}
!36 = distinct !{!36, !37, !"einsum_0: argument 0"}
!37 = distinct !{!37, !"einsum_0"}
!38 = !{!39}
!39 = distinct !{!39, !37, !"einsum_0: argument 1"}
!40 = !{!41}
!41 = distinct !{!41, !37, !"einsum_0: argument 2"}
!42 = !{!36, !39}
!43 = !{!39, !41}
!44 = !{!36, !41}
!45 = !{!46}
!46 = distinct !{!46, !47, !"einsum_1: argument 0"}
!47 = distinct !{!47, !"einsum_1"}
!48 = !{!49}
!49 = distinct !{!49, !47, !"einsum_1: argument 1"}
!50 = !{!51}
!51 = distinct !{!51, !47, !"einsum_1: argument 2"}
!52 = !{!46, !49}
!53 = !{!49, !51}
!54 = !{!46, !51}
!55 = !{!56}
!56 = distinct !{!56, !57, !"einsum_2: argument 0"}
!57 = distinct !{!57, !"einsum_2"}
!58 = !{!59}
!59 = distinct !{!59, !57, !"einsum_2: argument 1"}
!60 = !{!61}
!61 = distinct !{!61, !57, !"einsum_2: argument 2"}
!62 = !{!56, !59}
!63 = !{!59, !61}
!64 = !{!56, !61}
!65 = !{!66}
!66 = distinct !{!66, !67, !"einsum_3: argument 0"}
!67 = distinct !{!67, !"einsum_3"}
!68 = !{!69}
!69 = distinct !{!69, !67, !"einsum_3: argument 1"}
!70 = !{!71}
!71 = distinct !{!71, !67, !"einsum_3: argument 2"}
!72 = !{!66, !69}
!73 = !{!69, !71}
!74 = !{!66, !71}
!75 = !{!76}
!76 = distinct !{!76, !77, !"einsum_4: argument 0"}
!77 = distinct !{!77, !"einsum_4"}
!78 = !{!79}
!79 = distinct !{!79, !77, !"einsum_4: argument 1"}
!80 = !{!79, !81}
!81 = distinct !{!81, !77, !"einsum_4: argument 2"}
!82 = !{!76, !81}
!83 = !{!84, !85, i64 0}
!84 = !{!"timespec", !85, i64 0, !85, i64 8}
!85 = !{!"long", !10, i64 0}
!86 = !{!84, !85, i64 8}
