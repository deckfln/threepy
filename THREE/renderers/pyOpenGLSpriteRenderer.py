"""
/**
 * @author mikael emtinger / http:# //gomo.se/
 * @author alteredq / http:# //alteredqualia.com/
 */
"""
from ctypes import c_void_p

from PIL import Image, ImageDraw
from THREE.javascriparray import *
from THREE.CanvasTexture import *
from THREE.renderers.pyOpenGL.pyOpenGLProgram import pyOpenGLShader
from THREE.renderers.pyOpenGL.pyOpenGLUniforms import *


def _glGetActiveAttrib(program, index):
    bufSize = glGetProgramiv(program, GL_ACTIVE_ATTRIBUTE_MAX_LENGTH)
    length = GLsizei()
    size = GLint()
    type_ = GLenum()
    name = (GLchar * bufSize)()

    glGetActiveAttrib(program, index, bufSize, length, size, type_, name)
    return name.value, size.value, type_.value


class _Attributes:
    def __init(self):
        self.position = 0
        self.uv = 0
        

class _Uniforms:
    def __init__(self):
        self.uvOffset = None
        self.uvScale = None

        self.rotation = None
        self.scale = None

        self.color = None
        self.map = None
        self.opacity = None

        self.modelViewMatrix = None
        self.projectionMatrix = None

        self.fogType = None
        self.fogDensity = None
        self.fogNear = None
        self.fogFar = None
        self.fogColor = None

        self.alphaTest = None


class pyOpenGLSpriteRenderer:
    def __init__(self, renderer, state, textures, capabilities ):
        self.renderer = renderer
        self.state = state
        self.textures = textures
        self.capabilities = capabilities

        self.vertexBuffer = None
        self.elementBuffer = None
        self.program = None
        self.attributes = None
        self.uniforms = None

        self.texture = None

        # // decompose matrixWorld

        self.spritePosition = Vector3()
        self.spriteRotation = Quaternion()
        self.spriteScale = Vector3()

    def init(self):
        vertices = Float32Array( [
            - 0.5, - 0.5,  0, 0,
              0.5, - 0.5,  1, 0,
              0.5,   0.5,  1, 1,
            - 0.5,   0.5,  0, 1
        ] )

        faces = Uint16Array( [
            0, 1, 2,
            0, 2, 3
        ] )

        self.vertexBuffer  = glGenBuffers(1)
        self.elementBuffer = glGenBuffers(1)

        glBindBuffer( GL_ARRAY_BUFFER, self.vertexBuffer )
        glBufferData( GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW )

        glBindBuffer( GL_ELEMENT_ARRAY_BUFFER, self.elementBuffer )
        glBufferData( GL_ELEMENT_ARRAY_BUFFER, faces, GL_STATIC_DRAW )

        self.program = self.createProgram()

        self.attributes = _Attributes()
        self.attributes.position = glGetAttribLocation ( self.program, 'position' )
        self.attributes.uv = glGetAttribLocation ( self.program, 'uv' )

        # uni = pyOpenGLUniforms(self.program, self.renderer)

        self.uniforms = _Uniforms()
        self.uniforms.uvOffset = glGetUniformLocation( self.program, 'uvOffset' )
        self.uniforms.uvScale = glGetUniformLocation( self.program, 'uvScale' )

        self.uniforms.rotation = glGetUniformLocation( self.program, 'rotation' )
        self.uniforms.scale = glGetUniformLocation( self.program, 'scale' )

        self.uniforms.color = glGetUniformLocation( self.program, 'color' )
        self.uniforms.map = glGetUniformLocation( self.program, 'map' )
        self.uniforms.opacity = glGetUniformLocation( self.program, 'opacity' )

        self.uniforms.projectionMatrix = glGetUniformLocation(self.program, b'projectionMatrix')
        self.uniforms.modelViewMatrix = glGetUniformLocation(self.program, b'modelViewMatrix')

        self.uniforms.fogType = glGetUniformLocation( self.program, 'fogType' )
        self.uniforms.fogDensity = glGetUniformLocation( self.program, 'fogDensity' )
        self.uniforms.fogNear = glGetUniformLocation( self.program, 'fogNear' )
        self.uniforms.fogFar = glGetUniformLocation( self.program, 'fogFar' )
        self.uniforms.fogColor = glGetUniformLocation( self.program, 'fogColor' )

        self.uniforms.alphaTest = glGetUniformLocation( self.program, 'alphaTest' )

        image = Image.new("RGB", (8,8))
        d = ImageDraw.Draw(image)
        d.rectangle((0, 0, 8, 8), "#FFFFFF")

        # context.fillStyle = 'white'
        # context.fillRect( 0, 0, 8, 8 )

        self.texture = CanvasTexture( image )

    def render(self, sprites, scene, camera ):
        if len(sprites) == 0:
            return

        # // setup gl

        if self.program is None:
            self.init()

        self.state.useProgram( self.program )

        self.state.initAttributes()
        self.state.enableAttribute( self.attributes.position )
        self.state.enableAttribute( self.attributes.uv )
        self.state.disableUnusedAttributes()

        self.state.disable( GL_CULL_FACE )
        self.state.enable( GL_BLEND )

        glBindBuffer( GL_ARRAY_BUFFER, self.vertexBuffer )
        glVertexAttribPointer( self.attributes.position, 2, GL_FLOAT, False, 2 * 8, c_void_p(0) )
        glVertexAttribPointer( self.attributes.uv, 2, GL_FLOAT, False, 2 * 8, c_void_p(8) )

        glBindBuffer( GL_ELEMENT_ARRAY_BUFFER, self.elementBuffer )

        glUniformMatrix4fv( self.uniforms.projectionMatrix, 1, False, camera.projectionMatrix.elements )

        self.state.activeTexture( GL_TEXTURE0 )
        glUniform1i( self.uniforms.map, 0 )

        oldFogType = 0
        sceneFogType = 0
        fog = scene.fog

        if fog:
            glUniform3f( self.uniforms.fogColor, fog.color.r, fog.color.g, fog.color.b )

            if fog.isFog:
                glUniform1f( self.uniforms.fogNear, fog.near )
                glUniform1f( self.uniforms.fogFar, fog.far )

                glUniform1i( self.uniforms.fogType, 1 )
                oldFogType = 1
                sceneFogType = 1
            elif fog.my_class(isFogExp2):
                glUniform1f( self.uniforms.fogDensity, fog.density )

                glUniform1i( self.uniforms.fogType, 2 )
                oldFogType = 2
                sceneFogType = 2

        else:
            glUniform1i( self.uniforms.fogType, 0 )
            oldFogType = 0
            sceneFogType = 0

        # // update positions and sort

        for i in range(len(sprites)):
            sprite = sprites[ i ]

            sprite.modelViewMatrix.multiplyMatrices( camera.matrixWorldInverse, sprite.matrixWorld )
            sprite.z = - sprite.modelViewMatrix.elements[ 14 ]

        def painterSortStable(a):
            return a.renderOrder * 1000 + a.z * 100 + a.z

        sprites.sort( key=painterSortStable)

        # // render all sprites

        scale = Float32Array(2)

        for i in range(len(sprites)):
            sprite = sprites[ i ]
            material = sprite.material

            if material.visible == False:
                continue

            sprite.onBeforeRender( self.renderer, scene, camera, None, material, None )

            glUniform1f( self.uniforms.alphaTest, material.alphaTest )
            glUniformMatrix4fv( self.uniforms.modelViewMatrix, 1, False, sprite.modelViewMatrix.elements )

            sprite.matrixWorld.decompose( self.spritePosition, self.spriteRotation, self.spriteScale )

            scale[ 0 ] = self.spriteScale.x
            scale[ 1 ] = self.spriteScale.y

            fogType = 0

            if scene.fog and material.fog:
                fogType = sceneFogType

            if oldFogType != fogType:
                glUniform1i( self.uniforms.fogType, fogType )
                oldFogType = fogType

            if material.map is not None:
                glUniform2f( self.uniforms.uvOffset, material.map.offset.x, material.map.offset.y )
                glUniform2f( self.uniforms.uvScale, material.map.repeat.x, material.map.repeat.y )

            else:
                glUniform2f( self.uniforms.uvOffset, 0, 0 )
                glUniform2f( self.uniforms.uvScale, 1, 1 )

            glUniform1f( self.uniforms.opacity, material.opacity )
            glUniform3f( self.uniforms.color, material.color.r, material.color.g, material.color.b )

            glUniform1f( self.uniforms.rotation, material.rotation )
            glUniform2fv( self.uniforms.scale, 1, scale)

            self.state.setBlending( material.blending, material.blendEquation, material.blendSrc, material.blendDst, material.blendEquationAlpha, material.blendSrcAlpha, material.blendDstAlpha, material.premultipliedAlpha )
            self.state.buffers.depth.setTest( material.depthTest )
            self.state.buffers.depth.setMask( material.depthWrite )

            self.textures.setTexture2D( material.map or self.texture, 0 )

            glDrawElements( GL_TRIANGLES, 6, GL_UNSIGNED_SHORT, c_void_p(0) )

            sprite.onAfterRender( self.renderer, scene, camera, None, material, None)

        # // restore gl

        self.state.enable( GL_CULL_FACE )

        self.state.reset()

    def createProgram(self):
        self.program = glCreateProgram()

        vertexSource = "\n".join([
            '# version 330',
            'precision %s float;' % self.capabilities.precision ,

            '#define SHADER_NAME %s ' % 'SpriteMaterial',

            'uniform mat4 modelViewMatrix;',
            'uniform mat4 projectionMatrix;',
            'uniform float rotation;',
            'uniform vec2 scale;',
            'uniform vec2 uvOffset;',
            'uniform vec2 uvScale;',

            'attribute vec2 position;',
            'attribute vec2 uv;',

            'varying vec2 vUV;',

            'void main() {',

                'vUV = uvOffset + uv * uvScale;',

                'vec2 alignedPosition = position * scale;',

                'vec2 rotatedPosition;',
                'rotatedPosition.x = cos( rotation ) * alignedPosition.x - sin( rotation ) * alignedPosition.y;',
                'rotatedPosition.y = sin( rotation ) * alignedPosition.x + cos( rotation ) * alignedPosition.y;',

                'vec4 finalPosition;',

                'finalPosition = modelViewMatrix * vec4( 0.0, 0.0, 0.0, 1.0 );',
                'finalPosition.xy += rotatedPosition;',
                'finalPosition = projectionMatrix * finalPosition;',

                'gl_Position = finalPosition;',

            '}'
        ])
        fragmentSource = "\n".join([
            '#version 330',
            'precision %s float;' % self.capabilities.precision,

            '#define SHADER_NAME ' + 'SpriteMaterial',

            'uniform vec3 color;',
            'uniform sampler2D map;',
            'uniform float opacity;',

            'uniform int fogType;',
            'uniform vec3 fogColor;',
            'uniform float fogDensity;',
            'uniform float fogNear;',
            'uniform float fogFar;',
            'uniform float alphaTest;',

            'varying vec2 vUV;',

            'void main() {',

            'vec4 texture = texture2D( map, vUV );',

            'if (texture.a < alphaTest ) discard;',

            'gl_FragColor = vec4( color * texture.xyz, texture.a * opacity );',

            'if (fogType > 0 ) {',

            'float depth = gl_FragCoord.z / gl_FragCoord.w;',
            'float fogFactor = 0.0;',

            'if (fogType == 1 ) {',

            'fogFactor = smoothstep( fogNear, fogFar, depth );',

            '} else {',

            'const float LOG2 = 1.442695;',
            'fogFactor = exp2( - fogDensity * fogDensity * depth * depth * LOG2 );',
            'fogFactor = 1.0 - clamp( fogFactor, 0.0, 1.0 );',

            '}',

            'gl_FragColor = mix( gl_FragColor, vec4( fogColor, gl_FragColor.w ), fogFactor );',

            '}',

            '}'

        ])
        vertexShader = pyOpenGLShader( GL_VERTEX_SHADER, vertexSource )
        fragmentShader = pyOpenGLShader( GL_FRAGMENT_SHADER, fragmentSource )

        glAttachShader( self.program, vertexShader )
        glAttachShader( self.program, fragmentShader )

        glLinkProgram( self.program )

        return self.program

