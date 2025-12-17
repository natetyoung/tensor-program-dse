
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void einsum_0(float * restrict L0_X, float * restrict L0_WQ, float * restrict L0_Q) {
for (int m = 0; m < 64; m++) {
for (int k = 0; k < 256; k++) {
float acc = 0.0f;
for (int d = 0; d < 256; d++) {
acc += L0_X[m * 256 + d * 1] * L0_WQ[d * 256 + k * 1];
}
L0_Q[m * 256 + k * 1] = acc;
}
}
}

void einsum_1(float * restrict L0_Q, float * restrict L0_K, float * restrict L0_S) {
for (int m = 0; m < 64; m++) {
for (int n = 0; n < 64; n++) {
float acc = 0.0f;
for (int k = 0; k < 256; k++) {
acc += L0_Q[m * 256 + k * 1] * L0_K[n * 256 + k * 1];
}
L0_S[m * 64 + n * 1] = acc;
}
}
}

void einsum_2(float * restrict L0_S, float * restrict L0_V, float * restrict L0_O) {
for (int m = 0; m < 64; m++) {
for (int k = 0; k < 256; k++) {
float acc = 0.0f;
for (int n = 0; n < 64; n++) {
acc += L0_S[m * 64 + n * 1] * L0_V[n * 256 + k * 1];
}
L0_O[m * 256 + k * 1] = acc;
}
}
}

int main() {

        struct timespec start, end;
        clock_gettime(CLOCK_MONOTONIC, &start);
        float * restrict L0_X = (float*)malloc(sizeof(float) * 16384);

    for (int i = 0; i < 16384; i++)
        L0_X[i] = 1.0f;
    
float * restrict L0_WQ = (float*)malloc(sizeof(float) * 65536);

    for (int i = 0; i < 65536; i++)
        L0_WQ[i] = 1.0f;
    
float * restrict L0_Q = (float*)malloc(sizeof(float) * 16384);

    for (int i = 0; i < 16384; i++)
        L0_Q[i] = 1.0f;
    
float * restrict L0_K = (float*)malloc(sizeof(float) * 16384);

    for (int i = 0; i < 16384; i++)
        L0_K[i] = 1.0f;
    
float * restrict L0_S = (float*)malloc(sizeof(float) * 4096);

    for (int i = 0; i < 4096; i++)
        L0_S[i] = 1.0f;
    
float * restrict L0_V = (float*)malloc(sizeof(float) * 16384);

    for (int i = 0; i < 16384; i++)
        L0_V[i] = 1.0f;
    
float * restrict L0_O = (float*)malloc(sizeof(float) * 16384);

    for (int i = 0; i < 16384; i++)
        L0_O[i] = 1.0f;
    
einsum_0(L0_X, L0_WQ, L0_Q);
einsum_1(L0_Q, L0_K, L0_S);
einsum_2(L0_S, L0_V, L0_O);

    clock_gettime(CLOCK_MONOTONIC, &end);
    double t = (end.tv_sec - start.tv_sec) +
               (end.tv_nsec - start.tv_nsec) * 1e-9;
    printf("Time: %f\n", t);
    printf("Test: %f\n", L0_O[0]);
    return 0;
}
