; ModuleID = '../../gpt_polly.ll'
source_filename = "../../gpt_naive.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128"
target triple = "arm64-apple-macosx15.5.0"

%struct.timespec = type { i64, i64 }

@.str = private unnamed_addr constant [10 x i8] c"Time: %f\0A\00", align 1

; Function Attrs: noinline nounwind ssp uwtable(sync)
define i32 @main() #0 {
  %1 = alloca %struct.timespec, align 8
  %2 = alloca %struct.timespec, align 8
  %3 = tail call dereferenceable_or_null(33554432) ptr @malloc(i64 noundef 33554432) #4
  br label %4

4:                                                ; preds = %4, %0
  %.0291 = phi i32 [ 0, %0 ], [ %7, %4 ]
  %5 = zext nneg i32 %.0291 to i64
  %6 = getelementptr inbounds float, ptr %3, i64 %5
  store float 1.000000e+00, ptr %6, align 4
  %7 = add nuw nsw i32 %.0291, 1
  %8 = icmp ult i32 %.0291, 8388607
  br i1 %8, label %4, label %9, !llvm.loop !6

9:                                                ; preds = %4
  %10 = tail call dereferenceable_or_null(67108864) ptr @malloc(i64 noundef 67108864) #4
  br label %11

11:                                               ; preds = %11, %9
  %.0490 = phi i32 [ 0, %9 ], [ %14, %11 ]
  %12 = zext nneg i32 %.0490 to i64
  %13 = getelementptr inbounds float, ptr %10, i64 %12
  store float 1.000000e+00, ptr %13, align 4
  %14 = add nuw nsw i32 %.0490, 1
  %15 = icmp ult i32 %.0490, 16777215
  br i1 %15, label %11, label %16, !llvm.loop !8

16:                                               ; preds = %11
  %17 = tail call dereferenceable_or_null(33554432) ptr @malloc(i64 noundef 33554432) #4
  br label %18

18:                                               ; preds = %18, %16
  %.0689 = phi i32 [ 0, %16 ], [ %21, %18 ]
  %19 = zext nneg i32 %.0689 to i64
  %20 = getelementptr inbounds float, ptr %17, i64 %19
  store float 1.000000e+00, ptr %20, align 4
  %21 = add nuw nsw i32 %.0689, 1
  %22 = icmp ult i32 %.0689, 8388607
  br i1 %22, label %18, label %23, !llvm.loop !9

23:                                               ; preds = %18
  %24 = tail call dereferenceable_or_null(67108864) ptr @malloc(i64 noundef 67108864) #4
  br label %25

25:                                               ; preds = %25, %23
  %.0888 = phi i32 [ 0, %23 ], [ %28, %25 ]
  %26 = zext nneg i32 %.0888 to i64
  %27 = getelementptr inbounds float, ptr %24, i64 %26
  store float 1.000000e+00, ptr %27, align 4
  %28 = add nuw nsw i32 %.0888, 1
  %29 = icmp ult i32 %.0888, 16777215
  br i1 %29, label %25, label %30, !llvm.loop !10

30:                                               ; preds = %25
  %31 = tail call dereferenceable_or_null(33554432) ptr @malloc(i64 noundef 33554432) #4
  br label %32

32:                                               ; preds = %32, %30
  %.01087 = phi i32 [ 0, %30 ], [ %35, %32 ]
  %33 = zext nneg i32 %.01087 to i64
  %34 = getelementptr inbounds float, ptr %31, i64 %33
  store float 1.000000e+00, ptr %34, align 4
  %35 = add nuw nsw i32 %.01087, 1
  %36 = icmp ult i32 %.01087, 8388607
  br i1 %36, label %32, label %37, !llvm.loop !11

37:                                               ; preds = %32
  %38 = tail call dereferenceable_or_null(67108864) ptr @malloc(i64 noundef 67108864) #4
  br label %39

39:                                               ; preds = %39, %37
  %.01286 = phi i32 [ 0, %37 ], [ %42, %39 ]
  %40 = zext nneg i32 %.01286 to i64
  %41 = getelementptr inbounds float, ptr %38, i64 %40
  store float 1.000000e+00, ptr %41, align 4
  %42 = add nuw nsw i32 %.01286, 1
  %43 = icmp ult i32 %.01286, 16777215
  br i1 %43, label %39, label %44, !llvm.loop !12

44:                                               ; preds = %39
  %45 = tail call dereferenceable_or_null(33554432) ptr @malloc(i64 noundef 33554432) #4
  br label %46

46:                                               ; preds = %46, %44
  %.01485 = phi i32 [ 0, %44 ], [ %49, %46 ]
  %47 = zext nneg i32 %.01485 to i64
  %48 = getelementptr inbounds float, ptr %45, i64 %47
  store float 1.000000e+00, ptr %48, align 4
  %49 = add nuw nsw i32 %.01485, 1
  %50 = icmp ult i32 %.01485, 8388607
  br i1 %50, label %46, label %51, !llvm.loop !13

51:                                               ; preds = %46
  %52 = tail call dereferenceable_or_null(16777216) ptr @malloc(i64 noundef 16777216) #4
  br label %53

53:                                               ; preds = %53, %51
  %.01684 = phi i32 [ 0, %51 ], [ %56, %53 ]
  %54 = zext nneg i32 %.01684 to i64
  %55 = getelementptr inbounds float, ptr %52, i64 %54
  store float 1.000000e+00, ptr %55, align 4
  %56 = add nuw nsw i32 %.01684, 1
  %57 = icmp ult i32 %.01684, 4194303
  br i1 %57, label %53, label %58, !llvm.loop !14

58:                                               ; preds = %53
  %59 = tail call dereferenceable_or_null(33554432) ptr @malloc(i64 noundef 33554432) #4
  br label %60

60:                                               ; preds = %60, %58
  %.01883 = phi i32 [ 0, %58 ], [ %63, %60 ]
  %61 = zext nneg i32 %.01883 to i64
  %62 = getelementptr inbounds float, ptr %59, i64 %61
  store float 1.000000e+00, ptr %62, align 4
  %63 = add nuw nsw i32 %.01883, 1
  %64 = icmp ult i32 %.01883, 8388607
  br i1 %64, label %60, label %65, !llvm.loop !15

65:                                               ; preds = %60
  %66 = tail call dereferenceable_or_null(67108864) ptr @malloc(i64 noundef 67108864) #4
  br label %67

67:                                               ; preds = %67, %65
  %.02082 = phi i32 [ 0, %65 ], [ %70, %67 ]
  %68 = zext nneg i32 %.02082 to i64
  %69 = getelementptr inbounds float, ptr %66, i64 %68
  store float 1.000000e+00, ptr %69, align 4
  %70 = add nuw nsw i32 %.02082, 1
  %71 = icmp ult i32 %.02082, 16777215
  br i1 %71, label %67, label %72, !llvm.loop !16

72:                                               ; preds = %67
  %73 = tail call dereferenceable_or_null(33554432) ptr @malloc(i64 noundef 33554432) #4
  br label %74

74:                                               ; preds = %74, %72
  %.02281 = phi i32 [ 0, %72 ], [ %77, %74 ]
  %75 = zext nneg i32 %.02281 to i64
  %76 = getelementptr inbounds float, ptr %73, i64 %75
  store float 1.000000e+00, ptr %76, align 4
  %77 = add nuw nsw i32 %.02281, 1
  %78 = icmp ult i32 %.02281, 8388607
  br i1 %78, label %74, label %79, !llvm.loop !17

79:                                               ; preds = %74
  %80 = tail call dereferenceable_or_null(268435456) ptr @malloc(i64 noundef 268435456) #4
  br label %81

81:                                               ; preds = %81, %79
  %.02480 = phi i32 [ 0, %79 ], [ %84, %81 ]
  %82 = zext nneg i32 %.02480 to i64
  %83 = getelementptr inbounds float, ptr %80, i64 %82
  store float 1.000000e+00, ptr %83, align 4
  %84 = add nuw nsw i32 %.02480, 1
  %85 = icmp ult i32 %.02480, 67108863
  br i1 %85, label %81, label %86, !llvm.loop !18

86:                                               ; preds = %81
  %87 = tail call dereferenceable_or_null(134217728) ptr @malloc(i64 noundef 134217728) #4
  br label %88

88:                                               ; preds = %88, %86
  %.02679 = phi i32 [ 0, %86 ], [ %91, %88 ]
  %89 = zext nneg i32 %.02679 to i64
  %90 = getelementptr inbounds float, ptr %87, i64 %89
  store float 1.000000e+00, ptr %90, align 4
  %91 = add nuw nsw i32 %.02679, 1
  %92 = icmp ult i32 %.02679, 33554431
  br i1 %92, label %88, label %93, !llvm.loop !19

93:                                               ; preds = %88
  %94 = tail call dereferenceable_or_null(268435456) ptr @malloc(i64 noundef 268435456) #4
  br label %95

95:                                               ; preds = %95, %93
  %.02878 = phi i32 [ 0, %93 ], [ %98, %95 ]
  %96 = zext nneg i32 %.02878 to i64
  %97 = getelementptr inbounds float, ptr %94, i64 %96
  store float 1.000000e+00, ptr %97, align 4
  %98 = add nuw nsw i32 %.02878, 1
  %99 = icmp ult i32 %.02878, 67108863
  br i1 %99, label %95, label %100, !llvm.loop !20

100:                                              ; preds = %95
  %101 = tail call dereferenceable_or_null(33554432) ptr @malloc(i64 noundef 33554432) #4
  br label %102

102:                                              ; preds = %102, %100
  %.03077 = phi i32 [ 0, %100 ], [ %105, %102 ]
  %103 = zext nneg i32 %.03077 to i64
  %104 = getelementptr inbounds float, ptr %101, i64 %103
  store float 1.000000e+00, ptr %104, align 4
  %105 = add nuw nsw i32 %.03077, 1
  %106 = icmp ult i32 %.03077, 8388607
  br i1 %106, label %102, label %107, !llvm.loop !21

107:                                              ; preds = %102
  %108 = call i32 @clock_gettime(i32 noundef 6, ptr noundef nonnull %1) #5
  br label %.preheader52

.preheader52:                                     ; preds = %131, %107
  %.03176 = phi i32 [ 0, %107 ], [ %132, %131 ]
  br label %109

.preheader51:                                     ; preds = %131
  br label %.preheader50

109:                                              ; preds = %128, %.preheader52
  %.03275 = phi i32 [ 0, %.preheader52 ], [ %129, %128 ]
  %110 = shl nuw nsw i32 %.03176, 12
  %111 = or disjoint i32 %.03275, %110
  %112 = zext nneg i32 %111 to i64
  %113 = getelementptr inbounds float, ptr %17, i64 %112
  store float 0.000000e+00, ptr %113, align 4
  br label %114

114:                                              ; preds = %114, %109
  %.03374 = phi i32 [ 0, %109 ], [ %126, %114 ]
  %115 = or disjoint i32 %.03374, %110
  %116 = zext nneg i32 %115 to i64
  %117 = getelementptr inbounds float, ptr %3, i64 %116
  %118 = load float, ptr %117, align 4
  %119 = shl nuw nsw i32 %.03374, 12
  %120 = add nuw nsw i32 %119, %.03275
  %121 = zext nneg i32 %120 to i64
  %122 = getelementptr inbounds float, ptr %10, i64 %121
  %123 = load float, ptr %122, align 4
  %124 = load float, ptr %113, align 4
  %125 = call float @llvm.fmuladd.f32(float %118, float %123, float %124)
  store float %125, ptr %113, align 4
  %126 = add nuw nsw i32 %.03374, 1
  %127 = icmp ult i32 %.03374, 4095
  br i1 %127, label %114, label %128, !llvm.loop !22

128:                                              ; preds = %114
  %129 = add nuw nsw i32 %.03275, 1
  %130 = icmp ult i32 %.03275, 4095
  br i1 %130, label %109, label %131, !llvm.loop !23

131:                                              ; preds = %128
  %132 = add nuw nsw i32 %.03176, 1
  %133 = icmp ult i32 %.03176, 2047
  br i1 %133, label %.preheader52, label %.preheader51, !llvm.loop !24

.preheader50:                                     ; preds = %156, %.preheader51
  %.03473 = phi i32 [ 0, %.preheader51 ], [ %157, %156 ]
  br label %134

.preheader49:                                     ; preds = %156
  br label %.preheader48

134:                                              ; preds = %153, %.preheader50
  %.03572 = phi i32 [ 0, %.preheader50 ], [ %154, %153 ]
  %135 = shl nuw nsw i32 %.03473, 12
  %136 = or disjoint i32 %.03572, %135
  %137 = zext nneg i32 %136 to i64
  %138 = getelementptr inbounds float, ptr %31, i64 %137
  store float 0.000000e+00, ptr %138, align 4
  br label %139

139:                                              ; preds = %139, %134
  %.03671 = phi i32 [ 0, %134 ], [ %151, %139 ]
  %140 = or disjoint i32 %.03671, %135
  %141 = zext nneg i32 %140 to i64
  %142 = getelementptr inbounds float, ptr %3, i64 %141
  %143 = load float, ptr %142, align 4
  %144 = shl nuw nsw i32 %.03671, 12
  %145 = add nuw nsw i32 %144, %.03572
  %146 = zext nneg i32 %145 to i64
  %147 = getelementptr inbounds float, ptr %24, i64 %146
  %148 = load float, ptr %147, align 4
  %149 = load float, ptr %138, align 4
  %150 = call float @llvm.fmuladd.f32(float %143, float %148, float %149)
  store float %150, ptr %138, align 4
  %151 = add nuw nsw i32 %.03671, 1
  %152 = icmp ult i32 %.03671, 4095
  br i1 %152, label %139, label %153, !llvm.loop !25

153:                                              ; preds = %139
  %154 = add nuw nsw i32 %.03572, 1
  %155 = icmp ult i32 %.03572, 4095
  br i1 %155, label %134, label %156, !llvm.loop !26

156:                                              ; preds = %153
  %157 = add nuw nsw i32 %.03473, 1
  %158 = icmp ult i32 %.03473, 2047
  br i1 %158, label %.preheader50, label %.preheader49, !llvm.loop !27

.preheader48:                                     ; preds = %181, %.preheader49
  %.03770 = phi i32 [ 0, %.preheader49 ], [ %182, %181 ]
  br label %159

.preheader47:                                     ; preds = %181
  br label %.preheader46

159:                                              ; preds = %178, %.preheader48
  %.03869 = phi i32 [ 0, %.preheader48 ], [ %179, %178 ]
  %160 = shl nuw nsw i32 %.03770, 12
  %161 = or disjoint i32 %.03869, %160
  %162 = zext nneg i32 %161 to i64
  %163 = getelementptr inbounds float, ptr %45, i64 %162
  store float 0.000000e+00, ptr %163, align 4
  br label %164

164:                                              ; preds = %164, %159
  %.02968 = phi i32 [ 0, %159 ], [ %176, %164 ]
  %165 = or disjoint i32 %.02968, %160
  %166 = zext nneg i32 %165 to i64
  %167 = getelementptr inbounds float, ptr %3, i64 %166
  %168 = load float, ptr %167, align 4
  %169 = shl nuw nsw i32 %.02968, 12
  %170 = add nuw nsw i32 %169, %.03869
  %171 = zext nneg i32 %170 to i64
  %172 = getelementptr inbounds float, ptr %38, i64 %171
  %173 = load float, ptr %172, align 4
  %174 = load float, ptr %163, align 4
  %175 = call float @llvm.fmuladd.f32(float %168, float %173, float %174)
  store float %175, ptr %163, align 4
  %176 = add nuw nsw i32 %.02968, 1
  %177 = icmp ult i32 %.02968, 4095
  br i1 %177, label %164, label %178, !llvm.loop !28

178:                                              ; preds = %164
  %179 = add nuw nsw i32 %.03869, 1
  %180 = icmp ult i32 %.03869, 4095
  br i1 %180, label %159, label %181, !llvm.loop !29

181:                                              ; preds = %178
  %182 = add nuw nsw i32 %.03770, 1
  %183 = icmp ult i32 %.03770, 2047
  br i1 %183, label %.preheader48, label %.preheader47, !llvm.loop !30

.preheader46:                                     ; preds = %207, %.preheader47
  %.02767 = phi i32 [ 0, %.preheader47 ], [ %208, %207 ]
  br label %184

.preheader45:                                     ; preds = %207
  br label %.preheader44

184:                                              ; preds = %204, %.preheader46
  %.02566 = phi i32 [ 0, %.preheader46 ], [ %205, %204 ]
  %185 = shl nuw nsw i32 %.02767, 11
  %186 = add nuw nsw i32 %.02566, %185
  %187 = zext nneg i32 %186 to i64
  %188 = getelementptr inbounds float, ptr %52, i64 %187
  store float 0.000000e+00, ptr %188, align 4
  br label %189

189:                                              ; preds = %189, %184
  %.02365 = phi i32 [ 0, %184 ], [ %202, %189 ]
  %190 = shl nuw nsw i32 %.02767, 12
  %191 = add nuw nsw i32 %.02365, %190
  %192 = zext nneg i32 %191 to i64
  %193 = getelementptr inbounds float, ptr %17, i64 %192
  %194 = load float, ptr %193, align 4
  %195 = shl nuw nsw i32 %.02566, 12
  %196 = add nuw nsw i32 %.02365, %195
  %197 = zext nneg i32 %196 to i64
  %198 = getelementptr inbounds float, ptr %31, i64 %197
  %199 = load float, ptr %198, align 4
  %200 = load float, ptr %188, align 4
  %201 = call float @llvm.fmuladd.f32(float %194, float %199, float %200)
  store float %201, ptr %188, align 4
  %202 = add nuw nsw i32 %.02365, 1
  %203 = icmp ult i32 %.02365, 4095
  br i1 %203, label %189, label %204, !llvm.loop !31

204:                                              ; preds = %189
  %205 = add nuw nsw i32 %.02566, 1
  %206 = icmp ult i32 %.02566, 2047
  br i1 %206, label %184, label %207, !llvm.loop !32

207:                                              ; preds = %204
  %208 = add nuw nsw i32 %.02767, 1
  %209 = icmp ult i32 %.02767, 2047
  br i1 %209, label %.preheader46, label %.preheader45, !llvm.loop !33

.preheader44:                                     ; preds = %233, %.preheader45
  %.02164 = phi i32 [ 0, %.preheader45 ], [ %234, %233 ]
  br label %210

.preheader43:                                     ; preds = %233
  br label %.preheader42

210:                                              ; preds = %230, %.preheader44
  %.01963 = phi i32 [ 0, %.preheader44 ], [ %231, %230 ]
  %211 = shl nuw nsw i32 %.02164, 12
  %212 = add nuw nsw i32 %.01963, %211
  %213 = zext nneg i32 %212 to i64
  %214 = getelementptr inbounds float, ptr %59, i64 %213
  store float 0.000000e+00, ptr %214, align 4
  br label %215

215:                                              ; preds = %215, %210
  %.01762 = phi i32 [ 0, %210 ], [ %228, %215 ]
  %216 = shl nuw nsw i32 %.02164, 11
  %217 = add nuw nsw i32 %.01762, %216
  %218 = zext nneg i32 %217 to i64
  %219 = getelementptr inbounds float, ptr %52, i64 %218
  %220 = load float, ptr %219, align 4
  %221 = shl nuw nsw i32 %.01762, 12
  %222 = add nuw nsw i32 %221, %.01963
  %223 = zext nneg i32 %222 to i64
  %224 = getelementptr inbounds float, ptr %45, i64 %223
  %225 = load float, ptr %224, align 4
  %226 = load float, ptr %214, align 4
  %227 = call float @llvm.fmuladd.f32(float %220, float %225, float %226)
  store float %227, ptr %214, align 4
  %228 = add nuw nsw i32 %.01762, 1
  %229 = icmp ult i32 %.01762, 2047
  br i1 %229, label %215, label %230, !llvm.loop !34

230:                                              ; preds = %215
  %231 = add nuw nsw i32 %.01963, 1
  %232 = icmp ult i32 %.01963, 4095
  br i1 %232, label %210, label %233, !llvm.loop !35

233:                                              ; preds = %230
  %234 = add nuw nsw i32 %.02164, 1
  %235 = icmp ult i32 %.02164, 2047
  br i1 %235, label %.preheader44, label %.preheader43, !llvm.loop !36

.preheader42:                                     ; preds = %258, %.preheader43
  %.01561 = phi i32 [ 0, %.preheader43 ], [ %259, %258 ]
  br label %236

.preheader41:                                     ; preds = %258
  br label %.preheader40

236:                                              ; preds = %255, %.preheader42
  %.01360 = phi i32 [ 0, %.preheader42 ], [ %256, %255 ]
  %237 = shl nuw nsw i32 %.01561, 12
  %238 = or disjoint i32 %.01360, %237
  %239 = zext nneg i32 %238 to i64
  %240 = getelementptr inbounds float, ptr %73, i64 %239
  store float 0.000000e+00, ptr %240, align 4
  br label %241

241:                                              ; preds = %241, %236
  %.01159 = phi i32 [ 0, %236 ], [ %253, %241 ]
  %242 = or disjoint i32 %.01159, %237
  %243 = zext nneg i32 %242 to i64
  %244 = getelementptr inbounds float, ptr %59, i64 %243
  %245 = load float, ptr %244, align 4
  %246 = shl nuw nsw i32 %.01159, 12
  %247 = add nuw nsw i32 %246, %.01360
  %248 = zext nneg i32 %247 to i64
  %249 = getelementptr inbounds float, ptr %66, i64 %248
  %250 = load float, ptr %249, align 4
  %251 = load float, ptr %240, align 4
  %252 = call float @llvm.fmuladd.f32(float %245, float %250, float %251)
  store float %252, ptr %240, align 4
  %253 = add nuw nsw i32 %.01159, 1
  %254 = icmp ult i32 %.01159, 4095
  br i1 %254, label %241, label %255, !llvm.loop !37

255:                                              ; preds = %241
  %256 = add nuw nsw i32 %.01360, 1
  %257 = icmp ult i32 %.01360, 4095
  br i1 %257, label %236, label %258, !llvm.loop !38

258:                                              ; preds = %255
  %259 = add nuw nsw i32 %.01561, 1
  %260 = icmp ult i32 %.01561, 2047
  br i1 %260, label %.preheader42, label %.preheader41, !llvm.loop !39

.preheader40:                                     ; preds = %284, %.preheader41
  %.0958 = phi i32 [ 0, %.preheader41 ], [ %285, %284 ]
  br label %261

.preheader39:                                     ; preds = %284
  br label %.preheader

261:                                              ; preds = %281, %.preheader40
  %.0757 = phi i32 [ 0, %.preheader40 ], [ %282, %281 ]
  %262 = shl nuw nsw i32 %.0958, 14
  %263 = add nuw nsw i32 %.0757, %262
  %264 = zext nneg i32 %263 to i64
  %265 = getelementptr inbounds float, ptr %87, i64 %264
  store float 0.000000e+00, ptr %265, align 4
  br label %266

266:                                              ; preds = %266, %261
  %.0556 = phi i32 [ 0, %261 ], [ %279, %266 ]
  %267 = shl nuw nsw i32 %.0958, 12
  %268 = add nuw nsw i32 %.0556, %267
  %269 = zext nneg i32 %268 to i64
  %270 = getelementptr inbounds float, ptr %73, i64 %269
  %271 = load float, ptr %270, align 4
  %272 = shl nuw nsw i32 %.0556, 14
  %273 = add nuw nsw i32 %272, %.0757
  %274 = zext nneg i32 %273 to i64
  %275 = getelementptr inbounds float, ptr %80, i64 %274
  %276 = load float, ptr %275, align 4
  %277 = load float, ptr %265, align 4
  %278 = call float @llvm.fmuladd.f32(float %271, float %276, float %277)
  store float %278, ptr %265, align 4
  %279 = add nuw nsw i32 %.0556, 1
  %280 = icmp ult i32 %.0556, 4095
  br i1 %280, label %266, label %281, !llvm.loop !40

281:                                              ; preds = %266
  %282 = add nuw nsw i32 %.0757, 1
  %283 = icmp ult i32 %.0757, 16383
  br i1 %283, label %261, label %284, !llvm.loop !41

284:                                              ; preds = %281
  %285 = add nuw nsw i32 %.0958, 1
  %286 = icmp ult i32 %.0958, 2047
  br i1 %286, label %.preheader40, label %.preheader39, !llvm.loop !42

.preheader:                                       ; preds = %310, %.preheader39
  %.0355 = phi i32 [ 0, %.preheader39 ], [ %311, %310 ]
  br label %287

287:                                              ; preds = %307, %.preheader
  %.0154 = phi i32 [ 0, %.preheader ], [ %308, %307 ]
  %288 = shl nuw nsw i32 %.0355, 12
  %289 = add nuw nsw i32 %.0154, %288
  %290 = zext nneg i32 %289 to i64
  %291 = getelementptr inbounds float, ptr %101, i64 %290
  store float 0.000000e+00, ptr %291, align 4
  br label %292

292:                                              ; preds = %292, %287
  %.053 = phi i32 [ 0, %287 ], [ %305, %292 ]
  %293 = shl nuw nsw i32 %.0355, 14
  %294 = add nuw nsw i32 %.053, %293
  %295 = zext nneg i32 %294 to i64
  %296 = getelementptr inbounds float, ptr %87, i64 %295
  %297 = load float, ptr %296, align 4
  %298 = shl nuw nsw i32 %.053, 12
  %299 = add nuw nsw i32 %298, %.0154
  %300 = zext nneg i32 %299 to i64
  %301 = getelementptr inbounds float, ptr %94, i64 %300
  %302 = load float, ptr %301, align 4
  %303 = load float, ptr %291, align 4
  %304 = call float @llvm.fmuladd.f32(float %297, float %302, float %303)
  store float %304, ptr %291, align 4
  %305 = add nuw nsw i32 %.053, 1
  %306 = icmp ult i32 %.053, 16383
  br i1 %306, label %292, label %307, !llvm.loop !43

307:                                              ; preds = %292
  %308 = add nuw nsw i32 %.0154, 1
  %309 = icmp ult i32 %.0154, 4095
  br i1 %309, label %287, label %310, !llvm.loop !44

310:                                              ; preds = %307
  %311 = add nuw nsw i32 %.0355, 1
  %312 = icmp ult i32 %.0355, 2047
  br i1 %312, label %.preheader, label %313, !llvm.loop !45

313:                                              ; preds = %310
  %314 = call i32 @clock_gettime(i32 noundef 6, ptr noundef nonnull %2) #5
  %315 = load i64, ptr %2, align 8
  %316 = load i64, ptr %1, align 8
  %317 = sub nsw i64 %315, %316
  %318 = sitofp i64 %317 to double
  %319 = getelementptr inbounds %struct.timespec, ptr %2, i64 0, i32 1
  %320 = load i64, ptr %319, align 8
  %321 = getelementptr inbounds %struct.timespec, ptr %1, i64 0, i32 1
  %322 = load i64, ptr %321, align 8
  %323 = sub nsw i64 %320, %322
  %324 = sitofp i64 %323 to double
  %325 = call double @llvm.fmuladd.f64(double %324, double 1.000000e-09, double %318)
  %326 = call i32 (ptr, ...) @printf(ptr noundef nonnull dereferenceable(1) @.str, double noundef %325) #5
  ret i32 0
}

; Function Attrs: allocsize(0)
declare ptr @malloc(i64 noundef) #1

declare i32 @clock_gettime(i32 noundef, ptr noundef) #2

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fmuladd.f32(float, float, float) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.fmuladd.f64(double, double, double) #3

declare i32 @printf(ptr noundef, ...) #2

attributes #0 = { noinline nounwind ssp uwtable(sync) "frame-pointer"="non-leaf" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+complxnum,+crc,+dotprod,+fp-armv8,+fp16fml,+fullfp16,+jsconv,+lse,+neon,+pauth,+ras,+rcpc,+rdm,+sha2,+sha3,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }
attributes #1 = { allocsize(0) "frame-pointer"="non-leaf" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+complxnum,+crc,+dotprod,+fp-armv8,+fp16fml,+fullfp16,+jsconv,+lse,+neon,+pauth,+ras,+rcpc,+rdm,+sha2,+sha3,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }
attributes #2 = { "frame-pointer"="non-leaf" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+complxnum,+crc,+dotprod,+fp-armv8,+fp16fml,+fullfp16,+jsconv,+lse,+neon,+pauth,+ras,+rcpc,+rdm,+sha2,+sha3,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }
attributes #3 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #4 = { nounwind allocsize(0) }
attributes #5 = { nounwind }

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 2, !"SDK Version", [2 x i32] [i32 15, i32 5]}
!1 = !{i32 1, !"wchar_size", i32 4}
!2 = !{i32 8, !"PIC Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 1}
!4 = !{i32 7, !"frame-pointer", i32 1}
!5 = !{!"clang version 18.1.8 (https://github.com/llvm/llvm-project.git 3b5b5c1ec4a3095ab096dd780e84d7ab81f3d7ff)"}
!6 = distinct !{!6, !7}
!7 = !{!"llvm.loop.mustprogress"}
!8 = distinct !{!8, !7}
!9 = distinct !{!9, !7}
!10 = distinct !{!10, !7}
!11 = distinct !{!11, !7}
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
!35 = distinct !{!35, !7}
!36 = distinct !{!36, !7}
!37 = distinct !{!37, !7}
!38 = distinct !{!38, !7}
!39 = distinct !{!39, !7}
!40 = distinct !{!40, !7}
!41 = distinct !{!41, !7}
!42 = distinct !{!42, !7}
!43 = distinct !{!43, !7}
!44 = distinct !{!44, !7}
!45 = distinct !{!45, !7}
