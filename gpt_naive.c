
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
int main() {
float *L0_X = (float*)malloc(sizeof(float) * 8388608);

    for (int i = 0; i < 8388608; i++)
        L0_X[i] = 1.0f;
    
float *L0_WQ = (float*)malloc(sizeof(float) * 16777216);

    for (int i = 0; i < 16777216; i++)
        L0_WQ[i] = 1.0f;
    
float *L0_Q = (float*)malloc(sizeof(float) * 8388608);

    for (int i = 0; i < 8388608; i++)
        L0_Q[i] = 1.0f;
    
float *L0_WK = (float*)malloc(sizeof(float) * 16777216);

    for (int i = 0; i < 16777216; i++)
        L0_WK[i] = 1.0f;
    
float *L0_K = (float*)malloc(sizeof(float) * 8388608);

    for (int i = 0; i < 8388608; i++)
        L0_K[i] = 1.0f;
    
float *L0_WV = (float*)malloc(sizeof(float) * 16777216);

    for (int i = 0; i < 16777216; i++)
        L0_WV[i] = 1.0f;
    
float *L0_V = (float*)malloc(sizeof(float) * 8388608);

    for (int i = 0; i < 8388608; i++)
        L0_V[i] = 1.0f;
    
float *L0_S = (float*)malloc(sizeof(float) * 4194304);

    for (int i = 0; i < 4194304; i++)
        L0_S[i] = 1.0f;
    
float *L0_O = (float*)malloc(sizeof(float) * 8388608);

    for (int i = 0; i < 8388608; i++)
        L0_O[i] = 1.0f;
    
float *L0_Wo = (float*)malloc(sizeof(float) * 16777216);

    for (int i = 0; i < 16777216; i++)
        L0_Wo[i] = 1.0f;
    
float *L0_Y = (float*)malloc(sizeof(float) * 8388608);

    for (int i = 0; i < 8388608; i++)
        L0_Y[i] = 1.0f;
    
float *L0_W1 = (float*)malloc(sizeof(float) * 67108864);

    for (int i = 0; i < 67108864; i++)
        L0_W1[i] = 1.0f;
    
float *L0_H = (float*)malloc(sizeof(float) * 33554432);

    for (int i = 0; i < 33554432; i++)
        L0_H[i] = 1.0f;
    
float *L0_W2 = (float*)malloc(sizeof(float) * 67108864);

    for (int i = 0; i < 67108864; i++)
        L0_W2[i] = 1.0f;
    
float *L0_Z = (float*)malloc(sizeof(float) * 8388608);

    for (int i = 0; i < 8388608; i++)
        L0_Z[i] = 1.0f;
    

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);
    for (int m = 0; m < 2048; m++) {
for (int k = 0; k < 4096; k++) {
L0_Q[m * 4096 + k * 1] = 0.0f;
for (int d = 0; d < 4096; d++) {
L0_Q[m * 4096 + k * 1] += L0_X[m * 4096 + d * 1] * L0_WQ[d * 4096 + k * 1];
}
}
}
for (int m = 0; m < 2048; m++) {
for (int k = 0; k < 4096; k++) {
L0_K[m * 4096 + k * 1] = 0.0f;
for (int d = 0; d < 4096; d++) {
L0_K[m * 4096 + k * 1] += L0_X[m * 4096 + d * 1] * L0_WK[d * 4096 + k * 1];
}
}
}
for (int m = 0; m < 2048; m++) {
for (int k = 0; k < 4096; k++) {
L0_V[m * 4096 + k * 1] = 0.0f;
for (int d = 0; d < 4096; d++) {
L0_V[m * 4096 + k * 1] += L0_X[m * 4096 + d * 1] * L0_WV[d * 4096 + k * 1];
}
}
}
for (int m = 0; m < 2048; m++) {
for (int n = 0; n < 2048; n++) {
L0_S[m * 2048 + n * 1] = 0.0f;
for (int k = 0; k < 4096; k++) {
L0_S[m * 2048 + n * 1] += L0_Q[m * 4096 + k * 1] * L0_K[n * 4096 + k * 1];
}
}
}
for (int m = 0; m < 2048; m++) {
for (int k = 0; k < 4096; k++) {
L0_O[m * 4096 + k * 1] = 0.0f;
for (int n = 0; n < 2048; n++) {
L0_O[m * 4096 + k * 1] += L0_S[m * 2048 + n * 1] * L0_V[n * 4096 + k * 1];
}
}
}
for (int m = 0; m < 2048; m++) {
for (int d = 0; d < 4096; d++) {
L0_Y[m * 4096 + d * 1] = 0.0f;
for (int k = 0; k < 4096; k++) {
L0_Y[m * 4096 + d * 1] += L0_O[m * 4096 + k * 1] * L0_Wo[k * 4096 + d * 1];
}
}
}
for (int m = 0; m < 2048; m++) {
for (int f = 0; f < 16384; f++) {
L0_H[m * 16384 + f * 1] = 0.0f;
for (int d = 0; d < 4096; d++) {
L0_H[m * 16384 + f * 1] += L0_Y[m * 4096 + d * 1] * L0_W1[d * 16384 + f * 1];
}
}
}
for (int m = 0; m < 2048; m++) {
for (int d = 0; d < 4096; d++) {
L0_Z[m * 4096 + d * 1] = 0.0f;
for (int f = 0; f < 16384; f++) {
L0_Z[m * 4096 + d * 1] += L0_H[m * 16384 + f * 1] * L0_W2[f * 4096 + d * 1];
}
}
}

    clock_gettime(CLOCK_MONOTONIC, &end);
    double t = (end.tv_sec - start.tv_sec) +
               (end.tv_nsec - start.tv_nsec) * 1e-9;
    printf("Time: %f\n", t);
    return 0;
}
