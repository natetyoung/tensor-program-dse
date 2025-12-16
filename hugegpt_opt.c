#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void einsum_0(float * restrict L0_X, float * restrict L0_WQ, float * restrict L0_Q) {
    for (int t_d=0; t_d<4096; t_d++) {
        for (int s_m_L0_X=0; s_m_L0_X<2; s_m_L0_X++) {
            // LD/ST L0_X[(s_m_L0_X)*4096 + (t_d)*1]
            L0_X[(s_m_L0_X)*4096 + (t_d)*1] = L0_X[(s_m_L0_X)*4096 + (t_d)*1];
        }
        for (int s_k_L0_WQ=0; s_k_L0_WQ<4096; s_k_L0_WQ++) {
            // LD/ST L0_WQ[(t_d)*4096 + (s_k_L0_WQ)*1]
            L0_WQ[(t_d)*4096 + (s_k_L0_WQ)*1] = L0_WQ[(t_d)*4096 + (s_k_L0_WQ)*1];
        }
        for (int s_m_L0_Q=0; s_m_L0_Q<2; s_m_L0_Q++) {
            for (int s_k_L0_Q=0; s_k_L0_Q<4096; s_k_L0_Q++) {
                // LD/ST L0_Q[(s_m_L0_Q)*4096 + (s_k_L0_Q)*1]
                L0_Q[(s_m_L0_Q)*4096 + (s_k_L0_Q)*1] = L0_Q[(s_m_L0_Q)*4096 + (s_k_L0_Q)*1];
            }
        }
    }
}

void einsum_1(float * restrict L0_Q, float * restrict L0_K, float * restrict L0_S) {
    for (int s_m_L0_Q=0; s_m_L0_Q<2; s_m_L0_Q++) {
        for (int s_k_L0_Q=0; s_k_L0_Q<4096; s_k_L0_Q++) {
            // LD/ST L0_Q[(s_m_L0_Q)*4096 + (s_k_L0_Q)*1]
            L0_Q[(s_m_L0_Q)*4096 + (s_k_L0_Q)*1] = L0_Q[(s_m_L0_Q)*4096 + (s_k_L0_Q)*1];
        }
    }
    for (int s_n_L0_K=0; s_n_L0_K<2048; s_n_L0_K++) {
        // LD/ST L0_K[(s_n_L0_K)*4096]
        L0_K[(s_n_L0_K)*4096] = L0_K[(s_n_L0_K)*4096];
    }
    for (int s_m_L0_S=0; s_m_L0_S<2; s_m_L0_S++) {
        for (int s_n_L0_S=0; s_n_L0_S<2048; s_n_L0_S++) {
            // LD/ST L0_S[(s_m_L0_S)*2048 + (s_n_L0_S)*1]
            L0_S[(s_m_L0_S)*2048 + (s_n_L0_S)*1] = L0_S[(s_m_L0_S)*2048 + (s_n_L0_S)*1];
        }
    }
}

void einsum_2(float * restrict L0_S, float * restrict L0_V, float * restrict L0_O) {
    for (int s_m_L0_S=0; s_m_L0_S<2; s_m_L0_S++) {
        for (int s_n_L0_S=0; s_n_L0_S<2048; s_n_L0_S++) {
            // LD/ST L0_S[(s_m_L0_S)*2048 + (s_n_L0_S)*1]
            L0_S[(s_m_L0_S)*2048 + (s_n_L0_S)*1] = L0_S[(s_m_L0_S)*2048 + (s_n_L0_S)*1];
        }
    }
    for (int s_n_L0_V=0; s_n_L0_V<2048; s_n_L0_V++) {
        // LD/ST L0_V[(s_n_L0_V)*4096]
        L0_V[(s_n_L0_V)*4096] = L0_V[(s_n_L0_V)*4096];
    }
    for (int s_m_L0_O=0; s_m_L0_O<2; s_m_L0_O++) {
        for (int s_k_L0_O=0; s_k_L0_O<4096; s_k_L0_O++) {
            // LD/ST L0_O[(s_m_L0_O)*4096 + (s_k_L0_O)*1]
            L0_O[(s_m_L0_O)*4096 + (s_k_L0_O)*1] = L0_O[(s_m_L0_O)*4096 + (s_k_L0_O)*1];
        }
    }
}

void einsum_3(float * restrict L0_O, float * restrict L0_Wo, float * restrict L0_Y) {
    for (int s_m_L0_O=0; s_m_L0_O<2; s_m_L0_O++) {
        for (int s_k_L0_O=0; s_k_L0_O<4096; s_k_L0_O++) {
            // LD/ST L0_O[(s_m_L0_O)*4096 + (s_k_L0_O)*1]
            L0_O[(s_m_L0_O)*4096 + (s_k_L0_O)*1] = L0_O[(s_m_L0_O)*4096 + (s_k_L0_O)*1];
        }
    }
    for (int s_d_L0_Wo=0; s_d_L0_Wo<4096; s_d_L0_Wo++) {
        // LD/ST L0_Wo[(s_d_L0_Wo)*1]
        L0_Wo[(s_d_L0_Wo)*1] = L0_Wo[(s_d_L0_Wo)*1];
    }
    for (int s_m_L0_Y=0; s_m_L0_Y<2; s_m_L0_Y++) {
        for (int s_d_L0_Y=0; s_d_L0_Y<4096; s_d_L0_Y++) {
            // LD/ST L0_Y[(s_m_L0_Y)*4096 + (s_d_L0_Y)*1]
            L0_Y[(s_m_L0_Y)*4096 + (s_d_L0_Y)*1] = L0_Y[(s_m_L0_Y)*4096 + (s_d_L0_Y)*1];
        }
    }
}

void einsum_4(float * restrict L0_Y, float * restrict L0_W1, float * restrict L0_H) {
    for (int t_m=0; t_m<1024; t_m++) {
        for (int s_m_L0_Y=0; s_m_L0_Y<2; s_m_L0_Y++) {
            for (int s_d_L0_Y=0; s_d_L0_Y<4096; s_d_L0_Y++) {
                // LD/ST L0_Y[(t_m + s_m_L0_Y)*4096 + (s_d_L0_Y)*1]
                L0_Y[(t_m + s_m_L0_Y)*4096 + (s_d_L0_Y)*1] = L0_Y[(t_m + s_m_L0_Y)*4096 + (s_d_L0_Y)*1];
            }
        }
        for (int s_f_L0_W1=0; s_f_L0_W1<16384; s_f_L0_W1++) {
            // LD/ST L0_W1[(s_f_L0_W1)*1]
            L0_W1[(s_f_L0_W1)*1] = L0_W1[(s_f_L0_W1)*1];
        }
        for (int s_m_L0_H=0; s_m_L0_H<2; s_m_L0_H++) {
            for (int s_f_L0_H=0; s_f_L0_H<16384; s_f_L0_H++) {
                // LD/ST L0_H[(t_m + s_m_L0_H)*16384 + (s_f_L0_H)*1]
                L0_H[(t_m + s_m_L0_H)*16384 + (s_f_L0_H)*1] = L0_H[(t_m + s_m_L0_H)*16384 + (s_f_L0_H)*1];
            }
        }
    }
}

void einsum_5(float * restrict L0_H, float * restrict L0_W2, float * restrict L0_Z) {
    for (int s_m_L0_H=0; s_m_L0_H<2; s_m_L0_H++) {
        for (int s_f_L0_H=0; s_f_L0_H<16384; s_f_L0_H++) {
            // LD/ST L0_H[(s_m_L0_H)*16384 + (s_f_L0_H)*1]
            L0_H[(s_m_L0_H)*16384 + (s_f_L0_H)*1] = L0_H[(s_m_L0_H)*16384 + (s_f_L0_H)*1];
        }
    }
    for (int s_f_L0_W2=0; s_f_L0_W2<16384; s_f_L0_W2++) {
        // LD/ST L0_W2[(s_f_L0_W2)*4096]
        L0_W2[(s_f_L0_W2)*4096] = L0_W2[(s_f_L0_W2)*4096];
    }
    for (int s_m_L0_Z=0; s_m_L0_Z<2; s_m_L0_Z++) {
        // LD/ST L0_Z[(s_m_L0_Z)*4096]
        L0_Z[(s_m_L0_Z)*4096] = L0_Z[(s_m_L0_Z)*4096];
    }
}

int main() {
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    float * restrict L0_H = (float*)malloc(sizeof(float) * 33554432);
    for (int i=0;i<33554432;i++) L0_H[i] = 1.0f;

    float * restrict L0_K = (float*)malloc(sizeof(float) * 8388608);
    for (int i=0;i<8388608;i++) L0_K[i] = 1.0f;

    float * restrict L0_O = (float*)malloc(sizeof(float) * 8388608);
    for (int i=0;i<8388608;i++) L0_O[i] = 1.0f;

    float * restrict L0_Q = (float*)malloc(sizeof(float) * 8388608);
    for (int i=0;i<8388608;i++) L0_Q[i] = 1.0f;

    float * restrict L0_S = (float*)malloc(sizeof(float) * 4194304);
    for (int i=0;i<4194304;i++) L0_S[i] = 1.0f;

    float * restrict L0_V = (float*)malloc(sizeof(float) * 8388608);
    for (int i=0;i<8388608;i++) L0_V[i] = 1.0f;

    float * restrict L0_W1 = (float*)malloc(sizeof(float) * 67108864);
    for (int i=0;i<67108864;i++) L0_W1[i] = 1.0f;

    float * restrict L0_W2 = (float*)malloc(sizeof(float) * 67108864);
    for (int i=0;i<67108864;i++) L0_W2[i] = 1.0f;

    float * restrict L0_WQ = (float*)malloc(sizeof(float) * 16777216);
    for (int i=0;i<16777216;i++) L0_WQ[i] = 1.0f;

    float * restrict L0_Wo = (float*)malloc(sizeof(float) * 16777216);
    for (int i=0;i<16777216;i++) L0_Wo[i] = 1.0f;

    float * restrict L0_X = (float*)malloc(sizeof(float) * 8388608);
    for (int i=0;i<8388608;i++) L0_X[i] = 1.0f;

    float * restrict L0_Y = (float*)malloc(sizeof(float) * 8388608);
    for (int i=0;i<8388608;i++) L0_Y[i] = 1.0f;

    float * restrict L0_Z = (float*)malloc(sizeof(float) * 8388608);
    for (int i=0;i<8388608;i++) L0_Z[i] = 1.0f;

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
