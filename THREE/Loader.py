"""
/**
 * @author alteredq / http:# //alteredqualia.com/
 */
"""
import re
import THREE._Math as _Math
from THREE.Color import *
from THREE.TextureLoader import *
from THREE.MaterialLoader import *


class Handlers:
    def __init__(self):
        self.handlers = []

    def add(self, regex, loader):
        self.handlers.extend([regex, loader])

    def get(self, file):
        handlers = self.handlers

        for i in range(0, len(handlers), 2):
            regex = handlers[i]
            loader = handlers[i + 1]

            if re.search(regex, file):
                return loader

        return None


class Loader:
    Handlers = Handlers()

    def initMaterials(materials, texturePath, crossOrigin ):
        array = [None for i in range(len(materials))]

        for i in range(len(materials)):
            array[ i ] = Loader.createMaterial( materials[ i ], texturePath, crossOrigin )

        return array

    def createMaterial(m, texturePath, crossOrigin ):
        BlendingMode = {
            'NoBlending': NoBlending,
            'NormalBlending': NormalBlending,
            'AdditiveBlending': AdditiveBlending,
            'SubtractiveBlending': SubtractiveBlending,
            'MultiplyBlending': MultiplyBlending,
            'CustomBlending': CustomBlending
        }

        color = Color()
        textureLoader = TextureLoader()
        materialLoader = MaterialLoader()

        # // convert from old material format

        textures = {}

        def loadTexture( path, repeat, offset, wrap, anisotropy ):
            fullPath = texturePath + path
            loader = Loader.Handlers.get( fullPath )

            if loader is not None:
                texture = loader.load( fullPath )
            else:
                textureLoader.setCrossOrigin( crossOrigin )
                texture = textureLoader.load( fullPath )

            if repeat is not None:
                texture.repeat.fromArray( repeat )

                if repeat[ 0 ] != 1:
                    texture.wrapS = RepeatWrapping
                if repeat[ 1 ] != 1:
                    texture.wrapT = RepeatWrapping

            if offset is not None:
                texture.offset.fromArray( offset )

            if wrap is not None:
                if wrap[ 0 ] == 'repeat':
                    texture.wrapS = RepeatWrapping
                if wrap[ 0 ] == 'mirror':
                    texture.wrapS = MirroredRepeatWrapping

                if wrap[ 1 ] == 'repeat':
                    texture.wrapT = RepeatWrapping
                if wrap[ 1 ] == 'mirror':
                    texture.wrapT = MirroredRepeatWrapping

            if anisotropy is not None:
                texture.anisotropy = anisotropy

            uuid = _Math.generateUUID()

            textures[ uuid ] = texture

            return uuid

        # //

        json = {
            'uuid': _Math.generateUUID(),
            'type': 'MeshLambertMaterial'
        }

        for name in m:
            value = m[ name ]

            if name == 'DbgColor' or \
                name == 'DbgIndex' or \
                name == 'opticalDensity' or \
                name == 'illumination':
                continue
            elif name == 'DbgName':
                json['name'] = value
            elif name == 'blending':
                json['blending'] = BlendingMode[ value ]
            elif name == 'colorAmbient' or \
                name == 'mapAmbient':
                print( 'THREE.Loader.createMaterial:', name, 'is no longer supported.' )
            elif name == 'colorDiffuse':
                json['color'] = color.fromArray( value ).getHex()
            elif name == 'colorSpecular':
                json['specular'] = color.fromArray( value ).getHex()
            elif name == 'colorEmissive':
                json['emissive'] = color.fromArray( value ).getHex()
            elif name == 'specularCoef':
                json['shininess'] = value
            elif name == 'shading':
                if value.lower() == 'basic':
                    json['type'] = 'MeshBasicMaterial'
                if value.lower() == 'phong':
                    json['type'] = 'MeshPhongMaterial'
                if value.lower() == 'standard':
                    json['type'] = 'MeshStandardMaterial'
            elif name == 'mapDiffuse':
                w = None
                r = None
                o = None
                a = None

                if 'mapDiffuseRepeat' in m:
                    r = m['mapDiffuseRepeat']
                if 'mapDiffuseOffset' in m:
                    o = m['mapDiffuseOffset']
                if 'mapDiffuseWrap' in m:
                    w = m['mapDiffuseWrap']
                if 'mapDiffuseAnisotropy' in m:
                    a = m['mapDiffuseAnisotropy']
                json['map'] = loadTexture( value, r, o, w, a)
            elif name == 'mapDiffuseRepeat' or \
                name == 'mapDiffuseOffset' or \
                name == 'mapDiffuseWrap' or \
                name == 'mapDiffuseAnisotropy':
                continue
            elif name == 'mapEmissive':
                json['emissiveMap'] = loadTexture( value, m['mapEmissiveRepeat'], m['mapEmissiveOffset'], m['mapEmissiveWrap'], m['mapEmissiveAnisotropy'] )
            elif name == 'mapEmissiveRepeat' or \
                name == 'mapEmissiveOffset' or \
                name == 'mapEmissiveWrap'or \
                name == 'mapEmissiveAnisotropy':
                continue
            elif name == 'mapLight':
                json['lightMap'] = loadTexture( value, m.mapLightRepeat, m.mapLightOffset, m.mapLightWrap, m.mapLightAnisotropy )
            elif name == 'mapLightRepeat' or \
                name == 'mapLightOffset' or \
                name == 'mapLightWrap' or \
                name == 'mapLightAnisotropy':
                continue
            elif name == 'mapAO':
                json['aoMap'] = loadTexture( value, m.mapAORepeat, m.mapAOOffset, m.mapAOWrap, m.mapAOAnisotropy )
            elif name == 'mapAORepeat' or \
                name == 'mapAOOffset' or \
                name == 'mapAOWrap' or \
                name == 'mapAOAnisotropy':
                continue
            elif name == 'mapBump':
                json['bumpMap'] = loadTexture( value, m.mapBumpRepeat, m.mapBumpOffset, m.mapBumpWrap, m.mapBumpAnisotropy )
            elif name == 'mapBumpScale':
                json['bumpScale'] = value
            elif name == 'mapBumpRepeat' or \
                name == 'mapBumpOffset' or \
                name == 'mapBumpWrap' or \
                name == 'mapBumpAnisotropy':
                continue
            elif name == 'mapNormal':
                json['normalMap'] = loadTexture( value, m.mapNormalRepeat, m.mapNormalOffset, m.mapNormalWrap, m.mapNormalAnisotropy )
            elif name == 'mapNormalFactor':
                json['normalScale'] = [ value, value ]
            elif name == 'mapNormalRepeat' or \
                name == 'mapNormalOffset' or \
                name == 'mapNormalWrap' or \
                name == 'mapNormalAnisotropy':
                continue
            elif name == 'mapSpecular':
                json['specularMap'] = loadTexture( value, m.mapSpecularRepeat, m.mapSpecularOffset, m.mapSpecularWrap, m.mapSpecularAnisotropy )
            elif name == 'mapSpecularRepeat' or \
                name == 'mapSpecularOffset' or \
                name == 'mapSpecularWrap' or \
                name == 'mapSpecularAnisotropy':
                continue
            elif name == 'mapMetalness':
                json['metalnessMap'] = loadTexture( value, m.mapMetalnessRepeat, m.mapMetalnessOffset, m.mapMetalnessWrap, m.mapMetalnessAnisotropy )
            elif name == 'mapMetalnessRepeat' or \
                name == 'mapMetalnessOffset' or \
                name == 'mapMetalnessWrap' or \
                name == 'mapMetalnessAnisotropy':
                continue
            elif name == 'mapRoughness':
                json['roughnessMap'] = loadTexture( value, m.mapRoughnessRepeat, m.mapRoughnessOffset, m.mapRoughnessWrap, m.mapRoughnessAnisotropy )
            elif name == 'mapRoughnessRepeat' or \
                 name == 'mapRoughnessOffset' or \
                name == 'mapRoughnessWrap' or \
                name == 'mapRoughnessAnisotropy':
                continue
            elif name == 'mapAlpha':
                json['alphaMap'] = loadTexture( value, m.mapAlphaRepeat, m.mapAlphaOffset, m.mapAlphaWrap, m.mapAlphaAnisotropy )
            elif name == 'mapAlphaRepeat' or \
                name == 'mapAlphaOffset' or \
                name == 'mapAlphaWrap' or \
                name == 'mapAlphaAnisotropy':
                continue
            elif name == 'flipSided':
                json['side'] = BackSide
            elif name == 'doubleSided':
                json['side'] = DoubleSide
            elif name == 'transparency':
                print( 'THREE.Loader.createMaterial: transparency has been renamed to opacity' )
                json['opacity'] = value
            elif name == 'depthTest' or \
                name == 'depthWrite' or \
                name == 'colorWrite' or \
                name == 'opacity' or \
                name == 'reflectivity' or \
                name == 'transparent' or \
                name == 'visible' or \
                name == 'wireframe':
                json[ name ] = value
            elif name == 'vertexColors':
                if value == True:
                    json['vertexColors'] = VertexColors
                if value == 'face':
                    json['vertexColors'] = FaceColors
            else:
                raise RuntimeError( 'THREE.Loader.createMaterial: Unsupported', name, value )

        if json['type'] == 'MeshBasicMaterial':
            del json['emissive']
        if json['type'] != 'MeshPhongMaterial':
            del json['specular']

        if 'opacity' in json and json['opacity'] < 1:
            json['transparent'] = True

        materialLoader.setTextures( textures )

        return materialLoader.parse( json )

    def extractUrlBase(url ):
        parts = url.split( '/' )

        if len(parts) == 1:
            return './'

        parts.pop()

        return '/'.join(parts) + '/'

    def __init__(self):
        self.onLoadStart = None
        self.onLoadProgress = None
        self.onLoadComplete = None


