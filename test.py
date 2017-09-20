#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
07-attrib.py

OpenGL 2.0 rendering using vertex attributes

Copyright (c) 2010, Renaud Blanch <rndblnch at gmail dot com>
Licence: GPLv3 or higher <http://www.gnu.org/licenses/gpl.html>
"""


# imports ####################################################################

import sys

from math import exp, modf
from time import time
from ctypes import sizeof, c_float, c_void_p, c_uint, c_uint16

from OpenGL.GLUT import *
from OpenGL.GL import *

import THREE as THREE
from THREE import *

# shader
vert_shader = """
uniform mat4 transformationMatrix;

varying vec4 fragmentColor;

void main() {
    gl_Position = projectionMatrix * viewMatrix * transformationMatrix * vec4(position, 1.);
//    gl_TexCoord[0] = gl_TextureMatrix[0] * vec4(tex_coord, 1.);
    
    fragmentColor = vec4(color, 1.);
}
    """
    
frag_shader = """
const float alpha_threshold = .55;

varying vec4 fragmentColor;
        
void main() {
    
    vec4 color = fragmentColor;
    gl_FragColor = color;
}
    """
    
# object #####################################################################

def flatten(*lll):
    return [u for ll in lll for l in ll for u in l]

def flatten1(*lll):
    return [l for ll in lll for l in ll]

uint_size = sizeof(c_uint)
uint16_size = sizeof(c_uint16)
float_size = sizeof(c_float)

# display ####################################################################


def screen_shot(name="screen_shot.png"):
    """window screenshot."""
    width, height = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
    data = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
    
    import png
    png.write(open(name, "wb"), width, height, 3, data)


def reshape(width, height):
    """window reshape callback."""
    glViewport(0, 0, width, height)
    
#    glMatrixMode(GL_PROJECTION)
#    glLoadIdentity()
#    radius = .5 * min(width, height)
#    w, h = width/radius, height/radius
#    if perspective:
#       glFrustum(-w, w, -h, h, 8, 16)
#        glTranslate(0, 0, -12)
#        glScale(1.5, 1.5, 1.5)
#    else:
#        glOrtho(-w, w, -h, h, -2, 2)
    
#    glMatrixMode(GL_MODELVIEW)
#    glLoadIdentity()


def display():
    """window redisplay callback."""
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    draw_object()
    glutSwapBuffers()


# interaction ################################################################

PERSPECTIVE, LIGHTING, TEXTURING = b'p', b'l', b't'

perspective = False
lighting = False
texturing = False


def keyboard(c, x=0, y=0):
    """keyboard callback."""
    global perspective, lighting, texturing
    
    if c == PERSPECTIVE:
        perspective = not perspective
        reshape(glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT))
    
    elif c == LIGHTING:
        lighting = not lighting
        glUniform1i(locations[b"lighting"], lighting)
    
    elif c == TEXTURING:
        texturing = not texturing
        glUniform1i(locations[b"texturing"], texturing)
        if texturing:
            animate_texture()
    
    elif c == b's':
        screen_shot()
    
    elif c == b'q':
        sys.exit(0)
    glutPostRedisplay()


rotating = False
scaling = False

rotation = THREE.Quaternion()
scale = 1.


def screen2space(x, y):
    width, height = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
    radius = min(width, height)*scale
    return (2.*x-width)/radius, -(2.*y-height)/radius


def mouse(button, state, x, y):
    global rotating, scaling, x0, y0
    if button == GLUT_LEFT_BUTTON:
        rotating = (state == GLUT_DOWN)
    elif button == GLUT_RIGHT_BUTTON:
        scaling = (state == GLUT_DOWN)
    x0, y0 = x, y


def motion(x1, y1):
    global x0, y0, rotation, scale
    if rotating:
        p0 = screen2space(x0, y0)
        p1 = screen2space(x1, y1)
        # TODO
        # rotation = q.product(rotation, q.arcball(*p0), q.arcball(*p1))
        rotation._x += 0.01
        
    if scaling:
        scale *= exp(((x1-x0)-(y1-y0))*.01)
    x0, y0 = x1, y1
    glutPostRedisplay()


# setup ######################################################################

WINDOW_SIZE = 640, 480

def _glGetActiveAttrib(program, index):
    bufSize = glGetProgramiv(program, GL_ACTIVE_ATTRIBUTE_MAX_LENGTH)
    length = GLsizei()
    size = GLint()
    type_ = GLenum()
    name = (GLchar * bufSize)()

    glGetActiveAttrib(program, index, bufSize, length, size, type_, name)
    return name.value, size.value, type_.value


class _AttributeLocations:
    def __init__(self, program, identifiers=None ):
        self._attributes = {}

        n = glGetProgramiv( program, GL_ACTIVE_ATTRIBUTES )

        for i in range(n):
            info = _glGetActiveAttrib( program, i )
            name = info[0]

            self._attributes[ name ] = glGetAttribLocation( program, name )

    def __getattr__(self, item):
        bytes = item.encode("utf-8")
        if bytes in self._attributes:
            return self._attributes[bytes]

        #raise RuntimeError("pyOpenGL: no OpenGL Attribute ", item)
        return None

    def has(self, item):
        bytes = item.encode("utf-8")
        return bytes in self._attributes

"""
def addLineNumbers(string):
    lines = string.split('\n')

    for i in range(len(lines)):
        lines[i] = "%d : %s" % (i + 1, lines[i])

    return "\n".join(lines)


def pyOpenGLShader(type, string):
    shader = glCreateShader(type)
    glShaderSource(shader, string)
    glCompileShader(shader)

    if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
        raise RuntimeError('THREE.WebGLShader: Shader couldn\'t compile.')

    if glGetShaderInfoLog(shader) != '':
        if type == GL_VERTEX_SHADER:
            t = 'vertex'
        else:
            t = 'fragment'
        print('THREE.WebGLShader: glGetShaderInfoLog()', t, glGetShaderInfoLog(shader), addLineNumbers(string))

    return shader


_programIdCount = 0


class pyOpenGLProgram:
    def __init__(self, renderer, extensions, code, material, shader, parameters):
        global _programIdCount
        self.id = _programIdCount
        _programIdCount += 1
        self.code = code
        self.usedTimes = 1

        vertexShader = shader.vertexShader
        fragmentShader = shader.fragmentShader

        glVertexShader = pyOpenGLShader( GL_VERTEX_SHADER, vertexShader )
        glFragmentShader = pyOpenGLShader( GL_FRAGMENT_SHADER, fragmentShader )

        program = glCreateProgram()

        glAttachShader( program, glVertexShader )
        glAttachShader( program, glFragmentShader )

        # // Force a particular attribute to index 0.
        glLinkProgram( program )
        glValidateProgram(program)

        programLog = glGetProgramInfoLog( program ).decode("utf-8")
        vertexLog = glGetShaderInfoLog( glVertexShader ).decode("utf-8")
        fragmentLog = glGetShaderInfoLog( glFragmentShader ).decode("utf-8")

        runnable = True
        haveDiagnostics = True

        if not glGetProgramiv( program, GL_LINK_STATUS ):
            runnable = False
            raise RuntimeError( 'THREE.pyOpenGLProgram: shader error: ', glGetError(), 'gl.VALIDATE_STATUS', glGetProgramiv( program, GL_VALIDATE_STATUS ), 'gl.getProgramInfoLog', programLog, vertexLog, fragmentLog )
        elif programLog != '':
            print( 'THREE.WebGLProgram: glGetProgramInfoLog()', programLog )
        elif vertexLog == '' or fragmentLog == '':
            haveDiagnostics = False

        if haveDiagnostics:
            self.diagnostics = {
                'runnable': runnable,
                'material': material,

                'programLog': programLog,

                'vertexShader': {
                    'log': vertexLog,
                    'prefix': vertexShader
                },

                'fragmentShader': {
                    'log': fragmentLog,
                    'prefix': fragmentShader
                }
            }

        # // clean up
        # TODO: really delete now ?
        # glDeleteShader( glVertexShader )
        # glDeleteShader( glFragmentShader )

        # // set up caching for uniform locations

        self.cachedUniforms = pyOpenGLUniforms(program, renderer)
        self.cachedAttributes = _AttributeLocations( self.program )

        for a in self.cachedAttributes.attributes:
            glBindAttribLocation(program, self.cachedAttributes.attributes[a], a)

        self.program = program
        self.vertexShader = glVertexShader
        self.fragmentShader = glFragmentShader

    def getUniforms(self):
        return self.cachedUniforms

    # // set up caching for attribute locations 

    def getAttributes(self):
        return self.cachedAttributes

    def stat(self):
        glUseProgram(self.program)

    def stop(self):
        glUseProgram(0)
"""


class myShader():
    def __init__(self, vertexShader, fragmentShader):
        self.name = ""
        self.vertexShader = vertexShader
        self.fragmentShader = fragmentShader

"""
class Shader:
    def __init__(self, vert_shader, frag_shader):
        self.vertexShader = self.loadShader(vert_shader, GL_VERTEX_SHADER)
        self.fragmentShader = self.loadShader(frag_shader, GL_FRAGMENT_SHADER)
        self.program = glCreateProgram()
        self.mat4array = np.zeros(16,'f')

        glAttachShader(self.program, self.vertexShader)
        glAttachShader(self.program, self.fragmentShader)

        glLinkProgram(self.program)
        glValidateProgram(self.program)

        #self._getAllUnifromLocations()
        self.uniforms = pyOpenGLUniforms(self.program,None)
        self.cachedAttributes = _AttributeLocations( self.program )
        self._bindAttributes()


    def _getAllUnifromLocations(self):
        self.uniforms = pyOpenGLUniforms(self.program,None)

    def getAttributes(self):
        return self.cachedAttributes

    def _bindAttribute(self, attribute, variableName):
        glBindAttribLocation(self.program,attribute, variableName)
        
    def start(self):
        glUseProgram(self.program)
        
    def stop(self):
        glUseProgram(0)
        
    def cleanUp(self):
        self.stop()
        glDetachShader(self.program, self.vertexShader)
        glDetachShader(self.program, self.fragmentShader)
        glDeleteShader(self.vertexShader)
        glDeleteShader(self.fragmentShader)
        glDeleteProgram(self.program)
        
    def loadShader(self, source, type):
        # place to load from disk
        return pyOpenGLShader(type, source)

        
class StaticShader(Shader):
    def __init__(self, vert_shader, frag_shader):
        super().__init__(vert_shader, frag_shader)

    def _bindAttributes(self):
        for a in self.cachedAttributes._attributes:
            glBindAttribLocation(self.program, self.cachedAttributes._attributes[a], a)
    #    super()._bindAttribute(0, b"vertex")
    #    super()._bindAttribute(1, b"text_coord")
    #    super()._bindAttribute(2, b"normal")
    #    super()._bindAttribute(3, b"color")

    def loadTransformationMatrix(self, matrix):
        self.uniforms.setValue(None, "transformationMatrix", matrix)

    def loadProjectionMatrix(self, matrix):
        self.uniforms.setValue(None, "projectionMatrix", matrix)

    def loadViewMatrix(self, matrix):
        self.uniforms.setValue(None, "viewMatrix", matrix)

    def enableVertexAttrib(self, model):
    #    glEnableVertexAttribArray(model.vbo_positions)
    #    glEnableVertexAttribArray(model.vbo_normals)
    #    glEnableVertexAttribArray(model.vbo_colors)
    #    glEnableVertexAttribArray(model.vbo_uvs)
        for a in self.cachedAttributes._attributes:
            glEnableVertexAttribArray(self.cachedAttributes._attributes[a])

    def disableVertexAttrib(self, model):
    #    glDisableVertexAttribArray(model.vbo_positions)
    #    glDisableVertexAttribArray(model.vbo_normals)
    #    glDisableVertexAttribArray(model.vbo_colors)
    #    glDisableVertexAttribArray(model.vbo_uvs)
        for a in self.cachedAttributes._attributes:
            glDisableVertexAttribArray(self.cachedAttributes._attributes[a])

    def loadModelViewMatrix(self, object, camera):
        self.loadTransformationMatrix(object.matrixWorld)
        self.loadProjectionMatrix(camera.projectionMatrix)
        self.loadViewMatrix(camera.matrixWorldInverse)
"""

###########################


class Model:
    def __init__(self, vaoID, vertexCount, object3D):
        self.vaoID = vaoID
        self.vertexCount = vertexCount
        self.textureID = 0
        self.vbo_positions = 0
        self.vbo_uvs = 2
        self.vbo_normals = 3
        self.vbo_colors = 1
        self.object3D = object3D


class Loader:
    def __init__(self):
        self.vaoList = []
        self.vboList = []
        self.texturesList = []

    def loadModel(self, object3D, program):
        bufferGeometry = object3D.geometry

        indexes = bufferGeometry.index

        positions = bufferGeometry.attributes.position
        uvs = bufferGeometry.attributes.uv
        normals = bufferGeometry.attributes.normal
        colors = bufferGeometry.attributes.color

        vaoID = self.createVAO()
        model = Model(vaoID, len(indexes.array), object3D)

        self.bindIndexBuffer(indexes)

        programAttributes = program.getAttributes()

        if programAttributes.has('position'):
            self.createVBO(programAttributes.position, positions, 3)
        if programAttributes.has('color'):
            self.createVBO(programAttributes.color, colors, 3)
        if programAttributes.has('tex_coord'):
            self.createVBO(programAttributes.tex_coord, uvs, 2)
        if programAttributes.has('normal'):
            self.createVBO(programAttributes.normal, normals, 3)

        self.unbindVAO()
        return model

    def loadTexture(self, file=None):
        textureID = init_texture()
        self.texturesList.append(textureID)
        return textureID

    def createVAO(self):
        vaoID = glGenVertexArrays(1)
        glBindVertexArray(vaoID)
        self.vaoList.append(vaoID)
        return vaoID

    def createVBO(self, attribute, data, itemSize):
        vboID = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vboID)
        # k = [ f for f in data.array ]
        # buffer = (c_float * len(k))(*k)
        glBufferData(GL_ARRAY_BUFFER, data.array, GL_STATIC_DRAW)
        glVertexAttribPointer(attribute, itemSize, GL_FLOAT, GL_FALSE, 0, c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        self.vboList.append(vboID)

    def unbindVAO(self):
        glBindVertexArray(0)

    def bindIndexBuffer(self, indexes):
        vboID = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, vboID)
        # buffer = UInt16(indexes)
        # k = [ f for f in indexes.array ]
        # buffer = (c_uint*len(k))(*k)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indexes.array, GL_STATIC_DRAW)
        self.vboList.append(vboID)

    def cleanUp(self):
        for vaoID in self.vaoList:
            glDeleteVertexArrays(vaoID)

        for vboID in self.vboList:
            glDeleteBuffers(vboID)

        for textureID in self.texturesList:
            glDeleteTextures(textureID)

###########################


def render():
    global renderer, program, model, camera, shader
    renderer.prepare()
    #glUseProgram(program.program)
    program.start()
    renderer.render(model, program, shader, camera)
    #glUseProgram(0)
    program.stop()
    glutSwapBuffers()


def update():
    global renderer, shader, model, camera
    object = model.object3D

    object.rotation.x += 0.001
    object.rotation.y += 0.001

    object.updateMatrix()
    object.updateMatrixWorld()
    render()


class pyOpenGLShadowMap:
    def __init__(self):
        self.enabled = False


class Renderer:
    def __init__(self, argv):
        self.name = "pyOpenGL"
        self._init_glut(argv)
        self._init_opengl()
        self.gammaFactor = 0
        self.gammaOutput = 0
        self.gammaInput = 0
        self.maxMorphTargets = 0
        self.maxMorphNormals = 0
        self.shadowMap = pyOpenGLShadowMap()
        self.toneMapping = 0
        self.physicallyCorrectLights = False

    def prepare(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def render(self, model, program, shader, camera):
        glBindVertexArray(model.vaoID)

        #programAttributes = program.getAttributes()
        #for a in programAttributes.attributes:
        #    glEnableVertexAttribArray(programAttributes.attributes[a])
        program.enableVertexAttrib()

        object = model.object3D
        object.modelViewMatrix.multiplyMatrices(camera.matrixWorldInverse, object.matrixWorld)

        uniforms = program.getUniforms()
        uniforms.setValue(None, "transformationMatrix", object.matrixWorld)
        uniforms.setValue(None, "projectionMatrix", camera.projectionMatrix)
        uniforms.setValue(None, "viewMatrix", camera.matrixWorldInverse)
        #shader.loadModelViewMatrix(object, camera)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_3D, model.textureID)

        glDrawElements(GL_TRIANGLES, model.vertexCount, GL_UNSIGNED_INT, c_void_p(0))

        #for a in programAttributes.attributes:
        #    glDisableVertexAttribArray(programAttributes.attributes[a])
        #shader.disableVertexAttrib(model)

        glBindVertexArray(0)

    def getRenderTarget(self):
        return None

    def _init_glut(self, argv):
        """glut initialization."""
        glutInit(argv)
        glutInitWindowSize(*WINDOW_SIZE)
        glutInitDisplayMode(GLUT_RGBA|GLUT_DOUBLE|GLUT_DEPTH)
        
        glutCreateWindow(argv[0].encode())
        
        glutReshapeFunc(reshape)
        glutDisplayFunc(render)
        glutKeyboardFunc(keyboard)
        glutMouseFunc(mouse)
        glutMotionFunc(motion)
        glutIdleFunc(update)

    def _init_opengl(self):
        # depth test
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        
        # lighting
        """
        light_position = [1., 1., 2., 0.]
        glLight(GL_LIGHT0, GL_POSITION, light_position)
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1., 1., 1., 1.])
        glMaterialf(GL_FRONT, GL_SHININESS, 100.)    
        """
        # initial state
#        for k in [PERSPECTIVE, LIGHTING, TEXTURING]:
#            keyboard(k)


# main #######################################################################


renderer =None
shader = None
model = None
texture = None
camera = None
program = None


def main(argv=None):
    global renderer, program, model, camera, shader

    if argv is None:
        argv = sys.argv

    renderer = Renderer(argv)

    width, height = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)

    camera = THREE.PerspectiveCamera(45, width/height, 0.1, 20000)
    camera.position = THREE.Vector3(0, 0, 3)
    camera.updateMatrixWorld()
    loader = Loader()

    bgcube = THREE.BoxBufferGeometry(1, 1, 1, 1, 1, 1)
    colors = []
    for i in range(int(bgcube.attributes.position.count)):
        p = THREE.Vector3(bgcube.attributes.position.getX(i), bgcube.attributes.position.getY(i), bgcube.attributes.position.getZ(i))
        colors.extend([p.x+0.5, p.y+0.5, p.z+0.5])
    bgcube.addAttribute('color', Float32BufferAttribute(colors, 3))

    cube = Object3D()
    cube.geometry = bgcube

    shader = myShader(vert_shader, frag_shader)
    material = THREE.ShaderMaterial({
        'vertexShader': vert_shader,
        'fragmentShader': frag_shader
    })

    extensions = pyOpenGLExtensions()
    extensions.get('WEBGL_depth_texture')
    extensions.get('OES_texture_float')
    extensions.get('OES_texture_float_linear')
    extensions.get('OES_texture_half_float')
    extensions.get('OES_texture_half_float_linear')
    extensions.get('OES_standard_derivatives')
    extensions.get('ANGLE_instanced_arrays')

    capabilities = pyOpenGLCapabilities(extensions, {})
    programs = pyOpenGLPrograms(renderer, extensions, capabilities)
    parameters = programs.getParameters(material, lights, [], None, 0, 0, cube)
    programs = programs.acquireProgram(material, shader, parameters, None)

    program = pyOpenGLProgram(renderer, None, None, material, shader, {
        'precision': capabilities.precision,
        'supportsVertexTextures': capabilities.vertexTextures,
        'maxBones': 0,

        'shaderID': 0,

        'outputEncoding': 0,
        'map': 0,
        'mapEncoding': 0,
        'envMapMode': 0,
        'envMapEncoding': 0,
        'envMapCubeUV': 0,
        'lightMap': 0,
        'aoMap': 0,
        'emissiveMap': 0,
        'emissiveMapEncoding': 0,
        'bumpMap': 0,
        'normalMap': 0,
        'displacementMap': 0,
        'roughnessMap': 0,
        'envMap': 0,
        'metalnessMap': 0,
        'specularMap': 0,
        'alphaMap': 0,
        'gradientMap': 0,
        'combine': 0,
        'vertexColors': True,
        'fog': 0,
        'useFog': 0,
        'fogExp': 0,
        'flatShading': 0,
        'sizeAttenuation': 0,
        'logarithmicDepthBuffer': capabilities.logarithmicDepthBuffer,
        'skinning': 0,
        'maxBones': 0,
        'useVertexTexture': 0,
        'morphTargets': 0,
        'morphNormals': 0,
        'maxMorphTargets': 0,
        'maxMorphNormals': 0,
        'numDirLights': 0,
        'numPointLights': 0,
        'numSpotLights': 0,
        'numRectAreaLights': 0,
        'numHemiLights': 0,
        'numClippingPlanes': 0,
        'numClipIntersection': 0,
        'dithering': 0,
        'shadowMapEnabled': 0,
        'toneMapping': 0,
        'physicallyCorrectLights': 0,
        'premultipliedAlpha': 0,
        'alphaTest': 0,
        'doubleSided': 0,
        'flipSided': 0,
        'depthPacking': 0
    })

    model = loader.loadModel(cube, program)
    # model.textureID = loader.loadTexture()

    return glutMainLoop()


if __name__ == "__main__":
    sys.exit(main())