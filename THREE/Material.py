"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 * @author alteredq / http:# //alteredqualia.com/
 */
"""
import json
import THREE._Math as _Math
from THREE.Constants import *
from THREE.pyOpenGLObject import *
from THREE.Uniforms import *

_materialId = 0

# // TODO: Copied from Object3D.toJSON


def _extractFromCache( cache ):
    values = []

    for key in cache :
        data = cache[ key ]
        del data.metadata
        values.push( data )

    return values


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
        self.program = None
        """
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
        self.index0AttributeName = None
        self.clipping = False
        # self.emissive = None
        self.defaultAttributeValues = None
        self.skinning = None
        self.morphTargets = None
        self.morphNormals = None
        self.callback = None
        self.wireframe = False
        self.linewidth = 1
        self.color = None
        """
		
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
                print("THREE.%s: %s is not a property of self material." % (self.type , key) )
                continue

            currentValue = self[ key ]

            if isinstance(currentValue, int) or isinstance(currentValue, float) or isinstance(currentValue, str):
                self[ key ] = newValue
            elif key == 'overdraw':
                # // ensure overdraw is backwards-compatible with legacy boolean type
                self[key] = Number(newValue)
            elif key == 'uniforms':
                self[key] = Uniforms(newValue)
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
        data['uuid'] = self.uuid
        data['type'] = self.type

        if self.name != '':
            data['name'] = self.name

        if 'color' in self.__dict__ and self.color.isColor:
            data['color'] = self.color.getHex()

        if 'roughness' in self.__dict__:
            data['roughness'] = self.roughness
        if 'metalness' in self.__dict__:
            data['metalness'] = self.metalness

        if 'emissive' in self.__dict__ and self.emissive.isColor:
            data['emissive'] = self.emissive.getHex()
        if 'specular' in self.__dict__ and self.specular.isColor:
            data['specular'] = self.specular.getHex()
        if 'shininess' in self.__dict__:
            data['shininess'] = self.shininess
        if 'clearCoat' in self.__dict__:
            data['clearCoat'] = self.clearCoat
        if 'clearCoatRoughness' in self.__dict__:
            data['clearCoatRoughness'] = self.clearCoatRoughness

        if 'map' in self.__dict__ and self.map and self.map.isTexture:
            data['map'] = self.map.toJSON( meta ).uuid
        if 'alphaMap' in self.__dict__ and self.alphaMap and self.alphaMap.isTexture:
            data['alphaMap'] = self.alphaMap.toJSON( meta ).uuid
        if 'lightMap' in self.__dict__ and self.lightMap and self.lightMap.isTexture:
            data['lightMap'] = self.lightMap.toJSON( meta ).uuid
        if 'bumpMap' in self.__dict__ and self.bumpMap.isTexture:
            data['bumpMap'] = self.bumpMap.toJSON( meta ).uuid
            data['bumpScale'] = self.bumpScale
        if 'normalMap' in self.__dict__ and self.normalMap.isTexture:
            data['normalMap'] = self.normalMap.toJSON( meta ).uuid
            data['normalScale'] = self.normalScale.toArray()
        if 'displacementMap' in self.__dict__ and self.displacementMap.isTexture:
            data['displacementMap'] = self.displacementMap.toJSON( meta ).uuid
            data['displacementScale'] = self.displacementScale
            data['displacementBias'] = self.displacementBias
        if 'roughnessMap' in self.__dict__ and self.roughnessMap.isTexture:
            data['roughnessMap'] = self.roughnessMap.toJSON( meta ).uuid
        if 'metalnessMap' in self.__dict__ and self.metalnessMap.isTexture:
            data['metalnessMap'] = self.metalnessMap.toJSON( meta ).uuid

        if 'emissiveMap' in self.__dict__ and self.emissiveMap.isTexture:
            data['emissiveMap'] = self.emissiveMap.toJSON( meta ).uuid
        if 'specularMap' in self.__dict__ and self.specularMap and self.specularMap.isTexture:
            data['specularMap'] = self.specularMap.toJSON( meta ).uuid

        if 'envMap' in self.__dict__ and self.envMap and self.envMap.isTexture :
            data['envMap'] = self.envMap.toJSON( meta ).uuid
            data['reflectivity'] = self.reflectivity; # // Scale behind envMap

        if 'gradientMap' in self.__dict__ and self.gradientMap.isTexture:
            data['gradientMap'] = self.gradientMap.toJSON( meta ).uuid

        if 'size' in self.__dict__ is not None:
            data['size'] = self.size
        if 'sizeAttenuation' in self.__dict__ is not None:
            data['sizeAttenuation'] = self.sizeAttenuation

        if self.blending != NormalBlending:
            data['blending'] = self.blending
        if self.flatShading:
            data['flatShading'] = self.flatShading
        if self.side != FrontSide:
            data['side'] = self.side
        if self.vertexColors != NoColors:
            data['vertexColors'] = self.vertexColors

        if self.opacity < 1:
            data['opacity'] = self.opacity
        if self.transparent:
            data['transparent'] = self.transparent

        data['depthFunc'] = self.depthFunc
        data['depthTest'] = self.depthTest
        data['depthWrite'] = self.depthWrite

        if self.dithering:
            data['dithering'] = True

        if self.alphaTest > 0:
            data['alphaTest'] = self.alphaTest
        if self.premultipliedAlpha:
            data['premultipliedAlpha'] = self.premultipliedAlpha

        if self.wireframe:
            data['wireframe'] = self.wireframe
        if self.wireframeLinewidth > 1:
            data['wireframeLinewidth'] = self.wireframeLinewidth
        if self.wireframeLinecap != 'round':
            data['wireframeLinecap'] = self.wireframeLinecap
        if self.wireframeLinejoin != 'round':
            data['wireframeLinejoin'] = self.wireframeLinejoin

        if self.morphTargets:
            data['morphTargets'] = True
        if self.skinning:
            data['skinning'] = True

        if not self.visible:
            data['visible'] = False
        if json.dumps( self.userData ) != '{}':
            data['userData'] = self.userData

        if isRoot:
            textures = _extractFromCache( meta.textures )
            images = _extractFromCache( meta.images )

            if textures.length > 0:
                data['textures'] = textures
            if images.length > 0:
                data['images'] = images

        return data

    def clone(self):
        return type(self)().copy( self )

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
        self.userData = json.loads( json.dumps( source.userData ) )

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