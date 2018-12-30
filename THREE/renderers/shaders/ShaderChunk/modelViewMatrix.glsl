layout (std140) uniform modelViewMatricesBlock
{
    uniform mat4 modelViewMatrices[1024];
};
mat4 modelViewMatrix = viewMatrix * modelMatrix;
