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

from OpenGL_accelerate import *
import THREE.pyOpenGL.OpenGL as cOpenGL

from THREE import *
import THREE._Math as _Math
from THREE.ShaderLib import *
from THREE.Javascript import *
from THREE.Constants import *
from THREE.pyOpenGLSpriteRenderer import *
from THREE.pyOpenGLMorphtargets import *
from THREE.DataTexture import *
from THREE.Shader import *
from THREE.OcTree import *


"""
stubs
"""

class pyOpenGLFlareRenderer:
    def __init__(self, renderer, state, textures, capabilities) :
        self.renderer = renderer

    def render(self, flares, scene, camera, viewport):
        return True

"""
***************************************************
"""


class _infoMemory:
    def __init__(self):
        self.geometries = 0
        self.textures = 0


class _infoRender:
    def __init__(self):
        self.frame = 0
        self.calls = 0
        self.vertices = 0
        self.faces = 0
        self.points = 0


class _info:
    def __init__(self, render, memory, programs):
        self.render = render
        self.memory = memory
        self.programs = programs


class _vr:
    def __init__(self):
        self.enabled = False

    def getDevice(self):
        return None

    def dispose(self):
        return True


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

        """
        """
        self.parameters = parameters or {}

        """
        """
        self._premultipliedAlpha = self.parameters.premultipliedAlpha if hasattr(self.parameters, 'premultipliedAlpha') else True
        """
        """
        self.shadowsArray = []
        self.lightsArray = []

        self.currentRenderList = None

        self.spritesArray = []
        self.flaresArray = []

        self._width = 800
        self._height = 600
        self._pixelRatio = 1

        """
        """
        self.onWindowResize = None
        self.onKeyDown = None
        self.animationFrame = None

        self.extensions = pyOpenGLExtensions()
        self.extensions.get('WEBGL_depth_texture')
        self.extensions.get('OES_texture_float')
        self.extensions.get('OES_texture_float_linear')
        self.extensions.get('OES_texture_half_float')
        self.extensions.get('OES_texture_half_float_linear')
        self.extensions.get('OES_standard_derivatives')
        self.extensions.get('ANGLE_instanced_arrays')
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
        self._currentRenderTarget = None
        self._currentFramebuffer = None
        self._currentMaterialId = -1
        self._currentGeometryProgram = ''

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
        """
        // info
        """
        self._infoMemory = _infoMemory()
        self._infoRender = _infoRender()
        self.info = _info(self._infoRender, self._infoMemory, None)

        self.utils = pyOpenGLUtils(self.extensions)

        self.capabilities = pyOpenGLCapabilities(self.extensions, {})

        self.state = pyOpenGLState(self.extensions, self.utils)
        self.state.scissor(self._currentScissor.copy(self._scissor).multiplyScalar(self._pixelRatio))
        self.state.viewport(self._currentViewport.copy(self._viewport).multiplyScalar(self._pixelRatio))

        self.properties = pyOpenGLProperties()
        self.textures = pyOpenGLTextures(self.extensions, self.state, self.properties, self.capabilities, self.utils, self._infoMemory)
        self.attributes = pyOpenGLAttributes()
        self.geometries = pyOpenGLGeometries(self.attributes, self._infoMemory)
        self.objects = pyOpenGLObjects(self.geometries, self._infoRender)
        self.morphtargets = pyOpenGLMorphtargets()
        self.programCache = pyOpenGLPrograms(self, self.extensions, self.capabilities)
        self.lights = pyOpenGLLights()
        self.renderLists = pyOpenGLRenderLists()

        self.background = pyOpenGLBackground(self, self.state, self.geometries, self._premultipliedAlpha)

        self.bufferRenderer = pyOpenGLBufferRenderer(self.extensions, self._infoRender)
        self.indexedBufferRenderer = pyOpenGLIndexedBufferRenderer(self.extensions, self._infoRender)

        self.flareRenderer = pyOpenGLFlareRenderer(self, self.state, self.textures, self.capabilities)
        self.spriteRenderer = pyOpenGLSpriteRenderer(self, self.state, self.textures, self.capabilities)

        self.info.programs = self.programCache.programs

        """
        """
        self.model = None
        self.program = None
        """
        """
        self._projScreenMatrix = Matrix4()
        self.renderList = []
        """
        // vr
        """
        self.vr = _vr()
        """
        // shadow map
        """
        self.shadowMap = pyOpenGLShadowMap(self, self.objects, self.capabilities.maxTextureSize)
        """
        // Clearing
        """
        self.getClearColor = self.background.getClearColor
        self.setClearColor = self.background.setClearColor
        self.getClearAlpha = self.background.getClearAlpha
        self.setClearAlpha = self.background.setClearAlpha
        """
        //
        """
        self._vector3 = Vector3()

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
        device = self.vr.getDevice()

        if device and device.isPresenting:
            print('THREE.WebGLRenderer: Can\'t change size while VR device is presenting.')
            return
        self._width = width
        self._height = height

        self.setViewport(0, 0, width, height)

    def setViewport (self, x, y, width, height):
        self._viewport.set(x, self._height - y - height, width, height)
        self.state.viewport(self._currentViewport.copy(self._viewport).multiplyScalar(self._pixelRatio))

    def setScissor(self, x, y, width, height):
        self._scissor.set(x, self._height - y - height, width, height)
        self.state.scissor(self._currentScissor.copy(self._scissor).multiplyScalar(self._pixelRatio))

    def setScissorTest(self,  bool):
        self._scissorTest = bool
        self.state.setScissorTest(bool)

    def clear(self, color=True, depth=True, stencil=True):
        bits = 0
        if color:
            bits |= GL_COLOR_BUFFER_BIT
        if depth:
            bits |= GL_DEPTH_BUFFER_BIT
        if stencil:
            bits |= GL_STENCIL_BUFFER_BIT

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
        self.vr.dispose()

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
            elif material.lights and materialProperties.lightsHash != self.lights.state.hash:
                material.needsUpdate = True
            elif materialProperties.numClippingPlanes is not None and (
                            materialProperties.numClippingPlanes != self._clipping.numPlanes or
                            materialProperties.numIntersection != self._clipping.numIntersection):
                material.needsUpdate = True

        if material.needsUpdate:
            self._initMaterial(material, fog, object)
            material.needsUpdate = False

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

            if material.my_class(isShaderMaterial) or \
                    material.my_class(isMeshPhongMaterial) or \
                    material.my_class(isMeshStandardMaterial) or \
                    material.envMap is not None:

                if 'cameraPosition' in p_uniforms.map:
                    uCamPos = p_uniforms.map['cameraPosition']
                    uCamPos.setValue(Vector3().setFromMatrixPosition(camera.matrixWorld))

            if material.my_class(isMeshPhongMaterial) or \
                    material.my_class(isMeshLambertMaterial) or \
                    material.my_class(isMeshBasicMaterial) or \
                    material.my_class(isMeshStandardMaterial) or \
                    material.my_class(isShaderMaterial) or \
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
                    size = _Math.nextPowerOfTwo(math.ceil(size))
                    size = max(size, 4)

                    boneMatrices = np.zeros(size * size * 4, 'f')  # // 4 floats per RGBA pixel
                    boneMatrices[0:len(skeleton.boneMatrices)] = skeleton.boneMatrices[:]  # // copy current values

                    boneTexture = DataTexture(boneMatrices, size, size, RGBAFormat, FloatType)

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

            offset = uvScaleMap.offset
            repeat = uvScaleMap.repeat

            uniforms.offsetRepeat.value.set(offset.x, offset.y, repeat.x, repeat.y)

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
            offset = material.map.offset
            repeat = material.map.repeat

            uniforms.offsetRepeat.value.set(offset.x, offset.y, repeat.x, repeat.y)

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

        if material.normalMap:
            uniforms.normalMap.value = material.normalMap
            uniforms.normalScale.value.copy(material.normalScale)

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

        if material.normalMap:
            uniforms.normalMap.value = material.normalMap
            uniforms.normalScale.value.copy(material.normalScale)

        if material.displacementMap:
            uniforms.displacementMap.value = material.displacementMap
            uniforms.displacementScale.value = material.displacementScale
            uniforms.displacementBias.value = material.displacementBias

        if material.envMap:
            # //uniforms.envMap.value = material.envMap; // part of uniforms common
            uniforms.envMapIntensity.value = material.envMapIntensity

    def _refreshUniformsPhysical(self, uniforms, material):
        uniforms.clearCoat.value = material.clearCoat
        uniforms.clearCoatRoughness.value = material.clearCoatRoughness

        self._refreshUniformsStandard(self, uniforms, material)

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

    def _initMaterial(self, material, fog, object):
        global ShaderLib
        materialProperties = self.properties.get(material)

        parameters = self.programCache.getParameters(material, self.lights.state, self.shadowsArray, fog,
                                                     self._clipping.numPlanes, self._clipping.numIntersection, object)

        code = self.programCache.getProgramCode(material, parameters)

        program = materialProperties.program
        programChange = True

        if program is None:
            material.onDispose(self._onMaterialDispose)
        elif program.code != code:
            # // changed glsl or parameters
            self._releaseMaterialProgramReference(material)
        elif parameters.shaderID:
            # // same glsl and uniform list
            return
        else:
            # // only rebuild uniform list
            programChange = False

        if programChange:
            if parameters['shaderID']:
                shader = ShaderLib[parameters['shaderID']]

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

        materialProperties.lightsHash = self.lights.state.hash

        if material.lights:
            # // wire up the material to this renderer's lighting state
            uniforms.ambientLightColor.value = self.lights.state.ambient
            uniforms.directionalLights.value = self.lights.state.directional
            uniforms.spotLights.value = self.lights.state.spot
            uniforms.rectAreaLights.value = self.lights.state.rectArea
            uniforms.pointLights.value = self.lights.state.point
            uniforms.hemisphereLights.value = self.lights.state.hemi

            uniforms.directionalShadowMap.value = self.lights.state.directionalShadowMap
            uniforms.directionalShadowMatrix.value = self.lights.state.directionalShadowMatrix
            uniforms.spotShadowMap.value = self.lights.state.spotShadowMap
            uniforms.spotShadowMatrix.value = self.lights.state.spotShadowMatrix
            uniforms.pointShadowMap.value = self.lights.state.pointShadowMap
            uniforms.pointShadowMatrix.value = self.lights.state.pointShadowMatrix
        # // TODO (abelnation): add area lights shadow info to uniforms

        progUniforms = materialProperties.program.getUniforms()
        uniformsList = pyOpenGLUniforms.seqWithValue(progUniforms.seq, uniforms)

        materialProperties.uniformsList = uniformsList

    def _setupVertexAttributes(self, material, program, geometry, startIndex=0):
        # if geometry and geometry.my_class(isInstancedBufferGeometry):
        #    if extensions.get('ANGLE_instanced_arrays') is None:
        #        raise RuntimeError('THREE.WebGLRenderer.setupVertexAttributes: using THREE.InstancedBufferGeometry but hardware does not support extension ANGLE_instanced_arrays.')

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

                if geometryAttribute.my_class(isBufferAttribute):
                    if geometryAttribute.my_class(isInstancedBufferAttribute):
                        glEnableVertexAttribArray(programAttribute)
                        glVertexAttribDivisor(programAttribute, geometryAttribute.meshPerAttribute)

                        if geometry.maxInstancedCount is None:
                            geometry.maxInstancedCount = geometryAttribute.meshPerAttribute * geometryAttribute.count
                    else:
                        glEnableVertexAttribArray(programAttribute)

                    glBindBuffer(GL_ARRAY_BUFFER, buffer)
                    pointer = startIndex * size * bytesPerElement
                    if not pointer:
                        pointer = None
                    else:
                        pointer = c_void_p(pointer)
                    cOpenGL.glVertexAttribPointer(programAttribute, size, type, normalized, 0, pointer)

                elif geometryAttribute.my_class(isInterleavedBufferAttribute):
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
                    pyOpenGL.OpenGL.glVertexAttribPointer(programAttribute, size, type, normalized, stride * bytesPerElement, c_void_p((startIndex * stride + offset) * bytesPerElement))

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

    def renderBufferDirect(self, camera, fog, geometry, material, object, group):
        """

        :param camera:
        :param fog:
        :param geometry:
        :param material:
        :param object:
        :param group:
        :return:
        """
        self.state.setMaterial(material)

        program = self._setProgram(camera, fog, material, object)
        self.program = program
        wireframe = material.wireframe
        geometryProgram = "%d_%d_%d" % (geometry.id, program.id,  wireframe)

        updateBuffers = False

        if geometryProgram != self._currentGeometryProgram:
            self._currentGeometryProgram = geometryProgram
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

        if object.vao == 0:
            object.vao = glGenVertexArrays(1)
            glBindVertexArray(object.vao)
            self._setupVertexAttributes(material, program, geometry)

            if index:
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, attribute.buffer)

            glBindVertexArray(0)
            if index:
                 glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

            object.update_vao = False


        # //

        dataCount = 0

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
            return

        # //

        glBindVertexArray(object.vao)

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

        if geometry and geometry.my_class(isInstancedBufferGeometry):
            if geometry.maxInstancedCount > 0:
                renderer.renderInstances(geometry, drawStart, drawCount)
        else:
            renderer.render(drawStart, drawCount)

        glBindVertexArray(0)

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

        object.modelViewMatrix.updated = object.normalMatrix.updated = False

        if camera.matrixWorldInverse.updated or object.matrixWorld.updated:
            object.modelViewMatrix.multiplyMatrices(camera.matrixWorldInverse, object.matrixWorld)
            object.normalMatrix.getNormalMatrix(object.modelViewMatrix)
            object.modelViewMatrix.updated = True
            object.normalMatrix.updated = True

        if object.my_class(isImmediateRenderObject):
            self.state.setMaterial(material)

            program = self._setProgram(camera, scene.fog, material, object)

            self._currentGeometryProgram = ''

            self._renderObjectImmediate(object, program, material)
        else:
            self.renderBufferDirect(camera, scene.fog, geometry, material, object, group)

        object.onAfterRender(self, scene, camera, geometry, material, group)

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
                        bounds = camera2.bounds

                    x = bounds.x * self._width
                    y = bounds.y * self._height
                    width = bounds.z * self._width
                    height = bounds.w * self._height

                    self.state.viewport(self._currentViewport.set(x, y, width, height).multiplyScalar(self._pixelRatio))
                    self.state.scissor(self._currentScissor.set(x, y, width, height).multiplyScalar(self._pixelRatio))
                    self.state.setScissorTest(True)

                    self._renderObject(object, scene, camera2, geometry, material, group)
            else:
                self._currentArrayCamera = None
                self._renderObject(object, scene, camera, geometry, material, group)

    # // Buffer rendering

    def _renderObjectImmediate(self, object, program, material):
        """

        :param object:
        :param program:
        :param material:
        :return:
        """
        object.render(
            self._renderBufferImmediate(object, program, material)
       )

    def _renderBufferImmediate(self, object, program, material):
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

            if not material.my_class(isMeshPhongMaterial) and \
                    not material.my_class(isMeshStandardMaterial) and \
                    not material.my_class(isMeshNormalMaterial) and \
                    material.flatShading:

                for i in range(0, object.count * 3, 9):
                    array = object.normalArray

                    nx = (array[i + 0] + array[i + 3] + array[i + 6]) / 3
                    ny = (array[i + 1] + array[i + 4] + array[i + 7]) / 3
                    nz = (array[i + 2] + array[i + 5] + array[i + 8]) / 3

                    array[i + 0] = nx
                    array[i + 1] = ny
                    array[i + 2] = nz

                    array[i + 3] = nx
                    array[i + 4] = ny
                    array[i + 5] = nz

                    array[i + 6] = nx
                    array[i + 7] = ny
                    array[i + 8] = nz

            glBufferData(GL_ARRAY_BUFFER, object.normalArray, GL_DYNAMIC_DRAW)

            self.state.enableAttribute(programAttributes.normal)

            pyOpenGL.OpenGL.glVertexAttribPointer(programAttributes.normal, 3, GL_FLOAT, GL_FALSE, 0, None)

        if object.hasUvs and material.map:
            glBindBuffer(GL_ARRAY_BUFFER, buffers.uv)
            glBufferData(GL_ARRAY_BUFFER, object.uvArray, GL_DYNAMIC_DRAW)

            self.state.enableAttribute(programAttributes.uv)

            pyOpenGL.OpenGL.glVertexAttribPointer(programAttributes.uv, 2, GL_FLOAT, GL_FALSE, 0, None)

        if object.hasColors and material.vertexColors != NoColors:
            glBindBuffer(GL_ARRAY_BUFFER, buffers.color)
            glBufferData(GL_ARRAY_BUFFER, object.colorArray, GL_DYNAMIC_DRAW)

            self.state.enableAttribute(programAttributes.color)

            pyOpenGL.OpenGL.glVertexAttribPointer(programAttributes.color, 3, GL_FLOAT, GL_FALSE, 0, None)

        self.state.disableUnusedAttributes()

        glDrawArrays(GL_TRIANGLES, 0, object.count)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        object.count = 0

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

    def _projectObject(self, object, camera, sortObjects, test_culled=True):
        """

        :param object:
        :param camera:
        :param sortObjects:
        :return:
        """
        if not object.visible:
            return

        _vector3 = self._vector3
        visible = object.layers.test(camera.layers)

        if visible:
            if object.my_class(isMesh) or object.my_class(isLine) or object.my_class(isPoints):
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
                self.lightsArray.append(object)

                if object.castShadow:
                    self.shadowsArray.append(object)

            elif object.my_class(isSprite):
                if not object.frustumCulled or self._frustum.intersectsSprite(object):
                    self.spritesArray.append(object)

            elif object.my_class(isLensFlare):
                self.flaresArray.append(object)

            elif object.my_class(isImmediateRenderObject):
                if sortObjects:
                    _vector3.setFromMatrixPosition(object.matrixWorld).applyMatrix4(self._projScreenMatrix)

                self.currentRenderList.push(object, None, object.material, _vector3.z, None)

            elif object.my_class(isOctree):
                self._projectOctree(object, camera, sortObjects)
                return

        children = object.children
        for i in children:
            self._projectObject(i, camera, sortObjects)

    def _renderInstances(self, scene, camera):
        """
        Render all instances objects in the scene
        :param scene:
        :param camera:
        :return:
        """
        _vector3 = self._vector3

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

        self._currentGeometryProgram = ''
        self._currentMaterialId = - 1
        self._currentCamera = None

        # // update scene graph

        if scene.autoUpdate:
            scene.updateMatrixWorld()

        # // update camera matrices and frustum

        if camera.parent is None:
            camera.updateMatrixWorld()

        if self.vr.enabled:
            camera = self.vr.getCamera(camera)

        self._projScreenMatrix.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse)
        self._frustum.setFromMatrix(self._projScreenMatrix)

        self.lightsArray.clear()
        self.shadowsArray.clear()

        self.spritesArray.clear()
        self.flaresArray.clear()

        self._localClippingEnabled = self.localClippingEnabled
        self._clippingEnabled = self._clipping.init(self.clippingPlanes, self._localClippingEnabled, camera)

        self.currentRenderList = self.renderLists.get(scene, camera)
        self.currentRenderList.init()

        self._projectObject(scene, camera, self.sortObjects)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        if self.sortObjects:
            self.currentRenderList.sort()

        # //

        if self._clippingEnabled:
            self._clipping.beginShadows()

        self.shadowMap.render(self.shadowsArray, scene, camera)

        self.lights.setup(self.lightsArray, self.shadowsArray, camera)

        if self._clippingEnabled:
            self._clipping.endShadows()

        # //

        self._infoRender.frame += 1
        self._infoRender.calls = 0
        self._infoRender.vertices = 0
        self._infoRender.faces = 0
        self._infoRender.points = 0

        self.setRenderTarget(renderTarget)

        # //

        self.background.render(self.currentRenderList, scene, camera, forceClear)

        # // render scene

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

        # // custom renderers

        self.spriteRenderer.render(self.spritesArray, scene, camera)
        self.flareRenderer.render(self.flaresArray, scene, camera, self._currentViewport)

        # // Generate mipmap if we're using any kind of mipmap filtering

        if renderTarget:
            self.textures.updateRenderTargetMipmap(renderTarget)

        # // Ensure depth buffer writing is enabled so it can be cleared on next render

        self.state.buffers.depth.setTest(True)
        self.state.buffers.depth.setMask(True)
        self.state.buffers.color.setMask(True)

        self.state.setPolygonOffset(False)

        if self.vr.enabled:
            self.vr.submitFrame()

        # // _gl.finish()

    def getRenderTarget(self):
        """

        :return:
        """
        return self._currentRenderTarget

    def setRenderTarget (self, renderTarget):
        """

        :param renderTarget:
        :return:
        """
        self._currentRenderTarget = renderTarget

        if renderTarget and self.properties.get(renderTarget).frameBuffer is None:
            self.textures.setupRenderTarget(renderTarget)

        _framebuffer = 0
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
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_CUBE_MAP_POSITIVE_X + renderTarget.activeCubeFace, textureProperties.__webglTexture, renderTarget.activeMipMapLevel)

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
