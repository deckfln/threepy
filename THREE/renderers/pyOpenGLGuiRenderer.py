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
        self.map = None

        self.modelViewMatrix = None
        self.projectionMatrix = None


class pyOpenGLGuiRenderer:
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

        self.vao = -1

        if renderer.parameters['gui'] is None:
            image = Image.new("RGBA", (8,8))
            d = ImageDraw.Draw(image)
            d.rectangle((0, 0, 8, 8), "#00000000")

            # context.fillStyle = 'white'
            # context.fillRect( 0, 0, 8, 8 )

            self.texture = CanvasTexture( image )
        else:
            self.texture = renderer.parameters['gui']

    def init(self):
        vertices = Float32Array( [
            - 1, - 1,  0, 0,
              1, - 1,  1, 0,
              1,   1,  1, 1,
            - 1,   1,  0, 1
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

        # uni = pyOpenGLUniforms(self.program, self.renderer)

        self.uniforms = _Uniforms()
        self.uniforms.map = glGetUniformLocation( self.program, 'map')

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        glBindBuffer( GL_ARRAY_BUFFER, self.vertexBuffer )
        glEnableVertexAttribArray(self.attributes.position)
        OpenGL.raw.GL.VERSION.GL_2_0.glVertexAttribPointer( self.attributes.position, 2, GL_FLOAT, False, 2 * 8, None )
        glBindBuffer( GL_ELEMENT_ARRAY_BUFFER, self.elementBuffer )
        glBindVertexArray(0)

        glBindBuffer( GL_ELEMENT_ARRAY_BUFFER, 0 )
        glBindBuffer( GL_ARRAY_BUFFER, 0 )

    def render(self):
        # // setup gl

        if self.program is None:
            self.init()

        self.state.useProgram( self.program )

        """
        self.state.initAttributes(self.vao)
        self.state.enableAttribute( self.attributes.position, self.vao )
        self.state.disableUnusedAttributes(self.vao)
        """

        self.state.disable( GL_CULL_FACE )
        self.state.enable( GL_BLEND )

        glBindVertexArray(self.vao)

        self.state.activeTexture( GL_TEXTURE0 )
        glUniform1i( self.uniforms.map, 0 )

        # self.state.setBlending( material.blending, material.blendEquation, material.blendSrc, material.blendDst, material.blendEquationAlpha, material.blendSrcAlpha, material.blendDstAlpha, material.premultipliedAlpha )
        self.state.buffers.depth.setTest(False)
        #self.state.buffers.depth.setMask(False)

        self.textures.setTexture2D( self.texture, 0 )

        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_SHORT, c_void_p(0))

        self.state.buffers.depth.setTest(True)
        #self.state.buffers.depth.setMask(True)

        # restore gl
        glBindVertexArray(0)

        self.state.enable( GL_CULL_FACE )
        # self.state.reset()

    def createProgram(self):
        self.program = glCreateProgram()

        vertexSource = "\n".join([
            '# version 330',
            'precision %s float;' % self.capabilities.precision ,

            '#define SHADER_NAME %s ' % 'GUIMaterial',

            'uniform mat4 modelViewMatrix;',
            'uniform mat4 projectionMatrix;',
            'uniform vec2 uvOffset;',

            'attribute vec2 position;',

            'varying vec2 vUv;',

            'void main() {',

                'vUv = vec2((position.x + 1) / 2, (position.y + 1) / 2);'

                'vec4 finalPosition;',

                'finalPosition = modelViewMatrix * vec4( 0.0, 0.0, 0.0, 1.0 );',
                'finalPosition = projectionMatrix * finalPosition;',

                'gl_Position = vec4(position.x, position.y, 0.0, 1.0);',

            '}'
        ])
        fragmentSource = "\n".join([
            '#version 330',
            'precision %s float;' % self.capabilities.precision,

            '#define SHADER_NAME ' + 'GUIMaterial',

            'uniform vec3 color;',
            'uniform sampler2D map;',

            'varying vec2 vUv;',

            'void main() {',

                'gl_FragColor = texture2D( map, vUv );',

            '}'

        ])
        vertexShader = pyOpenGLShader( GL_VERTEX_SHADER, vertexSource )
        fragmentShader = pyOpenGLShader( GL_FRAGMENT_SHADER, fragmentSource )

        glAttachShader( self.program, vertexShader )
        glAttachShader( self.program, fragmentShader )

        glLinkProgram( self.program )

        return self.program
