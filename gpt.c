
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
void einsum_0(float * restrict L0_X, float * restrict L0_WQ, float * restrict L0_Q) {
for (int m = 0; m < 2048; m++) {
for (int k = 0; k < 4096; k++) {
float acc = 0.0f;
for (int d = 0; d < 4096; d++) {
acc += L0_X[m * 4096 + d * 1] * L0_WQ[d * 4096 + k * 1];
}
L0_Q[m * 4096 + k * 1] = acc;
}
}
}

void einsum_1(float * restrict L0_X, float * restrict L0_WK, float * restrict L0_K) {
for (int m = 0; m < 2048; m++) {
for (int k = 0; k < 4096; k++) {
float acc = 0.0f;
for (int d = 0; d < 4096; d++) {
acc += L0_X[m * 4096 + d * 1] * L0_WK[d * 4096 + k * 1];
}
L0_K[m * 4096 + k * 1] = acc;
}
}
}

void einsum_2(float * restrict L0_X, float * restrict L0_WV, float * restrict L0_V) {
for (int m = 0; m < 2048; m++) {
for (int k = 0; k < 4096; k++) {
float acc = 0.0f;
for (int d = 0; d < 4096; d++) {
acc += L0_X[m * 4096 + d * 1] * L0_WV[d * 4096 + k * 1];
}
L0_V[m * 4096 + k * 1] = acc;
}
}
}

void einsum_3(float * restrict L0_Q, float * restrict L0_K, float * restrict L0_S) {
for (int m = 0; m < 2048; m++) {
for (int n = 0; n < 2048; n++) {
float acc = 0.0f;
for (int k = 0; k < 4096; k++) {
acc += L0_Q[m * 4096 + k * 1] * L0_K[n * 4096 + k * 1];
}
L0_S[m * 2048 + n * 1] = acc;
}
}
}

void einsum_4(float * restrict L0_S, float * restrict L0_V, float * restrict L0_O) {
for (int m = 0; m < 2048; m++) {
for (int k = 0; k < 4096; k++) {
float acc = 0.0f;
for (int n = 0; n < 2048; n++) {
acc += L0_S[m * 2048 + n * 1] * L0_V[n * 4096 + k * 1];
}
L0_O[m * 4096 + k * 1] = acc;
}
}
}

void einsum_5(float * restrict L0_O, float * restrict L0_Wo, float * restrict L0_Y) {
for (int m = 0; m < 2048; m++) {
for (int d = 0; d < 4096; d++) {
float acc = 0.0f;
for (int k = 0; k < 4096; k++) {
acc += L0_O[m * 4096 + k * 1] * L0_Wo[k * 4096 + d * 1];
}
L0_Y[m * 4096 + d * 1] = acc;
}
}
}

void einsum_6(float * restrict L0_Y, float * restrict L0_W1, float * restrict L0_H) {
for (int m = 0; m < 2048; m++) {
for (int f = 0; f < 16384; f++) {
float acc = 0.0f;
for (int d = 0; d < 4096; d++) {
acc += L0_Y[m * 4096 + d * 1] * L0_W1[d * 16384 + f * 1];
}
L0_H[m * 16384 + f * 1] = acc;
}
}
}

void einsum_7(float * restrict L0_H, float * restrict L0_W2, float * restrict L0_Z) {
for (int m = 0; m < 2048; m++) {
for (int d = 0; d < 4096; d++) {
float acc = 0.0f;
for (int f = 0; f < 16384; f++) {
acc += L0_H[m * 16384 + f * 1] * L0_W2[f * 4096 + d * 1];
}
L0_Z[m * 4096 + d * 1] = acc;
}
}
}

int main() {
float * restrict L0_X = (float*)malloc(sizeof(float) * 8388608);

    for (int i = 0; i < 8388608; i++)
        L0_X[i] = 1.0f;
    
float * restrict L0_WQ = (float*)malloc(sizeof(float) * 16777216);

    for (int i = 0; i < 16777216; i++)
        L0_WQ[i] = 1.0f;
    
float * restrict L0_Q = (float*)malloc(sizeof(float) * 8388608);

    for (int i = 0; i < 8388608; i++)
        L0_Q[i] = 1.0f;
    
float * restrict L0_WK = (float*)malloc(sizeof(float) * 16777216);

    for (int i = 0; i < 16777216; i++)
        L0_WK[i] = 1.0f;
    
float * restrict L0_K = (float*)malloc(sizeof(float) * 8388608);

    for (int i = 0; i < 8388608; i++)
        L0_K[i] = 1.0f;
    
float * restrict L0_WV = (float*)malloc(sizeof(float) * 16777216);

    for (int i = 0; i < 16777216; i++)
        L0_WV[i] = 1.0f;
    
float * restrict L0_V = (float*)malloc(sizeof(float) * 8388608);

    for (int i = 0; i < 8388608; i++)
        L0_V[i] = 1.0f;
    
float * restrict L0_S = (float*)malloc(sizeof(float) * 4194304);

    for (int i = 0; i < 4194304; i++)
        L0_S[i] = 1.0f;
    
float * restrict L0_O = (float*)malloc(sizeof(float) * 8388608);

    for (int i = 0; i < 8388608; i++)
        L0_O[i] = 1.0f;
    
float * restrict L0_Wo = (float*)malloc(sizeof(float) * 16777216);

    for (int i = 0; i < 16777216; i++)
        L0_Wo[i] = 1.0f;
    
float * restrict L0_Y = (float*)malloc(sizeof(float) * 8388608);

    for (int i = 0; i < 8388608; i++)
        L0_Y[i] = 1.0f;
    
float * restrict L0_W1 = (float*)malloc(sizeof(float) * 67108864);

    for (int i = 0; i < 67108864; i++)
        L0_W1[i] = 1.0f;
    
float * restrict L0_H = (float*)malloc(sizeof(float) * 33554432);

    for (int i = 0; i < 33554432; i++)
        L0_H[i] = 1.0f;
    
float * restrict L0_W2 = (float*)malloc(sizeof(float) * 67108864);

    for (int i = 0; i < 67108864; i++)
        L0_W2[i] = 1.0f;
    
float * restrict L0_Z = (float*)malloc(sizeof(float) * 8388608);

    for (int i = 0; i < 8388608; i++)
        L0_Z[i] = 1.0f;
    

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);
    einsum_0(L0_X, L0_WQ, L0_Q);
einsum_1(L0_X, L0_WK, L0_K);
einsum_2(L0_X, L0_WV, L0_V);
einsum_3(L0_Q, L0_K, L0_S);
einsum_4(L0_S, L0_V, L0_O);
einsum_5(L0_O, L0_Wo, L0_Y);
einsum_6(L0_Y, L0_W1, L0_H);
einsum_7(L0_H, L0_W2, L0_Z);

    clock_gettime(CLOCK_MONOTONIC, &end);
    double t = (end.tv_sec - start.tv_sec) +
               (end.tv_nsec - start.tv_nsec) * 1e-9;
    printf("Time: %f\n", t);
    return 0;
}
