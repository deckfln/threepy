// _get_normal_matrix(const mat4 modelViewMatrix)
mat3 normalMatrix;

normalMatrix[0][0] = modelViewMatrix[0][0];    normalMatrix[1][0] = modelViewMatrix[1][0];    normalMatrix[2][0] = modelViewMatrix[2][0];
normalMatrix[0][1] = modelViewMatrix[0][1];    normalMatrix[1][1] = modelViewMatrix[1][1];    normalMatrix[2][1] = modelViewMatrix[2][1];
normalMatrix[0][2] = modelViewMatrix[0][2];    normalMatrix[1][2] = modelViewMatrix[1][2];    normalMatrix[2][2] = modelViewMatrix[2][2];

normalMatrix = inverse(normalMatrix);
normalMatrix = transpose(normalMatrix);

// vec3 transformedNormal = normalMatrices[objectID] * objectNormal;
vec3 transformedNormal = normalMatrix * objectNormal;

#ifdef FLIP_SIDED

	transformedNormal = - transformedNormal;

#endif
