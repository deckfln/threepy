#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP )

	vec4 worldPosition = modelMatrices[objectID] * vec4( transformed, 1.0 );

#endif
