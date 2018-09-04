"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
import re
import os
import json as JSON

from THREE.Constants import *

from THREE.math.Color import *
from THREE.core.Object3D import *
from THREE.objects.Group import *
from THREE.objects.Sprite import *
from THREE.objects.Points import *
from THREE.objects.Line import *
from THREE.objects.LineLoop import *
from THREE.objects.LineSegments import *
#FIXME from THREE.objects.LOD import *
from THREE.objects.Mesh import *
from THREE.objects.SkinnedMesh import *
from THREE.extras.core.Shape import *
from THREE.scenes.Fog import *
from THREE.scenes.FogExp2 import *
from THREE.lights.HemisphereLight import *
from THREE.lights.SpotLights import *
from THREE.lights.PointLight import *
from THREE.lights.DirectionalLight import *
from THREE.lights.AmbientLight import *
from THREE.lights.RectAreaLight import *
from THREE.cameras.OrthographicCamera import *
from THREE.cameras.PerspectiveCamera import *
from THREE.scenes.Scene import *
from THREE.textures.CubeTexture import *
from THREE.textures.Texture import *
from THREE.loaders.ImageLoader import *
from THREE.loaders.LoadingManager import *
from THREE.animation.AnimationClip import *
from THREE.loaders.MaterialLoader import *
from THREE.loaders.BufferGeometryLoader import *
from THREE.loaders.JSONLoader import *
from THREE.loaders.FileLoader import *
from THREE.geometries.Geometries import *
from THREE.extras.core.Curves import *


class ObjectLoader:
    def __init__(self, manager=None):
        self.manager = manager if manager is not None else DefaultLoadingManager
        self.texturePath = None
        self.path = None

    def load(self, url, onLoad=None, onProgress=None, onError=None):
        if self.texturePath is None:
            if self.path:
                self.texturePath = self.path + '/' + url[0:url.rfind('/') + 1]
            else:
                self.texturePath = url[0:url.rfind('/') + 1]

        loader = FileLoader(self.manager)
        loader.setPath(self.path)

        text = loader.load(url, None, onProgress, onError)

        try:
            json = JSON.loads(text)
        except:
            if onError is not None:
                onError(error)

            raise RuntimeError('THREE:ObjectLoader: Can\'t parse ' + url + '.', error.message)

        if 'metadata' not in json or 'type' not in json['metadata'] or json['metadata']['type'].lower() == 'geometry':
            raise RuntimeError('THREE.ObjectLoader: Can\'t load ' + url + '. Use THREE.JSONLoader instead.')

        return self.parse(json, onLoad)

    def setTexturePath(self, value):
        self.texturePath = value
        return self

    def setPath(self, value):
        self.path = value
        return self

    def parse(self, json, onLoad):
        if 'shapes' in json:
            shapes = self.parseShape(json['shapes'])
        else:
            shapes = []
        geometries = self.parseGeometries(json['geometries'], shapes)

        def _load():
            if onLoad is not None:
                onLoad(object)
        
        images = self.parseImages(json['images'], _load)

        textures = self.parseTextures(json['textures'], images)
        materials = self.parseMaterials(json['materials'], textures)

        object = self.parseObject(json['object'], geometries, materials)

        if 'animations' in json:
            object.animations = self.parseAnimations(json['animations'])

        if 'images' not in json or len(json['images']) == 0:
            if onLoad is not None:
                onLoad(object)

        return object

    def parseShape(self, json):
        shapes = {}

        if json is not None:
            for js in json:
                shape = Shape().fromJSON(js)
                shapes[shape.uuid] = shape

        return shapes

    def parseGeometries(self, json, shapes):
        global Geometries
        geometries = {}

        if json is not None:
            geometryLoader = JSONLoader()
            bufferGeometryLoader = BufferGeometryLoader()

            for data in json:
                dtype = data['type']
                if dtype == 'PlaneGeometry' or dtype == 'PlaneBufferGeometry':
                    geometry = Geometries[data.type](
                        data['width'],
                        data['height'],
                        data['widthSegments'],
                        data['heightSegments']
                    )

                elif dtype == 'BoxGeometry' or dtype == 'BoxBufferGeometry' or dtype == 'CubeGeometry':
                    # backwards compatible

                    geometry = Geometries[dtype](
                        data['width'],
                        data['height'],
                        data['depth'],
                        data['widthSegments'],
                        data['heightSegments'],
                        data['depthSegments']
                    )

                elif dtype == 'CircleGeometry' or dtype == 'CircleBufferGeometry':
                    geometry = Geometries[dtype](
                        data['radius'],
                        data['segments'],
                        data['thetaStart'],
                        data['thetaLength']
                    )

                elif dtype == 'CylinderGeometry' or dtype == 'CylinderBufferGeometry':
                    geometry = Geometries[data.type](
                        data['radiusTop'],
                        data['radiusBottom'],
                        data['height'],
                        data['radialSegments'],
                        data['heightSegments'],
                        data['openEnded'],
                        data['thetaStart'],
                        data['thetaLength']
                    )

                elif dtype == 'ConeGeometry' or dtype == 'ConeBufferGeometry':
                    geometry = Geometries[dtype](
                        data['radius'],
                        data['height'],
                        data['radialSegments'],
                        data['heightSegments'],
                        data['openEnded'],
                        data['thetaStart'],
                        data['thetaLength']
                    )

                elif dtype == 'SphereGeometry' or dtype == 'SphereBufferGeometry':
                    geometry = Geometries[dtype](
                        data['radius'],
                        data['widthSegments'],
                        data['heightSegments'],
                        data['phiStart'],
                        data['phiLength'],
                        data['thetaStart'],
                        data['thetaLength']
                    )

                elif dtype == 'DodecahedronGeometry' or \
                    dtype == 'DodecahedronBufferGeometry' or \
                    dtype == 'IcosahedronGeometry' or \
                    dtype == 'IcosahedronBufferGeometry' or \
                    dtype == 'OctahedronGeometry' or \
                    dtype == 'OctahedronBufferGeometry' or \
                    dtype == 'TetrahedronGeometry' or \
                    dtype == 'TetrahedronBufferGeometry':
                    geometry = Geometries[dtype](
                        data['radius'],
                        data['detail']
                    )

                elif dtype == 'RingGeometry' or dtype == 'RingBufferGeometry':
                    geometry = Geometries[dtype](
                        data['innerRadius'],
                        data['outerRadius'],
                        data['thetaSegments'],
                        data['phiSegments'],
                        data['thetaStart'],
                        data['thetaLength']
                    )

                elif dtype == 'TorusGeometry' or dtype == 'TorusBufferGeometry':
                    geometry = Geometries[dtype](
                        data['radius'],
                        data['tube'],
                        data['radialSegments'],
                        data['tubularSegments'],
                        data['arc']
                    )

                elif dtype == 'TorusKnotGeometry' or dtype == 'TorusKnotBufferGeometry':
                    geometry = Geometries[dtype](
                        data['radius'],
                        data['tube'],
                        data['tubularSegments'],
                        data['radialSegments'],
                        data['p'],
                        data['q']
                    )

                elif dtype == 'LatheGeometry' or dtype == 'LatheBufferGeometry':
                    geometry = Geometries[dtype](
                        data['points'],
                        data['segments'],
                        data['phiStart'],
                        data['phiLength']
                    )

                elif dtype == 'PolyhedronGeometry' or dtype == 'PolyhedronBufferGeometry':
                    geometry = Geometries[dtype](
                        data['vertices'],
                        data['indices'],
                        data['radius'],
                        data['details']
                    )

                elif dtype == 'ShapeGeometry' or dtype == 'ShapeBufferGeometry':
                    geometryShapes = []

                    for d in data['shapes']:
                        shape = shapes[d]

                        geometryShapes.append(shape)

                    geometry = Geometries[dtype](
                        geometryShapes,
                        data['curveSegments']
                    )

                elif dtype == 'ExtrudeGeometry' or dtype == 'ExtrudeBufferGeometry':
                    geometryShapes = []

                    for d in data.shapes:
                        shape = shapes[d]

                        geometryShapes.append(shape)

                    if 'option' in data and 'extrudePath' in data['options']:
                        extrudePath = data['options']['extrudePath']

                        data.options.extrudePath = Curves[extrudePath.type]().fromJSON(extrudePath)

                    geometry = Geometries[dtype](
                        geometryShapes,
                        data['options']
                    )

                elif dtype == 'BufferGeometry':
                    geometry = bufferGeometryLoader.parse(data)

                elif dtype == 'Geometry':
                    geometry = geometryLoader.parse(data, self.texturePath)
                    geometry = geometry['geometry']

                else:
                    raise RuntimeWarning('THREE.ObjectLoader: Unsupported geometry type "' + data.type + '"')

                geometry.uuid = data['uuid']

                if 'name' in data:
                    geometry.name = data['name']
                if geometry.my_class(isBufferGeometry) and 'userData' in data:
                    geometry.userData = data['userData']

                geometries[data['uuid']] = geometry

        return geometries

    def parseMaterials(self, json, textures):
        materials = {}

        if json is not None:
            loader = MaterialLoader()
            loader.setTextures(textures)

            for data in json:
                if data['type'] == 'MultiMaterial':
                    # Deprecated
                    array = []

                    for material in data.materials:
                        array.append(loader.parse(material))

                    materials[data['uuid']] = array

                else:
                    materials[data['uuid']] = loader.parse(data)

        return materials

    def parseAnimations(self, json):
        animations = []

        for data in json:
            clip = AnimationClip.parse(data)

            if 'uuid' in data:
                clip.uuid = data['uuid']

            animations.append(clip)

        return animations

    def parseImages(self, json, onLoad):
        images = {}

        def loadImage(url):
            self.manager.itemStart(url)

            def _end():
                self.manager.itemEnd(url)

            def _error():
                self.manager.itemEnd(url)
                self.manager.itemError(url)

            return loader.load(url, None, _end, _error)

        if json is not None and len(json) > 0:
            manager = LoadingManager(onLoad)

            loader = ImageLoader(manager)

            for image in json:
                url = image['url']

                if type(url) is list:
                    # load array of images e.g CubeTexture

                    images[image['uuid']] = []

                    for currentUrl in url:
                        r = '/^(\/\/)|([a-z]+:(\/\/)?)/i'
                        path = currentUrl if re.match(currentUrl, r) else self.texturePath + currentUrl

                        images[image['uuid']].append(loadImage(path))

                else:
                    # load single image
                    r = '/^(\/\/)|([a-z]+:(\/\/)?)/i'
                    path = image['url'] if re.search(image['url'], r) else self.texturePath + image['url']

                    images[image['uuid']] = loadImage(path)

        return images

    def parseTextures(self, json, images):
        def parseConstant(value, typ):
            if type(value) is float:
                return value

            print('THREE.ObjectLoader.parseTexture: Constant should be in numeric form.', value)

            return typ[value]

        textures = {}

        if json is not None:
            for data in json:
                if 'image' not in data:
                    raise RuntimeWarning('THREE.ObjectLoader: No "image" specified for', data.uuid)

                if data['image'] not in images:
                    raise RuntimeWarning('THREE.ObjectLoader: Undefined image', data.image)

                if type(images[data['image']]) is list:
                    texture = CubeTexture(images[data['image']])
                else:
                    texture = Texture(images[data['image']])

                texture.needsUpdate = True

                texture.uuid = data['uuid']

                if 'name' in data:
                    texture.name = data['name']

                if 'mapping' in data:
                    texture.mapping = parseConstant(data['mapping'], TEXTURE_MAPPING)

                if 'offset' in data:
                    texture.offset.fromArray(data['offset'])
                if 'repeat' in data:
                    texture.repeat.fromArray(data['repeat'])
                if 'center' in data:
                    texture.center.fromArray(data['center'])
                if 'rotation' in data:
                    texture.rotation = data['rotation']

                if 'wrap' in data:
                    texture.wrapS = parseConstant(data['wrap'][0], TEXTURE_WRAPPING)
                    texture.wrapT = parseConstant(data['wrap'][1], TEXTURE_WRAPPING)

                if 'format' in data:
                        texture.format = data['format']

                if 'minFilter' in data:
                    texture.minFilter = parseConstant(data['minFilter'], TEXTURE_FILTER)
                if 'magFilter' in data:
                    texture.magFilter = parseConstant(data['magFilter'], TEXTURE_FILTER)
                if 'anisotropy' in data:
                    texture.anisotropy = data['anisotropy']

                if 'flipY' in data:
                    texture.flipY = data['flipY']

                textures[data['uuid']] = texture

        return textures

    def parseObject(self, data, geometries, materials):
        def getGeometry(name):
            if name not in geometries:
                raise RuntimeWarning('THREE.ObjectLoader: Undefined geometry', name)
            return geometries[name]

        def getMaterial(name):
            if name is None:
                return None

            if type(name) is list:
                array = []

                for uuid in name:
                    if uuid not in materials:
                        raise RuntimeWarning('THREE.ObjectLoader: Undefined material', uuid)

                    array.append(materials[uuid])

                return array

            if name not in materials:
                raise RuntimeWarning('THREE.ObjectLoader: Undefined material', name)

            return materials[name]

        if data['type'] == 'Scene':
            object = Scene()

            if 'background' in data:
                if Number.isInteger(data['background']):
                    object.background = Color(data['background'])

            if 'fog' in data:
                if data['fog']['type'] == 'Fog':
                    object.fog = Fog(data['fog']['color'], data['fog']['near'], data['fog']['far'])

                elif data['fog']['type'] == 'FogExp2':
                    object.fog = FogExp2(data['fog']['color'], data['fog']['density'])

        elif data['type'] == 'PerspectiveCamera':

            object = PerspectiveCamera(data['fov'], data['aspect'], data['near'], data['far'])

            if 'focus' in data:
                object.focus = data['focus']
            if 'zoom' in data:
                object.zoom = data['zoom']
            if 'filmGauge' in data:
                object.filmGauge = data['filmGauge']
            if 'filmOffset' in data:
                object.filmOffset = data['filmOffset']
            if 'view' in data:
                object.view = Object.assign({}, data['view'])

        elif data['type'] == 'OrthographicCamera':
            object = OrthographicCamera(data['left'], data['right'], data['top'], data['bottom'], data['near'], data['far'])

            if 'zoom' in data:
                object.zoom = data['zoom']
            if 'view' in data:
                object.view = Object.assign({}, data['view'])

        elif data['type'] == 'AmbientLight':
            if 'intensity' in data:
                object = AmbientLight(data['color'], data['intensity'])
            else:
                object = AmbientLight(data['color'])

        elif data['type'] == 'DirectionalLight':
            if 'intensity' in data:
                object = DirectionalLight(data['color'], data['intensity'])
            else:
                object = DirectionalLight(data['color'])

        elif data['type'] == 'PointLight':
            if 'intensity' in data:
                if 'distance' in data:
                    if 'decay' in data:
                        object = PointLight(data['color'], data['intensity'], data['distance'], data['decay'])
                    else:
                        object = PointLight(data['color'], data['intensity'], data['distance'])
                else:
                    object = PointLight(data['color'], data['intensity'])
            else:
                object = PointLight(data['color'])

        elif data['type'] == 'RectAreaLight':
            if 'intensity' in data:
                if 'width' in data:
                    object = RectAreaLight(data['color'], data['intensity'], data['width'], data['height'])
                else:
                    object = RectAreaLight(data['color'], data['intensity'])
            else:
                object = RectAreaLight(data['color'])

        elif data['type'] == 'SpotLight':
            if 'intensity' in data:
                if 'distance' in data:
                    if 'angle' in data:
                        if 'penumbra' in data:
                            if 'decay' in data:
                                object = SpotLight(data['color'], data['intensity'], data['distance'], data['angle'],
                                           data['penumbra'], data['decay'])
                            else:
                                object = SpotLight(data['color'], data['intensity'], data['distance'], data['angle'],
                                                   data['penumbra'])
                        else:
                            object = SpotLight(data['color'], data['intensity'], data['distance'], data['angle'])

                    else:
                        object = SpotLight(data['color'], data['intensity'], data['distance'])
                else:
                    object = SpotLight(data['color'], data['intensity'])
            else:
                object = SpotLight(data['color'])

        elif data['type'] == 'HemisphereLight':
            if 'intensity' in data:
                object = HemisphereLight(data['color'], data['groundColor'], data['intensity'])
            else:
                object = HemisphereLight(data['color'], data['groundColor'])

        elif data['type'] == 'SkinnedMesh':
            print('THREE.ObjectLoader.parseObject() does not support SkinnedMesh yet.')

        elif data['type'] == 'Mesh':
            geometry = getGeometry(data['geometry'])
            material = getMaterial(data['material'])

            if geometry.bones and len(geometry.bones) > 0 :
                object = SkinnedMesh(geometry, material)

            else:
                object = Mesh(geometry, material)

        elif data['type'] == 'LOD':
            object = LOD()

        elif data['type'] == 'Line':
            object = Line(getGeometry(data['geometry']), getMaterial(data['material']), data['mode'])

        elif data['type'] == 'LineLoop':
            object = LineLoop(getGeometry(data['geometry']), getMaterial(data['material']))

        elif data['type'] == 'LineSegments':
            object = LineSegments(getGeometry(data['geometry']), getMaterial(data['material']))

        elif data['type'] == 'PointCloud' or data['type'] == 'Points':
            object = Points(getGeometry(data['geometry']), getMaterial(data['material']))

        elif data['type'] == 'Sprite':
            object = Sprite(getMaterial(data['material']))

        elif data['type'] == 'Group':
            object = Group()

        else:
            object = Object3D()

        object.uuid = data['uuid']

        if 'name' in data:
            object.name = data['name']

        if 'matrix' in data:
            object.matrix.fromArray(data['matrix'])

            if 'matrixAutoUpdate' in data:
                object.matrixAutoUpdate = data['matrixAutoUpdate']
            if object.matrixAutoUpdate:
                object.matrix.decompose(object.position, object.quaternion, object.scale)

        else:
            if 'position' in data:
                object.position.fromArray(data['position'])
            if 'rotation' in data:
                object.rotation.fromArray(data['rotation'])
            if 'quaternion' in data:
                object.quaternion.fromArray(data['quaternion'])
            if 'scale' in data:
                object.scale.fromArray(data['scale'])

        if 'castShadow' in data:
            object.castShadow = data['castShadow']
        if 'receiveShadow' in data:
            object.receiveShadow = data['receiveShadow']

        if 'shadow' in data:
            if 'bias' in data['shadow']:
                object.shadow.bias = data['shadow']['bias']
            if 'radius' in data['shadow']:
                object.shadow.radius = data['shadow']['radius']
            if 'mapSize' in data['shadow']:
                object.shadow.mapSize.fromArray(data['shadow']['mapSize'])
            if 'camera' in data.shadow:
                object.shadow.camera = self.parseObject(data['shadow']['camera'])

        if 'visible' in data:
            object.visible = data['visible']
        if 'frustumCulled' in data:
            object.frustumCulled = data['frustumCulled']
        if 'renderOrder' in data:
            object.renderOrder = data['renderOrder']
        if 'userData' in data:
            object.userData = data['userData']
        if 'layers' in data:
            object.layers.mask = data['layers']

        if 'children' in data:
            children = data['children']

            for child in children:
                object.add(self.parseObject(child, geometries, materials))

        if data['type'] == 'LOD':
            levels = data['levels']

            for level in levels:
                child = object.getObjectByProperty('uuid', level.object)

                if child is not None :
                    object.addLevel(child, level.distance)

        return object

TEXTURE_MAPPING = {
    'UVMapping': UVMapping,
    'CubeReflectionMapping': CubeReflectionMapping,
    'CubeRefractionMapping': CubeRefractionMapping,
    'EquirectangularReflectionMapping': EquirectangularReflectionMapping,
    'EquirectangularRefractionMapping': EquirectangularRefractionMapping,
    'SphericalReflectionMapping': SphericalReflectionMapping,
    'CubeUVReflectionMapping': CubeUVReflectionMapping,
    'CubeUVRefractionMapping': CubeUVRefractionMapping
}

TEXTURE_WRAPPING = {
    'RepeatWrapping': RepeatWrapping,
    'ClampToEdgeWrapping': ClampToEdgeWrapping,
    'MirroredRepeatWrapping': MirroredRepeatWrapping
}

TEXTURE_FILTER = {
    'NearestFilter': NearestFilter,
    'NearestMipMapNearestFilter': NearestMipMapNearestFilter,
    'NearestMipMapLinearFilter': NearestMipMapLinearFilter,
    'LinearFilter': LinearFilter,
    'LinearMipMapNearestFilter': LinearMipMapNearestFilter,
    'LinearMipMapLinearFilter': LinearMipMapLinearFilter
}
