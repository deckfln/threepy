"""
/**
 * @author zz85 / http:# //www.lab4games.net/zz85/blog
 *
 * Creates extruded geometry from a path shape.
 *
 * parameters = {
 *
 *  curveSegments: <int>, # // number of points on the curves
 *  steps: <int>, # // number of points for z-side extrusions / used for subdividing segments of extrude spline too
 *  amount: <int>, # // Depth to extrude the shape
 *
 *  bevelEnabled: <bool>, # // turn on bevel
 *  bevelThickness: <float>, # // how deep into the original shape bevel goes
 *  bevelSize: <float>, # // how far from shape outline is bevel
 *  bevelSegments: <int>, # // number of bevel layers
 *
 *  extrudePath: <THREE.Curve> # // curve to extrude shape along
 *  frames: <Object> # // containing arrays of tangents, normals, binormals
 *
 *  UVGenerator: <Object> # // object that provides UV generator functions
 *
 * }
 */
"""
from THREE.core.Geometry import *
import THREE.ShapeUtils as ShapeUtils


class _WorldUVGenerator:
    def generateTopUV(geometry, vertices, indexA, indexB, indexC ):
        a_x = vertices[ indexA * 3 ]
        a_y = vertices[ indexA * 3 + 1 ]
        b_x = vertices[ indexB * 3 ]
        b_y = vertices[ indexB * 3 + 1 ]
        c_x = vertices[ indexC * 3 ]
        c_y = vertices[ indexC * 3 + 1 ]

        return [
            Vector2( a_x, a_y ),
            Vector2( b_x, b_y ),
            Vector2( c_x, c_y )
        ]

    def generateSideWallUV(geometry, vertices, indexA, indexB, indexC, indexD ):
        a_x = vertices[ indexA * 3 ]
        a_y = vertices[ indexA * 3 + 1 ]
        a_z = vertices[ indexA * 3 + 2 ]
        b_x = vertices[ indexB * 3 ]
        b_y = vertices[ indexB * 3 + 1 ]
        b_z = vertices[ indexB * 3 + 2 ]
        c_x = vertices[ indexC * 3 ]
        c_y = vertices[ indexC * 3 + 1 ]
        c_z = vertices[ indexC * 3 + 2 ]
        d_x = vertices[ indexD * 3 ]
        d_y = vertices[ indexD * 3 + 1 ]
        d_z = vertices[ indexD * 3 + 2 ]

        if abs( a_y - b_y ) < 0.01:
            return [
                Vector2( a_x, 1 - a_z ),
                Vector2( b_x, 1 - b_z ),
                Vector2( c_x, 1 - c_z ),
                Vector2( d_x, 1 - d_z )
            ]

        else:
            return [
                Vector2( a_y, 1 - a_z ),
                Vector2( b_y, 1 - b_z ),
                Vector2( c_y, 1 - c_z ),
                Vector2( d_y, 1 - d_z )
            ]


# // ExtrudeGeometry

class ExtrudeGeometry(Geometry):
    def __init__(self, shapes, options):
        super().__init__()

        self.type = 'ExtrudeGeometry'

        self.parameters = {
            'shapes': shapes,
            'options': options
        }

        self.fromBufferGeometry(ExtrudeBufferGeometry(shapes, options))
        self.mergeVertices()

    def ExtrudeGeometry(self):
        data = super().toJSON()

        shapes = self.parameters.shapes
        options = self.parameters.options

        return toJSON( shapes, options, data )

# // ExtrudeBufferGeometry


class ExtrudeBufferGeometry(BufferGeometry):
    def __init__(self, shapes=None, options=None):
        super().__init__()

        self.type = 'ExtrudeBufferGeometry'

        self.parameters = {
            'shapes': shapes,
            'options': options
        }

        shapes = shapes if isinstance(shapes, list) else [shapes]

        verticesArray = []
        uvArray = []

        def addShape(shape):
            placeholder = []
            # options
            curveSegments = options['curveSegments'] if 'curveSegments' in options else 12
            steps = options['steps'] if 'steps' in options else 1
            depth = options['depth'] if 'depth' in options else 100

            bevelEnabled = options['bevelEnabled'] if 'bevelEnabled' in options else True  # // false
            bevelThickness = options['bevelThickness'] if 'bevelThickness' in options else 6  # // 10
            bevelSize = options['bevelSize'] if 'bevelSize' in options else bevelThickness - 2  # // 8
            bevelSegments = options['bevelSegments'] if 'bevelSegments' in options else 3

            extrudePath = options['extrudePath'] if 'extrudePath' in options else None

            uvgen = options['UVGenerator'] if 'UVGenerator' in options else _WorldUVGenerator

            extrudePts = False
            extrudeByPath = False

            if extrudePath:
                extrudePts = extrudePath.getSpacedPoints(steps)

                extrudeByPath = True
                bevelEnabled = False  # // bevels not supported for path extrusion

                # // SETUP TNB variables

                # // TODO1 - have a .isClosed in spline?

                splineTube = extrudePath.computeFrenetFrames(steps, False)

                # // console.log(splineTube, 'splineTube', splineTube.normals.length, 'steps', steps, 'extrudePts', extrudePts.length)

                binormal = Vector3()
                normal = Vector3()
                position2 = Vector3()

            # // Safeguards if bevels are not enabled

            if not bevelEnabled:
                bevelSegments = 0
                bevelThickness = 0
                bevelSize = 0

            # // Variables initialization
            shapePoints = shape.extractPoints(curveSegments)

            vertices = shapePoints['shape']
            holes = shapePoints['holes']

            reverse = not ShapeUtils.isClockWise(vertices)

            if reverse:
                vertices.reverse()

                # // Maybe we should also check if holes are in the opposite direction, just to be safe ...

                for h in range(len(holes)):
                    ahole = holes[h]
                    if ShapeUtils.isClockWise(ahole):
                        ahole.reverse()

            faces = ShapeUtils.triangulateShape(vertices, holes)

            # /* Vertices */

            contour = vertices[:]  # // vertices has all points but contour has only points of circumference

            for h in range(len(holes)):
                ahole = holes[h]
                vertices += ahole

            def scalePt2(pt, vec, size):
                if not vec:
                    raise RuntimeError("THREE.ExtrudeGeometry: vec does not exist")

                return vec.clone().multiplyScalar(size).add(pt)

            vlen = len(vertices)
            flen = len(faces)

            def sign(x):
                return 1 if x >= 0 else -1

            def v(x, y, z):
                placeholder.append(x)
                placeholder.append(y)
                placeholder.append(z)

            def f3(a, b, c):
                addVertex(a)
                addVertex(b)
                addVertex(c)

                nextIndex = int(len(verticesArray) / 3)
                uvs = uvgen.generateTopUV(self, verticesArray, nextIndex - 3, nextIndex - 2, nextIndex - 1)

                addUV(uvs[0])
                addUV(uvs[1])
                addUV(uvs[2])

            def f4(a, b, c, d):
                addVertex(a)
                addVertex(b)
                addVertex(d)

                addVertex(b)
                addVertex(c)
                addVertex(d)

                nextIndex = int(len(verticesArray) / 3)
                uvs = uvgen.generateSideWallUV(self, verticesArray, nextIndex - 6, nextIndex - 3, nextIndex - 2,
                                               nextIndex - 1)

                addUV(uvs[0])
                addUV(uvs[1])
                addUV(uvs[3])

                addUV(uvs[1])
                addUV(uvs[2])
                addUV(uvs[3])

            def addVertex(index):
                verticesArray.append(placeholder[index * 3 + 0])
                verticesArray.append(placeholder[index * 3 + 1])
                verticesArray.append(placeholder[index * 3 + 2])

            def addUV(vector2):
                uvArray.append(vector2.x)
                uvArray.append(vector2.y)

            # // Find directions for point movement
            def getBevelVec(inPt, inPrev, inNext):
                # // computes for inPt the corresponding point inPt' on a contour
                # //   shifted by 1 unit (length of normalized vector) to the left
                # // if we walk along contour clockwise, self contour is outside the old one
                # //
                # // inPt' is the intersection of the two lines parallel to the two
                # //  adjacent edges of inPt at a distance of 1 unit on the left side.

                # // good reading for geometry algorithms (here: line-line intersection)
                # // http:# //geomalgorithms.com/a05-_intersect-1.html

                v_prev_x = inPt.x - inPrev.x
                v_prev_y = inPt.y - inPrev.y
                v_next_x = inNext.x - inPt.x
                v_next_y = inNext.y - inPt.y

                v_prev_lensq = (v_prev_x * v_prev_x + v_prev_y * v_prev_y)

                # // check for collinear edges
                collinear0 = (v_prev_x * v_next_y - v_prev_y * v_next_x)

                if abs(collinear0) > Number.EPSILON:
                    # // not collinear
                    # // length of vectors for normalizing

                    v_prev_len = math.sqrt(v_prev_lensq)
                    v_next_len = math.sqrt(v_next_x * v_next_x + v_next_y * v_next_y)

                    # // shift adjacent points by unit vectors to the left

                    ptPrevShift_x = (inPrev.x - v_prev_y / v_prev_len)
                    ptPrevShift_y = (inPrev.y + v_prev_x / v_prev_len)

                    ptNextShift_x = (inNext.x - v_next_y / v_next_len)
                    ptNextShift_y = (inNext.y + v_next_x / v_next_len)

                    # // scaling factor for v_prev to intersection point

                    sf = ((ptNextShift_x - ptPrevShift_x) * v_next_y - (ptNextShift_y - ptPrevShift_y) * v_next_x) / (
                                v_prev_x * v_next_y - v_prev_y * v_next_x)

                    # // vector from inPt to intersection point

                    v_trans_x = (ptPrevShift_x + v_prev_x * sf - inPt.x)
                    v_trans_y = (ptPrevShift_y + v_prev_y * sf - inPt.y)

                    # // Don't normalize!, otherwise sharp corners become ugly
                    # //  but prevent crazy spikes
                    v_trans_lensq = (v_trans_x * v_trans_x + v_trans_y * v_trans_y)
                    if v_trans_lensq <= 2:
                        return Vector2(v_trans_x, v_trans_y)
                    else:
                        shrink_by = math.sqrt(v_trans_lensq / 2)

                else:
                    # // handle special case of collinear edges

                    direction_eq = False  # // assumes: opposite
                    if v_prev_x > Number.EPSILON:
                        if v_next_x > Number.EPSILON:
                            direction_eq = True

                    else:
                        if v_prev_x < - Number.EPSILON:
                            if v_next_x < - Number.EPSILON:
                                direction_eq = True

                        else:
                            if sign(v_prev_y) == sign(v_next_y):
                                direction_eq = True

                    if direction_eq:
                        # // console.log("Warning: lines are a straight sequence")
                        v_trans_x = - v_prev_y
                        v_trans_y = v_prev_x
                        shrink_by = math.sqrt(v_prev_lensq)

                    else:
                        # // console.log("Warning: lines are a straight spike")
                        v_trans_x = v_prev_x
                        v_trans_y = v_prev_y
                        shrink_by = math.sqrt(v_prev_lensq / 2)

                return Vector2(v_trans_x / shrink_by, v_trans_y / shrink_by)

            contourMovements = [None for i in range(len(contour))]

            i = 0
            il = len(contour)
            j = il - 1
            k = i + 1
            while i < il:

                if j == il:
                    j = 0
                if k == il:
                    k = 0

                # //  (j)---(i)---(k)
                # // console.log('i,j,k', i, j , k)

                contourMovements[i] = getBevelVec(contour[i], contour[j], contour[k])

                i += 1
                j += 1
                k += 1

            holesMovements = []
            verticesMovements = contourMovements[:]

            for ahole in holes:
                oneHoleMovements = [None for i in range(len(ahole))]

                i = 0
                il = len(ahole)
                j = il - 1
                k = i + 1
                while i < il:
                    if j == il:
                        j = 0
                    if k == il:
                        k = 0

                    # //  (j)---(i)---(k)
                    oneHoleMovements[i] = getBevelVec(ahole[i], ahole[j], ahole[k])

                    i += 1
                    j += 1
                    k += 1

                holesMovements.append(oneHoleMovements)
                verticesMovements += oneHoleMovements

            # // Loop bevelSegments, 1 for the front, 1 for the back
            for b in range(bevelSegments):
                # //for ( b = bevelSegments; b > 0; b -- ):

                t = b / bevelSegments
                z = bevelThickness * math.cos(t * math.pi / 2)
                bs = bevelSize * math.sin(t * math.pi / 2)

                # // contract shape

                for i in range(len(contour)):
                    vert = scalePt2(contour[i], contourMovements[i], bs)
                    v(vert.x, vert.y, - z)

                # // expand holes

                for h in range(len(holes)):
                    ahole = holes[h]
                    oneHoleMovements = holesMovements[h]

                    for i in range(len(ahole)):
                        vert = scalePt2(ahole[i], oneHoleMovements[i], bs)
                        v(vert.x, vert.y, - z)

            bs = bevelSize

            # // Back facing vertices

            for i in range(vlen):
                vert = scalePt2(vertices[i], verticesMovements[i], bs) if bevelEnabled else vertices[i]

                if not extrudeByPath:
                    v(vert.x, vert.y, 0)

                else:
                    # // v( vert.x, vert.y + extrudePts[ 0 ].y, extrudePts[ 0 ].x )
                    normal.copy(splineTube['normals'][0]).multiplyScalar(vert.x)
                    binormal.copy(splineTube['binormals'][0]).multiplyScalar(vert.y)

                    position2.copy(extrudePts[0]).add(normal).add(binormal)

                    v(position2.x, position2.y, position2.z)

            # // Add stepped vertices...
            # // Including front facing vertices
            for s in range(1, steps + 1):
                for i in range(vlen):
                    vert = scalePt2(vertices[i], verticesMovements[i], bs) if bevelEnabled else vertices[i]

                    if not extrudeByPath:
                        v(vert.x, vert.y, depth / steps * s)

                    else:
                        # // v( vert.x, vert.y + extrudePts[ s - 1 ].y, extrudePts[ s - 1 ].x )

                        normal.copy(splineTube['normals'][s]).multiplyScalar(vert.x)
                        binormal.copy(splineTube['binormals'][s]).multiplyScalar(vert.y)

                        position2.copy(extrudePts[s]).add(normal).add(binormal)

                        v(position2.x, position2.y, position2.z)

            # // Add bevel segments planes

            # //for ( b = 1; b <= bevelSegments; b ++ ):
            for b in range(bevelSegments - 1, -1, -1):
                t = b / bevelSegments
                z = bevelThickness * math.cos(t * math.pi / 2)
                bs = bevelSize * math.sin(t * math.pi / 2)

                # // contract shape
                for i in range(len(contour)):
                    vert = scalePt2(contour[i], contourMovements[i], bs)
                    v(vert.x, vert.y, depth + z)

                # // expand holes
                for h in range(len(holes)):
                    ahole = holes[h]
                    oneHoleMovements = holesMovements[h]

                    for i in range(len(ahole)):
                        vert = scalePt2(ahole[i], oneHoleMovements[i], bs)

                        if not extrudeByPath:
                            v(vert.x, vert.y, depth + z)

                        else:
                            v(vert.x, vert.y + extrudePts[steps - 1].y, extrudePts[steps - 1].x + z)


            # //# ///  Internal functions
            def buildLidFaces():
                start = len(verticesArray) / 3

                if bevelEnabled:
                    layer = 0  # // steps + 1
                    offset = vlen * layer

                    # // Bottom faces

                    for i in range(flen):
                        face = faces[i]
                        f3(face[2] + offset, face[1] + offset, face[0] + offset)

                    layer = steps + bevelSegments * 2
                    offset = vlen * layer

                    # // Top faces

                    for i in range(flen):
                        face = faces[i]
                        f3(face[0] + offset, face[1] + offset, face[2] + offset)

                else:
                    # // Bottom faces
                    for i in range(flen):
                        face = faces[i]
                        f3(face[2], face[1], face[0])

                    # // Top faces

                    for i in range(flen):
                        face = faces[i]
                        f3(face[0] + vlen * steps, face[1] + vlen * steps, face[2] + vlen * steps)

                self.addGroup(start, len(verticesArray) / 3 - start, 0)

            # // Create faces for the z-sides of the shape
            def buildSideFaces():
                start = len(verticesArray) / 3
                layeroffset = 0
                sidewalls(contour, layeroffset)
                layeroffset += len(contour)

                for h in range(len(holes)):
                    ahole = holes[h]
                    sidewalls(ahole, layeroffset)

                    # //, true
                    layeroffset += len(ahole)

                self.addGroup(start, len(verticesArray) / 3 - start, 1)

            def sidewalls(contour, layeroffset):
                i = len(contour) - 1

                while i >= 0:
                    j = i
                    k = i - 1
                    if k < 0:
                        k = len(contour) - 1

                    # //console.log('b', i,j, i-1, k,vertices.length)

                    s = 0
                    sl = steps + bevelSegments * 2

                    for s in range(sl):
                        slen1 = vlen * s
                        slen2 = vlen * (s + 1)

                        a = layeroffset + j + slen1
                        b = layeroffset + k + slen1
                        c = layeroffset + k + slen2
                        d = layeroffset + j + slen2

                        f4(a, b, c, d)

                    i -= 1

            # // Top and bottom faces

            buildLidFaces()

            # // Sides faces

            buildSideFaces()

        for shape in shapes:
            addShape( shape )

        # build geometry

        self.addAttribute('position', Float32BufferAttribute(verticesArray, 3) )
        self.addAttribute('uv', Float32BufferAttribute(uvArray, 2) )

        self.computeVertexNormals()

    def getArrays(self):
        positionAttribute = self.getAttribute("position")
        verticesArray = positionAttribute.array[:] if positionAttribute else []

        uvAttribute = self.getAttribute("uv")
        uvArray = uvAttribute.array[:] if uvAttribute else []

        IndexAttribute = self.index
        indicesArray = IndexAttribute.array[:] if IndexAttribute else []

        return {
            'position': verticesArray,
            'uv': uvArray,
            'index': indicesArray
        }

    def addShapeList(self, shapes, options):
        sl = len(shapes)
        options['arrays'] = self.getArrays()

        for s in range(sl):
            shape = shapes[ s ]
            self.addShape( shape, options )

        self.setIndex(options['arrays']['index'])
        self.addAttribute('position', Float32BufferAttribute(options['arrays']['position'], 3))
        self.addAttribute('uv', Float32BufferAttribute(options['arrays']['uv'], 2))

    def toJSON(self):
        data = super().toJSON()

        shapes = self.parameters['shapes']
        options = self.parameters['options']

        return toJSON(shapes, options, data)


def toJSON(shapes, options, data):
    data['shapes'] = []

    if type(shapes) is list:
        for shape in shapes:
            data.shapes.append( shape.uuid )

    else:
        data['shapes'].append( shapes.uuid )

    if options['extrudePath'] is not None:
        data['options'].extrudePath = options['extrudePath'].toJSON()

    return data

