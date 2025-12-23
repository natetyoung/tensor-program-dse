; ModuleID = 'med_gpt/medgpt_opt_16384.c'
source_filename = "med_gpt/medgpt_opt_16384.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128-Fn32"
target triple = "arm64-apple-macosx15.0.0"

%struct.timespec = type { i64, i64 }

@.str = private unnamed_addr constant [10 x i8] c"Time: %f\0A\00", align 1
@.memset_pattern.6 = private unnamed_addr constant [4 x float] [float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00], align 16

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_0(ptr noalias nocapture noundef %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef readonly %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %42
  %5 = phi i1 [ true, %3 ], [ false, %42 ]
  %6 = phi i64 [ 0, %3 ], [ 64, %42 ]
  br label %8

7:                                                ; preds = %42
  ret void

8:                                                ; preds = %4, %43
  %9 = phi i64 [ 0, %4 ], [ %44, %43 ]
  %10 = icmp ult i64 %9, 411
  %11 = sub nsw i64 512, %9
  %12 = and i64 %11, 4294967294
  %13 = select i1 %10, i64 102, i64 %12
  br label %14

14:                                               ; preds = %8, %39
  %15 = phi i64 [ 0, %8 ], [ %40, %39 ]
  %16 = shl nsw i64 %15, 11
  %17 = getelementptr inbounds i8, ptr %1, i64 %16
  br label %18

18:                                               ; preds = %36, %14
  %19 = phi i64 [ %37, %36 ], [ 0, %14 ]
  %20 = or disjoint i64 %19, %6
  %21 = shl nuw nsw i64 %20, 9
  %22 = or disjoint i64 %21, %15
  %23 = getelementptr inbounds float, ptr %2, i64 %22
  %24 = load float, ptr %23, align 4, !tbaa !6
  %25 = getelementptr inbounds float, ptr %0, i64 %21
  br label %26

26:                                               ; preds = %26, %18
  %27 = phi i64 [ %34, %26 ], [ 0, %18 ]
  %28 = add nuw nsw i64 %27, %9
  %29 = getelementptr inbounds float, ptr %17, i64 %28
  %30 = load float, ptr %29, align 4, !tbaa !6
  %31 = getelementptr inbounds float, ptr %25, i64 %28
  %32 = load float, ptr %31, align 4, !tbaa !6
  %33 = tail call float @llvm.fmuladd.f32(float %30, float %24, float %32)
  store float %33, ptr %31, align 4, !tbaa !6
  %34 = add nuw nsw i64 %27, 1
  %35 = icmp eq i64 %34, %13
  br i1 %35, label %36, label %26, !llvm.loop !10

36:                                               ; preds = %26
  %37 = add nuw nsw i64 %19, 1
  %38 = icmp eq i64 %37, 64
  br i1 %38, label %39, label %18, !llvm.loop !13

39:                                               ; preds = %36
  %40 = add nuw nsw i64 %15, 1
  %41 = icmp eq i64 %40, 512
  br i1 %41, label %43, label %14, !llvm.loop !14

42:                                               ; preds = %43
  br i1 %5, label %4, label %7, !llvm.loop !15

43:                                               ; preds = %39
  %44 = add nuw nsw i64 %9, 102
  %45 = icmp ult i64 %9, 410
  br i1 %45, label %8, label %42, !llvm.loop !16
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
  %6 = phi i64 [ 0, %3 ], [ 64, %42 ]
  br label %7

7:                                                ; preds = %4, %38
  %8 = phi i64 [ 0, %4 ], [ %39, %38 ]
  br label %9

9:                                                ; preds = %35, %7
  %10 = phi i64 [ %36, %35 ], [ 0, %7 ]
  %11 = shl nsw i64 %10, 11
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
  %23 = shl nsw i64 %22, 11
  %24 = getelementptr inbounds i8, ptr %19, i64 %23
  %25 = load float, ptr %24, align 4, !tbaa !6
  %26 = shl nsw i64 %22, 9
  %27 = getelementptr inbounds i8, ptr %13, i64 %26
  %28 = load float, ptr %27, align 4, !tbaa !6
  %29 = tail call float @llvm.fmuladd.f32(float %25, float %18, float %28)
  store float %29, ptr %27, align 4, !tbaa !6
  %30 = add nuw nsw i64 %21, 1
  %31 = icmp eq i64 %30, 64
  br i1 %31, label %32, label %20, !llvm.loop !17

32:                                               ; preds = %20
  %33 = add nuw nsw i64 %15, 1
  %34 = icmp eq i64 %33, 102
  br i1 %34, label %35, label %14, !llvm.loop !18

35:                                               ; preds = %32
  %36 = add nuw nsw i64 %10, 1
  %37 = icmp eq i64 %36, 128
  br i1 %37, label %38, label %9, !llvm.loop !19

38:                                               ; preds = %35
  %39 = add nuw nsw i64 %8, 102
  %40 = icmp ult i64 %8, 410
  br i1 %40, label %7, label %42, !llvm.loop !20

41:                                               ; preds = %42
  ret void

42:                                               ; preds = %38
  br i1 %5, label %4, label %41, !llvm.loop !21
}

; Function Attrs: nofree norecurse nosync nounwind ssp memory(argmem: readwrite) uwtable(sync)
define void @einsum_2(ptr noalias nocapture noundef readonly %0, ptr noalias nocapture noundef readonly %1, ptr noalias nocapture noundef %2) local_unnamed_addr #0 {
  br label %4

4:                                                ; preds = %3, %12
  %5 = phi i1 [ true, %3 ], [ false, %12 ]
  %6 = phi i64 [ 0, %3 ], [ 64, %12 ]
  br label %8

7:                                                ; preds = %12
  ret void

8:                                                ; preds = %4, %13
  %9 = phi i64 [ 0, %4 ], [ %14, %13 ]
  %10 = getelementptr inbounds float, ptr %2, i64 %9
  %11 = getelementptr inbounds float, ptr %1, i64 %9
  br label %16

12:                                               ; preds = %13
  br i1 %5, label %4, label %7, !llvm.loop !22

13:                                               ; preds = %24
  %14 = add nuw nsw i64 %9, 1
  %15 = icmp eq i64 %14, 512
  br i1 %15, label %12, label %8, !llvm.loop !23

16:                                               ; preds = %8, %24
  %17 = phi i64 [ 0, %8 ], [ %25, %24 ]
  %18 = or disjoint i64 %17, %6
  %19 = shl nsw i64 %18, 11
  %20 = getelementptr inbounds i8, ptr %10, i64 %19
  %21 = load float, ptr %20, align 4, !tbaa !6
  %22 = shl nsw i64 %18, 9
  %23 = getelementptr inbounds i8, ptr %0, i64 %22
  br label %27

24:                                               ; preds = %27
  store float %35, ptr %20, align 4, !tbaa !6
  %25 = add nuw nsw i64 %17, 1
  %26 = icmp eq i64 %25, 64
  br i1 %26, label %13, label %16, !llvm.loop !24

27:                                               ; preds = %16, %27
  %28 = phi i64 [ 0, %16 ], [ %36, %27 ]
  %29 = phi float [ %21, %16 ], [ %35, %27 ]
  %30 = getelementptr inbounds float, ptr %23, i64 %28
  %31 = load float, ptr %30, align 4, !tbaa !6
  %32 = shl nsw i64 %28, 11
  %33 = getelementptr inbounds i8, ptr %11, i64 %32
  %34 = load float, ptr %33, align 4, !tbaa !6
  %35 = tail call float @llvm.fmuladd.f32(float %31, float %34, float %29)
  %36 = add nuw nsw i64 %28, 1
  %37 = icmp eq i64 %36, 128
  br i1 %37, label %24, label %27, !llvm.loop !25
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

11:                                               ; preds = %47, %0
  %12 = phi i1 [ true, %0 ], [ false, %47 ]
  %13 = phi i64 [ 0, %0 ], [ 64, %47 ]
  br label %14

14:                                               ; preds = %48, %11
  %15 = phi i64 [ 0, %11 ], [ %49, %48 ]
  %16 = icmp ult i64 %15, 411
  %17 = sub nuw nsw i64 512, %15
  %18 = select i1 %16, i64 102, i64 %17
  br label %19

19:                                               ; preds = %44, %14
  %20 = phi i64 [ 0, %14 ], [ %45, %44 ]
  %21 = shl nsw i64 %20, 11
  %22 = getelementptr inbounds i8, ptr %5, i64 %21
  br label %23

23:                                               ; preds = %41, %19
  %24 = phi i64 [ %42, %41 ], [ 0, %19 ]
  %25 = or disjoint i64 %24, %13
  %26 = shl nuw nsw i64 %25, 9
  %27 = or disjoint i64 %26, %20
  %28 = getelementptr inbounds float, ptr %4, i64 %27
  %29 = load float, ptr %28, align 4, !tbaa !6, !alias.scope !31, !noalias !33
  %30 = getelementptr inbounds float, ptr %6, i64 %26
  br label %31

31:                                               ; preds = %31, %23
  %32 = phi i64 [ %39, %31 ], [ 0, %23 ]
  %33 = add nuw nsw i64 %32, %15
  %34 = getelementptr inbounds float, ptr %22, i64 %33
  %35 = load float, ptr %34, align 4, !tbaa !6, !alias.scope !29, !noalias !34
  %36 = getelementptr inbounds float, ptr %30, i64 %33
  %37 = load float, ptr %36, align 4, !tbaa !6, !alias.scope !26, !noalias !35
  %38 = call float @llvm.fmuladd.f32(float %35, float %29, float %37)
  store float %38, ptr %36, align 4, !tbaa !6, !alias.scope !26, !noalias !35
  %39 = add nuw nsw i64 %32, 1
  %40 = icmp eq i64 %39, %18
  br i1 %40, label %41, label %31, !llvm.loop !10

41:                                               ; preds = %31
  %42 = add nuw nsw i64 %24, 1
  %43 = icmp eq i64 %42, 64
  br i1 %43, label %44, label %23, !llvm.loop !13

44:                                               ; preds = %41
  %45 = add nuw nsw i64 %20, 1
  %46 = icmp eq i64 %45, 512
  br i1 %46, label %48, label %19, !llvm.loop !14

47:                                               ; preds = %48
  br i1 %12, label %11, label %51, !llvm.loop !15

48:                                               ; preds = %44
  %49 = add nuw nsw i64 %15, 102
  %50 = icmp ult i64 %15, 410
  br i1 %50, label %14, label %47, !llvm.loop !16

51:                                               ; preds = %47
  call void @llvm.experimental.noalias.scope.decl(metadata !36)
  call void @llvm.experimental.noalias.scope.decl(metadata !39)
  call void @llvm.experimental.noalias.scope.decl(metadata !41)
  br label %52

52:                                               ; preds = %89, %51
  %53 = phi i1 [ true, %51 ], [ false, %89 ]
  %54 = phi i64 [ 0, %51 ], [ 64, %89 ]
  br label %55

55:                                               ; preds = %86, %52
  %56 = phi i64 [ 0, %52 ], [ %87, %86 ]
  br label %57

57:                                               ; preds = %83, %55
  %58 = phi i64 [ %84, %83 ], [ 0, %55 ]
  %59 = shl nsw i64 %58, 11
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
  %71 = shl nsw i64 %70, 11
  %72 = getelementptr inbounds i8, ptr %67, i64 %71
  %73 = load float, ptr %72, align 4, !tbaa !6, !alias.scope !39, !noalias !44
  %74 = shl nsw i64 %70, 9
  %75 = getelementptr inbounds i8, ptr %61, i64 %74
  %76 = load float, ptr %75, align 4, !tbaa !6, !alias.scope !36, !noalias !45
  %77 = call float @llvm.fmuladd.f32(float %73, float %66, float %76)
  store float %77, ptr %75, align 4, !tbaa !6, !alias.scope !36, !noalias !45
  %78 = add nuw nsw i64 %69, 1
  %79 = icmp eq i64 %78, 64
  br i1 %79, label %80, label %68, !llvm.loop !17

80:                                               ; preds = %68
  %81 = add nuw nsw i64 %63, 1
  %82 = icmp eq i64 %81, 102
  br i1 %82, label %83, label %62, !llvm.loop !18

83:                                               ; preds = %80
  %84 = add nuw nsw i64 %58, 1
  %85 = icmp eq i64 %84, 128
  br i1 %85, label %86, label %57, !llvm.loop !19

86:                                               ; preds = %83
  %87 = add nuw nsw i64 %56, 102
  %88 = icmp ult i64 %56, 410
  br i1 %88, label %55, label %89, !llvm.loop !20

89:                                               ; preds = %86
  br i1 %53, label %52, label %90, !llvm.loop !21

90:                                               ; preds = %89
  call void @llvm.experimental.noalias.scope.decl(metadata !46)
  call void @llvm.experimental.noalias.scope.decl(metadata !49)
  call void @llvm.experimental.noalias.scope.decl(metadata !51)
  br label %91

91:                                               ; preds = %98, %90
  %92 = phi i1 [ true, %90 ], [ false, %98 ]
  %93 = phi i64 [ 0, %90 ], [ 64, %98 ]
  br label %94

94:                                               ; preds = %99, %91
  %95 = phi i64 [ 0, %91 ], [ %100, %99 ]
  %96 = getelementptr inbounds float, ptr %10, i64 %95
  %97 = getelementptr inbounds float, ptr %9, i64 %95
  br label %102

98:                                               ; preds = %99
  br i1 %92, label %91, label %124, !llvm.loop !22

99:                                               ; preds = %110
  %100 = add nuw nsw i64 %95, 1
  %101 = icmp eq i64 %100, 512
  br i1 %101, label %98, label %94, !llvm.loop !23

102:                                              ; preds = %110, %94
  %103 = phi i64 [ 0, %94 ], [ %111, %110 ]
  %104 = or disjoint i64 %103, %93
  %105 = shl nsw i64 %104, 11
  %106 = getelementptr inbounds i8, ptr %96, i64 %105
  %107 = load float, ptr %106, align 4, !tbaa !6, !alias.scope !51, !noalias !53
  %108 = shl nsw i64 %104, 9
  %109 = getelementptr inbounds i8, ptr %8, i64 %108
  br label %113

110:                                              ; preds = %113
  store float %121, ptr %106, align 4, !tbaa !6, !alias.scope !51, !noalias !53
  %111 = add nuw nsw i64 %103, 1
  %112 = icmp eq i64 %111, 64
  br i1 %112, label %99, label %102, !llvm.loop !24

113:                                              ; preds = %113, %102
  %114 = phi i64 [ 0, %102 ], [ %122, %113 ]
  %115 = phi float [ %107, %102 ], [ %121, %113 ]
  %116 = getelementptr inbounds float, ptr %109, i64 %114
  %117 = load float, ptr %116, align 4, !tbaa !6, !alias.scope !46, !noalias !54
  %118 = shl nsw i64 %114, 11
  %119 = getelementptr inbounds i8, ptr %97, i64 %118
  %120 = load float, ptr %119, align 4, !tbaa !6, !alias.scope !49, !noalias !55
  %121 = call float @llvm.fmuladd.f32(float %117, float %120, float %115)
  %122 = add nuw nsw i64 %114, 1
  %123 = icmp eq i64 %122, 128
  br i1 %123, label %110, label %113, !llvm.loop !25

124:                                              ; preds = %98
  %125 = call i32 @clock_gettime(i32 noundef 6, ptr noundef nonnull %2) #9
  %126 = load i64, ptr %2, align 8, !tbaa !56
  %127 = load i64, ptr %1, align 8, !tbaa !56
  %128 = sub nsw i64 %126, %127
  %129 = sitofp i64 %128 to double
  %130 = getelementptr inbounds i8, ptr %2, i64 8
  %131 = load i64, ptr %130, align 8, !tbaa !59
  %132 = getelementptr inbounds i8, ptr %1, i64 8
  %133 = load i64, ptr %132, align 8, !tbaa !59
  %134 = sub nsw i64 %131, %133
  %135 = sitofp i64 %134 to double
  %136 = call double @llvm.fmuladd.f64(double %135, double 1.000000e-09, double %129)
  %137 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str, double noundef %136)
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
