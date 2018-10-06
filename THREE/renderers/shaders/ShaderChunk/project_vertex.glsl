vec4 mvPosition = modelViewMatrices[objectID] * vec4( transformed, 1.0 );

gl_Position = projectionMatrix * mvPosition;
