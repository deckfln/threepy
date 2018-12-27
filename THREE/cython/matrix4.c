#include <xmmintrin.h>

/*
void M4x4_SSE(float *A, float *B, float *C) {
    __m128 row1 = _mm_load_ps(&B[0]);
    __m128 row2 = _mm_load_ps(&B[4]);
    __m128 row3 = _mm_load_ps(&B[8]);
    __m128 row4 = _mm_load_ps(&B[12]);
    for(int i=0; i<4; i++) {
        __m128 brod1 = _mm_set1_ps(A[4*i + 0]);
        __m128 brod2 = _mm_set1_ps(A[4*i + 1]);
        __m128 brod3 = _mm_set1_ps(A[4*i + 2]);
        __m128 brod4 = _mm_set1_ps(A[4*i + 3]);
        __m128 row = _mm_add_ps(
                    _mm_add_ps(
                        _mm_mul_ps(brod1, row1),
                        _mm_mul_ps(brod2, row2)),
                    _mm_add_ps(
                        _mm_mul_ps(brod3, row3),
                        _mm_mul_ps(brod4, row4)));
        _mm_store_ps(&C[4*i], row);
    }
}
*/

// Shuffle Parameters
#define SHUFFLE_PARAM(x,y,z,w) \
	((x) |(y) <<2 | ((z) <<4) | ((w)<<6))
#define _mm_replicate_x_ps(v) \
	_mm_shuffle_ps((v),(v),SHUFFLE_PARAM(0,0,0,0))
#define _mm_replicate_y_ps(v) \
	_mm_shuffle_ps((v),(v),SHUFFLE_PARAM(1,1,1,1))
#define _mm_replicate_z_ps(v) \
	_mm_shuffle_ps((v),(v),SHUFFLE_PARAM(2,2,2,2))
#define _mm_replicate_w_ps(v) \
	_mm_shuffle_ps((v),(v),SHUFFLE_PARAM(3,3,3,3))

#define __mm_madd_ps(a,b,c) \
	_mm_add_ps(_mm_mul_ps((a),(b)),(c))

// Matrix 4x4 and Matrix 4x4 multiplication
void M4x4_SSE(float *A, float *B, float *C)
{
    __m128 aA[4] = {
        _mm_load_ps(&A[0]),
        _mm_load_ps(&A[4]),
        _mm_load_ps(&A[8]),
        _mm_load_ps(&A[12])
        };
    __m128 aB[4] = {
        _mm_load_ps(&B[0]),
        _mm_load_ps(&B[4]),
        _mm_load_ps(&B[8]),
        _mm_load_ps(&B[12])
        };
    __m128 MulResult[4];

	for (int i = 0; i < 4; i++){
		MulResult[i] = _mm_mul_ps(_mm_replicate_x_ps(aA[i]), aB[0]);
		MulResult[i] = __mm_madd_ps(_mm_replicate_y_ps(aA[i]), aB[1], MulResult[i]);
		MulResult[i] = __mm_madd_ps(_mm_replicate_z_ps(aA[i]), aB[2], MulResult[i]);
		MulResult[i] = __mm_madd_ps(_mm_replicate_w_ps(aA[i]), aB[3], MulResult[i]);

        _mm_store_ps(&C[4*i], MulResult[i]);
	}
}

void M4x4(float *ae, float *be, float *te)
{
    __m128 am[4] = {
        _mm_load_ps(ae + 0),
        _mm_load_ps(ae + 4),
        _mm_load_ps(ae + 8),
        _mm_load_ps(ae + 12)
        };
    __m128 rm[4];
    _MM_TRANSPOSE4_PS(am[0], am[1], am[2], am[3]);

    for (int i=0; i<4; i++) {
        __m128 rowa = am[i];
        __m128 rowb = _mm_load_ps(be);
        __m128 row0 = _mm_mul_ps(rowa, rowb);

        rowb = _mm_load_ps(be + 4);
        __m128 row1 = _mm_mul_ps(rowa, rowb);

        rowb = _mm_load_ps(be + 8);
        __m128 row2 = _mm_mul_ps(rowa, rowb);

        rowb = _mm_load_ps(be + 12);
        __m128 row3 = _mm_mul_ps(rowa, rowb);

        _MM_TRANSPOSE4_PS(row0, row1, row2, row3);
        __m128 row0x = _mm_add_ps(row0, row1);
        __m128 row0y = _mm_add_ps(row2, row3);
        rm[i] = _mm_add_ps(row0x, row0y);
    }

    _MM_TRANSPOSE4_PS(rm[0], rm[1], rm[2], rm[3]);
    _mm_store_ps(te, rm[0]);
    _mm_store_ps(te+4, rm[1]);
    _mm_store_ps(te+8, rm[2]);
    _mm_store_ps(te+12, rm[3]);
}