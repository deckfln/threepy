layout (std140) uniform modelMatricesBlock
{
    uniform mat4 modelMatrices[1024];
};
mat4 modelMatrix = modelMatrices[objectID];
