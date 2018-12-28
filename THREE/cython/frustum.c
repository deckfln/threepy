// https://www.gamedev.net/articles/programming/general-and-gameplay-programming/frustum-culling-r4613/
#include <xmmintrin.h>
#include <emmintrin.h>

void sse_culling_spheres(float *spheres, int num_objects, int *culling_res, float *frustum_planes)
{
	int *culling_res_sse = &culling_res[0];

	//to optimize calculations we gather xyzw elements in separate vectors
	__m128 zero_v = _mm_setzero_ps();
	__m128 frustum_planes_x[6];
	__m128 frustum_planes_y[6];
	__m128 frustum_planes_z[6];
	__m128 frustum_planes_d[6];

	int i, j;
	for (i = 0; i < 6; i++)
	{
	    j = i *4;
		frustum_planes_x[i] = _mm_set1_ps(frustum_planes[j]);
		frustum_planes_y[i] = _mm_set1_ps(frustum_planes[j + 1]);
		frustum_planes_z[i] = _mm_set1_ps(frustum_planes[j + 2]);
		frustum_planes_d[i] = _mm_set1_ps(frustum_planes[j + 3]);
	}

	//we process 4 objects per step
	for (i = 0; i < num_objects; i += 4)
	{
    	//load bounding sphere data
		__m128 spheres_pos_x = _mm_load_ps(spheres);
		__m128 spheres_pos_y = _mm_load_ps(spheres + 4);
		__m128 spheres_pos_z = _mm_load_ps(spheres + 8);
		__m128 spheres_radius = _mm_load_ps(spheres + 12);
		spheres += 16;

	    //but for our calculations we need transpose data, to collect x, y, z and w coordinates in separate vectors
		_MM_TRANSPOSE4_PS(spheres_pos_x, spheres_pos_y, spheres_pos_z, spheres_radius);
		__m128 spheres_neg_radius = _mm_sub_ps(zero_v, spheres_radius); // negate all elements

		__m128 intersection_res = _mm_setzero_ps();
		for (j = 0; j < 6; j++) //plane index
		{
		//1. calc distance to plane dot(sphere_pos.xyz, plane.xyz) + plane.w
		//2. if distance < sphere radius, then sphere outside frustum
			__m128 dot_x = _mm_mul_ps(spheres_pos_x, frustum_planes_x[j]);
			__m128 dot_y = _mm_mul_ps(spheres_pos_y, frustum_planes_y[j]);
			__m128 dot_z = _mm_mul_ps(spheres_pos_z, frustum_planes_z[j]);

			__m128 sum_xy = _mm_add_ps(dot_x, dot_y);
			__m128 sum_zw = _mm_add_ps(dot_z, frustum_planes_d[j]);
			__m128 distance_to_plane = _mm_add_ps(sum_xy, sum_zw);

			__m128 plane_res = _mm_cmple_ps(distance_to_plane, spheres_neg_radius); //dist < -sphere_r ?
			intersection_res = _mm_or_ps(intersection_res, plane_res); //if yes - sphere behind the plane & outside frustum
		}

		//store result
		__m128i intersection_res_i = _mm_cvtps_epi32(intersection_res);
		_mm_store_si128((__m128i *)&culling_res_sse, intersection_res_i);
		culling_res_sse += 4;
	}
}