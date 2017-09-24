"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 * @author alteredq / http:# //alteredqualia.com/
 */
"""
import THREE._Math as _Math
from THREE.Constants import *
from THREE.pyOpenGLObject import *


_materialId = 0

# // TODO: Copied from Object3D.toJSON


def _extractFromCache( cache ):
    values = []

    for key in cache :
        data = cache[ key ]
        del data.metadata
        values.push( data )

    return values


class _uniform:
    def __init__(self, dic):
        if type in dic:
            self.type = dic['type']
        self.value = dic['value']
        self.needsUpdate = True


class _uniforms:
    def __init__(self, lst):
        super().__setattr__('_uniforms', {})
        for uniform in lst:
            self._uniforms[uniform] = _uniform(lst[uniform])

    def __getattr__(self, item):
        try:
            return self._uniforms[item]
        except KeyError:
            raise AttributeError

    def __setattr__(self, key, value):
        self._uniforms[key] = value

    def __delattr__(self, item):
        del self._uniforms[item]

    def __iter__(self):
        return iter(self._uniforms)

    def __getitem__(self, item):
        return self._uniforms[item]


class Material(pyOpenGLObject):
    isMaterial = True
    
    def __init__(self):
        global _materialId
        self.id = _materialId
        _materialId += 1
        self.uuid = _Math.generateUUID()

        self.name = ''
        self.type = 'Material'

        self.fog = True
        self.lights = True

        self.blending = NormalBlending
        self.side = FrontSide
        self.flatShading = False
        self.vertexColors = NoColors # // THREE.NoColors, THREE.VertexColors, THREE.FaceColors

        self.opacity = 1
        self.transparent = False

        self.blendSrc = SrcAlphaFactor
        self.blendDst = OneMinusSrcAlphaFactor
        self.blendEquation = AddEquation
        self.blendSrcAlpha = None
        self.blendDstAlpha = None
        self.blendEquationAlpha = None

        self.depthFunc = LessEqualDepth
        self.depthTest = True
        self.depthWrite = True

        self.clippingPlanes = None
        self.clipIntersection = False
        self.clipShadows = False

        self.colorWrite = True

        self.precision = None  # // override the renderer's default precision for self material

        self.polygonOffset = False
        self.polygonOffsetFactor = 0
        self.polygonOffsetUnits = 0

        self.dithering = False

        self.alphaTest = 0
        self.premultipliedAlpha = False

        self.overdraw = 0  # // Overdrawn pixels (typically between 0 and 1) for fixing antialiasing gaps in CanvasRenderer

        self.visible = True

        self.userData = {}

        self.needsUpdate = True

        #FDE addition
        self.defines = None
        self.map = None
        self.envMap = None
        self.lightMap = None
        self.aoMap = None
        self.emissiveMap = None
        self.bumpMap = None
        self.normalMap = None
        self.displacementMap = None
        self.roughnessMap = None
        self.metalnessMap = None
        self.specularMap = None
        self.alphaMap = None
        self.gradientMap = None
        self.combine = False
        self.sizeAttenuation = 0
        self.depthPacking = False
        self.program = None
        self.index0AttributeName = None
        self.clipping = False
        self.emissive = None
        self.defaultAttributeValues = None
        self.skinning = None
        self.morphTargets = None
        self.morphNormals = None
        self.callback = None
        self.wireframe = False
        self.linewidth = 1
        self.color = None

    def onBeforeCompile(self, shader):
        return True

    def onDispose(self, callback):
        self.callback = callback

    def __getitem__(self, item):
        return self.__dict__[item]

    def __setitem__(self, item, value):
        self.__dict__[item] = value

    def setValues(self, values):
        if values is None:
            return

        for key in values:
            newValue = values[ key ]

            if newValue is None:
                print( "THREE.Material: '" + key + "' parameter is undefined." )
                continue

            # // for backward compatability if shading is set in the constructor
            if key == 'shading' :
                print( 'THREE.' + self.type + ': .shading has been removed. Use the boolean .flatShading instead.' )
                self.flatShading = True if newValue == FlatShading else False
                continue

            if key not in self.__dict__:
                print("THREE." + self.type + ": '" + key + "' is not a property of self material.")
                continue

            currentValue = self[ key ]

            if isinstance(currentValue, int) or isinstance(currentValue, float) or isinstance(currentValue, str):
                self[ key ] = newValue
            elif key == 'overdraw':
                # // ensure overdraw is backwards-compatible with legacy boolean type
                self[key] = Number(newValue)
            elif key == 'uniforms':
                self[key] = _uniforms(newValue)
            elif currentValue and currentValue.isColor:
                currentValue.set( newValue )
            elif (currentValue and currentValue.isVector3 ) and ( newValue and newValue.isVector3):
                currentValue.copy( newValue )
            else:
                self[ key ] = newValue

    def toJSON(self, meta=None):
        isRoot = meta is None

        if isRoot:
            meta = {
                'textures': {},
                'images': {}
            }

        data = {
            'metadata': {
                'version': '4.5',
                'type': 'Material',
                'generator': 'Material.toJSON'
            }
        }

        # // standard Material serialization
        data.uuid = self.uuid
        data.type = self.type

        if self.name != '':
            data.name = self.name

        if self.color and self.color.isColor:
            data.color = self.color.getHex()

        if self.roughness is not None:
            data.roughness = self.roughness
        if self.metalness is not None:
            data.metalness = self.metalness

        if self.emissive and self.emissive.isColor:
            data.emissive = self.emissive.getHex()
        if self.specular and self.specular.isColor:
            data.specular = self.specular.getHex()
        if self.shininess is not None:
            data.shininess = self.shininess
        if self.clearCoat is not None:
            data.clearCoat = self.clearCoat
        if self.clearCoatRoughness is not None:
            data.clearCoatRoughness = self.clearCoatRoughness

        if self.map and self.map.isTexture:
            data.map = self.map.toJSON( meta ).uuid
        if self.alphaMap and self.alphaMap.isTexture:
            data.alphaMap = self.alphaMap.toJSON( meta ).uuid
        if self.lightMap and self.lightMap.isTexture:
            data.lightMap = self.lightMap.toJSON( meta ).uuid
        if self.bumpMap and self.bumpMap.isTexture:
            data.bumpMap = self.bumpMap.toJSON( meta ).uuid
            data.bumpScale = self.bumpScale
        if self.normalMap and self.normalMap.isTexture:
            data.normalMap = self.normalMap.toJSON( meta ).uuid
            data.normalScale = self.normalScale.toArray()
        if self.displacementMap and self.displacementMap.isTexture:
            data.displacementMap = self.displacementMap.toJSON( meta ).uuid
            data.displacementScale = self.displacementScale
            data.displacementBias = self.displacementBias
        if self.roughnessMap and self.roughnessMap.isTexture:
            data.roughnessMap = self.roughnessMap.toJSON( meta ).uuid
        if self.metalnessMap and self.metalnessMap.isTexture:
            data.metalnessMap = self.metalnessMap.toJSON( meta ).uuid

        if self.emissiveMap and self.emissiveMap.isTexture:
            data.emissiveMap = self.emissiveMap.toJSON( meta ).uuid
        if self.specularMap and self.specularMap.isTexture:
            data.specularMap = self.specularMap.toJSON( meta ).uuid

        if self.envMap and self.envMap.isTexture :
            data.envMap = self.envMap.toJSON( meta ).uuid
            data.reflectivity = self.reflectivity; # // Scale behind envMap

        if self.gradientMap and self.gradientMap.isTexture:
            data.gradientMap = self.gradientMap.toJSON( meta ).uuid

        if self.size is not None:
            data.size = self.size
        if self.sizeAttenuation is not None:
            data.sizeAttenuation = self.sizeAttenuation

        if self.blending != NormalBlending:
            data.blending = self.blending
        if self.flatShading == True:
            data.flatShading = self.flatShading
        if self.side != FrontSide:
            data.side = self.side
        if self.vertexColors != NoColors:
            data.vertexColors = self.vertexColors

        if self.opacity < 1:
            data.opacity = self.opacity
        if self.transparent == True:
            data.transparent = self.transparent

        data.depthFunc = self.depthFunc
        data.depthTest = self.depthTest
        data.depthWrite = self.depthWrite

        if self.dithering:
            data.dithering = True

        if self.alphaTest > 0:
            data.alphaTest = self.alphaTest
        if self.premultipliedAlpha:
            data.premultipliedAlpha = self.premultipliedAlpha

        if self.wireframe:
            data.wireframe = self.wireframe
        if self.wireframeLinewidth > 1:
            data.wireframeLinewidth = self.wireframeLinewidth
        if self.wireframeLinecap != 'round':
            data.wireframeLinecap = self.wireframeLinecap
        if self.wireframeLinejoin != 'round':
            data.wireframeLinejoin = self.wireframeLinejoin

        if self.morphTargets == True:
            data.morphTargets = True
        if self.skinning == True:
            data.skinning = True

        if self.visible == False:
            data.visible = False
        if JSON.stringify( self.userData ) != '{}':
            data.userData = self.userData

        if isRoot:
            textures = _extractFromCache( meta.textures )
            images = _extractFromCache( meta.images )

            if textures.length > 0:
                data.textures = textures
            if images.length > 0:
                data.images = images

        return data

    def clone(self):
        return Material().copy( self )

    def copy(self, source):
        self.name = source.name

        self.fog = source.fog
        self.lights = source.lights

        self.blending = source.blending
        self.side = source.side
        self.flatShading = source.flatShading
        self.vertexColors = source.vertexColors

        self.opacity = source.opacity
        self.transparent = source.transparent

        self.blendSrc = source.blendSrc
        self.blendDst = source.blendDst
        self.blendEquation = source.blendEquation
        self.blendSrcAlpha = source.blendSrcAlpha
        self.blendDstAlpha = source.blendDstAlpha
        self.blendEquationAlpha = source.blendEquationAlpha

        self.depthFunc = source.depthFunc
        self.depthTest = source.depthTest
        self.depthWrite = source.depthWrite

        self.colorWrite = source.colorWrite

        self.precision = source.precision

        self.polygonOffset = source.polygonOffset
        self.polygonOffsetFactor = source.polygonOffsetFactor
        self.polygonOffsetUnits = source.polygonOffsetUnits

        self.dithering = source.dithering

        self.alphaTest = source.alphaTest
        self.premultipliedAlpha = source.premultipliedAlpha

        self.overdraw = source.overdraw

        self.visible = source.visible
        self.userData = JSON.parse( JSON.stringify( source.userData ) )

        self.clipShadows = source.clipShadows
        self.clipIntersection = source.clipIntersection

        srcPlanes = source.clippingPlanes
        dstPlanes = None

        if srcPlanes is not None:
            n = len(srcPlanes)
            dstPlanes = [ None for i in range(n) ]

            for i in range(n):
                dstPlanes[ i ] = srcPlanes[ i ].clone()

        self.clippingPlanes = dstPlanes

        return self

    def dispose(self, callback):
        if self.callback:
            self.callback(self)