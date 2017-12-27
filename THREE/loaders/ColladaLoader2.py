"""
/**
 * @author mrdoob / http:#mrdoob.com/
 * @author Mugen87 / https:#github.com/Mugen87
 */
"""
from lxml import etree
from xml.dom import minidom
import re

import THREE
from THREE.Vector3 import *
from THREE.Quaternion import *
from THREE.Matrix4 import *
from THREE.Javascript import *
from THREE.Skeleton import *
from THREE.SkinnedMesh import *
from THREE.Loader import *
from THREE.LoadingManager import *
import THREE._Math as _Math


class _keyframes:
    def __init__(self, time, value):
        self.time = time
        self.value = value


class _skinVertex:
    def __init__(self, index, weight):
        self.index = index
        self.weight = weight


class _skinJoint:
    def __init__(self, name, boneInverse):
        self.name = name
        self.boneInverse = boneInverse


class _skinArray:
    def __init__(self, stride):
        self.array = []
        self.stride = stride


class _skin:
    def __init__(self, stride):
        self.joints = []  # self must be an array to preserve the joint order
        self.indices = _skinArray(stride)
        self.weights = _skinArray(stride)


class _controler:
    def __init__(self, id, skin):
        self.id = id
        self.skin = skin


class _geometry:
    def __init__(self, name):
        self.name = name
        self.sources = {}
        self.vertices = {}
        self.primitives = []


class Collada:
    def __init__(self, animations, kinematics, library, scene):
        self.animations = animations
        self.kinematics = kinematics
        self.library = library
        self.scene = scene


class ColladaLoader:
    crossOrigin = 'Anonymous'
    
    def __init__(self, manager=None):
        self.manager = manager if manager is not None else THREE.DefaultLoadingManager

    def load(self, url, onLoad=None, onProgress=None, onError=None):
        path = THREE.Loader.extractUrlBase(url)

        collada = self.parse(url, path)

        if onLoad is not None:
            onLoad(collada)

        return collada

    def convertUpAxis(self, value):
        print('THREE.ColladaLoader.options.convertUpAxis: TODO')

    options = property(None, convertUpAxis)


    def setCrossOrigin(self, value):
        self.crossOrigin = value

    def parse(self, text, path):
        matrix = THREE.Matrix4()
        position = THREE.Vector3()
        scale = THREE.Vector3()
        quaternion = THREE.Quaternion()
        vector = THREE.Vector3()
        kinematics = {}

        def _parseFloats(string):
            if len(text) == 0:
                return []

            t = re.sub("^\s*", "", string)
            t = re.sub("\s*$", "", t)
            lines = re.split(r'\s+', t)
            array = np.zeros(len(lines), np.float64)
            for i in range(len(lines)):
                if lines[i] != "":
                    array[i] = float(lines[i])
                else:
                    array[i] = 0

            return array

        def getElementsByTagName(xml, name):
            # Non recursive xml.getElementsByTagName() ...
            array = []
            childNodes = xml.childNodes

            for child in childNodes:
                if child.nodeName == name:
                    array.append(child)

            return array

        def getElementsBySelector(xml, name, value):
            if xml._attrs is None:
                return None

            if name in xml._attrs and xml._attrs[name].nodeValue == value:
                return xml

            childNodes = xml.childNodes
            for child in childNodes:
                if child.nodeType != 3:
                    ret = getElementsBySelector(child, name, value)
                    if ret is not None:
                        return ret

            return None

        def parseStrings(text):
            if len(text) == 0:
                return []

            parts = re.split(r"\s+", text.strip())
            array = [ parts[i] for i in range(len(parts)) ]

            return array

        def parseFloats(text):
            if len(text) == 0:
                return []

            parts = re.split(r"\s+", text.strip())
            array = [float(part) for part in parts]

            return array

        def parseInts(text):
            if len(text) == 0:
                return []

            parts = re.split(r"\s+", text.strip())
            array = [int(part) for part in parts]

            return array

        def parseId(text):
            return text[1:]

        def isEmpty(object):
            return len(object.__dict__) == 0

        # asset

        def parseAsset(xml):
            return javascriptObject({
                'unit': parseAssetUnit(getElementsByTagName(xml, 'unit')[0]),
                'upAxis': parseAssetUpAxis(getElementsByTagName(xml, 'up_axis')[0])
            })

        def parseAssetUnit(xml):
            meter = xml.getAttribute('meter')
            return float(meter) if meter != '' else 1

        def parseAssetUpAxis(xml):
            return xml.firstChild.data if xml is not None else 'Y_UP'

        # library

        def parseLibrary(xml, libraryName, nodeName, parser):
            library = getElementsByTagName(xml, libraryName)

            if len(library) > 0:
                elements = getElementsByTagName(library[0], nodeName)

                for element in elements:
                    parser(element)

        def buildLibrary(data, builder):
            for name in data:
                object = data[name]
                object.build = builder(data[name])

        # get

        def getBuild(data, builder):
            if data.build is not None:
                return data.build

            data.build = builder(data)

            return data.build

        # animation

        def parseAnimation(xml):
            data = javascriptObject({
                'sources': {},
                'samplers': {},
                'channels': {}
            })

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'source':
                    id = child.getAttribute('id')
                    data.sources[id] = parseSource(child)
                elif child.nodeName == 'sampler':
                    id = child.getAttribute('id')
                    data.samplers[id] = parseAnimationSampler(child)
                elif child.nodeName == 'channel':
                    id = child.getAttribute('target')
                    data.channels[id] = parseAnimationChannel(child)
                else:
                    print(child)

            library.animations[xml.getAttribute('id')] = data

        def parseAnimationSampler(xml):
            data = javascriptObject({
                'inputs': {},
            })

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'input':
                    id = parseId(child.getAttribute('source'))
                    semantic = child.getAttribute('semantic')
                    data.inputs[semantic] = id

            return data

        def parseAnimationChannel(xml):
            data = javascriptObject({})

            target = xml.getAttribute('target')

            # parsing SID Addressing Syntax

            parts = target.split('/')

            id = parts.pop(0)
            sid = parts.pop(0)

            # check selection syntax

            arraySyntax = '(' in sid
            memberSyntax = '.' in sid

            if memberSyntax:
                #  member selection access

                parts = sid.split('.')
                sid = parts.pop(0)
                data.member = parts.pop(0)

            elif arraySyntax:
                # array-access syntax. can be used to express fields in one-dimensional vectors or two-dimensional matrices.

                indices = sid.split('(')
                sid = indices.pop(0)

                for i in range(len(indices)):
                    indices[i] = int(indices[i].replace(')', ''))

                data.indices = indices

            data.id = id
            data.sid = sid

            data.arraySyntax = arraySyntax
            data.memberSyntax = memberSyntax

            data.sampler = parseId(xml.getAttribute('source'))

            return data

        def buildAnimation(data):
            tracks = []

            channels = data.channels
            samplers = data.samplers
            sources = data.sources

            for target in channels:
                channel = channels[target]
                sampler = samplers[channel.sampler]

                inputId = sampler.inputs.INPUT
                outputId = sampler.inputs.OUTPUT
                interpolationId = sampler.inputs.INTERPOLATION

                inputSource = sources[inputId]
                outputSource = sources[outputId]
                interpolationSource = sources[interpolationId]

                animation = buildAnimationChannel(channel, inputSource, outputSource, interpolationSource)

                createKeyframeTracks(animation, tracks)

            return tracks

        def getAnimation(id):
            return getBuild(library.animations[id], buildAnimation)

        def buildAnimationChannel(channel, inputSource, outputSource, interpolationSource):
            node = library.nodes[channel.id]
            object3D = getNode(node.id)

            transform = node.transforms[channel.sid]
            defaultMatrix = node.matrix.clone().transpose()

            data = {}

            # the collada spec allows the animation of data in various ways.
            # depending on the transform type (matrix, translate, rotate, scale), we execute different logic

            if transform == 'matrix':
                for i in range(len(inputSource.array)):
                    time = inputSource.array[i]
                    stride = i * outputSource.stride

                    if channel.arraySyntax is True:
                        value = outputSource.array[stride]
                        index = channel.indices[0] + 4 * channel.indices[1]

                        # TODO FDE: fix it to handle the array
                        data[time][index] = value

                    else:
                        data[time] = [outputSource.array[stride + j] for j in range(outputSource.stride)]

            elif transform == 'translate':
                print('THREE.ColladaLoader: Animation transform type "%s" not yet implemented.', transform)

            elif transform == 'rotate':
                print('THREE.ColladaLoader: Animation transform type "%s" not yet implemented.', transform)

            elif transform == 'scale':
                print('THREE.ColladaLoader: Animation transform type "%s" not yet implemented.', transform)

            keyframes = prepareAnimationData(data, defaultMatrix)

            animation = javascriptObject({
                'name': object3D.uuid,
                'keyframes': keyframes
            })

            return animation

        def prepareAnimationData(data, defaultMatrix):
            keyframes = []

            # transfer data into a sortable array

            for time in data:
                keyframes.append(_keyframes(time, data[time]))

            # ensure keyframes are sorted by time

            # array sort def
            def _ascending(a):
                return a.time
                
            keyframes.sort(key = _ascending)

            # now we clean up all animation data, so we can use them for keyframe tracks

            for i in range(16):
                transformAnimationData(keyframes, i, defaultMatrix.elements[i])

            return keyframes

        def createKeyframeTracks(animation, tracks):
            keyframes = animation.keyframes
            name = animation.name

            times = []
            positionData = []
            quaternionData = []
            scaleData = []

            for keyframe in keyframes:
                time = keyframe.time
                value = keyframe.value

                matrix.fromArray(value).transpose()
                matrix.decompose(position, quaternion, scale)

                times.append(time)
                positionData.extend([position.x, position.y, position.z])
                quaternionData.extend([quaternion.x, quaternion.y, quaternion.z, quaternion.w])
                scaleData.extend([scale.x, scale.y, scale.z])

            if len(positionData) > 0:
                tracks.append(THREE.VectorKeyframeTrack(name + '.position', times, positionData))
            if len(quaternionData) > 0:
                tracks.append(THREE.QuaternionKeyframeTrack(name + '.quaternion', times, quaternionData))
            if len(scaleData) > 0:
                tracks.append(THREE.VectorKeyframeTrack(name + '.scale', times, scaleData))

            return tracks

        def transformAnimationData(keyframes, property, defaultValue):
            empty = True

            # check, if values of a property are missing in our keyframes
            # TODO FDE: improve handling missing properties
            for keyframe in keyframes:
                if keyframe.value[property] is not None:
                    #keyframe.value[property] = None    # mark as missing
                    #
                    #                else:
                    empty = False

            if empty is True:
                # no values at all, so we set a default value
                for keyframe in keyframes:
                    keyframe.value[property] = defaultValue

            else:
                # filling gaps
                createMissingKeyframes(keyframes, property)

        def createMissingKeyframes(keyframes, property):
            for i in range(len(keyframes)):
                keyframe = keyframes[i]
                if property not in keyframe.value:
                    prev = getPrev(keyframes, i, property)
                    next = getNext(keyframes, i, property)

                    if prev is None:
                        keyframe.value[property] = next.value[property]
                        continue

                    if next is None:
                        keyframe.value[property] = prev.value[property]
                        continue

                    interpolate(keyframe, prev, next, property)

        def getPrev(keyframes, i, property):
            while i >= 0:
                keyframe = keyframes[i]

                if keyframe.value[property] is not None:
                    return keyframe

                i -= 1

            return None

        def getNext(keyframes, i, property):
            while i < len(keyframes):
                keyframe = keyframes[i]

                if keyframe.value[property] is not None:
                    return keyframe

                i += 1

            return None

        def interpolate(key, prev, next, property):
            if (next.time - prev.time) == 0:
                key.value[property] = prev.value[property]
                return

            key.value[property] = ((key.time - prev.time) * (next.value[property] - prev.value[property]) / (next.time - prev.time)) + prev.value[property]

        # animation clips

        def parseAnimationClip(xml):
            data = javascriptObject({
                'name': xml.getAttribute('id') or 'default',
                'start': float(xml.getAttribute('start') or 0),
                'end': float(xml.getAttribute('end') or 0),
                'animations': []
            })

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'instance_animation':
                    data.animations.append(parseId(child.getAttribute('url')))

            library.clips[xml.getAttribute('id')] = data

        def buildAnimationClip(data):
            tracks = []

            name = data.name
            duration = (data.end - data.start) or - 1
            animations = data.animations

            for animationTracks in animations:
                for j in range(len(animationTracks)):
                    tracks.append(animationTracks[j])

            return THREE.AnimationClip(name, duration, tracks)

        def getAnimationClip(id):
            return getBuild(library.clips[id], buildAnimationClip)

        # controller

        def parseController(xml):
            data = javascriptObject({})

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'skin':
                    # there is exactly one skin per controller
                    data.id = parseId(child.getAttribute('source'))
                    data.skin = parseSkin(child)

            library.controllers[xml.getAttribute('id')] = data

        def parseSkin(xml):
            data = javascriptObject({
                'sources': {}
            })

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'bind_shape_matrix':
                    data.bindShapeMatrix = _parseFloats(child.firstChild.data)

                elif child.nodeName == 'source':
                    id = child.getAttribute('id')
                    data.sources[id] = parseSource(child)
                
                elif child.nodeName =='joints':
                    data.joints = parseJoints(child)
                    
                elif child.nodeName =='vertex_weights':
                    data.vertexWeights = parseVertexWeights(child)
                    
            return data

        def parseJoints(xml):
            data = javascriptObject({
                'inputs': {}
            })

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'input':
                    semantic = child.getAttribute('semantic')
                    id = parseId(child.getAttribute('source'))
                    data.inputs[semantic] = id

            return data

        def parseVertexWeights(xml):
            data = javascriptObject({
                'inputs': {}
            })

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'input':
                    semantic = child.getAttribute('semantic')
                    id = parseId(child.getAttribute('source'))
                    offset = int(child.getAttribute('offset'))
                    data.inputs[semantic] = javascriptObject({ 'id': id, 'offset': offset })

                elif child.nodeName == 'vcount':
                    data.vcount = parseInts(child.firstChild.data)

                elif child.nodeName == 'v':
                    data.v = parseInts(child.firstChild.data)

            return data

        def buildController(data):
            build = _controler(
                data.id,
                buildSkin(data.skin)
            )

            # we enhance the 'sources' property of the corresponding geometry with our skin data

            geometry = library.geometries[build.id]
            geometry.sources['skinIndices'] = build.skin.indices
            geometry.sources['skinWeights'] = build.skin.weights

            return build

        def buildSkin(data):
            BONE_LIMIT = 4

            build = _skin(BONE_LIMIT)

            # array sort def
            def _descending(a):
                return a.weight

            sources = data.sources
            vertexWeights = data.vertexWeights

            vcount = vertexWeights.vcount
            v = vertexWeights.v
            jointOffset = vertexWeights.inputs.JOINT.offset
            weightOffset = vertexWeights.inputs.WEIGHT.offset

            jointSource = data.sources[data.joints.inputs.JOINT]
            inverseSource = data.sources[data.joints.inputs.INV_BIND_MATRIX]

            weights = sources[vertexWeights.inputs.WEIGHT.id].array
            stride = 0

            # procces skin data for each vertex

            for jointCount in vcount:
                # self is the amount of joints that affect a single vertex
                vertexSkinData = []

                for j in range(jointCount):
                    skinIndex = v[stride + jointOffset]
                    weightId = v[stride + weightOffset]
                    skinWeight = weights[weightId]

                    vertexSkinData.append(_skinVertex(skinIndex, skinWeight ))

                    stride += 2

                # we sort the joints in descending order based on the weights.
                # self ensures, we only procced the most important joints of the vertex

                vertexSkinData.sort(key=_descending, reverse=True)

                # now we provide for each vertex a set of four index and weight values.
                # the order of the skin data matches the order of vertices

                for j in range(BONE_LIMIT):
                    if j >= len(vertexSkinData):
                        build.indices.array.append(0)
                        build.weights.array.append(0)
                    else:
                        d = vertexSkinData[j]
                        if d is not None:
                            build.indices.array.append(d.index)
                            build.weights.array.append(d.weight)
                        else:
                            build.indices.array.append(0)
                            build.weights.array.append(0)

            # setup bind matrix

            build.bindMatrix = THREE.Matrix4().fromArray(data.bindShapeMatrix).transpose()

            # process bones and inverse bind matrix data

            for i in range(len(jointSource.array)):
                name = jointSource.array[i]
                boneInverse = THREE.Matrix4().fromArray(inverseSource.array, i * inverseSource.stride).transpose()

                build.joints.append(_skinJoint(name, boneInverse ))

            return build

        def getController(id):
            return getBuild(library.controllers[id], buildController)

        # image

        def parseImage(xml):
            data = javascriptObject({})

            ge = getElementsByTagName(xml, 'init_from')
            if len(ge) > 0:
                data.init_from = ge[0].firstChild.data

            library.images[xml.getAttribute('id')] = data

        def buildImage(data):
            if data.build is not None:
                return data.build

            return data.init_from

        def getImage(id):
            return getBuild(library.images[id], buildImage)

        # effect

        def parseEffect(xml):
            data = javascriptObject({})

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'profile_COMMON':
                    data.profile = parseEffectProfileCOMMON(child)

            library.effects[xml.getAttribute('id')] = data

        def parseEffectProfileCOMMON(xml):
            data = javascriptObject({
                'surfaces': {},
                'samplers': {}
            })

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'newparam':
                    parseEffectNewparam(child, data)

                elif child.nodeName == 'technique':
                    data.technique = parseEffectTechnique(child)

            return data

        def parseEffectNewparam(xml, data):
            sid = xml.getAttribute('sid')

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'surface':
                    data.surfaces[sid] = parseEffectSurface(child)

                elif child.nodeName == 'sampler2D':
                    data.samplers[sid] = parseEffectSampler(child)

        def parseEffectSurface(xml):
            data = javascriptObject({})

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'init_from':
                    data.init_from = child.firstChild.data

            return data

        def parseEffectSampler(xml):
            data = javascriptObject({})

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'source':
                    data.source = child.firstChild.data

            return data

        def parseEffectTechnique(xml):
            data = javascriptObject({})

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'constant' or child.nodeName == 'lambert' or child.nodeName == 'blinn' or child.nodeName == 'phong':
                    data.type = child.nodeName
                    data.parameters = parseEffectParameters(child)

            return data

        def parseEffectParameters(xml):
            data = javascriptObject({})

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'emission' or \
                    child.nodeName == 'diffuse' or \
                    child.nodeName == 'specular' or \
                    child.nodeName == 'shininess' or \
                    child.nodeName == 'transparent' \
                    or child.nodeName == 'transparency':
                        data[child.nodeName] = parseEffectParameter(child)

            return data

        def parseEffectParameter(xml):
            data = javascriptObject({})

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'color':
                    data[child.nodeName] = _parseFloats(child.firstChild.data)

                elif child.nodeName == 'float':
                    data[child.nodeName] = float(child.firstChild.data)

                elif child.nodeName == 'texture':
                    data[child.nodeName] = javascriptObject({ 'id': child.getAttribute('texture'), 'extra': parseEffectParameterTexture(child) })

            return data

        def parseEffectParameterTexture(xml):
            data = javascriptObject({
                'technique': {}
            })

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'extra':
                    parseEffectParameterTextureExtra(child, data)

            return data

        def parseEffectParameterTextureExtra(xml, data):
            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'technique':
                    parseEffectParameterTextureExtraTechnique(child, data)

        def parseEffectParameterTextureExtraTechnique(xml, data):
            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'repeatU' or child.nodeName == 'repeatV' or child.nodeName == 'offsetU' or child.nodeName == 'offsetV':
                    data.technique[child.nodeName] = float(child.firstChild.data)

                elif child.nodeName == 'wrapU' or child.nodeName == 'wrapV':
                    # some files have values for wrapU/wrapV which become NaN via parseInt
                    if child.firstChild.data.upper() == 'TRUE':
                        data.technique[child.nodeName] = 1

                    elif child.firstChild.data.upper() == 'FALSE':
                        data.technique[child.nodeName] = 0

                    else:
                        data.technique[child.nodeName] = int(child.firstChild.data)

        def buildEffect(data):
            return data

        def getEffect(id):
            return getBuild(library.effects[id], buildEffect)

        # material
        def parseMaterial(xml):
            data = javascriptObject({
                'name': xml.getAttribute('name')
            })

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'instance_effect':
                    data.url = parseId(child.getAttribute('url'))

            library.materials[xml.getAttribute('id')] = data

        def buildMaterial(data):
            effect = getEffect(data.url)
            technique = effect.profile.technique

            if technique.type == 'phong' or technique.type == 'blinn':
                material = THREE.MeshPhongMaterial()

            elif technique.type == 'lambert':
                material = THREE.MeshLambertMaterial()

            else:
                material = THREE.MeshBasicMaterial()

            material.name = data.name

            def getTexture(textureObject):
                sampler = effect.profile.samplers[textureObject.id]

                if sampler is not None:
                    surface = effect.profile.surfaces[sampler.source]

                    texture = textureLoader.load(getImage(surface.init_from))

                    extra = textureObject.extra

                    if extra is not None and extra.technique is not None and isEmpty(extra.technique) == False:
                        technique = extra.technique

                        texture.wrapS = THREE.RepeatWrapping if technique.wrapU else THREE.ClampToEdgeWrapping
                        texture.wrapT = THREE.RepeatWrapping if technique.wrapV else THREE.ClampToEdgeWrapping

                        texture.offset.set(technique.offsetU or 0, technique.offsetV or 0)
                        texture.repeat.set(technique.repeatU or 1, technique.repeatV or 1)

                    else:
                        texture.wrapS = THREE.RepeatWrapping
                        texture.wrapT = THREE.RepeatWrapping

                    return texture

                raise RuntimeError('THREE.ColladaLoader: Undefined sampler', textureObject.id)

            parameters = technique.parameters

            for key in parameters:
                parameter = parameters[key]

                if key == 'diffuse':
                    if 'color' in parameter:
                        material.color.fromArray(parameter.color)
                    if 'texture' in parameter:
                        material.map = getTexture(parameter.texture)
                elif key == 'specular':
                    if 'color' in parameter:
                        material.specular.fromArray(parameter.color)
                    if parameter.texture:
                        material.specularMap = getTexture(parameter.texture)
                elif key == 'shininess':
                    if 'float' in parameter:
                        material.shininess = parameter.float
                elif key == 'emission':
                    if 'color' in parameter:
                        material.emissive.fromArray(parameter.color)
                elif key == 'transparent':
                    # if parameter.texture) material.alphaMap = getTexture(parameter.texture)
                    material.transparent = True
                elif key == 'transparency':
                    if 'float' in parameter is not None:
                        material.opacity = parameter.float
                    material.transparent = True

            return material

        def getMaterial(id):
            return getBuild(library.materials[id], buildMaterial)

        # camera

        def parseCamera(xml):
            data = javascriptObject({
                'name': xml.getAttribute('name')
            })

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'optics':
                    data.optics = parseCameraOptics(child)

            library.cameras[xml.getAttribute('id')] = data

        def parseCameraOptics(xml):
            for child in xml.childNodes:
                if child.nodeName == 'technique_common':
                    return parseCameraTechnique(child)

            return {}

        def parseCameraTechnique(xml):
            data = javascriptObject({})
            for child in xml.childNodes:
                if child.nodeName == 'perspective' or child.nodeName == 'orthographic':
                    data.technique = child.nodeName
                    data.parameters = parseCameraParameters(child)

            return data

        def parseCameraParameters(xml):
            data = javascriptObject({})

            for child in xml.childNodes:
                if child.nodeName == 'xfov' or child.nodeName == 'yfov' or child.nodeName == 'xmag' or \
                    child.nodeName == 'ymag' or child.nodeName == 'znear' or child.nodeName == 'zfar' or \
                    child.nodeName == 'aspect_ratio':
                        data[child.nodeName] = float(child.firstChild.data)

            return data

        def buildCamera(data):
            if data.optics.technique == 'perspective':
                camera = THREE.PerspectiveCamera(
                    data.optics.parameters.yfov,
                    data.optics.parameters.aspect_ratio,
                    data.optics.parameters.znear,
                    data.optics.parameters.zfar
               )

            elif data.optics.technique == 'orthographic':
                ymag = data.optics.parameters.ymag
                xmag = data.optics.parameters.xmag
                aspectRatio = data.optics.parameters.aspect_ratio

                xmag = ymag * aspectRatio  if (xmag is None) else xmag
                ymag = (xmag / aspectRatio) if (ymag is None) else ymag

                xmag *= 0.5
                ymag *= 0.5

                camera = THREE.OrthographicCamera(
                    - xmag, xmag, ymag, - ymag, # left, right, top, bottom
                    data.optics.parameters.znear,
                    data.optics.parameters.zfar
               )

            else:
                    camera = THREE.PerspectiveCamera()

            camera.name = data.name

            return camera

        def getCamera(id):
            return getBuild(library.cameras[id], buildCamera)

        # light

        def parseLight(xml):
            data = javascriptObject({})

            for child in xml.childNodes:
                if child.nodeType != 1 :
                    continue

                if child.nodeName == 'technique_common':
                    data = parseLightTechnique(child)

            library.lights[xml.getAttribute('id')] = data

        def parseLightTechnique(xml):
            data = javascriptObject({})

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'directional' or child.nodeName == 'point' or child.nodeName == 'spot' or child.nodeName == 'ambient':
                    data.technique = child.nodeName
                    data.parameters = parseLightParameters(child)

            return data

        def parseLightParameters(xml):
            data = javascriptObject({})

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'color':
                    array = _parseFloats(child.firstChild.data)
                    data.color = THREE.Color().fromArray(array)

                elif child.nodeName == 'falloff_angle':
                    data.falloffAngle = float(child.firstChild.data)

                elif child.nodeName == 'quadratic_attenuation':
                    f = float(child.firstChild.data)
                    data.distance = math.sqrt(1 / f) if f else 0

            return data

        def buildLight(data):
            light = None

            if data.technique == 'directional':
                light = THREE.DirectionalLight()

            elif data.technique == 'point':
                light = THREE.PointLight()

            elif data.technique == 'spot':
                light = THREE.SpotLight()

            elif data.technique == 'ambient':
                light = THREE.AmbientLight()

            if data.parameters.color:
                light.color.copy(data.parameters.color)
            if data.parameters.distance:
                light.distance = data.parameters.distance

            return light

        def getLight(id):
            return getBuild(library.lights[id], buildLight)

        # geometry

        def parseGeometry(xml):
            data = _geometry(xml.getAttribute('name'))

            mesh = getElementsByTagName(xml, 'mesh')[0]

            for child in mesh.childNodes:
                if child.nodeType != 1:
                    continue

                id = child.getAttribute('id')

                if child.nodeName == 'source':
                    data.sources[id] = parseSource(child)

                elif child.nodeName == 'vertices':
                    # data.sources[id] = data.sources[parseId(getElementsByTagName(child, 'input')[0].getAttribute('source'))]
                    data.vertices = parseGeometryVertices(child)

                elif child.nodeName == 'polygons':
                    print('THREE.ColladaLoader: Unsupported primitive type: ', child.nodeName)

                elif child.nodeName == 'lines' or child.nodeName == 'linestrips' or child.nodeName == 'polylist' or child.nodeName == 'triangles':
                    data.primitives.append(parseGeometryPrimitive(child))

                else:
                    print(child)

            library.geometries[xml.getAttribute('id')] = data

        def parseSource(xml):
            data = javascriptObject({
                'array': [],
                'stride': 3
            })

            for child in xml.childNodes:
                if child.nodeType != 1 :
                    continue

                if child.nodeName == 'float_array':
                    data.array = _parseFloats(child.firstChild.data)

                elif child.nodeName == 'Name_array':
                    data.array = parseStrings(child.firstChild.data)

                elif child.nodeName == 'technique_common':
                    accessor = getElementsByTagName(child, 'accessor')[0]

                    if accessor is not None:
                        v = accessor.getAttribute('stride')
                        if v != "":
                            data.stride = int(v)
                        else:
                            data.stride = 0

            return data

        def parseGeometryVertices(xml):
            data = javascriptObject({})

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                data[child.getAttribute('semantic')] = parseId(child.getAttribute('source'))

            return data

        def parseGeometryPrimitive(xml):
            primitive = javascriptObject({
                'type': xml.nodeName,
                'material': xml.getAttribute('material'),
                'count':  int(xml.getAttribute('count')),
                'inputs': {},
                'stride': 0
            })

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'input':
                    id = parseId(child.getAttribute('source'))
                    semantic = child.getAttribute('semantic')
                    offset = int(child.getAttribute('offset'))
                    primitive.inputs[semantic] = javascriptObject({ 'id': id, 'offset': offset })
                    primitive.stride = max(primitive.stride, offset + 1)

                elif child.nodeName == 'vcount':
                    primitive.vcount = parseInts(child.firstChild.data)

                elif child.nodeName == 'p':
                    primitive.p = parseInts(child.firstChild.data)

            return primitive

        def groupPrimitives(primitives):
            build = javascriptObject({})

            for primitive in primitives:
                if not primitive.type in build:
                    build[primitive.type] = []

                build[primitive.type].append(primitive)

            return build

        def buildGeometry(data):
            build = {}

            sources = data.sources
            vertices = data.vertices
            primitives = data.primitives

            if len(primitives) == 0:
                return {}

            # our goal is to create one buffer geoemtry for a single type of primitives
            # first, we group all primitives by their type

            groupedPrimitives = groupPrimitives(primitives)

            for type in groupedPrimitives:
                # second, we create for each type of primitives (polylist,triangles or lines) a buffer geometry
                build[type] = buildGeometryType(groupedPrimitives[type], sources, vertices)

            return build

        def buildGeometryType(primitives, sources, vertices):
            build = javascriptObject({})

            position = _skinArray(0)
            normal = _skinArray(0)
            uv = _skinArray(0)
            color = _skinArray(0)

            skinIndex = _skinArray( 4 )
            skinWeight = _skinArray( 4 )

            geometry = THREE.BufferGeometry()

            materialKeys = []

            start = 0
            count = 0

            for p in range(len(primitives)):
                primitive = primitives[p]
                inputs = primitive.inputs
                triangleCount = 1

                if primitive.vcount and primitive.vcount[0] == 4:
                    triangleCount = 2    # one quad -> two triangles

                # groups

                if primitive.type == 'lines' or primitive.type == 'linestrips':
                    count = primitive.count * 2

                else:
                    count = primitive.count * 3 * triangleCount

                geometry.addGroup(start, count, p)
                start += count

                # material
                if primitive.material:
                    materialKeys.append(primitive.material)

                # geometry data
                for name in inputs:
                    input = inputs[name]

                    if name == 'VERTEX':
                        for key in vertices:
                            id =  vertices[key]

                            if key == 'POSITION':
                                buildGeometryData(primitive, sources[id], input.offset, position.array)
                                position.stride = sources[id].stride

                                if 'skinWeights' in sources and 'skinIndices' in sources:
                                    buildGeometryData(primitive, sources['skinIndices'], input.offset, skinIndex.array)
                                    buildGeometryData(primitive, sources['skinWeights'], input.offset, skinWeight.array)

                            elif key == 'NORMAL':
                                buildGeometryData(primitive, sources[id], input.offset, normal.array)
                                normal.stride = sources[id].stride

                            elif key == 'COLOR':
                                buildGeometryData(primitive, sources[id], input.offset, color.array)
                                color.stride = sources[id].stride

                            elif key == 'TEXCOORD':
                                buildGeometryData(primitive, sources[id], input.offset, uv.array)
                                uv.stride = sources[id].stride

                            else:
                                print('THREE.ColladaLoader: Semantic "%s" not handled in geometry build process.', key)

                    elif name == 'NORMAL':
                        buildGeometryData(primitive, sources[input.id], input.offset, normal.array)
                        normal.stride = sources[input.id].stride

                    elif name == 'COLOR':
                        buildGeometryData(primitive, sources[input.id], input.offset, color.array)
                        color.stride = sources[input.id].stride

                    elif name == 'TEXCOORD':
                        buildGeometryData(primitive, sources[input.id], input.offset, uv.array)
                        uv.stride = sources[input.id].stride

            # build geometry

            if len(position.array) > 0:
                geometry.addAttribute('position', THREE.Float32BufferAttribute(position.array, position.stride))
            if len(normal.array) > 0:
                geometry.addAttribute('normal', THREE.Float32BufferAttribute(normal.array, normal.stride))
            if len(color.array) > 0:
                geometry.addAttribute('color', THREE.Float32BufferAttribute(color.array, color.stride))
            if len(uv.array) > 0:
                geometry.addAttribute('uv', THREE.Float32BufferAttribute(uv.array, uv.stride))

            if len(skinIndex.array) > 0:
                geometry.addAttribute('skinIndex', THREE.Float32BufferAttribute(skinIndex.array, skinIndex.stride))
            if len(skinWeight.array) > 0:
                geometry.addAttribute('skinWeight', THREE.Float32BufferAttribute(skinWeight.array, skinWeight.stride))

            build.data = geometry
            build.type = primitives[0].type
            build.materialKeys = materialKeys

            return build

        def buildGeometryData(primitive, source, offset, array):
            indices = primitive.p
            stride = primitive.stride
            vcount = primitive.vcount

            def pushVector(i):
                index = indices[i + offset] * sourceStride
                length = index + sourceStride

                while index < length:
                    array.append(sourceArray[index])
                    index += 1

            maxcount = 0

            sourceArray = source.array
            sourceStride = source.stride

            if primitive.vcount is not None:
                index = 0

                for count in vcount:
                    if count == 4:
                        a = index + stride * 0
                        b = index + stride * 1
                        c = index + stride * 2
                        d = index + stride * 3

                        pushVector(a); pushVector(b); pushVector(d)
                        pushVector(b); pushVector(c); pushVector(d)

                    elif count == 3:
                        a = index + stride * 0
                        b = index + stride * 1
                        c = index + stride * 2

                        pushVector(a); pushVector(b); pushVector(c)

                    else:
                        maxcount = max(maxcount, count)

                    index += stride * count

                if maxcount > 0:
                    print('THREE.ColladaLoader: Geometry has faces with more than 4 vertices.')

            else:
                for i in range(0, len(indices), stride):
                    pushVector(i)

        def getGeometry(id):
            return getBuild(library.geometries[id], buildGeometry)

        # kinematics
        def parseKinematicsModel(xml):
            data = javascriptObject({
                'name': xml.getAttribute('name') or '',
                'joints': [],
                'links': []
            })

            for child in xml.childNodes:
                if child.nodeType != 1 :
                    continue

                if child.nodeName == 'technique_common':
                    parseKinematicsTechniqueCommon(child, data)

            library.kinematicsModels[xml.getAttribute('id')] = data

        def buildKinematicsModel(data):
            if data.build is not None:
                return data.build

            return data

        def getKinematicsModel(id):
            return getBuild(library.kinematicsModels[id], buildKinematicsModel)

        def parseKinematicsTechniqueCommon(xml, data):
            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'joint':
                    data.joints.append(parseKinematicsJoint(child))

                elif child.nodeName == 'link':
                    data.links.append(parseKinematicsLink(child))

        def parseKinematicsJoint(xml):
            data = None
            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'prismatic' or child.nodeName == 'revolute':
                    data = parseKinematicsJointParameter(child)

            return data

        def parseKinematicsJointParameter(xml, data=None):
            data = javascriptObject({
                'sid':  xml.getAttribute('sid'),
                'name': xml.getAttribute('name') or '',
                'axis': THREE.Vector3(),
                'limits': {
                    'min': 0,
                    'max': 0
                },
                'type': xml.nodeName,
                'static': False,
                'zeroPosition': 0,
                'middlePosition': 0
            })

            for child in xml.childNodes:
                if child.nodeType != 1 :
                    continue

                if child.nodeName == 'axis':
                    array = _parseFloats(child.firstChild.data)
                    data.axis.fromArray(array)
                elif child.nodeName == 'limits':
                    max = child.getElementsByTagName('max')[0]
                    min = child.getElementsByTagName('min')[0]

                    data.limits.max = float(max.firstChild.data)
                    data.limits.min = float(min.firstChild.data)

            # if min is equal to or greater than max, consider the joint static
            if data.limits.min >= data.limits.max:
                data.static = True

            # calculate middle position
            data.middlePosition = (data.limits.min + data.limits.max) / 2.0

            return data

        def parseKinematicsLink(xml):
            data = javascriptObject({
                'sid': xml.getAttribute('sid'),
                'name': xml.getAttribute('name') or '',
                'attachments': [],
                'transforms': []
            })

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'attachment_full':
                    data.attachments.append(parseKinematicsAttachment(child))

                elif child.nodeName == 'matrix' or child.nodeName == 'translate' or child.nodeName == 'rotate':
                    data.transforms.append(parseKinematicsTransform(child))

            return data

        def parseKinematicsAttachment(xml):
            data = javascriptObject({
                'joint': xml.getAttribute('joint').split('/').pop(),
                'transforms': [],
                'links': []
            })

            for child in xml.childNodes:
                if child.nodeType != 1 :
                    continue

                if child.nodeName == 'link':
                    data.links.append(parseKinematicsLink(child))

                elif child.nodeName == 'matrix' or child.nodeName == 'translate' or child.nodeName == 'rotate':
                    data.transforms.append(parseKinematicsTransform(child))

            return data

        def parseKinematicsTransform(xml):
            data = javascriptObject({
                'type': xml.nodeName
            })

            array = _parseFloats(xml.firstChild.data)

            if data.type == 'matrix':
                data.obj = THREE.Matrix4()
                data.obj.fromArray(array).transpose()

            elif data.type == 'translate':
                data.obj = THREE.Vector3()
                data.obj.fromArray(array)

            elif data.type == 'rotate':
                data.obj = THREE.Vector3()
                data.obj.fromArray(array)
                data.angle = _Math.degToRad(array[3])

            return data

        def parseKinematicsScene(xml):
            data = javascriptObject({
                'bindJointAxis': []
            })

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'bind_joint_axis':
                    data.bindJointAxis.append(parseKinematicsBindJointAxis(child))

            library.kinematicsScenes[parseId(xml.getAttribute('url'))] = data

        def parseKinematicsBindJointAxis(xml):
            data = javascriptObject({
                'target': xml.getAttribute('target').split('/').pop()
            })

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'axis':
                    param = child.getElementsByTagName('param')[0]
                    data.axis = param.firstChild.data
                    data.jointIndex = int(data.axis.split('joint').pop().split('.')[0])

            return data

        def buildKinematicsScene(data):
            if data.build is not None:
                return data.build

            return data

        def getKinematicsScene(id):
            return getBuild(library.kinematicsScenes[id], buildKinematicsScene)

        def setupKinematics():
            nonlocal kinematics

            kinematicsModelId = library.kinematicsModels.__dict__.keys()
            kinematicsSceneId = library.kinematicsScenes.__dict__.keys()
            visualSceneId = library.visualScenes.__dict__.keys()

            if len(kinematicsModelId) == 0 or len(kinematicsSceneId) == 0:
                return

            kinematicsModelId = list(kinematicsModelId)[0]
            kinematicsSceneId = list(kinematicsSceneId)[0]
            visualSceneId = list(visualSceneId)[0]

            kinematicsModel = getKinematicsModel(kinematicsModelId)
            kinematicsScene = getKinematicsScene(kinematicsSceneId)
            visualScene = getVisualScene(visualSceneId)

            bindJointAxis = kinematicsScene.bindJointAxis
            jointMap = {}

            def connect(jointIndex, visualElement):
                visualElementId = visualElement.getAttribute('id')
                visualElementName = visualElement.getAttribute('name')
                joint = kinematicsModel.joints[jointIndex]

                def _traverse(object, scope=None):
                    if object.name == visualElementName:
                        jointMap[jointIndex] = javascriptObject({
                            'object': object,
                            'transforms': buildTransformList(visualElement),
                            'joint': joint,
                            'position': joint.zeroPosition
                        })

                visualScene.traverse(_traverse)

            for axis in bindJointAxis:
                # the result of the following query is an element of type 'translate', 'rotate','scale' or 'matrix'

                targetElement = getElementsBySelector(collada, 'sid', axis.target)

                if targetElement is not None:
                    # get the parent of the transfrom element
                    parentVisualElement = targetElement.parentNode

                    # connect the joint of the kinematics model with the element in the visual scene
                    connect(axis.jointIndex, parentVisualElement)

            m0 = THREE.Matrix4()

            def _getJointValue(jointIndex):
                jointData = jointMap[jointIndex]

                if jointData:
                    return jointData.position

                else:
                    print('THREE.ColladaLoader: Joint ' + jointIndex + ' doesn\'t exist.')

            def _setJointValue(jointIndex, value):
                jointData = jointMap[jointIndex]

                if jointData:
                    joint = jointData.joint

                    if value > joint.limits.max or value < joint.limits.min:
                        print('THREE.ColladaLoader: Joint %d value %d outside of limits (min:%d  max:%d)' % (jointIndex, value,  joint.limits.min, joint.limits.max))

                    elif joint.static:
                        print('THREE.ColladaLoader: Joint %d is static.' % jointIndex )

                    else:
                        object = jointData.object
                        axis = joint.axis
                        transforms = jointData.transforms

                        matrix.identity()

                        # each update, we have to apply all transforms in the correct order

                        for transform in transforms:
                            # if there is a connection of the transform node with a joint, apply the joint value
                            if transform.sid and transform.sid.index('joint%d' % jointIndex) != -1:
                                if joint.type == 'revolute':
                                    matrix.multiply(m0.makeRotationAxis(axis, _Math.degToRad(value)))

                                elif joint.type == 'prismatic':
                                    matrix.multiply(m0.makeTranslation(axis.x * value, axis.y * value, axis.z * value))

                                else:
                                    print('THREE.ColladaLoader: Unknown joint type: ' + joint.type)
                                    
                            else:
                                if transform.type == 'matrix':
                                    matrix.multiply(transform.obj)

                                elif transform.type == 'translate':
                                    matrix.multiply(m0.makeTranslation(transform.obj.x, transform.obj.y, transform.obj.z))

                                elif transform.type == 'scale':
                                    matrix.scale(transform.obj)

                                elif transform.type == 'rotate':
                                    matrix.multiply(m0.makeRotationAxis(transform.obj, transform.angle))

                        object.matrix.copy(matrix)
                        object.matrix.decompose(object.position, object.quaternion, object.scale)

                        jointMap[jointIndex].position = value

                else:
                    print('THREE.ColladaLoader: ' + jointIndex + ' does not exist.')
                    
            kinematics = javascriptObject({
                'joints': kinematicsModel and kinematicsModel.joints,
                'getJointValue': _getJointValue,
                'setJointValue': _setJointValue
            })

        def buildTransformList(node):
            transforms = []

            xml = getElementsBySelector(collada, 'id', node.attributes['id'].nodeValue)

            for child in xml.childNodes:
                if child.nodeType != 1:
                    continue

                if child.nodeName == 'matrix':
                    array = _parseFloats(child.firstChild.data)
                    matrix = THREE.Matrix4().fromArray(array).transpose()
                    transforms.append(javascriptObject({
                        'sid': child.getAttribute('sid'),
                        'type': child.nodeName,
                        'obj': matrix
                    }))

                elif child.nodeName == 'translate' or child.nodeName ==  'scale':
                    array = _parseFloats(child.firstChild.data)
                    vector = THREE.Vector3().fromArray(array)
                    transforms.append(javascriptObject({
                        'sid': child.getAttribute('sid'),
                        'type': child.nodeName,
                        'obj': vector
                    }))

                elif child.nodeName == 'rotate':
                    array = _parseFloats(child.firstChild.data)
                    vector = THREE.Vector3().fromArray(array)
                    angle = _Math.degToRad(array[3])
                    transforms.append(javascriptObject({
                        'sid': child.getAttribute('sid'),
                        'type': child.nodeName,
                        'obj': vector,
                        'angle': angle
                    }))

            return transforms

        def parseNode(xml):
            data = javascriptObject({
                'name': xml.getAttribute('name'),
                'type': xml.getAttribute('type'),
                'id': xml.getAttribute('id'),
                'sid': xml.getAttribute('sid'),
                'matrix': THREE.Matrix4(),
                'nodes': [],
                'instanceCameras': [],
                'instanceControllers': [],
                'instanceLights': [],
                'instanceGeometries': [],
                'instanceNodes': [],
                'transforms': {}
            })

            for child in xml.childNodes:
                if child.nodeType != 1 :
                    continue

                if child.nodeName == 'node':
                    if child.hasAttribute('id'):
                        data.nodes.append(child.getAttribute('id'))
                        parseNode(child)

                elif child.nodeName == 'instance_camera':
                    data.instanceCameras.append(parseId(child.getAttribute('url')))

                elif child.nodeName == 'instance_controller':
                    data.instanceControllers.append(parseNodeInstance(child))

                elif child.nodeName == 'instance_light':
                    data.instanceLights.append(parseId(child.getAttribute('url')))

                elif child.nodeName == 'instance_geometry':
                    data.instanceGeometries.append(parseNodeInstance(child))

                elif child.nodeName == 'instance_node':
                    data.instanceNodes.append(parseId(child.getAttribute('url')))

                elif child.nodeName == 'matrix':
                    array = _parseFloats(child.firstChild.data)
                    data.matrix.multiply(matrix.fromArray(array).transpose())
                    data.transforms[child.getAttribute('sid')] = child.nodeName

                elif child.nodeName == 'translate':
                    array = _parseFloats(child.firstChild.data)
                    vector.fromArray(array)
                    data.matrix.multiply(matrix.makeTranslation(vector.x, vector.y, vector.z))
                    data.transforms[child.getAttribute('sid')] = child.nodeName

                elif child.nodeName == 'rotate':
                    array = _parseFloats(child.firstChild.data)
                    angle = _Math.degToRad(array[3])
                    data.matrix.multiply(matrix.makeRotationAxis(vector.fromArray(array), angle))
                    data.transforms[child.getAttribute('sid')] = child.nodeName

                elif child.nodeName == 'scale':
                    array = _parseFloats(child.firstChild.data)
                    data.matrix.scale(vector.fromArray(array))
                    data.transforms[child.getAttribute('sid')] = child.nodeName

                elif child.nodeName == 'extra':
                        pass

                else:
                    print(child)
                    
            if xml.hasAttribute('id'):
                library.nodes[xml.getAttribute('id')] = data

            return data

        def parseNodeInstance(xml):
            data = javascriptObject({
                'id': parseId(xml.getAttribute('url')),
                'materials': {},
                'skeletons': []
            })

            for child in xml.childNodes:
                if child.nodeName == 'bind_material':
                    instances = child.getElementsByTagName('instance_material')

                    for instance in instances:
                        symbol = instance.getAttribute('symbol')
                        target = instance.getAttribute('target')

                        data.materials[symbol] = parseId(target)

                if child.nodeName == 'skeleton':
                    data.skeletons.append(parseId(child.firstChild.data))

                else:
                    pass

            return data

        def buildSkeleton(skeletons, joints):
            boneData = []
            sortedBoneData = [None for i in range(len(joints)) ]

            # a skeleton can have multiple root bones. collada expresses self
            # situtation with multiple "skeleton" tags per controller instance

            for skeleton in skeletons:
                root = getNode(skeleton)

                # setup bone data for a single bone hierarchy
                buildBoneHierarchy(root, joints, boneData)

            # sort bone data (the order is defined in the corresponding controller)
            for i in range(len(joints)):
                for j in range(len(boneData)):
                    data = boneData[j]

                    if data.bone.name == joints[i].name:
                        sortedBoneData[i] = data
                        data.processed = True
                        break

            # add unprocessed bone data at the end of the list
            for data in boneData:
                if data.processed is False:
                    sortedBoneData.append(data)
                    data.processed = True

            # setup arrays for skeleton creation
            bones = []
            boneInverses = []

            for data in sortedBoneData:
                bones.append(data.bone)
                boneInverses.append(data.boneInverse)

            return Skeleton(bones, boneInverses)

        def buildBoneHierarchy(root, joints, boneData):
            # setup bone data from visual scene
            def _traverse(obj, scope=None):
                if obj.isBone is True:
                    # retrieve the boneInverse from the controller data
                    boneInverse = None
                    for joint in joints:
                        if joint.name == obj.name:
                            boneInverse = joint.boneInverse
                            break

                    if boneInverse is None:
                        # Unfortunately, there can be joints in the visual scene that are not part of the
                        # corresponding controller. In self case, we have to create a dummy boneInverse matrix
                        # for the respective bone. This bone won't affect any vertices, because there are no skin indices
                        # and weights defined for it. But we still have to add the bone to the sorted bone list in order to
                        # ensure a correct animation of the model.

                         boneInverse = THREE.Matrix4()

                    boneData.append(javascriptObject({ 'bone': obj, 'boneInverse': boneInverse, 'processed': False }))

            root.traverse(_traverse)

        def buildNode(data):
            objects = []

            matrix = data.matrix
            nodes = data.nodes
            type = data.type
            instanceCameras = data.instanceCameras
            instanceControllers = data.instanceControllers
            instanceLights = data.instanceLights
            instanceGeometries = data.instanceGeometries
            instanceNodes = data.instanceNodes

            # nodes
            for node in nodes:
                objects.append(getNode(node))

            # instance cameras
            for instanceCamera in instanceCameras:
                objects.append(getCamera(instanceCamera).clone())

            # instance controllers
            for instance in instanceControllers:
                controller = getController(instance.id)
                geometries = getGeometry(controller.id)
                newObjects = buildObjects(geometries, instance.materials)

                skeletons = instance.skeletons
                joints = controller.skin.joints

                skeleton = buildSkeleton(skeletons, joints)

                for object in newObjects:
                    if object.isSkinnedMesh:
                        object.bind(skeleton, controller.skin.bindMatrix)
                        object.normalizeSkinWeights()

                    objects.append(object)

            # instance lights
            for instanceLight in instanceLights:
                objects.append(getLight(instanceLight).clone())

            # instance geometries
            for instance in instanceGeometries:
                # a single geometry instance in collada can lead to multiple object3Ds.
                # self is the case when primitives are combined like triangles and lines

                geometries = getGeometry(instance.id)
                newObjects = buildObjects(geometries, instance.materials)

                for newObject in newObjects:
                    objects.append(newObject)

            # instance nodes
            for instanceNode in instanceNodes:
                objects.append(getNode(instanceNode).clone())

            if len(nodes) == 0 and len(objects) == 1:
                object = objects[0]

            else:
                object = Bone() if (type == 'JOINT') else THREE.Group()

                for obj in objects:
                    object.add(obj)

            object.name = data.sid if (type == 'JOINT') else data.name
            object.matrix.copy(matrix)
            object.matrix.decompose(object.position, object.quaternion, object.scale)

            return object

        def resolveMaterialBinding(keys, instanceMaterials):
            materials = []

            for key in keys:
                id = instanceMaterials[key]
                materials.append(getMaterial(id))

            return materials

        def buildObjects(geometries, instanceMaterials):
            objects = []

            for type in geometries:
                geometry = geometries[type]

                materials = resolveMaterialBinding(geometry.materialKeys, instanceMaterials)

                # handle case if no materials are defined
                if len(materials) == 0:
                    if type == 'lines' or type == 'linestrips':
                        materials.append(THREE.LineBasicMaterial())

                    else:
                        materials.append(THREE.MeshPhongMaterial())

                # regard skinning
                skinning = ('skinIndex' in geometry.data.attributes)

                if skinning:
                    for material in materials:
                        material.skinning = True

                # choose between a single or multi materials (material array)
                material = materials[0] if (len(materials) == 1) else materials

                # now create a specific 3D object
                object = None
                if type == 'lines':
                    object = THREE.LineSegments(geometry.data, material)

                elif type == 'linestrips':
                    object = THREE.Line(geometry.data, material)

                elif type == 'triangles' or type == 'polylist':
                    if skinning:
                        object = SkinnedMesh(geometry.data, material)

                    else:
                        object = THREE.Mesh(geometry.data, material)

                objects.append(object)

            return objects

        def getNode(id):
            return getBuild(library.nodes[id], buildNode)

        # visual scenes
        def parseVisualScene(xml):
            data = javascriptObject({
                'name': xml.getAttribute('name'),
                'children': []
            })

            elements = getElementsByTagName(xml, 'node')

            for element in elements:
                data.children.append(parseNode(element))

            library.visualScenes[xml.getAttribute('id')] = data

        def buildVisualScene(data):
            group = THREE.Group()
            group.name = data.name

            children = data.children

            for child in children:
                if child.id is None:
                    group.add(buildNode(child))

                else:
                    # if there is an ID, let's try to get the finished build (e.g. joints are already build)
                    group.add(getNode(child.id))

            return group

        def getVisualScene(id):
            return getBuild(library.visualScenes[id], buildVisualScene)

        # scenes
        def parseScene(xml):
            instance = getElementsByTagName(xml, 'instance_visual_scene')[0]
            return getVisualScene(parseId(instance.getAttribute('url')))

        def setupAnimations():
            clips = library.clips

            if isEmpty(clips) is True:
                if isEmpty(library.animations) is False:
                    # if there are animations but no clips, we create a default clip for playback
                    tracks = []

                    for id in library.animations:
                        animationTracks = getAnimation(id)

                        for animationTrack in animationTracks:
                            tracks.append(animationTrack)

                    animations.append(THREE.AnimationClip('default', - 1, tracks))

            else:
                for id in clips:
                    animations.append(getAnimationClip(id))

        print('THREE.ColladaLoader')

        if len(text) == 0:
            return javascriptObject({ 'scene': THREE.Scene() })

        print('THREE.ColladaLoader: DOMParser')

        xml = minidom.parse(text)

        print('THREE.ColladaLoader: DOMParser')

        collada = getElementsByTagName(xml, 'COLLADA')[0]

        # metadata
        version = collada.getAttribute('version')
        print('THREE.ColladaLoader: File version', version)

        asset = parseAsset(getElementsByTagName(collada, 'asset')[0])
        textureLoader = THREE.TextureLoader(self.manager)
        textureLoader.setPath(path).setCrossOrigin(self.crossOrigin)

        #
        animations = []

        #

        library = javascriptObject({
            'animations': {},
            'clips': {},
            'controllers': {},
            'images': {},
            'effects': {},
            'materials': {},
            'cameras': {},
            'lights': {},
            'geometries': {},
            'nodes': {},
            'visualScenes': {},
            'kinematicsModels': {},
            'kinematicsScenes': {}
        })

        print('THREE.ColladaLoader: Parse')

        parseLibrary(collada, 'library_animations', 'animation', parseAnimation)
        parseLibrary(collada, 'library_animation_clips', 'animation_clip', parseAnimationClip)
        parseLibrary(collada, 'library_controllers', 'controller', parseController)
        parseLibrary(collada, 'library_images', 'image', parseImage)
        parseLibrary(collada, 'library_effects', 'effect', parseEffect)
        parseLibrary(collada, 'library_materials', 'material', parseMaterial)
        parseLibrary(collada, 'library_cameras', 'camera', parseCamera)
        parseLibrary(collada, 'library_lights', 'light', parseLight)
        parseLibrary(collada, 'library_geometries', 'geometry', parseGeometry)
        parseLibrary(collada, 'library_nodes', 'node', parseNode)
        parseLibrary(collada, 'library_visual_scenes', 'visual_scene', parseVisualScene)
        parseLibrary(collada, 'library_kinematics_models', 'kinematics_model', parseKinematicsModel)
        parseLibrary(collada, 'scene', 'instance_kinematics_scene', parseKinematicsScene)

        print('THREE.ColladaLoader: Parse')

        print('THREE.ColladaLoader: Build')

        buildLibrary(library.animations, buildAnimation)
        buildLibrary(library.clips, buildAnimationClip)
        buildLibrary(library.controllers, buildController)
        buildLibrary(library.images, buildImage)
        buildLibrary(library.effects, buildEffect)
        buildLibrary(library.materials, buildMaterial)
        buildLibrary(library.cameras, buildCamera)
        buildLibrary(library.lights, buildLight)
        buildLibrary(library.geometries, buildGeometry)
        buildLibrary(library.visualScenes, buildVisualScene)

        print('THREE.ColladaLoader: Build')

        setupAnimations()
        setupKinematics()

        scene = parseScene(getElementsByTagName(collada, 'scene')[0])

        if asset.upAxis == 'Z_UP':
            scene.rotation.x = - math.pi / 2

        scene.scale.multiplyScalar(asset.unit)

        print('THREE.ColladaLoader')

        return Collada(animations, kinematics, library, scene)
