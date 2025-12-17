#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void einsum_0(float * restrict L0_Q, float * restrict L0_WQ, float * restrict L0_X) {
    for (int m0 = 0; m0 < 128; m0 += 64) {
        for (int k0 = 0; k0 < 512; k0 += 102) {
            for (int d0 = 0; d0 < 512; d0 += 1) {
                for (int m1 = 0; m1 < 64; m1 += 1) {
                    for (int m1_i = 0; m1_i < ((m1 + 1 <= 128) ? 1 : (128 - m1)); m1_i++) {
                        int m = m1 + m0 + m1_i;
                        for (int k0_i = 0; k0_i < ((k0 + 102 <= 512) ? 102 : (512 - k0)); k0_i++) {
                            int k = k0 + k0_i;
                            for (int d0_i = 0; d0_i < ((d0 + 1 <= 512) ? 1 : (512 - d0)); d0_i++) {
                                int d = d0 + d0_i;
                                L0_Q[m * 512 + k * 1] += L0_WQ[d * 512 + k * 1] * L0_X[m * 512 + d * 1];
                            }
                        }
                    }
                }
            }
        }
    }
}

void einsum_1(float * restrict L0_S, float * restrict L0_Q, float * restrict L0_K) {
    for (int m0 = 0; m0 < 128; m0 += 64) {
        for (int k0 = 0; k0 < 512; k0 += 102) {
            for (int n0 = 0; n0 < 128; n0 += 1) {
                for (int k1 = 0; k1 < 102; k1 += 1) {
                    for (int m0_i = 0; m0_i < ((m0 + 64 <= 128) ? 64 : (128 - m0)); m0_i++) {
                        int m = m0 + m0_i;
                        for (int k1_i = 0; k1_i < ((k1 + 1 <= 512) ? 1 : (512 - k1)); k1_i++) {
                            int k = k1 + k0 + k1_i;
                            for (int n0_i = 0; n0_i < ((n0 + 1 <= 128) ? 1 : (128 - n0)); n0_i++) {
                                int n = n0 + n0_i;
                                L0_S[m * 128 + n * 1] += L0_Q[m * 512 + k * 1] * L0_K[n * 512 + k * 1];
                            }
                        }
                    }
                }
            }
        }
    }
}

void einsum_2(float * restrict L0_S, float * restrict L0_V, float * restrict L0_O) {
    for (int m0 = 0; m0 < 128; m0 += 64) {
        for (int k0 = 0; k0 < 512; k0 += 1) {
            for (int m1 = 0; m1 < 64; m1 += 1) {
                for (int m1_i = 0; m1_i < ((m1 + 1 <= 128) ? 1 : (128 - m1)); m1_i++) {
                    int m = m1 + m0 + m1_i;
                    for (int k0_i = 0; k0_i < ((k0 + 1 <= 512) ? 1 : (512 - k0)); k0_i++) {
                        int k = k0 + k0_i;
                        for (int n = 0; n < 128; n++) {
                        L0_O[m * 512 + k * 1] += L0_S[m * 128 + n * 1] * L0_V[n * 512 + k * 1];
                        }
                    }
                }
            }
        }
    }
}

int main() {

        struct timespec start, end;
        clock_gettime(CLOCK_MONOTONIC, &start);
        float * restrict L0_X = (float*)malloc(sizeof(float) * 65536);

    for (int i = 0; i < 65536; i++)
        L0_X[i] = 1.0f;
    
        float * restrict L0_WQ = (float*)malloc(sizeof(float) * 262144);

    for (int i = 0; i < 262144; i++)
        L0_WQ[i] = 1.0f;
    
        float * restrict L0_Q = (float*)malloc(sizeof(float) * 65536);

    for (int i = 0; i < 65536; i++)
        L0_Q[i] = 1.0f;
    
        float * restrict L0_K = (float*)malloc(sizeof(float) * 65536);

    for (int i = 0; i < 65536; i++)
        L0_K[i] = 1.0f;
    
        float * restrict L0_S = (float*)malloc(sizeof(float) * 16384);

    for (int i = 0; i < 16384; i++)
        L0_S[i] = 1.0f;
    
        float * restrict L0_V = (float*)malloc(sizeof(float) * 65536);

    for (int i = 0; i < 65536; i++)
        L0_V[i] = 1.0f;
    
        float * restrict L0_O = (float*)malloc(sizeof(float) * 65536);

    for (int i = 0; i < 65536; i++)
        L0_O[i] = 1.0f;
    
einsum_0(L0_Q, L0_WQ, L0_X);
einsum_1(L0_S, L0_Q, L0_K);
einsum_2(L0_S, L0_V, L0_O);

        clock_gettime(CLOCK_MONOTONIC, &end);
        double t = (end.tv_sec - start.tv_sec) +
                   (end.tv_nsec - start.tv_nsec) * 1e-9;
        printf("Time: %f\n", t);
        return 0;
}