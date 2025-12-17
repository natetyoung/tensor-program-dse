#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void einsum_0(float * restrict L0_X, float * restrict L0_WQ, float * restrict L0_Q) {
    for (int k0 = 0; k0 < 128; k0 += 1) {
        for (int k0_i = 0; k0_i < ((k0 + 1 <= 128) ? 1 : (128 - k0)); k0_i++) {
            int k = k0 + k0_i;
            for (int m = 0; m < 32; m++) {
            for (int d = 0; d < 128; d++) {
            L0_Q[m * 128 + k * 1] += L0_X[m * 128 + d * 1] * L0_WQ[d * 128 + k * 1];
            }
            }
        }
    }
}

void einsum_1(float * restrict L0_S, float * restrict L0_Q, float * restrict L0_K) {
    for (int k0 = 0; k0 < 128; k0 += 1) {
        for (int n0 = 0; n0 < 32; n0 += 1) {
            for (int k0_i = 0; k0_i < ((k0 + 1 <= 128) ? 1 : (128 - k0)); k0_i++) {
                int k = k0 + k0_i;
                for (int n0_i = 0; n0_i < ((n0 + 1 <= 32) ? 1 : (32 - n0)); n0_i++) {
                    int n = n0 + n0_i;
                    for (int m = 0; m < 32; m++) {
                    L0_S[m * 32 + n * 1] += L0_Q[m * 128 + k * 1] * L0_K[n * 128 + k * 1];
                    }
                }
            }
        }
    }
}

void einsum_2(float * restrict L0_S, float * restrict L0_O, float * restrict L0_V) {
    for (int k0 = 0; k0 < 128; k0 += 1) {
        for (int n0 = 0; n0 < 32; n0 += 1) {
            for (int k0_i = 0; k0_i < ((k0 + 1 <= 128) ? 1 : (128 - k0)); k0_i++) {
                int k = k0 + k0_i;
                for (int n0_i = 0; n0_i < ((n0 + 1 <= 32) ? 1 : (32 - n0)); n0_i++) {
                    int n = n0 + n0_i;
                    for (int m = 0; m < 32; m++) {
                    L0_O[m * 128 + k * 1] += L0_S[m * 32 + n * 1] * L0_V[n * 128 + k * 1];
                    }
                }
            }
        }
    }
}

int main() {

        struct timespec start, end;
        clock_gettime(CLOCK_MONOTONIC, &start);
        float * restrict L0_X = (float*)malloc(sizeof(float) * 4096);

    for (int i = 0; i < 4096; i++)
        L0_X[i] = 1.0f;
    
        float * restrict L0_WQ = (float*)malloc(sizeof(float) * 16384);

    for (int i = 0; i < 16384; i++)
        L0_WQ[i] = 1.0f;
    
        float * restrict L0_Q = (float*)malloc(sizeof(float) * 4096);

    for (int i = 0; i < 4096; i++)
        L0_Q[i] = 1.0f;
    
        float * restrict L0_K = (float*)malloc(sizeof(float) * 4096);

    for (int i = 0; i < 4096; i++)
        L0_K[i] = 1.0f;
    
        float * restrict L0_S = (float*)malloc(sizeof(float) * 1024);

    for (int i = 0; i < 1024; i++)
        L0_S[i] = 1.0f;
    
        float * restrict L0_V = (float*)malloc(sizeof(float) * 4096);

    for (int i = 0; i < 4096; i++)
        L0_V[i] = 1.0f;
    
        float * restrict L0_O = (float*)malloc(sizeof(float) * 4096);

    for (int i = 0; i < 4096; i++)
        L0_O[i] = 1.0f;
    
einsum_0(L0_X, L0_WQ, L0_Q);
einsum_1(L0_S, L0_Q, L0_K);
einsum_2(L0_S, L0_O, L0_V);

        clock_gettime(CLOCK_MONOTONIC, &end);
        double t = (end.tv_sec - start.tv_sec) +
                   (end.tv_nsec - start.tv_nsec) * 1e-9;
        printf("Time: %f\n", t);
        return 0;
}