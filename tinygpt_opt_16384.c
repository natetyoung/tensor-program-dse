#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void einsum_0(float * restrict L0_X, float * restrict L0_Q, float * restrict L0_WQ) {
    for (int k0 = 0; k0 < 128; k0 += 1) {
        for (int k0_i = 0; k0_i < ((k0 + 1 <= 128) ? 1 : (128 - k0)); k0_i++) {
            int k = k0 + k0_i;
            float acc = 0.0f;
            for (int d = 0; d < 128; d++) {
            for (int m = 0; m < 32; m++) {
            acc += L0_X[m * 128 + d * 1] * L0_Q[m * 128 + k * 1];
            }
            L0_WQ[d * 128 + k * 1] = acc;
            }
        }
    }
}

void einsum_1(float * restrict L0_S, float * restrict L0_Q, float * restrict L0_K) {
    for (int k0 = 0; k0 < 128; k0 += 1) {
        for (int k0_i = 0; k0_i < ((k0 + 1 <= 128) ? 1 : (128 - k0)); k0_i++) {
            int k = k0 + k0_i;
            float acc = 0.0f;
            for (int n = 0; n < 32; n++) {
            for (int m = 0; m < 32; m++) {
            acc += L0_S[m * 32 + n * 1] * L0_Q[m * 128 + k * 1];
            }
            L0_K[n * 128 + k * 1] = acc;
            }
        }
    }
}

void einsum_2(float * restrict L0_S, float * restrict L0_V, float * restrict L0_O) {
    for (int k0 = 0; k0 < 128; k0 += 1) {
        for (int k0_i = 0; k0_i < ((k0 + 1 <= 128) ? 1 : (128 - k0)); k0_i++) {
            int k = k0 + k0_i;
            float acc = 0.0f;
            for (int m = 0; m < 32; m++) {
            for (int n = 0; n < 32; n++) {
            acc += L0_S[m * 32 + n * 1] * L0_V[n * 128 + k * 1];
            }
            L0_O[m * 128 + k * 1] = acc;
            }
        }
    }
}

void einsum_3(float * restrict L0_Y, float * restrict L0_Wo, float * restrict L0_O) {
    for (int k0 = 0; k0 < 128; k0 += 1) {
        for (int k0_i = 0; k0_i < ((k0 + 1 <= 128) ? 1 : (128 - k0)); k0_i++) {
            int k = k0 + k0_i;
            float acc = 0.0f;
            for (int m = 0; m < 32; m++) {
            for (int d = 0; d < 128; d++) {
            acc += L0_Y[m * 128 + d * 1] * L0_Wo[k * 128 + d * 1];
            }
            L0_O[m * 128 + k * 1] = acc;
            }
        }
    }
}

void einsum_4(float * restrict L0_Y, float * restrict L0_H, float * restrict L0_W1) {
    for (int f0 = 0; f0 < 512; f0 += 1) {
        for (int d0 = 0; d0 < 128; d0 += 1) {
            for (int f0_i = 0; f0_i < ((f0 + 1 <= 512) ? 1 : (512 - f0)); f0_i++) {
                int f = f0 + f0_i;
                for (int d0_i = 0; d0_i < ((d0 + 1 <= 128) ? 1 : (128 - d0)); d0_i++) {
                    int d = d0 + d0_i;
                    float acc = 0.0f;
                    for (int m = 0; m < 32; m++) {
                    acc += L0_Y[m * 128 + d * 1] * L0_H[m * 512 + f * 1];
                    }
                    L0_W1[d * 512 + f * 1] = acc;
                }
            }
        }
    }
}

void einsum_5(float * restrict L0_Z, float * restrict L0_W2, float * restrict L0_H) {
    for (int f0 = 0; f0 < 512; f0 += 1) {
        for (int f0_i = 0; f0_i < ((f0 + 1 <= 512) ? 1 : (512 - f0)); f0_i++) {
            int f = f0 + f0_i;
            float acc = 0.0f;
            for (int m = 0; m < 32; m++) {
            for (int d = 0; d < 128; d++) {
            acc += L0_Z[m * 128 + d * 1] * L0_W2[f * 128 + d * 1];
            }
            L0_H[m * 512 + f * 1] = acc;
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
    
        float * restrict L0_Wo = (float*)malloc(sizeof(float) * 16384);

    for (int i = 0; i < 16384; i++)
        L0_Wo[i] = 1.0f;
    
        float * restrict L0_Y = (float*)malloc(sizeof(float) * 4096);

    for (int i = 0; i < 4096; i++)
        L0_Y[i] = 1.0f;
    
        float * restrict L0_W1 = (float*)malloc(sizeof(float) * 65536);

    for (int i = 0; i < 65536; i++)
        L0_W1[i] = 1.0f;
    
        float * restrict L0_H = (float*)malloc(sizeof(float) * 16384);

    for (int i = 0; i < 16384; i++)
        L0_H[i] = 1.0f;
    
        float * restrict L0_W2 = (float*)malloc(sizeof(float) * 65536);

    for (int i = 0; i < 65536; i++)
        L0_W2[i] = 1.0f;
    
        float * restrict L0_Z = (float*)malloc(sizeof(float) * 4096);

    for (int i = 0; i < 4096; i++)
        L0_Z[i] = 1.0f;
    
einsum_0(L0_X, L0_Q, L0_WQ);
einsum_1(L0_S, L0_Q, L0_K);
einsum_2(L0_S, L0_V, L0_O);
einsum_3(L0_Y, L0_Wo, L0_O);
einsum_4(L0_Y, L0_H, L0_W1);
einsum_5(L0_Z, L0_W2, L0_H);

        clock_gettime(CLOCK_MONOTONIC, &end);
        double t = (end.tv_sec - start.tv_sec) +
                   (end.tv_nsec - start.tv_nsec) * 1e-9;
        printf("Time: %f\n", t);
        return 0;
}