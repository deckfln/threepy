in vec3 position;
in vec3 normal;
in vec2 uv;

layout (std140) uniform camera
{
    uniform mat4 projectionMatrix;
    uniform mat4 viewMatrix;
};

#ifdef USE_INSTANCES
    in int objectID;
#else
    uniform int objectID;
#endif

#include <modelMatrix>
#include <modelViewMatrix>


//uniform mat4 modelMatrix;
//uniform mat4 modelViewMatrix;
//uniform mat3 normalMatrix;
uniform vec3 cameraPosition;

#ifdef USE_COLOR
    attribute vec3 color;
#endif

#ifdef USE_MORPHTARGETS
    attribute vec3 morphTarget0;
    attribute vec3 morphTarget1;
    attribute vec3 morphTarget2;
    attribute vec3 morphTarget3;

    #ifdef USE_MORPHNORMALS
        attribute vec3 morphNormal0;
        attribute vec3 morphNormal1;
        attribute vec3 morphNormal2;
        attribute vec3 morphNormal3;
    #else
        attribute vec3 morphTarget4;
        attribute vec3 morphTarget5;
        attribute vec3 morphTarget6;
        attribute vec3 morphTarget7;
    #endif
#endif

#ifdef USE_SKINNING
    attribute vec4 skinIndex;
    attribute vec4 skinWeight;
#endif
