"""
  * @author Kai Salmen / https:#kaisalmen.de
  * Development repository: https:#github.com/kaisalmen/WWOBJLoader
"""
import THREE
from THREE.LoadingManager import *
from THREE.javascriparray import *


"""
 * Constants used by THREE.OBJLoader2
"""
CODE_LF = 10
CODE_CR = 13
CODE_SPACE = 32
CODE_SLASH = 47
STRING_LF = '\n'
STRING_CR = '\r'
STRING_SPACE = ' '
STRING_SLASH = '/'
LINE_F = 'f'
LINE_G = 'g'
LINE_L = 'l'
LINE_O = 'o'
LINE_S = 's'
LINE_V = 'v'
LINE_VT = 'vt'
LINE_VN = 'vn'
LINE_MTLLIB = 'mtllib'
LINE_USEMTL = 'usemtl'


class Validator:
    def isValid(input):
        """
         * If given input is None or undefined, False is returned otherwise True.
         *
         * @param input Anything
         * @returns {boolean}
        """
        return input is not None

    def verifyInput(input, defaultValue):
        """
         * If given input is None or undefined, the defaultValue is returned otherwise the given input.
         *
         * @param input Anything
         * @param defaultValue Anything
         * @returns {*}
        """
        return defaultValue if input is None  else input


class RawObjectDescription:
    """
     * Descriptive information and data (vertices, normals, uvs) to passed on to mesh building def.
     * @class
     *
     * @param {string} objectName Name of the mesh
     * @param {string} groupName Name of the group
     * @param {string} materialName Name of the material
     * @param {number} smoothingGroup Normalized smoothingGroup (0: flat shading, 1: smooth shading)
    """
    def __init__(self, objectName, groupName, materialName, smoothingGroup):
        self.objectName = objectName
        self.groupName = groupName
        self.materialName = materialName
        self.smoothingGroup = smoothingGroup
        self.vertices = []
        self.colors = []
        self.uvs = []
        self.normals = []


class RawObject:
    """
     * {@link RawObject} is only used by {@link Parser}.
     * The user of OBJLoader2 does not need to care about self class.
     * It is defined publicly for inclusion in web worker based OBJ loader ({@link THREE.OBJLoader2.WWOBJLoader2})
    """
    def __init__(self, objectName=None, groupName=None, activeMtlName=None):
        self.globalVertexOffset = 1
        self.globalUvOffset = 1
        self.globalNormalOffset = 1

        self.vertices = []
        self.colors = []
        self.normals = []
        self.uvs = []

        # faces are stored according combined index of group, material and smoothingGroup (0 or not)
        self.activeMtlName = Validator.verifyInput(activeMtlName, '')
        self.objectName = Validator.verifyInput(objectName, '')
        self.groupName = Validator.verifyInput(groupName, '')
        self.activeSmoothingGroup = 1

        self.mtlCount = 0
        self.smoothingGroupCount = 0

        self.rawObjectDescriptions = {}
        # self default index is required as it is possible to define faces without 'g' or 'usemtl'
        index = self.buildIndex(self.activeMtlName, self.activeSmoothingGroup)
        self.rawObjectDescriptionInUse = RawObjectDescription(self.objectName, self.groupName, self.activeMtlName,
                                                              self.activeSmoothingGroup)
        self.rawObjectDescriptions[index] = self.rawObjectDescriptionInUse

    def buildIndex(self, materialName, smoothingGroup):
        return '%s|%d' % (materialName,smoothingGroup)

    def newInstanceFromObject(self, objectName, groupName):
        newRawObject = RawObject(objectName, groupName, self.activeMtlName)

        # move indices forward
        newRawObject.globalVertexOffset = self.globalVertexOffset + len(self.vertices) / 3
        newRawObject.globalUvOffset = self.globalUvOffset + len(self.uvs) / 2
        newRawObject.globalNormalOffset = self.globalNormalOffset + len(self.normals) / 3

        return newRawObject

    def newInstanceFromGroup(self, groupName):
        newRawObject = RawObject(self.objectName, groupName, self.activeMtlName)

        # keep current buffers and indices forward
        newRawObject.vertices = self.vertices
        newRawObject.colors = self.colors
        newRawObject.uvs = self.uvs
        newRawObject.normals = self.normals
        newRawObject.globalVertexOffset = self.globalVertexOffset
        newRawObject.globalUvOffset = self.globalUvOffset
        newRawObject.globalNormalOffset = self.globalNormalOffset

        return newRawObject

    def pushVertex(self, buffer):
        self.vertices.append(float(buffer[1]))
        self.vertices.append(float(buffer[2]))
        self.vertices.append(float(buffer[3]))

    def pushVertexAndVertextColors(self, buffer):
        self.vertices.append(float(buffer[1]))
        self.vertices.append(float(buffer[2]))
        self.vertices.append(float(buffer[3]))
        self.colors.append(float(buffer[4]))
        self.colors.append(float(buffer[5]))
        self.colors.append(float(buffer[6]))

    def pushUv(self, buffer):
        self.uvs.append(float(buffer[1]))
        self.uvs.append(float(buffer[2]))

    def pushNormal(self, buffer):
        self.normals.append(float(buffer[1]))
        self.normals.append(float(buffer[2]))
        self.normals.append(float(buffer[3]))

    def pushObject(self, objectName):
        self.objectName = objectName

    def pushMtllib(self, mtllibName):
        self.mtllibName = mtllibName

    def pushGroup(self, groupName):
        self.groupName = groupName
        self.verifyIndex()

    def pushUsemtl(self, mtlName):
        if self.activeMtlName == mtlName or not Validator.isValid(mtlName):
            return
        self.activeMtlName = mtlName
        self.mtlCount += 1

        self.verifyIndex()

    def pushSmoothingGroup(self, activeSmoothingGroup):
        try:
            normalized = int(activeSmoothingGroup)
        except:
            normalized = 0 if activeSmoothingGroup == "off" else 1

        if self.activeSmoothingGroup == normalized:
            return
        self.activeSmoothingGroup = normalized
        self.smoothingGroupCount += 1

        self.verifyIndex()

    def verifyIndex(self):
        index = self.buildIndex(self.activeMtlName, (0 if self.activeSmoothingGroup == 0 else 1))
        if index not in self.rawObjectDescriptions:
            self.rawObjectDescriptionInUse = RawObjectDescription(self.objectName, self.groupName, self.activeMtlName,
                                                                  self.activeSmoothingGroup)
            self.rawObjectDescriptions[index] = self.rawObjectDescriptionInUse

    def processFaces(self, buffer, bufferPointer, slashesCount):
        bufferLength = bufferPointer - 1

        # "f vertex ..."
        if slashesCount == 0:
            for i in range(2, bufferLength):
                self.attachFace(buffer[1])
                self.attachFace(buffer[i])
                self.attachFace(buffer[i + 1])

        # "f vertex/uv ..."
        elif bufferLength == slashesCount * 2:
            for i in range(3, bufferLength - 2, 2):
                self.attachFace(buffer[1], buffer[2])
                self.attachFace(buffer[i], buffer[i + 1])
                self.attachFace(buffer[i + 2], buffer[i + 3])

        # "f vertex/uv/normal ..."
        elif bufferLength * 2 == slashesCount * 3:
            for i in range(4, bufferLength - 3, 3):
                self.attachFace(buffer[1], buffer[2], buffer[3])
                self.attachFace(buffer[i], buffer[i + 1], buffer[i + 2])
                self.attachFace(buffer[i + 3], buffer[i + 4], buffer[i + 5])

        # "f vertex#normal ..."
        else:
            for i in range(3, bufferLength - 2, 2):
                self.attachFace(buffer[1], None, buffer[2])
                self.attachFace(buffer[i], None, buffer[i + 1])
                self.attachFace(buffer[i + 2], None, buffer[i + 3])

    def attachFace(self, faceIndexV, faceIndexU=None, faceIndexN=None):
        indexV = int(int(faceIndexV) - self.globalVertexOffset) * 3
        vertices = self.rawObjectDescriptionInUse.vertices
        if indexV < 0:
            indexV = 0
        vertices.append(self.vertices[indexV])
        vertices.append(self.vertices[indexV + 1])
        vertices.append(self.vertices[indexV + 2])
        indexV += 2

        if len(self.colors) > 0:
            indexV -= 2
            colors = self.rawObjectDescriptionInUse.colors
            colors.append(self.colors[indexV])
            colors.append(self.colors[indexV + 1])
            colors.append(self.colors[indexV + 2])
            indexV += 2

        if faceIndexU:
            indexU = int(int(faceIndexU) - self.globalUvOffset) * 2
            uvs = self.rawObjectDescriptionInUse.uvs
            if indexU >= 0:
                uvs.append(self.uvs[indexU])
                uvs.append(self.uvs[indexU + 1])
                indexU += 1

        if faceIndexN:
            indexN = int(int(faceIndexN) - self.globalNormalOffset) * 3
            normals = self.rawObjectDescriptionInUse.normals
            if indexN >= 0:
                normals.append(self.normals[indexN])
                normals.append(self.normals[indexN + 1])
                normals.append(self.normals[indexN + 2])
                indexN += 2

    def buildLineVvt(self, lineArray, length):
        """
         * Support for lines with or without texture. irst element in indexArray is the line identification
         * 0: "f vertex/uv        vertex/uv         ..."
         * 1: "f vertex            vertex             ..."
        """
        for i in range(1, length):
            self.vertices.append(int(lineArray[i]))
            self.uvs.append(int(lineArray[i]))

    def buildLineV(self, lineArray, length):
        for i in range(1, length):
            self.vertices.append(int(lineArray[i]))

    def finalize(self, meshCreator, inputObjectCount, debug):
        """
         * Clear any empty rawObjectDescription and calculate absolute vertex, normal and uv counts
        """
        temp = []
        index = 0
        absoluteVertexCount = 0
        absoluteColorCount = 0
        absoluteNormalCount = 0
        absoluteUvCount = 0

        for rawObjectDescription in self.rawObjectDescriptions.values():
            if len(rawObjectDescription.vertices) > 0:
                temp.append(rawObjectDescription)
                absoluteVertexCount += len(rawObjectDescription.vertices)
                absoluteColorCount += len(rawObjectDescription.colors)
                absoluteUvCount += len(rawObjectDescription.uvs)
                absoluteNormalCount += len(rawObjectDescription.normals)

        # don not continue if no result
        notEmpty = False
        if len(temp) > 0:
            if debug:
                self.createReport(inputObjectCount, True)
            meshCreator.buildMesh(
                temp,
                inputObjectCount,
                absoluteVertexCount,
                absoluteColorCount,
                absoluteNormalCount,
                absoluteUvCount
            )
            notEmpty = True

        return notEmpty

    def createReport(self, inputObjectCount, printDirectly):
        report = {
            'name': self.objectName if self.objectName else 'groups',
            'mtllibName': self.mtllibName,
            'vertexCount': len(self.vertices) / 3,
            'normalCount': len(self.normals) / 3,
            'uvCount': len(self.uvs) / 2,
            'smoothingGroupCount': self.smoothingGroupCount,
            'mtlCount': self.mtlCount,
            'rawObjectDescriptions': len(self.rawObjectDescriptions)
        }

        if printDirectly:
            print('Input Object number: ' + inputObjectCount + ' Object name: ' + report.name)
            print('Mtllib name: ' + report.mtllibName)
            print('Vertex count: ' + report.vertexCount)
            print('Normal count: ' + report.normalCount)
            print('UV count: ' + report.uvCount)
            print('SmoothingGroup count: ' + report.smoothingGroupCount)
            print('Material count: ' + report.mtlCount)
            print('Real RawObjectDescription count: ' + report.rawObjectDescriptions)
            print('')

        return report


class Parser:
    """
     * Parse OBJ data either from ArrayBuffer or string
     * @class
    """
    def __init__(self, meshCreator):
        self.meshCreator = meshCreator
        self.rawObject = None
        self.inputObjectCount = 1
        self.debug = False

    def setDebug(self, debug):
        self.debug = debug

    def validate(self):
        self.rawObject = RawObject()
        self.inputObjectCount = 1

    def parseArrayBuffer(self, arrayBuffer):
        """
         * Parse the provided arraybuffer
         * @memberOf Parser
         *
         * @param {Uint8Array} arrayBuffer OBJ data as Uint8Array
        """
        arrayBufferView = Uint8Array(arrayBuffer)
        buffer = [None for i in range(128)]
        bufferPointer = 0
        slashesCount = 0
        reachedFaces = False
        word = ''
        
        for code in arrayBufferView:
            if code == CODE_SPACE:
                if len(word) > 0:
                    buffer[bufferPointer] = word
                    bufferPointer += 1
                word = ''

            elif code == CODE_SLASH:
                slashesCount += 1
                if len(word) > 0:
                    buffer[bufferPointer] = word
                    bufferPointer += 1
                word = ''

            elif code == CODE_LF:
                if len(word) > 0:
                    buffer[bufferPointer] = word
                    bufferPointer += 1
                word = ''
                reachedFaces = self.processLine(buffer, bufferPointer, slashesCount, reachedFaces)
                bufferPointer = 0
                slashesCount = 0

            elif code == CODE_CR:
                pass
            else:
                word += chr(code)

    def parseText(self, text):
        """
         * Parse the provided text
         * @memberOf Parser
         *
         * @param {string} text OBJ data as string
        """
        length = text.length
        buffer = Array(128)
        bufferPointer = 0
        slashesCount = 0
        reachedFaces = False
        word = ''
        
        for char in text:

            if char == STRING_SPACE:
                if len(word) > 0:
                    buffer[bufferPointer] = word
                    bufferPointer += 1
                word = ''

            elif char == STRING_SLASH:
                slashesCount += 1
                if len(word) > 0:
                    buffer[bufferPointer] = word
                    bufferPointer += 1
                word = ''

            elif char == STRING_LF:
                if len(word) > 0:
                    buffer[bufferPointer] = word
                    bufferPointer += 1
                word = ''
                reachedFaces = self.processLine(buffer, bufferPointer, slashesCount, reachedFaces)
                bufferPointer = 0
                slashesCount = 0

            elif char == STRING_CR:
                pass
            else:
                word += char

    def processLine(self, buffer, bufferPointer, slashesCount, reachedFaces):
        if bufferPointer < 1:
            return reachedFaces

        bufferLength = bufferPointer - 1
        if buffer[0] == LINE_V:
            # object complete instance required if reached faces already (= reached next block of v)
            if reachedFaces:
                if len(self.rawObject.colors) > 0 and len(self.rawObject.colors) != len(self.rawObject.vertices):
                    raise RuntimeError('Vertex Colors were detected, but vertex count and color count do not matchnot')

                self.processCompletedObject(None, self.rawObject.groupName)
                reachedFaces = False

            if bufferLength == 3:
                self.rawObject.pushVertex(buffer)
            else:
                self.rawObject.pushVertexAndVertextColors(buffer)

        elif buffer[0] == LINE_VT:
            self.rawObject.pushUv(buffer)

        elif buffer[0] == LINE_VN:
            self.rawObject.pushNormal(buffer)

        elif buffer[0] == LINE_F:
            reachedFaces = True
            self.rawObject.processFaces(buffer, bufferPointer, slashesCount)

        elif buffer[0] == LINE_L:
            if bufferLength == slashesCount * 2:
                self.rawObject.buildLineVvt(buffer, bufferLength)
            else:
                self.rawObject.buildLineV(buffer, bufferLength)

        elif buffer[0] == LINE_S:
            self.rawObject.pushSmoothingGroup(buffer[1])
            self.flushStringBuffer(buffer, bufferPointer)

        elif buffer[0] == LINE_G:
            concatBuffer = ' '.join(buffer[1:bufferPointer]) if bufferLength > 1 else buffer[1]
            self.processCompletedGroup(concatBuffer)
            self.flushStringBuffer(buffer, bufferPointer)

        elif buffer[0] == LINE_O:
            concatBuffer = ' '.join(buffer[1:bufferPointer]) if bufferLength > 1 else buffer[1]
            if len(self.rawObject.vertices) > 0:
                self.processCompletedObject(concatBuffer, None)
                reachedFaces = False
            else:
                self.rawObject.pushObject(concatBuffer)

            self.flushStringBuffer(buffer, bufferPointer)

        elif buffer[0] == LINE_MTLLIB:
            concatBuffer = ' '.join(buffer[1:bufferPointer]) if bufferLength > 1 else buffer[1]
            self.rawObject.pushMtllib(concatBuffer)
            self.flushStringBuffer(buffer, bufferPointer)

        elif buffer[0] == LINE_USEMTL:
            concatBuffer = ' '.join(buffer[1:bufferPointer]) if bufferLength > 1 else buffer[1]
            self.rawObject.pushUsemtl(concatBuffer)
            self.flushStringBuffer(buffer, bufferPointer)

        return reachedFaces

    def flushStringBuffer(self, buffer, bufferLength):
        for i in range(bufferLength):
            buffer[i] = ''

    def processCompletedObject(self, objectName, groupName):
        self.rawObject.finalize(self.meshCreator, self.inputObjectCount, self.debug)
        self.inputObjectCount += 1
        self.rawObject = self.rawObject.newInstanceFromObject(objectName, groupName)

    def processCompletedGroup(self, groupName):
        notEmpty = self.rawObject.finalize(self.meshCreator, self.inputObjectCount, self.debug)
        if notEmpty:
            self.inputObjectCount += 1
            self.rawObject = self.rawObject.newInstanceFromGroup(groupName)
        else:
            # if a group was set that did not lead to object creation in finalize, then the group name has to be updated
            self.rawObject.pushGroup(groupName)

    def finalize(self):
        self.rawObject.finalize(self.meshCreator, self.inputObjectCount, self.debug)
        self.inputObjectCount += 1


class MeshCreator:
    """
     * MeshCreator is used to transform RawObjectDescriptions to THREE.Mesh
     *
     * @class
    """
    def __init__(self):
        self.sceneGraphBaseNode = None
        self.materials = None
        self.debug = False
        self.globalObjectCount = 1

        self.validated = False

    def setSceneGraphBaseNode(self, sceneGraphBaseNode):
        self.sceneGraphBaseNode = Validator.verifyInput(sceneGraphBaseNode, self.sceneGraphBaseNode)
        self.sceneGraphBaseNode = Validator.verifyInput(self.sceneGraphBaseNode, THREE.Group())

    def setMaterials(self, materials):
        self.materials = Validator.verifyInput(materials, self.materials)
        self.materials = Validator.verifyInput(self.materials, {'materials': []})

        if 'defaultMaterial' not in self.materials:
            defaultMaterial = THREE.MeshStandardMaterial({'color': 0xDCF1FF})
            defaultMaterial.name = 'defaultMaterial'
            self.materials['defaultMaterial'] = defaultMaterial

        if 'vertexColorMaterial' not in self.materials:
            vertexColorMaterial = THREE.MeshBasicMaterial({'color': 0xDCF1FF})
            vertexColorMaterial.name = 'vertexColorMaterial'
            vertexColorMaterial.vertexColors = THREE.VertexColors
            self.materials['vertexColorMaterial'] = vertexColorMaterial

    def setDebug(self, debug):
        self.debug = debug

    def validate(self):
        if self.validated:
            return

        self.setSceneGraphBaseNode(None)
        self.setMaterials(None)
        self.setDebug(None)
        self.globalObjectCount = 1

    def finalize(self):
        self.sceneGraphBaseNode = None
        self.materials = None
        self.validated = False

    def buildMesh(self, rawObjectDescriptions, inputObjectCount, absoluteVertexCount,
                                                 absoluteColorCount, absoluteNormalCount, absoluteUvCount):

        """
         * This is an internal def, but due to its importance to Parser it is documented.
         * RawObjectDescriptions are transformed to THREE.Mesh.
         * It is ensured that rawObjectDescriptions only contain objects with vertices (no need to check).
         * This method shall be overridden by the web worker implementation
         *
         * @param {RawObjectDescription[]} rawObjectDescriptions Array of descriptive information and data (vertices, normals, uvs) about the parsed object(s)
         * @param {number} inputObjectCount Number of objects already retrieved from OBJ
         * @param {number} absoluteVertexCount Sum of all vertices of all rawObjectDescriptions
         * @param {number} absoluteColorCount Sum of all vertex colors of all rawObjectDescriptions
         * @param {number} absoluteNormalCount Sum of all normals of all rawObjectDescriptions
         * @param {number} absoluteUvCount Sum of all uvs of all rawObjectDescriptions
        """
        if self.debug:
            print('MeshCreator.buildRawMeshData:\nInput object no.: ' + inputObjectCount)

        bufferGeometry = THREE.BufferGeometry()
        vertexBA = THREE.BufferAttribute(Float32Array(absoluteVertexCount), 3)
        bufferGeometry.addAttribute('position', vertexBA)

        if absoluteColorCount > 0:
            colorBA = THREE.BufferAttribute(Float32Array(absoluteColorCount), 3)
            bufferGeometry.addAttribute('color', colorBA)
        else:
            colorBA = None

        if absoluteNormalCount > 0:
            normalBA = THREE.BufferAttribute(Float32Array(absoluteNormalCount), 3)
            bufferGeometry.addAttribute('normal', normalBA)
        else:
            normalBA = None

        if absoluteUvCount > 0:
            uvBA = THREE.BufferAttribute(Float32Array(absoluteUvCount), 2)
            bufferGeometry.addAttribute('uv', uvBA)
        else:
            uvBA = None

        createMultiMaterial = len(rawObjectDescriptions) > 1
        materials = []
        materialIndex = 0
        materialIndexMapping = {}

        vertexBAOffset = 0
        vertexGroupOffset = 0
        colorBAOffset = 0
        normalBAOffset = 0
        uvBAOffset = 0

        if self.debug:
            print('Creating Multi-Material' if createMultiMaterial else 'Creating Material' + ' for object no.: ' + self.globalObjectCount)

        for rawObjectDescription in rawObjectDescriptions:
            materialName = rawObjectDescription.materialName
            material = self.materials['vertexColorMaterial'] if colorBA else self.materials[materialName]
            if not material:
                material = self.materials['defaultMaterial']
                if not material:
                    print('object_group "' + rawObjectDescription.objectName + '_' + rawObjectDescription.groupName +
                                                '" was defined without materialnot Assigning "defaultMaterial".')

            # clone material in case flat shading is needed due to smoothingGroup 0
            if rawObjectDescription.smoothingGroup == 0:
                materialName = material.name + '_flat'
                if materialName not in self.materials:
                    materialClone = material.clone()
                    materialClone.name = materialName
                    materialClone.flatShading = True
                    self.materials[materialName] = material.name

            vertexLength = len(rawObjectDescription.vertices)
            if createMultiMaterial:
                # re-use material if already used before. Reduces materials array size and eliminates duplicates
                if materialName not in materialIndexMapping:
                    selectedMaterialIndex = materialIndex
                    materialIndexMapping[materialName] = materialIndex
                    materials.append(material)
                    materialIndex += 1

                bufferGeometry.addGroup(vertexGroupOffset, vertexLength / 3, selectedMaterialIndex)
                vertexGroupOffset += vertexLength / 3

            vertexBA.set(rawObjectDescription.vertices, vertexBAOffset)
            vertexBAOffset += vertexLength

            if colorBA:
                colorBA.set(rawObjectDescription.colors, colorBAOffset)
                colorBAOffset += len(rawObjectDescription.colors)

            if normalBA:
                normalBA.set(rawObjectDescription.normals, normalBAOffset)
                normalBAOffset += len(rawObjectDescription.normals)

            if uvBA:
                uvBA.set(rawObjectDescription.uvs, uvBAOffset)
                uvBAOffset += len(rawObjectDescription.uvs)

            if self.debug:
                self.printReport(rawObjectDescription, selectedMaterialIndex)

        if not normalBA:
            bufferGeometry.computeVertexNormals()

        if createMultiMaterial:
            material = materials
        mesh = THREE.Mesh(bufferGeometry, material)
        mesh.name = rawObjectDescription.groupName if rawObjectDescription.groupName != '' else rawObjectDescription.objectName
        self.sceneGraphBaseNode.add(mesh)

        self.globalObjectCount += 1

    def printReport(self, rawObjectDescription, selectedMaterialIndex):
        materialIndexLine = Validator.isValid('\n materialIndex: ' + selectedMaterialIndex if selectedMaterialIndex else '')
        print(
            ' Output Object no.: ' + self.globalObjectCount +
            '\n objectName: ' + rawObjectDescription.objectName +
            '\n groupName: ' + rawObjectDescription.groupName +
            '\n materialName: ' + rawObjectDescription.materialName +
            materialIndexLine +
            '\n smoothingGroup: ' + rawObjectDescription.smoothingGroup +
            '\n #vertices: ' + len(rawObjectDescription.vertices) / 3 +
            '\n #colors: ' + len(rawObjectDescription.colors) / 3 +
            '\n #uvs: ' + len(rawObjectDescription.uvs) / 2 +
            '\n #normals: ' + len(rawObjectDescription.normals) / 3
       )

    
class OBJLoader2:
    """
     * Use self class to load OBJ data from files or to parse OBJ data from arraybuffer or text
     * @class
     *
     * @param {THREE.DefaultLoadingManager} [manager] The loadingManager for the loader to use. Default is {@link THREE.DefaultLoadingManager}
    """
    OBJLOADER2_VERSION = '1.4.1'

    def __init__(self, manager=None):
        print("Using THREE.OBJLoader2 version: " + self.OBJLOADER2_VERSION)
        self.manager = Validator.verifyInput(manager, THREE.DefaultLoadingManager)

        self.path = ''
        self.fileLoader = THREE.FileLoader(self.manager)

        self.meshCreator = MeshCreator()
        self.parser = Parser(self.meshCreator)

        self.validated = False
        self.obj = None

    def setPath(self, path):
        """
         * Base path to use.
         * @memberOf THREE.OBJLoader2
         *
         * @param {string} path The basepath
        """
        self.path = Validator.verifyInput(path, self.path)

    def setSceneGraphBaseNode(self, sceneGraphBaseNode):
        """
         * Set the node where the loaded objects will be attached.
         * @memberOf THREE.OBJLoader2
         *
         * @param {THREE.Object3D} sceneGraphBaseNode Scenegraph object where meshes will be attached
        """
        self.meshCreator.setSceneGraphBaseNode(sceneGraphBaseNode)

    def setMaterials(self, materials):
        """
         * Set materials loaded by MTLLoader or any other supplier of an Array of {@link THREE.Material}.
         * @memberOf THREE.OBJLoader2
         *
         * @param {THREE.Material[]} materials  Array of {@link THREE.Material} from MTLLoader
        """
        self.meshCreator.setMaterials(materials)

    def setDebug(self, parserDebug, meshCreatorDebug):
        """
         * Allows to set debug mode for the parser and the meshCreator.
         * @memberOf THREE.OBJLoader2
         *
         * @param {boolean} parserDebug Internal Parser will produce debug output
         * @param {boolean} meshCreatorDebug Internal MeshCreator will produce debug output
        """
        self.parser.setDebug(parserDebug)
        self.meshCreator.setDebug(meshCreatorDebug)

    def load(self, url, onLoad=None, onProgress=None, onError=None, useArrayBuffer=True):
        """
         * Use self convenient method to load an OBJ file at the given URL. Per default the fileLoader uses an arraybuffer
         * @memberOf THREE.OBJLoader2
         *
         * @param {string} url URL of the file to load
         * @param {callback} onLoad Called after loading was successfully completed
         * @param {callback} onProgress Called to report progress of loading. The argument will be the XMLHttpRequest instance, which contains {integer total} and {integer loaded} bytes.
         * @param {callback} onError Called after an error occurred during loading
         * @param {boolean} [useArrayBuffer=True] Set self to False to force string based parsing
        """
        self._validate()
        self.fileLoader.setPath(self.path)
        self.fileLoader.setResponseType('arraybuffer' if useArrayBuffer is not False else 'text')

        scope = self

        def _load(content):
            # only use parseText if useArrayBuffer is explicitly set to False
            scope.obj = scope.parse(content) if useArrayBuffer is not False else scope.parseText(content)
            if onLoad:
                onLoad(scope.obj)

        self.fileLoader.load(url, _load, onProgress, onError)
        return self.obj

    def parse(self, arrayBuffer):
        """
         * Default parse def: Parses OBJ file content stored in arrayBuffer and returns the sceneGraphBaseNode
         * @memberOf THREE.OBJLoader2
         *
         * @param {Uint8Array} arrayBuffer OBJ data as Uint8Array
        """
        # fast-fail on bad type
        if not (isinstance(arrayBuffer, bytes) or isinstance(arrayBuffer, Uint8Array)):
            raise RuntimeError('Provided input is not of type bytes ! Aborting...')

        print('Parsing arrayBuffer...')

        self._validate()
        self.parser.parseArrayBuffer(arrayBuffer)
        sceneGraphAttach = self._finalize()

        return sceneGraphAttach

    def parseText(self, text):
        """
         * Legacy parse def: Parses OBJ file content stored in string and returns the sceneGraphBaseNode
         * @memberOf THREE.OBJLoader2
         *
         * @param {string} text OBJ data as string
        """
        # fast-fail on bad type
        if not isinstance(text, str):
            raise RuntimeError('Provided input is not of type Stringnot Aborting...')

        print('Parsing text...')

        self._validate()
        self.parser.parseText(text)
        sceneGraphBaseNode = self._finalize()

        return sceneGraphBaseNode

    def _validate(self):
        if self.validated:
            return

        self.fileLoader = Validator.verifyInput(self.fileLoader, THREE.FileLoader(self.manager))
        self.parser.validate()
        self.meshCreator.validate()

        self.validated = True

    def _finalize(self):
        print('Global output object count: %s' % self.meshCreator.globalObjectCount)

        self.parser.finalize()
        self.fileLoader = None
        sceneGraphBaseNode = self.meshCreator.sceneGraphBaseNode
        self.meshCreator.finalize()
        self.validated = False

        return sceneGraphBaseNode

    def _getValidator(self):
        return Validator

    def _buildWebWorkerCode(self, funcBuildObject, funcBuildSingelton):
        workerCode = ''
        workerCode += funcBuildObject('Consts', Consts)
        workerCode += funcBuildObject('Validator', Validator)
        workerCode += funcBuildSingelton('Parser', 'Parser', Parser)
        workerCode += funcBuildSingelton('RawObject', 'RawObject', RawObject)
        workerCode += funcBuildSingelton('RawObjectDescription', 'RawObjectDescription', RawObjectDescription)
        return workerCode
