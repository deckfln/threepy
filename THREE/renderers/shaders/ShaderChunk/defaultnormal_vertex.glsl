vec3 transformedNormal = normalMatrices[objectID] * objectNormal;

#ifdef FLIP_SIDED

	transformedNormal = - transformedNormal;

#endif
