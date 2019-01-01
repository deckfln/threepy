"""
/**
 * @author mrdoob / http:#mrdoob.com/
 */
"""
import re
import THREE
from THREE.javascriparray import *


class _material:
    def __init__(self, index, name, mtllib, smooth, groupStart):
        self.index = index
        self.name = name
        self.mtllib = mtllib
        self.smooth = smooth
        self.groupStart = groupStart
        self.groupEnd = -1
        self.groupCount = -1
        self.inherited = False

    def clone(self, index):
        return _material(index if isinstance(index, int) else self.index, self.name, self.mtllib, self.smooth, self.groupStart)


class _geometry:
    def __init__(self):
        self.vertices = []
        self.normals = []
        self.uvs = []
        self.type = ''


class _object:
    def __init__(self, name, fromDeclaration):
        self.name = name or ''
        self.fromDeclaration = (fromDeclaration != False)

        self.geometry = _geometry()

        self.materials = []
        self.smooth = True

    def startMaterial(self, name, libraries):
        previous = self._finalize(False)

        # New usemtl declaration overwrites an inherited material, except if faces were declared
        # after the material, then it must be preserved for proper MultiMaterial continuation.
        if previous and (previous.inherited or previous.groupCount <= 0):
            del self.materials[previous.index]

        material = _material(len(self.materials),
                             name or '',
                             libraries[len(libraries) - 1] if isinstance(libraries, list) and len(libraries) > 0 else '',
                             previous.smooth if previous is not None else self.smooth,
                             previous.groupEnd if previous is not None else 0)

        self.materials.append(material)

        return material

    def currentMaterial(self):
        if len(self.materials) > 0:
            return self.materials[len(self.materials) - 1]

        return None

    def _finalize(self, end):
        lastMultiMaterial = self.currentMaterial()
        if lastMultiMaterial and lastMultiMaterial.groupEnd == -1:
            lastMultiMaterial.groupEnd = len(self.geometry.vertices) / 3
            lastMultiMaterial.groupCount = lastMultiMaterial.groupEnd - lastMultiMaterial.groupStart
            lastMultiMaterial.inherited = False

        # Ignore objects tail materials if no face declarations followed them before a o/g started.
        if end and len(self.materials) > 1:
            for mi in range(len(self.materials) - 1, -1, -1):
                if self.materials[mi].groupCount <= 0:
                    del self.materials[mi]

        # Guarantee at least one empty material, self makes the creation later more straight forward.
        if end and len(self.materials) == 0:
            self.materials.append(_material(0, '', None, self.smooth, None))

        return lastMultiMaterial

        
class _state:
    def __init__(self):
        self.objects = []
        self.object = {}
        self.vertices = []
        self.normals = []
        self.uvs = []
        self.materialLibraries = []

    def startObject(self, name, fromDeclaration=True):
        # If the current object (initial from reset) is not from a g/o declaration in the parsed
        # file. We need to use it for the first parsed g/o to keep things in sync.
        if self.object and self.object.fromDeclaration is False:
            self.object.name = name
            self.object.fromDeclaration = (fromDeclaration is not False)
            return

        previousMaterial = self.object.currentMaterial() if self.object and callable(self.object.currentMaterial) else None

        if self.object and callable(self.object._finalize):
            self.object._finalize(True)

        self.object = _object(name, fromDeclaration)

        # Inherit previous objects material.
        # Spec tells us that a declared material must be set to all objects until a material is declared.
        # If a usemtl declaration is encountered while self object is being parsed, it will
        # overwrite the inherited material. Exception being that there was already face declarations
        # to the inherited material, then it will be preserved for proper MultiMaterial continuation.

        if previousMaterial and previousMaterial.name and callable(previousMaterial.clone):
            declared = previousMaterial.clone(0)
            declared.inherited = True
            self.object.materials.append(declared)

        self.objects.append(self.object)

    def finalize(self):
        if self.object and callable(self.object._finalize):
            self.object._finalize(True)

    def parseVertexIndex(self, value, len):
        index = int(value or 0)
        return (index - 1 if index >= 0 else index + len / 3) * 3

    def parseNormalIndex(self, value, len):
        index = int(value or 0)
        return (index - 1 if index >= 0 else index + len / 3) * 3

    def parseUVIndex(self, value, len):
        index = int(value or 0)
        return (index - 1 if index >= 0 else index + len / 2) * 2

    def addVertex(self, a, b, c):
        src = self.vertices
        dst = self.object.geometry.vertices

        dst.extend([src[a + 0], src[a + 1], src[a + 2]])
        dst.extend([src[b + 0], src[b + 1], src[b + 2]])
        dst.extend([src[c + 0], src[c + 1], src[c + 2]])

    def addVertexLine(self, a):
        src = self.vertices
        dst = self.object.geometry.vertices

        dst.extend([src[a + 0], src[a + 1], src[a + 2]])

    def addNormal(self, a, b, c):
        src = self.normals
        dst = self.object.geometry.normals

        dst.extend([src[a + 0], src[a + 1], src[a + 2]])
        dst.extend([src[b + 0], src[b + 1], src[b + 2]])
        dst.extend([src[c + 0], src[c + 1], src[c + 2]])

    def addUV(self, a, b, c):
        src = self.uvs
        dst = self.object.geometry.uvs

        dst.extend([src[a + 0], src[a + 1]])
        dst.extend([src[b + 0], src[b + 1]])
        dst.extend([src[c + 0], src[c + 1]])

    def addUVLine(self, a):
        src = self.uvs
        dst = self.object.geometry.uvs

        dst.extend([src[a + 0], src[a + 1]])

    def addFace(self, a, b, c, ua, ub, uc, na, nb, nc):
        vLen = len(self.vertices)

        ia = self.parseVertexIndex(a, vLen)
        ib = self.parseVertexIndex(b, vLen)
        ic = self.parseVertexIndex(c, vLen)

        self.addVertex(ia, ib, ic)

        if ua is not None:
            uvLen = len(self.uvs)

            ia = self.parseUVIndex(ua, uvLen)
            ib = self.parseUVIndex(ub, uvLen)
            ic = self.parseUVIndex(uc, uvLen)

            if ia > 0 and ib > 0 and ic > 0:
                self.addUV(ia, ib, ic)

        if na is not None:
            # Normals are many times the same. If so, skip function call and parseInt.
            nLen = len(self.normals)
            ia = self.parseNormalIndex(na, nLen)

            ib = ia if na == nb else self.parseNormalIndex(nb, nLen)
            ic = ia if na == nc else self.parseNormalIndex(nc, nLen)

            self.addNormal(ia, ib, ic)

    def addLineGeometry(self, vertices, uvs):
        self.object.geometry.type = 'Line'

        vLen = len(self.vertices)
        uvLen = len(self.uvs)

        for vi in range(len(vertices)):
            self.addVertexLine(self.parseVertexIndex(vertices[vi], vLen))

        for uvi in range(len(uvs)):
            self.addUVLine(self.parseUVIndex(uvs[uvi], uvLen))

        
class OBJLoader:
    def __init__(self, manager=None):
        # o object_name | g group_name
        self.object_pattern = "^[og]\s*(.+)?"
        # mtllib file_reference
        self.material_library_pattern = "^mtllib"
        # usemtl material_name
        self.material_use_pattern = "^usemtl"

        self.manager = manager if (manager is not None) else THREE.DefaultLoadingManager
        self.materials = None

        self.path = None

    def ParserState(self):
        state = _state()
        state.startObject('', False)

        return state

    def load(self, url, onLoad=None, onProgress=None, onError=None):
        loader = THREE.FileLoader(self.manager)
        loader.setPath(self.path)
        text = loader.load(url, None, onProgress,  onError)
        obj = self.parse(text)
        if onLoad is not None:
            onLoad(obj)

        return obj

    def setPath(self, value):
        self.path = value

    def setMaterials(self, materials):
        self.materials = materials

        return self

    def parse(self, text):
        state = self.ParserState()

        if '\r\n' in text:
            # This is faster than String.split with regex that splits on both
            text = re.sub(r'/\r\n/g', '\n', text)

        if '\\\n' in text:
            # join lines separated by a line continuation character (\)
            text = re.sub(r"/\\\n/g", '', text)

        lines = text.split('\n')
        line = ''
        lineFirstChar = ''
        lineLength = 0
        result = []

        for line in lines:
            line = line.lstrip()

            lineLength = len(line)

            if lineLength == 0:
                continue

            lineFirstChar = line[0]

            # @todo invoke passed in handler if any
            if lineFirstChar == '#':
                continue

            if lineFirstChar == 'v':
                data = re.split(r"\s+", line)

                if data[0] == 'v':
                        state.vertices.extend([
                            float(data[1]),
                            float(data[2]),
                            float(data[3])
                       ])
                elif data[0] ==  'vn':
                        state.normals.extend([
                            float(data[1]),
                            float(data[2]),
                            float(data[3])
                       ])
                elif data[0] == 'vt':
                        state.uvs.extend([
                            float(data[1]),
                            float(data[2])
                       ])
            elif lineFirstChar == 'f':
                lineData = line[1:].strip()
                vertexData = re.split(r"\s+", lineData)
                faceVertices = []

                # Parse the face vertex data into an easy to work with format

                for vertex in vertexData:
                    if len(vertex) > 0:
                        vertexParts = re.split(r'/', vertex)
                        faceVertices.append(vertexParts)

                # Draw an edge between the first vertex and all subsequent vertices to form an n-gon
                v1 = faceVertices[0]

                for j in range(len(faceVertices)-1):
                    v2 = faceVertices[j]
                    v3 = faceVertices[j + 1]

                    state.addFace(
                        v1[0], v2[0], v3[0],
                        v1[1], v2[1], v3[1],
                        v1[2], v2[2], v3[2]
                   )

            elif lineFirstChar == 'l':
                lineParts = line.substring(1).trim().split(" ")
                lineVertices = []
                lineUVs = []

                if "/" in line:
                    lineVertices = lineParts
                else:
                    for li in range(len(lineParts)):
                        parts = lineParts[li].split("/")

                        if parts[0] != "":
                            lineVertices.append(parts[0])
                        if parts[1] != "":
                            lineUVs.append(parts[1])

                state.addLineGeometry(lineVertices, lineUVs)

            elif re.search(self.object_pattern, line) is not None:
                result = re.search(self.object_pattern, line)
                # o object_name
                # or
                # g group_name

                # WORKAROUND: https:#bugs.chromium.org/p/v8/issues/detail?id=2869
                # name = result[0].substr(1).trim()
                s = result.regs[1][0]
                name = line[s:].strip()

                state.startObject(name)

            elif re.search(self.material_use_pattern, line):
                # material
                state.object.startMaterial(line[7:].strip(), state.materialLibraries)

            elif re.search(self.material_library_pattern, line):
                # mtl file
                state.materialLibraries.append(line[7:].strip())

            elif lineFirstChar == 's':
                result = line.split(' ')

                # smooth shading

                # @todo Handle files that have varying smooth values for a set of faces inside one geometry,
                # but does not define a usemtl for each face set.
                # This should be detected and a dummy material created (later MultiMaterial and geometry groups).
                # This requires some care to not create extras material on each smooth value for "normal" obj files.
                # where explicit usemtl defines geometry groups.
                # Example asset: examples/models/obj/cerberus/Cerberus.obj

                """
                 * http:#paulbourke.net/dataformats/obj/
                 * or
                 * http:#www.cs.utah.edu/~boulos/cs3505/obj_spec.pdf
                 *
                 * From chapter "Grouping" Syntax explanation "s group_number":
                 * "group_number is the smoothing group number. To turn off smoothing groups, use a value of 0 or off.
                 * Polygonal elements use group numbers to put elements in different smoothing groups. For free-form
                 * surfaces, smoothing groups are either turned on or off; there is no difference between values greater
                 * than 0."
                """
                if len(result) > 1:
                    value = result[1].strip().lower()
                    state.object.smooth = (value != '0' and value != 'off')

                else:
                    # ZBrush can produce "s" lines #11707
                    state.object.smooth = True

                material = state.object.currentMaterial()
                if material:
                    material.smooth = state.object.smooth

            else:
                # Handle null terminated files without exception
                if line == '\0':
                    continue

                raise RuntimeError("Unexpected line: '" + line  + "'")

        state.finalize()

        container = THREE.Group()
        container.materialLibraries = state.materialLibraries[:]

        for object in state.objects:
            geometry = object.geometry
            materials = object.materials
            isLine = (geometry.type == 'Line')

            # Skip o/g line declarations that did not follow with any faces
            if len(geometry.vertices) == 0:
                continue

            buffergeometry = THREE.BufferGeometry()

            buffergeometry.addAttribute('position', THREE.BufferAttribute(Float32Array(geometry.vertices), 3))

            if len(geometry.normals) > 0:
                buffergeometry.addAttribute('normal', THREE.BufferAttribute(Float32Array(geometry.normals), 3))

            else:
                buffergeometry.computeVertexNormals()

            if len(geometry.uvs) > 0:
                buffergeometry.addAttribute('uv', THREE.BufferAttribute(Float32Array(geometry.uvs), 2))

            # Create materials

            createdMaterials = []

            for sourceMaterial in materials:
                material = None

                if self.materials is not None:
                    material = self.materials.create(sourceMaterial.name)

                    # mtl etc. loaders probably can't create line materials correctly, copy properties to a line material.
                    if isLine and material and not isinstance(material, THREE.LineBasicMaterial):
                        materialLine = THREE.LineBasicMaterial()
                        materialLine.copy(material)
                        material = materialLine

                if not material:
                    material = (THREE.MeshPhongMaterial() if not isLine else THREE.LineBasicMaterial())
                    material.name = sourceMaterial.name

                material.flatShading = False if sourceMaterial.smooth else True

                createdMaterials.append(material)

            # Create mesh

            if len(createdMaterials) > 1:
                mi = 0
                for sourceMaterial in materials:
                    buffergeometry.addGroup(sourceMaterial.groupStart, sourceMaterial.groupCount, mi)
                    mi += 1

                mesh = (THREE.Mesh(buffergeometry, createdMaterials) if not isLine else THREE.LineSegments(buffergeometry, createdMaterials))

            else:
                mesh = (THREE.Mesh(buffergeometry, createdMaterials[0]) if not isLine else THREE.LineSegments(buffergeometry, createdMaterials[0]))

            mesh.name = object.name

            container.add(mesh)

        return container
