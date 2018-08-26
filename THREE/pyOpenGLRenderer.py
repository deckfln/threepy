"""
/**
 * @author supereggbert / http://www.paulbrunt.co.uk/
 * @author mrdoob / http://mrdoob.com/
 * @author alteredq / http://alteredqualia.com/
 * @author szimek / https://github.com/szimek/
 * @author tschw
 */
"""
import sys
import time
import pygame
from pygame.locals import *
from ctypes import c_void_p
from threading import Thread
import queue

import THREE.pyOpenGL.OpenGL as cOpenGL

from THREE import *
from THREE.Constants import *
from THREE.renderers.pyOpenGL.pyOpenGLAnimation import *
from THREE.renderers.pyOpenGL.pyOpenGLBufferRenderer import *
from THREE.renderers.pyOpenGL.pyOpenGLCapabilities import *
from THREE.renderers.pyOpenGL.pyOpenGLIndexedBufferRenderer import *
from THREE.renderers.pyOpenGL.pyOpenGLInfo import *
from THREE.renderers.pyOpenGL.pyOpenGLRenderStates import *
import THREE._Math as _Math
from THREE.renderers.shaders.ShaderLib import *
from THREE.Javascript import *
from THREE.pyOpenGLSpriteRenderer import *
from THREE.pyOpenGLGuiRenderer import *
from THREE.pyOpenGLMorphtargets import *
from THREE.DataTexture import *
from THREE.Shader import *
from THREE.OcTree import *
from THREE.renderers.pyOpenGL.pyOpenGLUtils import *

import THREE.Global
import THREE.pyOpenGLProperties as pyOGLproperties


class pyOpenGLVAO:
    """
     VAO stub
    """
    def __init__(self, object3d):
        self.vao = glGenVertexArrays(1)
        geometry = object3d.geometry
        self.index = geometry.index.uuid if hasattr(geometry, 'index') and hasattr(geometry.index, "uuid") else None
        if hasattr(geometry, 'attributes'):
            attributes = geometry.attributes
            self.attributes = [ attribute.uuid if attribute is not None else None for attribute in attributes.__dict__.values()]


class pyOpenGLFlareRenderer:
    """
    stubs
    """

    def __init__(self, renderer, state, textures, capabilities) :
        self.renderer = renderer

    def render(self, flares, scene, camera, viewport):
        return True

"""
***************************************************
"""


class _vr:
    def __init__(self):
        self.enabled = False

    def getDevice(self):
        return None

    def dispose(self):
        return True


_vector3 = Vector3()


class _currentGeometryProgram:
    def __init__(self):
        self.geometry = None
        self.program = None
        self.wireframe = None


class _pyOpenGLRendererThread(Thread):
    """
    https://skryabiin.wordpress.com/2015/04/25/hello-world/
    SDL 2.0, OpenGL, and Multithreading (Windows)
    """

    def __init__(self, renderer, queue):
        Thread.__init__(self)
        self.renderer = renderer
        self.queue = queue

    def run(self):
        """Code à exécuter pendant l'exécution du thread."""
        q = self.queue
        while True:
            material, fog, object = q.get()
            # if item is None:
            #    break
            self.renderer._initMaterial(material, fog, object)
            material.needsUpdate = False

            q.task_done()


"""
*
*
*
"""
class pyOpenGLRenderer:
    """

    """
    drawMode = {
        TrianglesDrawMode: GL_TRIANGLES,
        TriangleStripDrawMode: GL_TRIANGLE_STRIP,
        TriangleFanDrawMode:GL_TRIANGLE_FAN
    }

    def __init__(self, parameters=None):
        """
        pyOpenGL
        """
        self.name = "pyOpenGL"

        self.queue = queue.Queue()
        # self.shaders_thread = _pyOpenGLRendererThread(self, self.queue)
        # self.shaders_thread.start()

        """
        """
        self.parameters = parameters or {}

        """
        """
        self._premultipliedAlpha = self.parameters.premultipliedAlpha if hasattr(self.parameters, 'premultipliedAlpha') else True
        self._powerPreference = self.parameters.powerPreference if hasattr(self.parameters, 'powerPreference') else 'default'

        """
        """
        self.currentRenderList = None
        self.currentRenderState = None

        self._width = 800
        self._height = 600
        self._pixelRatio = 1

        """
        """
        self.onWindowResize = None
        self.onKeyDown = None
        self.animationFrame = None

        """
        // clearing
        """
        self.autoClear = True
        self.autoClearColor = True
        self.autoClearDepth = True
        self.autoClearStencil = True
        """
        // scene graph
        """
        self.sortObjects = True
        """
        // user - defined    clipping
        """
        self.clippingPlanes = []
        self.localClippingEnabled = False
        """
        // physically based shading
        """
        self.gammaFactor = 2.0  # // for backwards compatibility
        self.gammaOutput = False
        self.gammaInput = True
        """
        // physical lights
        """
        self.physicallyCorrectLights = False
        """
        // tone mapping
        """
        self.toneMapping = LinearToneMapping
        self.toneMappingExposure = 1.0
        self.toneMappingWhitePoint = 1.0
        """
        // Morphs
        """
        self.maxMorphTargets = 8
        self.maxMorphNormals = 4
        """
        // internal properties
        """
        self._isContextLost = False
        """
        // internal state cache
        """
        self._framebuffer = None
        self._currentRenderTarget = None
        self._currentFramebuffer = None
        self._currentMaterialId = -1

        # geometry and program caching
        self._currentGeometryProgram = _currentGeometryProgram()

        self._currentCamera = None
        self._currentArrayCamera = None

        self._currentViewport = Vector4()
        self._currentScissor = Vector4()
        self._currentScissorTest = None

        # //

        self._usedTextureUnits = 0

        # //

        self._viewport = Vector4(0, 0, self._width, self._height)
        self._scissor = Vector4(0, 0, self._width, self._height)
        self._scissorTest = False
        """
        // frustum
        """
        self._frustum = Frustum()
        """
        // clipping
        """
        self._clipping = pyOpenGLClipping()
        self._clippingEnabled = 0
        self._localClippingEnabled = 0

        # initialize
        self.extensions = pyOpenGLExtensions()

        self.capabilities = pyOpenGLCapabilities(self.extensions, self.parameters)

        self.extensions.get('OES_texture_float_linear')

        self.utils = pyOpenGLUtils(self.extensions, self.capabilities)

        self.state = pyOpenGLState(self.extensions, self.utils, self.capabilities)
        self.state.scissor(self._currentScissor.copy(self._scissor).multiplyScalar(self._pixelRatio))
        self.state.viewport(self._currentViewport.copy(self._viewport).multiplyScalar(self._pixelRatio))

        self.info = pyOpenGLInfo()
        self.properties = pyOpenGLProperties()
        self.textures = pyOpenGLTextures(self.extensions, self.state, self.properties, self.capabilities, self.utils, self.info)
        self.attributes = pyOpenGLAttributes()
        self.geometries = pyOpenGLGeometries(self.attributes, self.info)
        self.objects = pyOpenGLObjects(self.geometries, self.info)
        self.morphtargets = pyOpenGLMorphtargets()
        self.programCache = pyOpenGLPrograms(self, self.extensions, self.capabilities)
        self.renderLists = pyOpenGLRenderLists()
        self.renderStates = pyOpenGLRenderStates()

        self.background = pyOpenGLBackground(self, self.state, self.objects, self._premultipliedAlpha)

        self.bufferRenderer = pyOpenGLBufferRenderer(self.extensions, self.info, self.capabilities)
        self.indexedBufferRenderer = pyOpenGLIndexedBufferRenderer(self.extensions, self.info, self.capabilities)

        self.guiRenderer = pyOpenGLGuiRenderer(self, self.state, self.textures, self.capabilities) if 'gui' in self.parameters else None

        self.info.programs = self.programCache.programs

        """
        // shadow map
        """
        self.shadowMap = pyOpenGLShadowMap(self, self.objects, self.capabilities.maxTextureSize)

        """
        """
        self.model = None
        self.program = None
        """
        """
        self._projScreenMatrix = Matrix4()
        self.renderList = []
        self.onAnimationFrameCallback = None
        self.animation = pyOpenGLAnimation()
        self.animation.setAnimationLoop(self.onAnimationFrame)

        """
        //
        """

    def _getTargetPixelRatio(self):
        return self._pixelRatio if self._currentRenderTarget is None else 1

    def getPixelRatio(self):
        return self._pixelRatio

    def setPixelRatio(self, value=None):
        if value is None:
            return

        self._pixelRatio = value

        self.setSize(self._width, self._height, False)

    def getSize(self):
        return {
            'width': self._width,
            'height': self._height
            }

    def setSize(self, width, height, updateStyle=False):
        self._width = width
        self._height = height

        self.setViewport(0, 0, width, height)

    def getDrawingBufferSize(self):
        return {
        'width': self._width * self._pixelRatio,
        'height': self._height * self._pixelRatio
        }

    def setDrawingBufferSize(self, width, height, pixelRatio):
        self._width = width
        self._height = height

        self._pixelRatio = pixelRatio

        self._width = width * pixelRatio
        self._height = height * pixelRatio

        self.setViewport(0, 0, width, height)

    def getCurrentViewport(self):
        return self._currentViewport

    def setViewport (self, x, y, width, height):
        self._viewport.set(x, self._height - y - height, width, height)
        self.state.viewport(self._currentViewport.copy(self._viewport).multiplyScalar(self._pixelRatio))

    def setScissor(self, x, y, width, height):
        self._scissor.set(x, self._height - y - height, width, height)
        self.state.scissor(self._currentScissor.copy(self._scissor).multiplyScalar(self._pixelRatio))

    def setScissorTest(self,  bool):
        self._scissorTest = bool
        self.state.setScissorTest(bool)

    def getClearColor(self):
        return self.background.getClearColor()

    def setClearColor(self):
        return self.background.setClearColor()

    def getClearAlpha(self):
        return self.background.getClearAlpha()

    def setClearAlpha(self):
        return self.background.setClearAlpha()

    def clear(self, color=True, depth=True, stencil=True):
        bits = 0
        if color:
            bits |= GL_COLOR_BUFFER_BIT
        if depth:
            bits |= GL_DEPTH_BUFFER_BIT
        if stencil:
            bits |= GL_STENCIL_BUFFER_BIT

        #FIXME
        glClear(bits)

    def clearColor(self):
        self.clear(True, False, False)

    def clearDepth(self):
        self.clear(False, True, False)

    def clearStencil(self):
        self.clear(False, False, True)

    def clearTarget(self, renderTarget, color, depth, stencil):
        self.setRenderTarget(renderTarget)
        self.clear(color, depth, stencil)

    def dispose(self):
        self.renderLists.dispose()
        self.renderStates.dispose()
        self.properties.dispose()
        self.objects.dispose()
        self.attributes.dispose()
        self.textures.dispose()
        self.animation.stop()

    def _releaseMaterialProgramReference(self, material):
        programInfo = self.properties.get(material).program
        material.program = None

        if programInfo is not None:
            self.programCache.releaseProgram(programInfo)

    def _deallocateMaterial(self, material):
        self._releaseMaterialProgramReference(material)
        self.properties.remove(material)

    def _onMaterialDispose(self, material):
        self._deallocateMaterial(material)

    #  Buffer rendering

    def _renderObjectImmediate(self, object, program):
        """

        :param object:
        :param program:
        :param material:
        :return:
        """
        object.render(
            self._renderBufferImmediate(object, program)
       )

    def _renderBufferImmediate(self, object, program):
        """

        :param object:
        :param program:
        :param material:
        :return:
        """
        self.state.initAttributes()

        buffers = self.properties.get(object)

        if object.hasPositions and not buffers.position:
            buffers.position = glGenBuffers(1)
        if object.hasNormals and not buffers.normal:
            buffers.normal = glGenBuffers(1)
        if object.hasUvs and not buffers.uv:
            buffers.uv = glGenBuffers(1)
        if object.hasColors and not buffers.color:
            buffers.color = glGenBuffers(1)

        programAttributes = self.program.getAttributes()

        if object.hasPositions:
            glBindBuffer(GL_ARRAY_BUFFER, buffers.position)
            glBufferData(GL_ARRAY_BUFFER, object.positionArray, GL_DYNAMIC_DRAW)

            self.state.enableAttribute(programAttributes.position)
            pyOpenGL.OpenGL.glVertexAttribPointer(programAttributes.position, 3, GL_FLOAT, GL_FALSE, 0, None)

        if object.hasNormals:
            glBindBuffer(GL_ARRAY_BUFFER, buffers.normal)
            glBufferData(GL_ARRAY_BUFFER, object.normalArray, GL_DYNAMIC_DRAW)

            self.state.enableAttribute(programAttributes.normal)

            pyOpenGL.OpenGL.glVertexAttribPointer(programAttributes.normal, 3, GL_FLOAT, GL_FALSE, 0, None)

        if object.hasUvs:
            glBindBuffer(GL_ARRAY_BUFFER, buffers.uv)
            glBufferData(GL_ARRAY_BUFFER, object.uvArray, GL_DYNAMIC_DRAW)

            self.state.enableAttribute(programAttributes.uv)

            pyOpenGL.OpenGL.glVertexAttribPointer(programAttributes.uv, 2, GL_FLOAT, GL_FALSE, 0, None)

        if object.hasColors:
            glBindBuffer(GL_ARRAY_BUFFER, buffers.color)
            glBufferData(GL_ARRAY_BUFFER, object.colorArray, GL_DYNAMIC_DRAW)

            self.state.enableAttribute(programAttributes.color)

            pyOpenGL.OpenGL.glVertexAttribPointer(programAttributes.color, 3, GL_FLOAT, GL_FALSE, 0, None)

        self.state.disableUnusedAttributes()

        glDrawArrays(GL_TRIANGLES, 0, object.count)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        object.count = 0

    def renderBufferDirect(self, camera, fog, geometry, material, object, group, renderer_id):
        """

        :param camera:
        :param fog:
        :param geometry:
        :param material:
        :param object:
        :param group:
        :return:
        """
        frontFaceCW = object.my_class(isMesh) and object.normalMatrix.determinant() < 0
        self.state.setMaterial(material, frontFaceCW)

        program = self._setProgram(camera, fog, material, object)
        if program is None:
            return False    # initialization of the shader was dlegated to the pyOpenGLShader Trhead

        self.program = program
        wireframe = material.wireframe
        geometryProgram = "%d_%d_%d" % (geometry.id, program.id,  wireframe)

        updateBuffers = False

        if self._currentGeometryProgram.geometry != geometry.id or \
            self._currentGeometryProgram.program != program.id or \
            self._currentGeometryProgram.wireframe != material.wireframe:

            self._currentGeometryProgram.geometry = geometry.id
            self._currentGeometryProgram.program = program.id
            self._currentGeometryProgram.wireframe = material.wireframe
            updateBuffers = True

        if hasattr(object, 'morphTargetInfluences'):
            self.morphtargets.update(object, geometry, material, program)
            updateBuffers = True

        # //

        index = geometry.index
        position = geometry.attributes.position
        rangeFactor = 1

        if wireframe:
            index = self.geometries.getWireframeAttribute(geometry)
            rangeFactor = 2

        renderer = self.bufferRenderer

        attribute = None
        if index:
            attribute = self.attributes.get(index)

            renderer = self.indexedBufferRenderer
            renderer.setIndex(attribute)

        vao = object.vao[renderer_id]
        if vao is None:
            # create the VAO and register all the attributes
            vao = pyOpenGLVAO(object)
            object.vao[renderer_id] = vao
            glBindVertexArray(vao.vao)
            self._setupVertexAttributes(material, program, geometry)

            if index:
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, attribute.buffer)

            glBindVertexArray(0)
            if index:
                 glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

            object.update_vao[renderer_id] = False
        else:
            # if any of the attribute changed, update the vao
            if index is not None and vao.index != index.uuid:
                glBindVertexArray(vao.vao)
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, attribute.buffer)
                glBindVertexArray(0)
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
                vao.index = index.uuid

        # //

        dataCount = 99999999999999999999999

        if index:
            dataCount = index.count
        elif position:
            dataCount = position.count

        rangeStart = geometry.drawRange.start * rangeFactor
        rangeCount = geometry.drawRange.count * rangeFactor

        groupStart = group.start * rangeFactor if group else 0
        groupCount = group.count * rangeFactor if group else float("+inf")

        drawStart = max(rangeStart, groupStart)
        drawEnd = min(dataCount, rangeStart + rangeCount, groupStart + groupCount) - 1

        drawCount = max(0, drawEnd - drawStart + 1)

        if drawCount == 0:
            return False

        # //

        glBindVertexArray(vao.vao)

        if object.my_class(isMesh):
            if not material.wireframe:
                renderer.setMode(self.drawMode[object.drawMode])
            else:
                self.state.setLineWidth(material.wireframeLinewidth * self._getTargetPixelRatio())
                renderer.setMode(GL_LINES)

        elif object.my_class(isLine):
            lineWidth = material.linewidth

            if lineWidth is None:
                lineWidth = 1  # // Not using Line*Material

            self.state.setLineWidth(lineWidth * self._getTargetPixelRatio())

            if object.my_class(isLineSegments):
                renderer.setMode(GL_LINES)
            elif object.my_class(isLineLoop):
                renderer.setMode(GL_LINE_LOOP)
            else:
                renderer.setMode(GL_LINE_STRIP)

        elif object.my_class(isPoints):
            renderer.setMode(GL_POINTS)
            # <OpenGL
            self.state.enable(GL_POINT_SPRITE)
            self.state.enable(GL_VERTEX_PROGRAM_POINT_SIZE)
            # OpenGL>

        elif object.my_class(isSprite):
            renderer.setMode(GL_TRIANGLES)

        if geometry and geometry.my_class(isInstancedBufferGeometry):
            if geometry.maxInstancedCount > 0:
                renderer.renderInstances(geometry, drawStart, drawCount)
        else:
            renderer.render(drawStart, drawCount)

        glBindVertexArray(0)

        return True

    def _setupVertexAttributes(self, material, program, geometry, startIndex=0):
        self.state.initAttributes()

        geometryAttributes = geometry.attributes
        programAttributes = program.getAttributes()
        materialDefaultAttributeValues = material.defaultAttributeValues

        for name in programAttributes:
            programAttribute = programAttributes[name]

            if programAttribute < 0:
                continue

            if hasattr(geometryAttributes, name):
                geometryAttribute = geometryAttributes.__dict__[name]

                if geometryAttribute is None:
                    print("_setupVertexAttributes: missing geometryAttribute")
                    continue

                normalized = geometryAttribute.normalized
                size = geometryAttribute.itemSize

                attribute = self.attributes.get(geometryAttribute)

                # // TODO Attribute may not be available on context restore
                if attribute is None:
                    continue

                buffer = attribute.buffer
                type = attribute.type
                bytesPerElement = attribute.bytesPerElement

                if geometryAttribute.my_class(isInterleavedBufferAttribute):
                    data = geometryAttribute.data
                    stride = data.stride
                    offset = geometryAttribute.offset

                    if data and data.my_class(isInstancedInterleavedBuffer):
                        glEnableVertexAttribArray(programAttribute)
                        glVertexAttribDivisor(programAttribute, data.meshPerAttribute)

                        if geometry.maxInstancedCount is None:
                            geometry.maxInstancedCount = data.meshPerAttribute * data.count
                    else:
                        glEnableVertexAttribArray(programAttribute)

                    glBindBuffer(GL_ARRAY_BUFFER, buffer)
                    pyOpenGL.OpenGL.glVertexAttribPointer(programAttribute, size, type, normalized, stride * bytesPerElement, c_void_p(offset * bytesPerElement))
                else:
                    if geometryAttribute.my_class(isInstancedBufferAttribute):
                        self.state.enableAttributeAndDivisor(programAttribute, geometryAttribute.meshPerAttribute)

                        if geometry.maxInstancedCount is None:
                            geometry.maxInstancedCount = geometryAttribute.meshPerAttribute * geometryAttribute.count
                    else:
                        self.state.enableAttribute(programAttribute)

                    glBindBuffer(GL_ARRAY_BUFFER, buffer)
                    pointer = startIndex * size * bytesPerElement
                    if not pointer:
                        pointer = None
                    else:
                        pointer = c_void_p(pointer)
                    cOpenGL.glVertexAttribPointer(programAttribute, size, type, normalized, 0, pointer)


            elif materialDefaultAttributeValues is not None:
                if name in materialDefaultAttributeValues:
                    value = materialDefaultAttributeValues[name]

                    if len(value) == 2:
                        glVertexAttrib2fv(programAttribute, value)
                    elif len(value) == 3:
                        glVertexAttrib3fv(programAttribute, value)
                    elif len(value) == 4:
                        glVertexAttrib4fv(programAttribute, value)
                    else:
                        glVertexAttrib1fv(programAttribute, value)

    # Compile

    def compile(self, scene, camera):
        self.currentRenderState = self.renderStates.get(scene, camera)
        self.currentRenderState.init()

        def _light(object):
            if object.my_class(isLight):
                self.currentRenderState.pushLight(object)

            if object.castShadow:
                self.currentRenderState.pushShadow( object )

        scene.traverse(_light)

        self.currentRenderState.setupLights( camera )

        def  _material( object ):
            if object.material:
                if type(object.material) is list:
                    for i in range(len(object.material)):
                        self._initMaterial( object.material[i], scene.fog, object )

                else:
                    self._initMaterial( object.material, scene.fog, object )

        scene.traverse(_material)

    # Animation Loop

    def onAnimationFrame(self, time):
        if self.onAnimationFrameCallback:
            self.onAnimationFrameCallback( time )

    def setAnimationLoop(self, callback):
        self.onAnimationFrameCallback = callback
        self.animation.start()

    # Rendering

    def render(self, scene, camera, renderTarget=None, forceClear=False):
        """
        :param scene:
        :param camera:
        :param renderTarget:
        :param forceClear:
        :return:
        """
        if not (camera and camera.my_class(isCamera)):
            raise RuntimeError('THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.')

        if self._isContextLost:
            return

        # // reset caching for this frame

        self._currentGeometryProgram.geometry = None
        self._currentGeometryProgram.program = None
        self._currentGeometryProgram.wireframe = False
        self._currentMaterialId = - 1
        self._currentCamera = None

        # clean up old objects
        for mesh in THREE.Global.dispose_objects_queue:
            self.objects.dispose(mesh)
        THREE.Global.dispose_objects_queue.clear()

        for texture in THREE.Global.dispose_properties_queue:
            self.textures.dispose(texture)
        THREE.Global.dispose_properties_queue.clear()

        # // update scene graph

        if scene.autoUpdate:
            scene.updateMatrixWorld()

        # // update camera matrices and frustum

        if camera.parent is None:
            camera.updateMatrixWorld()

        self.currentRenderState = self.renderStates.get(scene, camera)
        self.currentRenderState.init()

        scene.onBeforeRender(self, scene, camera, renderTarget)
        self._projScreenMatrix.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse)
        self._frustum.setFromMatrix(self._projScreenMatrix)

        self._localClippingEnabled = self.localClippingEnabled
        self._clippingEnabled = self._clipping.init(self.clippingPlanes, self._localClippingEnabled, camera)

        self.currentRenderList = self.renderLists.get(scene, camera)
        self.currentRenderList.init()

        self._projectObject(scene, camera, self.sortObjects)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        if self.sortObjects:
            self.currentRenderList.sort()

        # //
        if self._clippingEnabled:
            self._clipping.beginShadows()

        shadowsArray = self.currentRenderState.shadowsArray
        self.shadowMap.render(shadowsArray, scene, camera)
        self.currentRenderState.setupLights(camera)

        if self._clippingEnabled:
            self._clipping.endShadows()

        # //

        if self.info.autoReset:
            self.info.reset()

        self.setRenderTarget(renderTarget)
        self.state.enable(GL_MULTISAMPLE)
        # //

        self.background.render(self.currentRenderList, scene, camera, forceClear)

        # render scene

        self._renderInstances(scene, camera)

        opaqueObjects = self.currentRenderList.opaque
        transparentObjects = self.currentRenderList.transparent

        if scene.overrideMaterial:
            overrideMaterial = scene.overrideMaterial

            if len(opaqueObjects) > 0:
                self._renderObjects(opaqueObjects, scene, camera, overrideMaterial)
            if len(transparentObjects) > 0:
                self._renderObjects(transparentObjects, scene, camera, overrideMaterial)

        else:
            # // opaque pass (front-to-back order)
            if len(opaqueObjects) > 0:
                self._renderObjects(opaqueObjects, scene, camera)

            # // transparent pass (back-to-front order)
            if len(transparentObjects) > 0:
                self._renderObjects(transparentObjects, scene, camera)

        # custom renderers

        if self.guiRenderer:
            self.guiRenderer.render()

        # // Generate mipmap if we're using any kind of mipmap filtering

        if renderTarget:
            self.textures.updateRenderTargetMipmap(renderTarget)

        # // Ensure depth buffer writing is enabled so it can be cleared on next render

        self.state.buffers.depth.setTest(True)
        self.state.buffers.depth.setMask(True)
        self.state.buffers.color.setMask(True)

        self.state.setPolygonOffset(False)

        scene.onAfterRender(self, scene, camera)
        self.currentRenderList = None
        self.currentRenderState = None

    def _projectObject(self, object, camera, sortObjects, test_culled=True):
        """

        :param object:
        :param camera:
        :param sortObjects:
        :return:
        """
        global _vector3
        if not object.visible:
            return

        if object.layers.test(camera.layers) and object.my_class(isMesh | isLine | isPoints | isLight | isSprite | isLensFlare | isImmediateRenderObject | isOctree):
            if object.my_class(isMesh | isLine | isPoints):
                if object.my_class(isSkinnedMesh):
                    object.skeleton.update()

                if not test_culled or not object.frustumCulled or self._frustum.intersectsObject(object):
                    if sortObjects:
                        _vector3.setFromMatrixPosition(object.matrixWorld).applyMatrix4(self._projScreenMatrix)

                    geometry = self.objects.update(object)
                    material = object.material

                    if isinstance(material, list):
                        groups = geometry.groups

                        for group in groups:
                            groupMaterial = material[group.materialIndex]

                            if groupMaterial and groupMaterial.visible:
                                self.currentRenderList.push(object, geometry, groupMaterial, _vector3.z, group)

                    elif material.visible:
                        self.currentRenderList.push(object, geometry, material, _vector3.np[2], None)

            elif object.my_class(isLight):
                self.currentRenderState.pushLight( object )

                if object.castShadow:
                    self.urrentRenderState.pushShadow( object )

            elif object.my_class(isSprite):
                if not object.frustumCulled or self._frustum.intersectsSprite(object):
                    if sortObjects:
                        _vector3.setFromMatrixPosition( object.matrixWorld ).applyMatrix4( self._projScreenMatrix )

                    geometry = self.objects.update( object )
                    material = object.material

                    self.currentRenderList.push( object, geometry, material, _vector3.z, None)

            elif object.my_class(isLensFlare):
                self.flaresArray.append(object)

            elif object.my_class(isImmediateRenderObject):
                if sortObjects:
                    _vector3.setFromMatrixPosition(object.matrixWorld).applyMatrix4(self._projScreenMatrix)

                self.currentRenderList.push(object, None, object.material, _vector3.z, None)

            elif object.my_class(isOctree):
                self._projectOctree(object, camera, sortObjects)
                return

        for i in object.children:
            if i.visible:
                self._projectObject(i, camera, sortObjects)

    def _renderObjects(self, renderList, scene, camera, overrideMaterial=None):
        """

        :param renderList:
        :param scene:
        :param camera:
        :param overrideMaterial:
        :return:
        """
        for renderItem in renderList:
            object = renderItem.object
            geometry = renderItem.geometry
            material = renderItem.material if overrideMaterial is None else overrideMaterial
            group = renderItem.group

            if camera.my_class(isArrayCamera):
                self._currentArrayCamera = camera

                cameras = camera.cameras

                for camera2 in cameras:
                    if object.layers.test(camera2.layers):
                        if hasattr(camera2, 'viewport'): # XR
                            self.state.viewport( self._currentViewport.copy( camera2.viewport ) )
                        else:
                            bounds = camera2.bounds

                            x = bounds.x * self._width
                            y = bounds.y * self._height
                            width = bounds.z * self._width
                            height = bounds.w * self._height

                            self.state.viewport(self._currentViewport.set(x, y, width, height).multiplyScalar(self._pixelRatio))

                    self._renderObject(object, scene, camera2, geometry, material, group)
            else:
                self._currentArrayCamera = None
                self._renderObject(object, scene, camera, geometry, material, group)

    def _renderObject(self, object, scene, camera, geometry, material, group):
        """

        :param object:
        :param scene:
        :param camera:
        :param geometry:
        :param material:
        :param group:
        :return:
        """
        object.onBeforeRender(self, scene, camera, geometry, material, group)
        self.currentRenderState = self.renderStates.get(scene, self._currentArrayCamera or camera)

        object.modelViewMatrix.updated = object.normalMatrix.updated = False

        if camera.matrixWorldInverse.updated or object.matrixWorld.updated:
            object.modelViewMatrix.multiplyMatrices(camera.matrixWorldInverse, object.matrixWorld)
            object.normalMatrix.getNormalMatrix(object.modelViewMatrix)
            object.modelViewMatrix.updated = True
            object.normalMatrix.updated = True

        if object.my_class(isImmediateRenderObject):
            self.state.setMaterial(material)

            program = self._setProgram(camera, scene.fog, material, object)

            self._currentGeometryProgram.geometry = None
            self._currentGeometryProgram.program = None
            self._currentGeometryProgram.wireframe = False

            self._renderObjectImmediate(object, program, material)
        else:
            self.renderBufferDirect(camera, scene.fog, geometry, material, object, group, isViewRenderer)

        object.onAfterRender(self, scene, camera, geometry, material, group)
        self.currentRenderState = self.renderStates.get(scene, self._currentArrayCamera or camera)

    def _initMaterial(self, material, fog, object):
        global ShaderLib
        materialProperties = self.properties.get(material)

        lights = self.currentRenderState.lights
        shadowsArray = self.currentRenderState.shadowsArray
        lightsHash = materialProperties.lightsHash
        lightsStateHash = lights.state.hash

        parameters = self.programCache.getParameters(material, lights.state, shadowsArray, fog,
                                                     self._clipping.numPlanes, self._clipping.numIntersection, object)

        code = self.programCache.getProgramCode(material, parameters)

        program = materialProperties.program
        programChange = True

        if program is None:
            material.onDispose(self._onMaterialDispose)
        elif program.code != code:
            # // changed glsl or parameters
            self._releaseMaterialProgramReference(material)
        elif lightsHash.stateID != lightsStateHash.stateID or \
            lightsHash.directionalLength != lightsStateHash.directionalLength or \
            lightsHash.pointLength != lightsStateHash.pointLength or \
            lightsHash.spotLength != lightsStateHash.spotLength or \
            lightsHash.rectAreaLength != lightsStateHash.rectAreaLength or \
            lightsHash.hemiLength != lightsStateHash.hemiLength or \
            lightsHash.shadowsLength != lightsStateHash.shadowsLength:

            lightsHash.stateID = lightsStateHash.stateID
            lightsHash.directionalLength = lightsStateHash.directionalLength
            lightsHash.pointLength = lightsStateHash.pointLength
            lightsHash.spotLength = lightsStateHash.spotLength
            lightsHash.rectAreaLength = lightsStateHash.rectAreaLength
            lightsHash.hemiLength = lightsStateHash.hemiLength
            lightsHash.shadowsLength = lightsStateHash.shadowsLength

            programChange = False
        elif parameters['shaderID']:
            # // same glsl and uniform list
            return
        else:
            # // only rebuild uniform list
            programChange = False

        if programChange:
            if parameters['shaderID']:
                shader = getShaderLib(parameters['shaderID'])

                materialProperties.shader = Shader(material.type,
                                                    UniformsUtils.clone(shader.uniforms),
                                                    shader.vertexShader,
                                                    shader.fragmentShader)
            else:
                materialProperties.shader = Shader(material.type,
                                                    material.uniforms,
                                                    material.vertexShader,
                                                    material.fragmentShader)

            material.onBeforeCompile(materialProperties.shader)
            # Computing code again as onBeforeCompile may have changed the shaders
            code = self.programCache.getProgramCode( material, parameters )
            program = self.programCache.acquireProgram(material, materialProperties.shader, parameters, code)

            materialProperties.program = program
            material.program = program

        programAttributes = program.getAttributes()

        if material.morphTargets:
            material.numSupportedMorphTargets = 0
            for i in range(self.maxMorphTargets):
                k = 'morphTarget%d' % i
                if k in programAttributes and programAttributes[k] >= 0:
                    material.numSupportedMorphTargets += 1

        if material.morphNormals:
            material.numSupportedMorphNormals = 0
            for i in range(self.maxMorphNormals):
                k = 'morphNormal%d' % i
                if k in programAttributes and programAttributes[k] >= 0:
                    material.numSupportedMorphNormals += 1

        uniforms = materialProperties.shader.uniforms

        if not material.my_class(isShaderMaterial) and not material.my_class(isRawShaderMaterial) or material.clipping:
            materialProperties.numClippingPlanes = self._clipping.numPlanes
            materialProperties.numIntersection = self._clipping.numIntersection
            uniforms.clippingPlanes = self._clipping.uniform

        materialProperties.fog = fog

        # // store the light setup it was created for
        if lightsHash is None:
            materialProperties.lightsHash = lightsHash = LightHash()

        lightsHash.stateID = lightsStateHash.stateID
        lightsHash.directionalLength = lightsStateHash.directionalLength
        lightsHash.pointLength = lightsStateHash.pointLength
        lightsHash.spotLength = lightsStateHash.spotLength
        lightsHash.rectAreaLength = lightsStateHash.rectAreaLength
        lightsHash.hemiLength = lightsStateHash.hemiLength
        lightsHash.shadowsLength = lightsStateHash.shadowsLength

        if material.lights:
            # // wire up the material to this renderer's lighting state
            uniforms.ambientLightColor.value = lights.state.ambient
            uniforms.directionalLights.value = lights.state.directional
            uniforms.spotLights.value = lights.state.spot
            uniforms.rectAreaLights.value = lights.state.rectArea
            uniforms.pointLights.value = lights.state.point
            uniforms.hemisphereLights.value = lights.state.hemi

            uniforms.directionalShadowMap.value = lights.state.directionalShadowMap
            uniforms.directionalShadowMatrix.value = lights.state.directionalShadowMatrix
            uniforms.spotShadowMap.value = lights.state.spotShadowMap
            uniforms.spotShadowMatrix.value = lights.state.spotShadowMatrix
            uniforms.pointShadowMap.value = lights.state.pointShadowMap
            uniforms.pointShadowMatrix.value = lights.state.pointShadowMatrix
        # // TODO (abelnation): add area lights shadow info to uniforms

        progUniforms = materialProperties.program.getUniforms()
        uniformsList = pyOpenGLUniforms.seqWithValue(progUniforms.seq, uniforms)

        materialProperties.uniformsList = uniformsList

    def prepare(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def _setProgram(self, camera, fog, material, object):
        """

        :param camera:
        :param fog:
        :param material:
        :param object:
        :return:
        """
        self._usedTextureUnits = 0

        materialProperties = self.properties.get(material)
        lights = self.currentRenderState.lights
        lightsHash = materialProperties.lightsHash
        lightsStateHash = lights.state.hash

        if self._clippingEnabled:
            if self._localClippingEnabled or camera != self._currentCamera:
                useCache = camera == self._currentCamera and material.id == self._currentMaterialId

                # // we might want to call self function with some ClippingGroup
                # // object instead of the material, once it becomes feasible
                # // (#8465, #8379)
                self._clipping.setState(
                    material.clippingPlanes, material.clipIntersection, material.clipShadows,
                    camera, materialProperties, useCache)

        if not material.needsUpdate:
            if materialProperties.program is None:
                material.needsUpdate = True
            elif material.fog and materialProperties.fog != fog:
                material.needsUpdate = True
            elif material.lights and ( lightsHash.stateID != lightsStateHash.stateID or \
				lightsHash.directionalLength != lightsStateHash.directionalLength or \
				lightsHash.pointLength != lightsStateHash.pointLength or \
				lightsHash.spotLength != lightsStateHash.spotLength or \
				lightsHash.rectAreaLength != lightsStateHash.rectAreaLength or \
				lightsHash.hemiLength != lightsStateHash.hemiLength or \
				lightsHash.shadowsLength != lightsStateHash.shadowsLength ):
                material.needsUpdate = True
            elif materialProperties.numClippingPlanes is not None and (
                            materialProperties.numClippingPlanes != self._clipping.numPlanes or
                            materialProperties.numIntersection != self._clipping.numIntersection):
                material.needsUpdate = True

        if material.needsUpdate:
            self._initMaterial(material, fog, object)
            material.needsUpdate = False
            #self.queue.put([material, fog, object])
            #return None

        refreshProgram = False
        refreshMaterial = False
        refreshLights = False

        program = materialProperties.program
        p_uniforms = program.getUniforms()
        m_uniforms = materialProperties.shader.uniforms

        if self.state.useProgram(program.program):
            refreshProgram = True
            refreshMaterial = True
            refreshLights = True

        if material.id != self._currentMaterialId:
            self._currentMaterialId = material.id
            refreshMaterial = True

        if refreshProgram or camera != self._currentCamera:
            if camera.projectionMatrix.updated or not p_uniforms.map['projectionMatrix'].uploaded:
                p_uniforms.setValue('projectionMatrix', camera.projectionMatrix)

            if self.capabilities.logarithmicDepthBuffer:
                p_uniforms.setValue('logDepthBufFC', 2.0 / (math.log(camera.far + 1.0) / math.LN2))

            # // Avoid unneeded uniform updates per ArrayCamera's sub-camera

            if self._currentCamera != (self._currentArrayCamera or camera):
                self._currentCamera = (self._currentArrayCamera or camera)

                # // lighting uniforms depend on the camera so enforce an update
                # // now, in case self material supports lights - or later, when
                # // the next material that does gets activated:

                refreshMaterial = True  # // set to True on material change
                refreshLights = True  # // remains set until update done

            # // load material specific uniforms
            # // (shader material also gets them for the sake of genericity)

            if material.my_class(isShaderMaterial | isMeshPhongMaterial | isMeshStandardMaterial) or \
                    material.envMap is not None:

                if 'cameraPosition' in p_uniforms.map:
                    uCamPos = p_uniforms.map['cameraPosition']
                    uCamPos.setValue(Vector3().setFromMatrixPosition(camera.matrixWorld))

            if material.my_class(isMeshPhongMaterial | isMeshLambertMaterial | isMeshBasicMaterial | isMeshStandardMaterial | isShaderMaterial) or \
                    material.skinning:
                p_uniforms.setValue('viewMatrix', camera.matrixWorldInverse)

        # // skinning uniforms must be set even if material didn't change
        # // auto-setting of texture unit for bone texture must go before other textures
        # // not sure why, but otherwise weird things happen

        if material.skinning:
            p_uniforms.setOptional(object, 'bindMatrix')
            p_uniforms.setOptional(object, 'bindMatrixInverse')

            skeleton = object.skeleton

            if skeleton:
                bones = skeleton.bones

            if self.capabilities.floatVertexTextures:
                if skeleton.boneTexture is None:
                    # // layout (1 matrix = 4 pixels)
                    # //      RGBA RGBA RGBA RGBA (=> column1, column2, column3, column4)
                    # //  with  8x8  pixel texture max   16 bones * 4 pixels =  (8 * 8)
                    # //       16x16 pixel texture max   64 bones * 4 pixels = (16 * 16)
                    # //       32x32 pixel texture max  256 bones * 4 pixels = (32 * 32)
                    # //       64x64 pixel texture max 1024 bones * 4 pixels = (64 * 64)

                    size = math.sqrt(len(bones) * 4)  # // 4 pixels needed for 1 matrix
                    size = int(_Math.nextPowerOfTwo(math.ceil(size)))
                    size = max(size, 4)

                    boneMatrices = np.zeros(size * size * 4, 'f')  # // 4 floats per RGBA pixel
                    boneMatrices[0:len(skeleton.boneMatrices)] = skeleton.boneMatrices[:]  # // copy current values

                    boneTexture = DataTexture(boneMatrices, size, size, RGBAFormat, FloatType)
                    boneTexture.needsUpdate = True

                    skeleton.boneMatrices = boneMatrices
                    skeleton.boneTexture = boneTexture
                    skeleton.boneTextureSize = size

                p_uniforms.setValue('boneTexture', skeleton.boneTexture)
                p_uniforms.setValue('boneTextureSize', skeleton.boneTextureSize)
            else:
                p_uniforms.setOptional(skeleton, 'boneMatrices')

        if refreshMaterial:
            p_uniforms.setValue('toneMappingExposure', self.toneMappingExposure)
            p_uniforms.setValue('toneMappingWhitePoint', self.toneMappingWhitePoint)

            if material.lights:
                # // the current material requires lighting info

                # // note: all lighting uniforms are always set correctly
                # // they simply reference the renderer's state for their
                # // values
                # //
                # // use the current material's .needsUpdate flags to set
                # // the GL state when required

                self._markUniformsLightsNeedsUpdate(m_uniforms, refreshLights)

            # // refresh uniforms common to several materials

            if fog and material.fog:
                self._refreshUniformsFog(m_uniforms, fog)

            if material.my_class(isMeshBasicMaterial):
                self._refreshUniformsCommon(m_uniforms, material)

            elif material.my_class(isMeshLambertMaterial):
                self._refreshUniformsCommon(m_uniforms, material)
                self._refreshUniformsLambert(m_uniforms, material)

            elif material.my_class(isMeshPhongMaterial):
                self._refreshUniformsCommon(m_uniforms, material)

                if material.my_class(isMeshToonMaterial):
                    self._refreshUniformsToon(m_uniforms, material)
                else:
                    self._refreshUniformsPhong(m_uniforms, material)

            elif material.my_class(isMeshStandardMaterial):
                self._refreshUniformsCommon(m_uniforms, material)

                if material.my_class(isMeshPhysicalMaterial):
                    self._refreshUniformsPhysical(m_uniforms, material)
                else:
                    self._refreshUniformsStandard(m_uniforms, material)

            elif material.my_class(isMeshNormalMaterial):
                self._refreshUniformsCommon(m_uniforms, material)

            elif material.my_class(isMeshDepthMaterial):
                self._refreshUniformsCommon(m_uniforms, material)
                self._refreshUniformsDepth(m_uniforms, material)

            elif material.my_class(isMeshDistanceMaterial):
                self._refreshUniformsCommon(m_uniforms, material)
                self._refreshUniformsDistance(m_uniforms, material)

            elif material.my_class(isMeshNormalMaterial):
                self._refreshUniformsNormal(m_uniforms, material)

            elif material.my_class(isLineBasicMaterial):
                self._refreshUniformsLine(m_uniforms, material)

                if material.my_class(isLineDashedMaterial):
                    self._refreshUniformsDash(m_uniforms, material)

            elif material.my_class(isPointsMaterial):
                self._refreshUniformsPoints(m_uniforms, material)

            elif material.my_class(isSpriteMaterial):
                self._refreshUniformsSprites(m_uniforms, material)

            elif material.my_class(isShadowMaterial):
                m_uniforms.color.value = material.color
                m_uniforms.opacity.value = material.opacity

            # // RectAreaLight Texture
            # // TODO (mrdoob): Find a nicer implementation

            if hasattr(m_uniforms, 'ltcMat'):
                m_uniforms.ltcMat.value = UniformsLib['LTC_MAT_TEXTURE']
            if hasattr(m_uniforms, 'ltcMag'):
                m_uniforms.ltcMag.value = UniformsLib['LTC_MAG_TEXTURE']

            pyOpenGLUniforms.upload(None, materialProperties.uniformsList, m_uniforms, self)

            if material.my_class(isShaderMaterial) and material.uniformsNeedUpdate:
                pyOpenGLUniforms.upload( None, materialProperties.uniformsList, m_uniforms, self)
                material.uniformsNeedUpdate = False

            if material.my_class(isSpriteMaterial):
                p_uniforms.setValue( 'center', object.center )

        # // common matrices

        if object.modelViewMatrix.updated:
            # TODO FDE: why is there no object if we use the update flag
            p_uniforms.setValue('modelViewMatrix', object.modelViewMatrix)

        if object.normalMatrix.updated:
            p_uniforms.setValue('normalMatrix', object.normalMatrix)

        if object.matrixWorld.updated:
            p_uniforms.setValue('modelMatrix', object.matrixWorld)

        return program

    def _refreshUniformsCommon(self, uniforms, material):
        """
        // Uniforms (refresh uniforms objects)
        """
        uniforms.opacity.value = material.opacity

        if material.color:
            uniforms.diffuse.value = material.color

        if material.emissive:
            uniforms.emissive.value.copy(material.emissive).multiplyScalar(material.emissiveIntensity)

        if material.map is not None:
            uniforms.map.value = material.map

        if material.alphaMap is not None:
            uniforms.alphaMap.value = material.alphaMap

        if material.specularMap is not None:
            uniforms.specularMap.value = material.specularMap

        if material.envMap is not None:
            uniforms.envMap.value = material.envMap

            # // don't flip CubeTexture envMaps, flip everything else:
            # //  WebGLRenderTargetCube will be flipped for backwards compatibility
            # //  WebGLRenderTargetCube.texture will be flipped because it's a Texture and NOT a CubeTexture
            # // this check must be handled differently, or removed entirely, if WebGLRenderTargetCube uses a CubeTexture in the future
            uniforms.flipEnvMap.value = 1 if (not (material.envMap and material.envMap.my_class(isCubeTexture))) else - 1
            uniforms.reflectivity.value = material.reflectivity
            uniforms.refractionRatio.value = material.refractionRatio

            uniforms.maxMipLevel.value = self.properties.get(material.envMap)._maxMipLevel

        if material.lightMap is not None:
            uniforms.lightMap.value = material.lightMap
            uniforms.lightMapIntensity.value = material.lightMapIntensity

        if material.aoMap is not None:
            uniforms.aoMap.value = material.aoMap
            uniforms.aoMapIntensity.value = material.aoMapIntensity

        # // uv repeat and offset setting priorities
        #    // 1. color map
        #    // 2. specular map
        #    // 3. normal map
        #    // 4. bump map
        #    // 5. alpha map
        #    // 6. emissive map

        uvScaleMap = None
        if material.map:
            uvScaleMap = material.map
        elif material.specularMap:
            uvScaleMap = material.specularMap
        elif material.displacementMap:
            uvScaleMap = material.displacementMap
        elif material.normalMap:
            uvScaleMap = material.normalMap
        elif material.bumpMap:
            uvScaleMap = material.bumpMap
        elif material.roughnessMap:
            uvScaleMap = material.roughnessMap
        elif material.metalnessMap:
            uvScaleMap = material.metalnessMap
        elif material.alphaMap:
            uvScaleMap = material.alphaMap
        elif material.emissiveMap:
            uvScaleMap = material.emissiveMap

        if uvScaleMap is not None:
            # // backwards compatibility
            if uvScaleMap.my_class(isWebGLRenderTarget):
                uvScaleMap = uvScaleMap.texture

            if uvScaleMap.matrixAutoUpdate:
                uvScaleMap.updateMatrix()

            uniforms.uvTransform.value.copy( uvScaleMap.matrix )

    def _refreshUniformsLine(self, uniforms, material):
        uniforms.diffuse.value = material.color
        uniforms.opacity.value = material.opacity

    def _refreshUniformsDash(self, uniforms, material):
        uniforms.dashSize.value = material.dashSize
        uniforms.totalSize.value = material.dashSize + material.gapSize
        uniforms.scale.value = material.scale

    def _refreshUniformsPoints(self, uniforms, material):
        uniforms.diffuse.value = material.color
        uniforms.opacity.value = material.opacity
        uniforms.size.value = material.size * self._pixelRatio
        uniforms.scale.value = self._height * 0.5

        uniforms.map.value = material.map

        if material.map is not None:
            if material.map.matrixAutoUpdate:
                material.map.updateMatrix()

            uniforms.uvTransform.value.copy( material.map.matrix )

    def _refreshUniformsFog(self, uniforms, fog):
        uniforms.fogColor.value = fog.color

        if fog.my_class(isFog):
            uniforms.fogNear.value = fog.near
            uniforms.fogFar.value = fog.far
        elif fog.my_class(isFogExp2):
            uniforms.fogDensity.value = fog.density

    def _refreshUniformsLambert(self, uniforms, material):
        if material.emissiveMap:
            uniforms.emissiveMap.value = material.emissiveMap

    def _refreshUniformsPhong(self, uniforms, material):
        uniforms.specular.value = material.specular
        uniforms.shininess.value = max(material.shininess, 1e-4)  # // to prevent pow(0.0, 0.0)

        if material.emissiveMap:
            uniforms.emissiveMap.value = material.emissiveMap

        if material.bumpMap:
            uniforms.bumpMap.value = material.bumpMap
            uniforms.bumpScale.value = material.bumpScale
            if material.side == BackSide:
                uniforms.bumpScale.value *= - 1

        if material.normalMap:
            uniforms.normalMap.value = material.normalMap
            uniforms.normalScale.value.copy(material.normalScale)
            if material.side == BackSide:
                uniforms.normalScale.value.negate()

        if material.displacementMap:
            uniforms.displacementMap.value = material.displacementMap
            uniforms.displacementScale.value = material.displacementScale
            uniforms.displacementBias.value = material.displacementBias

    def _refreshUniformsToon(self, uniforms, material):
        self._refreshUniformsPhong(uniforms, material)

        if material.gradientMap:
            uniforms.gradientMap.value = material.gradientMap

    def _refreshUniformsStandard(self, uniforms, material):
        uniforms.roughness.value = material.roughness
        uniforms.metalness.value = material.metalness

        if material.roughnessMap:
            uniforms.roughnessMap.value = material.roughnessMap

        if material.metalnessMap:
            uniforms.metalnessMap.value = material.metalnessMap

        if material.emissiveMap:
            uniforms.emissiveMap.value = material.emissiveMap

        if material.bumpMap:
            uniforms.bumpMap.value = material.bumpMap
            uniforms.bumpScale.value = material.bumpScale
            if material.side == BackSide:
                uniforms.bumpScale.value *= - 1

        if material.normalMap:
            uniforms.normalMap.value = material.normalMap
            uniforms.normalScale.value.copy(material.normalScale)
            if material.side == BackSide:
                uniforms.normalScale.value.negate()

        if material.displacementMap:
            uniforms.displacementMap.value = material.displacementMap
            uniforms.displacementScale.value = material.displacementScale
            uniforms.displacementBias.value = material.displacementBias

        if material.envMap:
            # //uniforms.envMap.value = material.envMap; // part of uniforms common
            uniforms.envMapIntensity.value = material.envMapIntensity

    def _refreshUniformsPhysical(self, uniforms, material):
        self._refreshUniformsStandard(uniforms, material)

        uniforms.reflectivity.value = material.reflectivity  #also part of uniforms common
        uniforms.clearCoat.value = material.clearCoat
        uniforms.clearCoatRoughness.value = material.clearCoatRoughness

    def _refreshUniformsDepth(self, uniforms, material):
        if material.displacementMap:
            uniforms.displacementMap.value = material.displacementMap
            uniforms.displacementScale.value = material.displacementScale
            uniforms.displacementBias.value = material.displacementBias

    def _refreshUniformsDistance(self, uniforms, material):
        if material.displacementMap:
            uniforms.displacementMap.value = material.displacementMap
            uniforms.displacementScale.value = material.displacementScale
            uniforms.displacementBias.value = material.displacementBias

        uniforms.referencePosition.value.copy(material.referencePosition)
        uniforms.nearDistance.value = material.nearDistance
        uniforms.farDistance.value = material.farDistance

    def _refreshUniformsNormal(self, uniforms, material):
        if material.bumpMap:
            uniforms.bumpMap.value = material.bumpMap
            uniforms.bumpScale.value = material.bumpScale

        if material.normalMap:
            uniforms.normalMap.value = material.normalMap
            uniforms.normalScale.value.copy(material.normalScale)
            if material.side == BackSide:
                uniforms.bumpScale.value *= - 1

        if material.displacementMap:
            uniforms.displacementMap.value = material.displacementMap
            uniforms.displacementScale.value = material.displacementScale
            uniforms.displacementBias.value = material.displacementBias

    def _markUniformsLightsNeedsUpdate(self, uniforms, value):
        """
        // If uniforms are marked as clean, they don't need to be loaded to the GPU.
        """
        uniforms.ambientLightColor.needsUpdate = value

        uniforms.directionalLights.needsUpdate = value
        uniforms.pointLights.needsUpdate = value
        uniforms.spotLights.needsUpdate = value
        uniforms.rectAreaLights.needsUpdate = value
        uniforms.hemisphereLights.needsUpdate = value

    """
    //Textures
    """
    def allocTextureUnit(self):
        textureUnit = self._usedTextureUnits

        if textureUnit >= self.capabilities.maxTextures:
            raise RuntimeWarning('THREE.WebGLRenderer: Trying to use ' + textureUnit + ' texture units while this GPU supports only ' + self.capabilities.maxTextures)

        self._usedTextureUnits += 1
        return textureUnit

    def setTexture2D(self,  texture, slot):
        # warned = False
        # if texture and texture.my_class(isWebGLRenderTarget):
        #    if not warned:
        #        print("THREE.WebGLRenderer.setTexture2D: don't use render targets as textures. Use their .texture property instead.")
        #        warned = True

        #    texture = texture.texture

        self.textures.setTexture2D(texture, slot)

    def setTexture(self, texture, slot):
        # warned = False
        # if not warned:
        #    print("THREE.WebGLRenderer: .setTexture is deprecated, use setTexture2D instead.")
        #    warned = True
        self.textures.setTexture2D(texture, slot)

    def setTextureCube(self, texture, slot):
        warned = False

        # // backwards compatibility: peel texture.texture
        if texture and texture.my_class(isWebGLRenderTargetCube):
            if not warned:
                print(
                    "THREE.WebGLRenderer.setTextureCube: don't use cube render targets as textures. Use their .texture property instead.")
                warned = True

            texture = texture.texture

        # // currently relying on the fact that WebGLRenderTargetCube.texture is a Texture and NOT a CubeTexture
        # // TODO: unify these code paths
        if (texture and texture.my_class(isCubeTexture)) or (isinstance(texture.image, list) and len(texture.image) == 6):
            # // CompressedTexture can have Array in image :/
            # // this function alone should take care of cube textures
            self.textures.setTextureCube(texture, slot)
        else:
            # // assumed: texture property of THREE.WebGLRenderTargetCube
            self.textures.setTextureCubeDynamic(texture, slot)

    def setFramebuffer(self, value ):
        self._framebuffer = value

    def getRenderTarget(self):
        """

        :return:
        """
        return self._currentRenderTarget

    def setRenderTarget(self, renderTarget):
        """

        :param renderTarget:
        :return:
        """
        self._currentRenderTarget = renderTarget

        if renderTarget and self.properties.get(renderTarget).frameBuffer is None:
            self.textures.setupRenderTarget(renderTarget)

        _framebuffer = self._framebuffer
        isCube = False

        if renderTarget:
            frameBuffer = self.properties.get(renderTarget).frameBuffer

            if renderTarget.my_class(isWebGLRenderTargetCube):
                _framebuffer = frameBuffer[renderTarget.activeCubeFace]
                isCube = True
            else:
                _framebuffer = frameBuffer

            self._currentViewport.copy(renderTarget.viewport)
            self._currentScissor.copy(renderTarget.scissor)
            self._currentScissorTest = renderTarget.scissorTest

        else:
            self._currentViewport.copy(self._viewport).multiplyScalar(self._pixelRatio)
            self._currentScissor.copy(self._scissor).multiplyScalar(self._pixelRatio)
            self._currentScissorTest = self._scissorTest

        if self._currentFramebuffer != _framebuffer:
            glBindFramebuffer(GL_FRAMEBUFFER, _framebuffer)
            self._currentFramebuffer = _framebuffer

        self.state.viewport(self._currentViewport)
        self.state.scissor(self._currentScissor)
        self.state.setScissorTest(self._currentScissorTest)

        if isCube:
            textureProperties = self.properties.get(renderTarget.texture)
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,
                                   GL_TEXTURE_CUBE_MAP_POSITIVE_X + renderTarget.activeCubeFace,
                                   textureProperties.__webglTexture, renderTarget.activeMipMapLevel)

    def readRenderTargetPixels(self, renderTarget, x, y, width, height, buffer):
        if not ( renderTarget and renderTarget.my_class(isWebGLRenderTarget) ):
            raise RuntimeError( 'THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.' )

        framebuffer = self.properties.get( renderTarget ).__webglFramebuffer

        if framebuffer:
            restore = False

            if framebuffer != self._currentFramebuffer:
                glbindFramebuffer( GL_FRAMEBUFFER, framebuffer )
                restore = True

                texture = renderTarget.texture
                textureFormat = texture.format
                textureType = texture.type

                if textureFormat != RGBAFormat and utils.convert( textureFormat ) != glgetParameter( GL_IMPLEMENTATION_COLOR_READ_FORMAT ):
                    raise RuntimeError( 'THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.' )

                if textureType != UnsignedByteType and utils.convert( textureType ) != glgetParameter( GL_IMPLEMENTATION_COLOR_READ_TYPE ) and \
                    not ( textureType == FloatType ) and \
                    not ( textureType == HalfFloatType ):
                    raise RuntimeError( 'THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.' )

                if glcheckFramebufferStatus(GL_FRAMEBUFFER ) == GL_FRAMEBUFFER_COMPLETE:
                    # the following if statement ensures valid read requests (no out-of-bounds pixels, see #8604)

                    if ( x >= 0 and x <= ( renderTarget.width - width ) ) and ( y >= 0 and y <= ( renderTarget.height - height ) ):
                        glreadPixels( x, y, width, height, utils.convert( textureFormat ), utils.convert( textureType ), buffer )

            if restore:
                glbindFramebuffer(GL_FRAMEBUFFER, _currentFramebuffer)

    def copyFramebufferToTexture(self, position, texture, level ):
        width = texture.image.width
        height = texture.image.height
        glFormat = utils.convert( texture.format )

        self.setTexture2D( texture, 0 )

        glcopyTexImage2D( _gl.TEXTURE_2D, level or 0, glFormat, position.x, position.y, width, height, 0 )

    def copyTextureToTexture(self, position, srcTexture, dstTexture, level ):
        width = srcTexture.image.width
        height = srcTexture.image.height
        glFormat = utils.convert( dstTexture.format )
        glType = utils.convert( dstTexture.type )

        self.setTexture2D( dstTexture, 0 )

        if srcTexture.my_class(isDataTexture):
            gltexSubImage2D( GL_TEXTURE_2D, level or 0, position.x, position.y, width, height, glFormat, glType, srcTexture.image.data )

        else:
            gltexSubImage2D( GL_TEXTURE_2D, level or 0, position.x, position.y, glFormat, glType, srcTexture.image )

    # FDE extensions

    def _projectOctree(self, octree, camera, sortObjects, test_culled=True):
        """
        Hiarchical Frustrum using octree
        :param object:
        :param camera:
        :param sortObjects:
        :return:
        """

        visibility = self._frustum.intersectsOctree(octree) if test_culled else 1
        if visibility < 0:
            # completely outside of the frustrum
            return

        elif visibility > 0:
            # completely inside the frustrum
            if octree.leaf:
                # for leaf, test each object individually
                for child in octree.children:
                    self._projectObject(child, camera, sortObjects, False)
                #if len(octree.children) > 0:
                #    self._projectObject(octree.children[0], camera, sortObjects, False)

            else:
                # for branch, push all objects down
                #if len(octree.children) > 8:
                #    self._projectObject(octree.children[8], camera, sortObjects, False)
                for child in octree.children:
                    if child is not None:
                        self._projectOctree(child, camera, sortObjects, False)

        else:
            # partialy in the frustrum => recurse to find more
            if octree.leaf:
                # for leaf, test each object individually
                for child in octree.children:
                   self._projectObject(child, camera, sortObjects, False)
                #if len(octree.children) > 0:
                #    self._projectObject(octree.children[0], camera, sortObjects, False)
            else:
                # for branch, continue testing down
                #if len(octree.children) > 8:
                #    self._projectObject(octree.children[8], camera, sortObjects, False)
                for child in octree.children:
                    if child is not None:
                        self._projectOctree(child, camera, sortObjects, test_culled)

    def _renderInstances(self, scene, camera):
        """
        Render all instances objects in the scene
        :param scene:
        :param camera:
        :return:
        """
        global _vector3

        for instance in scene.instances:
            if instance.geometry.maxInstancedCount > 0:
                geometry = self.objects.update(instance)
                material = instance.material

                if isinstance(material, list):
                    groups = geometry.groups

                    for group in groups:
                        groupMaterial = material[group.materialIndex]

                        if groupMaterial and groupMaterial.visible:
                            self.currentRenderList.push(instance, geometry, groupMaterial, _vector3.z, group)

                elif material.visible:
                    self.currentRenderList.push(instance, geometry, material, _vector3.np[2], None)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
