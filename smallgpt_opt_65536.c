#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void einsum_0(float * restrict L0_X, float * restrict L0_WQ, float * restrict L0_Q) {
    for (int m_wrap=0; m_wrap<64; m_wrap++) {
        int m_start = m_wrap * (64 / 64);
        int m_end = (m_wrap == 64-1 ? 64 : m_start + (64 / 64));
        for (int m=m_start; m<m_end; m++) {
            for (int k=0; k<256; k++) {
                float acc = 0.0f;
                for (int d=0; d<256; d++) {
                    acc += L0_X[m*256 + d*1] * L0_WQ[d*256 + k*1];
                }
                L0_Q[m*256 + k*1] = acc;
            }
        }
    }
}
void einsum_1(float * restrict L0_Q, float * restrict L0_K, float * restrict L0_S) {
    for (int m=0; m<64; m++) {
        for (int n=0; n<64; n++) {
            float acc = 0.0f;
            for (int k=0; k<256; k++) {
                acc += L0_Q[m*256 + k*1] * L0_K[n*256 + k*1];
            }
            L0_S[m*64 + n*1] = acc;
        }
    }
}
void einsum_2(float * restrict L0_S, float * restrict L0_V, float * restrict L0_O) {
    for (int k_wrap=0; k_wrap<256; k_wrap++) {
        int k_start = k_wrap * (256 / 256);
        int k_end = (k_wrap == 256-1 ? 256 : k_start + (256 / 256));
        for (int m=0; m<64; m++) {
            for (int k=k_start; k<k_end; k++) {
                float acc = 0.0f;
                for (int n=0; n<64; n++) {
                    acc += L0_S[m*64 + n*1] * L0_V[n*256 + k*1];
                }
                L0_O[m*256 + k*1] = acc;
            }
        }
    }
}
void einsum_3(float * restrict L0_O, float * restrict L0_Wo, float * restrict L0_Y) {
    for (int m=0; m<64; m++) {
        for (int d=0; d<256; d++) {
            float acc = 0.0f;
            for (int k=0; k<256; k++) {
                acc += L0_O[m*256 + k*1] * L0_Wo[k*256 + d*1];
            }
            L0_Y[m*256 + d*1] = acc;
        }
    }
}
void einsum_4(float * restrict L0_Y, float * restrict L0_W1, float * restrict L0_H) {
    for (int m_wrap=0; m_wrap<64; m_wrap++) {
        int m_start = m_wrap * (64 / 64);
        int m_end = (m_wrap == 64-1 ? 64 : m_start + (64 / 64));
        for (int m=m_start; m<m_end; m++) {
            for (int f=0; f<1024; f++) {
                float acc = 0.0f;
                for (int d=0; d<256; d++) {
                    acc += L0_Y[m*256 + d*1] * L0_W1[d*1024 + f*1];
                }
                L0_H[m*1024 + f*1] = acc;
            }
        }
    }
}
void einsum_5(float * restrict L0_H, float * restrict L0_W2, float * restrict L0_Z) {
    for (int m=0; m<64; m++) {
        for (int d=0; d<256; d++) {
            float acc = 0.0f;
            for (int f=0; f<1024; f++) {
                acc += L0_H[m*1024 + f*1] * L0_W2[f*256 + d*1];
            }
            L0_Z[m*256 + d*1] = acc;
        }
    }
}
int main() {
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    float * restrict L0_H = (float*)malloc(sizeof(float) * 65536);
    for (int i=0;i<65536;i++) L0_H[i] = 1.0f;

    float * restrict L0_K = (float*)malloc(sizeof(float) * 16384);
    for (int i=0;i<16384;i++) L0_K[i] = 1.0f;

    float * restrict L0_O = (float*)malloc(sizeof(float) * 16384);
    for (int i=0;i<16384;i++) L0_O[i] = 1.0f;

    float * restrict L0_Q = (float*)malloc(sizeof(float) * 16384);
    for (int i=0;i<16384;i++) L0_Q[i] = 1.0f;

    float * restrict L0_S = (float*)malloc(sizeof(float) * 4096);
    for (int i=0;i<4096;i++) L0_S[i] = 1.0f;

    float * restrict L0_V = (float*)malloc(sizeof(float) * 16384);
    for (int i=0;i<16384;i++) L0_V[i] = 1.0f;

    float * restrict L0_W1 = (float*)malloc(sizeof(float) * 262144);
    for (int i=0;i<262144;i++) L0_W1[i] = 1.0f;

    float * restrict L0_W2 = (float*)malloc(sizeof(float) * 262144);
    for (int i=0;i<262144;i++) L0_W2[i] = 1.0f;

    float * restrict L0_WQ = (float*)malloc(sizeof(float) * 65536);
    for (int i=0;i<65536;i++) L0_WQ[i] = 1.0f;

    float * restrict L0_Wo = (float*)malloc(sizeof(float) * 65536);
    for (int i=0;i<65536;i++) L0_Wo[i] = 1.0f;

    float * restrict L0_X = (float*)malloc(sizeof(float) * 16384);
    for (int i=0;i<16384;i++) L0_X[i] = 1.0f;

    float * restrict L0_Y = (float*)malloc(sizeof(float) * 16384);
    for (int i=0;i<16384;i++) L0_Y[i] = 1.0f;

    float * restrict L0_Z = (float*)malloc(sizeof(float) * 16384);
    for (int i=0;i<16384;i++) L0_Z[i] = 1.0f;

    einsum_0(L0_X, L0_WQ, L0_Q);
    einsum_1(L0_Q, L0_K, L0_S);
    einsum_2(L0_S, L0_V, L0_O);
    einsum_3(L0_O, L0_Wo, L0_Y);
    einsum_4(L0_Y, L0_W1, L0_H);
    einsum_5(L0_H, L0_W2, L0_Z);

    clock_gettime(CLOCK_MONOTONIC, &end);
    double t = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) * 1e-9;
    printf("Time: %f\n", t);
    return 0;
}
