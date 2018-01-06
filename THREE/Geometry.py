"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 * @author kile / http:# //kile.stravaganza.org/
 * @author alteredq / http:# //alteredqualia.com/
 * @author mikael emtinger / http:# //gomo.se/
 * @author zz85 / http:# //www.lab4games.net/zz85/blog
 * @author bhouston / http:# //clara.io
 */
"""
import THREE._Math as _Math
from THREE.pyOpenGLObject import *
from THREE.Matrix3 import *
from THREE.Object3D import *
from THREE.Vector2 import *
from THREE.Color import *
from THREE.Face3 import *
from THREE.Sphere import *
from THREE.BufferGeometry import *
import numpy as np


class Geometry(pyOpenGLObject):
    isGeometry = True
    
    def __init__(self):
        self.id = GeometryIdCount()

        super().__init__()
        self.set_class(isGeometry)

        self.uuid = _Math.generateUUID()

        self.name = ''
        self.type = 'Geometry'

        self.vertices = []
        self.colors = []
        self.faces = []
        self.faceVertexUvs = [[]]

        self.morphTargets = []
        self.morphNormals = []

        self.skinWeights = []
        self.skinIndices = []

        self.lineDistances = []

        self.boundingBox = None
        self.boundingSphere = None

        # // update flags

        self.elementsNeedUpdate = False
        self.verticesNeedUpdate = False
        self.uvsNeedUpdate = False
        self.normalsNeedUpdate = False
        self.colorsNeedUpdate = False
        self.lineDistancesNeedUpdate = False
        self.groupsNeedUpdate = False

        self.callback = None
        self._bufferGeometry = None
        self._directGeometry = None
        self.bones = None

    def applyMatrix(self, matrix ):
        normalMatrix = Matrix3().getNormalMatrix( matrix )

        for i in range (len(self.vertices)):
            vertex = self.vertices[ i ]
            vertex.applyMatrix4( matrix )

        for i in range (len(self.faces)):
            face = self.faces[ i ]
            face.normal.applyMatrix3( normalMatrix ).normalize()

            for j in range(len(face.vertexNormals)):
                face.vertexNormals[ j ].applyMatrix3( normalMatrix ).normalize()

        if self.boundingBox != None:
            self.computeBoundingBox()

        if self.boundingSphere != None:
            self.computeBoundingSphere()

        self.verticesNeedUpdate = True
        self.normalsNeedUpdate = True

        return self

    def rotateX(self, angle):
        # // rotate geometry around world x-axis
        m1 = Matrix4()
        m1.makeRotationX( angle )
        self.applyMatrix( m1 )
        return self


    def rotateY(self, angle):
        # // rotate geometry around world y-axis
        m1 = Matrix4()
        m1.makeRotationY( angle )
        self.applyMatrix( m1 )
        return self


    def rotateZ(self, angle):
        # // rotate geometry around world z-axis
        m1 = Matrix4()
        m1.makeRotationZ( angle )
        self.applyMatrix( m1 )
        return self

    def translate(self, x, y, z):
        # // translate geometry
        m1 = Matrix4()
        m1.makeTranslation( x, y, z )
        self.applyMatrix( m1 )
        return self

    def scale(self, x, y, z):
        # // scale geometry
        m1 = Matrix4()
        m1.makeScale( x, y, z )
        self.applyMatrix( m1 )
        return self

    def lookAt(self, vector):
        obj = Object3D()
        obj.lookAt( vector )
        obj.updateMatrix()
        self.applyMatrix( obj.matrix )

    def fromBufferGeometry(self, geometry=None ):
        scope = self

        indices = geometry.index.array if geometry.index != None else None
        attributes = geometry.attributes

        positions = attributes.position.array
        normals = attributes.normal.array if 'normal' in attributes else None
        colors = attributes.color.array if 'colors' in attributes else None
        uvs = attributes.uv.array if 'uv' in attributes else None
        uvs2 = attributes.uv2.array if 'uv2' in attributes else None

        if uvs2 != None:
            self.faceVertexUvs[ 1 ] = []

        l = int(attributes.position.count)
        tempNormals = np.empty(l, THREE.Vector3) # []
        tempUVs = np.empty(l, THREE.Vector2) # []
        tempUVs2 = np.empty(l, THREE.Vector2) # []
        tempVertices = np.empty(l, THREE.Vector3)

        j = 0
        k = 0
        for i in range(0, len(positions), 3):
            # scope.vertices.append( Vector3( positions[ i ], positions[ i + 1 ], positions[ i + 2 ] ) )

            tempVertices[k] = Vector3( positions[ i ], positions[ i + 1 ], positions[ i + 2 ] )

            if normals is not None:
                # tempNormals.append( Vector3( normals[ i ], normals[ i + 1 ], normals[ i + 2 ] ) )
                tempNormals[k] = Vector3( normals[ i ], normals[ i + 1 ], normals[ i + 2 ] )

            if colors is not None:
                self.colors.append( Color( colors[ i ], colors[ i + 1 ], colors[ i + 2 ] ) )

            if uvs is not None:
                # tempUVs.append( Vector2( uvs[ j ], uvs[ j + 1 ] ) )
                tempUVs[k] = Vector2( uvs[ j ], uvs[ j + 1 ] )

            if uvs2 is not None:
                tempUVs2.append( Vector2( uvs2[ j ], uvs2[ j + 1 ] ) )

            j += 2
            k += 1

        self.vertices = tempVertices

        def addFace( a, b, c, materialIndex=None ):
            vertexNormals = [ tempNormals[ a ].clone(), tempNormals[ b ].clone(), tempNormals[ c ].clone() ] if normals is not None else []
            vertexColors = [ scope.colors[ a ].clone(), scope.colors[ b ].clone(), scope.colors[ c ].clone() ] if colors is not None else []

            face = Face3( a, b, c, vertexNormals, vertexColors, materialIndex )

            scope.faces.append( face )

            if uvs is not None:
                scope.faceVertexUvs[ 0 ].append( [ tempUVs[ a ].clone(), tempUVs[ b ].clone(), tempUVs[ c ].clone() ] )

            if uvs2 is not None:
                scope.faceVertexUvs[ 1 ].append( [ tempUVs2[ a ].clone(), tempUVs2[ b ].clone(), tempUVs2[ c ].clone() ] )

        groups = geometry.groups

        if len(groups) > 0:
            for i in range (len(groups)):
                group = groups[ i ]

                start = int(group.start)
                count = int(group.count)

                for j in range (start, start + count, 3):
                    if indices is not None:
                        addFace( indices[ j ], indices[ j + 1 ], indices[ j + 2 ], group.materialIndex )
                    else:
                        addFace( j, j + 1, j + 2, group.materialIndex )

        else:
            if indices is not None:
                for i in range(0, len(indices), 3 ):
                    addFace( indices[ i ], indices[ i + 1 ], indices[ i + 2 ] )

            else:
                for i in range (0, int(len(positions) / 3), 3 ):
                    addFace( i, i + 1, i + 2 )

        self.computeFaceNormals()

        if geometry.boundingBox != None:
            self.boundingBox = geometry.boundingBox.clone()

        if geometry.boundingSphere != None:
            self.boundingSphere = geometry.boundingSphere.clone()

        return self

    def center(self):
        self.computeBoundingBox()

        offset = self.boundingBox.getCenter().negate()

        self.translate( offset.x, offset.y, offset.z )

        return offset

    def normalize(self):
        self.computeBoundingSphere()

        center = self.boundingSphere.center
        radius = self.boundingSphere.radius

        s = 1 if radius == 0 else 1.0 / radius

        matrix = Matrix4()
        matrix.set(
            s, 0, 0, - s * center.x,
            0, s, 0, - s * center.y,
            0, 0, s, - s * center.z,
            0, 0, 0, 1
        )

        self.applyMatrix( matrix )

        return self

    def computeFaceNormals(self):
        cb = Vector3()
        ab = Vector3()

        for face in self.faces:
            vA = self.vertices[ face.a ]
            vB = self.vertices[ face.b ]
            vC = self.vertices[ face.c ]

            cb.subVectors( vC, vB )
            ab.subVectors( vA, vB )
            cb.cross( ab )

            cb.normalize()

            face.normal.copy( cb )

    def computeVertexNormals(self, areaWeighted=True ):
        vertices = self.vertices[:]

        for v in range(len(self.vertices)):
            vertices[ v ] = Vector3()

        if areaWeighted:
            # // vertex normals weighted by triangle areas
            # // http:# //www.iquilezles.org/www/articles/normals/normals.htm

            cb = Vector3()
            ab = Vector3()

            for f in range(len(self.faces)):
                face = self.faces[ f ]

                vA = self.vertices[ face.a ]
                vB = self.vertices[ face.b ]
                vC = self.vertices[ face.c ]

                cb.subVectors( vC, vB )
                ab.subVectors( vA, vB )
                cb.cross( ab )

                vertices[ face.a ].add( cb )
                vertices[ face.b ].add( cb )
                vertices[ face.c ].add( cb )

        else:
            self.computeFaceNormals()

            for f in range(len(self.faces)):
                face = self.faces[ f ]

                vertices[ face.a ].add( face.normal )
                vertices[ face.b ].add( face.normal )
                vertices[ face.c ].add( face.normal )

        for v in range(len(self.vertices)):
            vertices[ v ].normalize()

        for f in range(len(self.faces)):
            face = self.faces[ f ]

            vertexNormals = face.vertexNormals

            if vertexNormals.length == 3:
                vertexNormals[ 0 ].copy( vertices[ face.a ] )
                vertexNormals[ 1 ].copy( vertices[ face.b ] )
                vertexNormals[ 2 ].copy( vertices[ face.c ] )
            else:
                vertexNormals[ 0 ] = vertices[ face.a ].clone()
                vertexNormals[ 1 ] = vertices[ face.b ].clone()
                vertexNormals[ 2 ] = vertices[ face.c ].clone()

        if len(self.faces) > 0:
            self.normalsNeedUpdate = True

    def computeFlatVertexNormals(self):
        self.computeFaceNormals()

        for f in range(len(self.faces)):
            face = self.faces[ f ]

            vertexNormals = face.vertexNormals

            if vertexNormals.length == 3:
                vertexNormals[ 0 ].copy( face.normal )
                vertexNormals[ 1 ].copy( face.normal )
                vertexNormals[ 2 ].copy( face.normal )
            else:
                vertexNormals[ 0 ] = face.normal.clone()
                vertexNormals[ 1 ] = face.normal.clone()
                vertexNormals[ 2 ] = face.normal.clone()

        if len(self.faces) > 0:
            self.normalsNeedUpdate = True

    def computeMorphNormals(self):
        # // save original normals
        # // - create temp variables on first access
        # //   otherwise just copy (for faster repeated calls)

        for f in range(len(self.faces)):
            face = self.faces[ f ]

            if not face.__originalFaceNormal:
                face.__originalFaceNormal = face.normal.clone()
            else:
                face.__originalFaceNormal.copy( face.normal )

            if not face.__originalVertexNormals:
                face.__originalVertexNormals = []

            for i in range(len(face.vertexNormals)):
                if not face.__originalVertexNormals[ i ]:
                    face.__originalVertexNormals[ i ] = face.vertexNormals[ i ].clone()
                else:
                    face.__originalVertexNormals[ i ].copy( face.vertexNormals[ i ] )

        # // use temp geometry to compute face and vertex normals for each morph

        tmpGeo = Geometry()
        tmpGeo.faces = self.faces

        for i in range(len(self.morphTargets)):
            # // create on first access

            if not self.morphNormals[ i ]:
                self.morphNormals[ i ] = {}
                self.morphNormals[ i ].faceNormals = []
                self.morphNormals[ i ].vertexNormals = []

                dstNormalsFace = self.morphNormals[ i ].faceNormals
                dstNormalsVertex = self.morphNormals[ i ].vertexNormals

                for f in range(len(self.faces)):
                    faceNormal = Vector3()
                    vertexNormals = { 'a': Vector3(), 'b': Vector3(), 'c': Vector3() }

                    dstNormalsFace.append( faceNormal )
                    dstNormalsVertex.append( vertexNormals )

            morphNormals = self.morphNormals[ i ]

            # // set vertices to morph target

            tmpGeo.vertices = self.morphTargets[ i ].vertices

            # // compute morph normals

            tmpGeo.computeFaceNormals()
            tmpGeo.computeVertexNormals()

            # // store morph normals

            for f in range(len(self.faces)):
                face = self.faces[ f ]

                faceNormal = morphNormals.faceNormals[ f ]
                vertexNormals = morphNormals.vertexNormals[ f ]

                faceNormal.copy( face.normal )

                vertexNormals.a.copy( face.vertexNormals[ 0 ] )
                vertexNormals.b.copy( face.vertexNormals[ 1 ] )
                vertexNormals.c.copy( face.vertexNormals[ 2 ] )

        # // restore original normals

        for f in range(len(self.faces)):
            face = self.faces[ f ]

            face.normal = face.__originalFaceNormal
            face.vertexNormals = face.__originalVertexNormals

    def computeLineDistances(self):
        d = 0
        vertices = self.vertices

        for i in range(len(vertices)):
            if i > 0:
                d += vertices[ i ].distanceTo( vertices[ i - 1 ] )

            self.lineDistances[ i ] = d

    def computeBoundingBox(self):
        if self.boundingBox == None:
            self.boundingBox = Box3()

        self.boundingBox.setFromPoints( self.vertices )

    def computeBoundingSphere(self):
        if self.boundingSphere == None:
            self.boundingSphere = Sphere()

        self.boundingSphere.setFromPoints( self.vertices )

    def merge(self, geometry, matrix=None, materialIndexOffset=None ):
        if not ( geometry and geometry.my_class(isGeometry) ):
            raise RuntimeError( 'THREE.Geometry.merge(): geometry not an instance of THREE.Geometry.', geometry )

        vertexOffset = len(self.vertices)
        vertices1 = self.vertices
        vertices2 = geometry.vertices
        faces1 = self.faces
        faces2 = geometry.faces
        uvs1 = self.faceVertexUvs[ 0 ]
        uvs2 = geometry.faceVertexUvs[ 0 ]
        colors1 = self.colors
        colors2 = geometry.colors

        normalMatrix = Matrix3().getNormalMatrix( matrix ) if matrix is not None else None

        # // vertices

        for i in range(len(vertices2)):
            vertex = vertices2[ i ]

            vertexCopy = vertex.clone()

            if matrix is not None:
                vertexCopy.applyMatrix4( matrix )

            vertices1.append( vertexCopy )

        # // colors

        for i in range(len(colors2)):
            colors1.append( colors2[ i ].clone() )

        # // faces

        for i in range(len(faces2)):
            face = faces2[ i ]
            faceVertexNormals = face.vertexNormals
            faceVertexColors = face.vertexColors

            faceCopy = Face3( face.a + vertexOffset, face.b + vertexOffset, face.c + vertexOffset )
            faceCopy.normal.copy( face.normal )

            if normalMatrix is not None:
                faceCopy.normal.applyMatrix3( normalMatrix ).normalize()

            for j in range(len(faceVertexNormals)):
                normal = faceVertexNormals[ j ].clone()

                if normalMatrix is not None:
                    normal.applyMatrix3( normalMatrix ).normalize()

                faceCopy.vertexNormals.append( normal )

            faceCopy.color.copy( face.color )

            for j in range(len(faceVertexColors)):
                color = faceVertexColors[ j ]
                faceCopy.vertexColors.append( color.clone() )

            if face.materialIndex is not None and materialIndexOffset is not None:
                faceCopy.materialIndex = face.materialIndex + materialIndexOffset
            elif face.materialIndex is not None:
                faceCopy.materialIndex = face.materialIndex
            elif materialIndexOffset is not None:
                faceCopy.materialIndex = materialIndexOffset

            faces1.append( faceCopy )

        # // uvs

        for i in range(len(uvs2)):
            uv = uvs2[ i ]
            uvCopy = []

            if uv is None:
                continue

            for j in range(len(uv)):
                uvCopy.append( uv[ j ].clone() )

            uvs1.append( uvCopy )

    def mergeMesh(self, mesh ):
        if not ( mesh and mesh.my_class(isMesh) ):
            raise RuntimeError( 'THREE.Geometry.mergeMesh(): mesh not an instance of THREE.Mesh.', mesh )
            return

        if mesh.matrixAutoUpdate:
            mesh.updateMatrix()

        self.merge( mesh.geometry, mesh.matrix )

    """
    /*
     * Checks for duplicate vertices with hashmap.
     * Duplicated vertices are removed
     * and faces' vertices are updated.
     */
    """
    def mergeVertices(self):
        verticesMap = {}     # // Hashmap for looking up vertices by position coordinates (and making sure they are unique)
        unique = []
        changes = []

        precisionPoints = 4     # // number of decimal points, e.g. 4 for epsilon of 0.0001
        precision = math.pow( 10, precisionPoints )

        for i in range(len(self.vertices)):
            v = self.vertices[ i ]
            key = "%d_%d_%d" % (round( v.np[0] * precision ), round( v.np[1] * precision ), round( v.np[2] * precision ))

            if key not in verticesMap:
                verticesMap[ key ] = i
                unique.append( self.vertices[ i ] )
                changes.append(len(unique) - 1)
            else:
                # //console.log('Duplicate vertex found. ', i, ' could be using ', verticesMap[key])
                changes.append(changes[ verticesMap[ key ] ])

        # // if faces are completely degenerate after merging vertices, we
        # // have to remove them from the geometry.
        faceIndicesToRemove = []

        for i in range(len(self.faces)):
            face = self.faces[ i ]

            face.a = changes[ face.a ]
            face.b = changes[ face.b ]
            face.c = changes[ face.c ]

            indices = [ face.a, face.b, face.c ]

            # // if any duplicate vertices are found in a Face3
            # // we have to remove the face as nothing can be saved
            for n in range(3):
                if indices[ n ] == indices[ ( n + 1 ) % 3 ]:
                    faceIndicesToRemove.append( i )
                    break

        for i in range(len(faceIndicesToRemove) - 1, -1, -1):
            idx = faceIndicesToRemove[ i ]

            del self.faces[idx]

            for j in range(len(self.faceVertexUvs)):
                del self.faceVertexUvs[ j ][idx]

        # // Use unique set of vertices

        diff = len(self.vertices) - len(unique)
        self.vertices = np.array(unique, object)
        return diff

    def sortFacesByMaterialIndex(self):
        faces = self.faces
        length = len(faces)

        # // tag faces

        for i in range(length):
            faces[ i ]._id = i

        # // sort faces

        def materialIndexSort( a ):
            return a.materialIndex

        faces.sort( key=materialIndexSort )

        # // sort uvs

        uvs1 = self.faceVertexUvs[ 0 ]
        if uvs1 and len(uvs1) == length:
            newUvs1 = []

        if len(self.faceVertexUvs) > 1:
            uvs2 = self.faceVertexUvs[ 1 ]

            if uvs2 and len(uvs2) == length:
                newUvs2 = []
        else:
            newUvs2 = None

        for face in faces:
            id = face._id

            if newUvs1 is not None:
                newUvs1.append( uvs1[ id ] )
            if newUvs2 is not None:
                newUvs2.append( uvs2[ id ] )

        if newUvs1 is not None:
            self.faceVertexUvs[ 0 ] = newUvs1
        if newUvs2 is not None:
            self.faceVertexUvs[ 1 ] = newUvs2

    def toJSON(self):
        data = {
            'metadata': {
                'version': '4.5',
                'type': 'Geometry',
                'generator': 'Geometry.toJSON'
            }
        }

        def setBit( value, position, enabled ):
            return value | ( 1 << position ) if enabled else value & ( ~ ( 1 << position ) )

        def getNormalIndex( normal ):
            hash = normal.x.toString() + normal.y.toString() + normal.z.toString()

            if normalsHash[ hash ] != None:
                return normalsHash[ hash ]

            normalsHash[ hash ] = len(normals) / 3
            normals.extend([ normal.x, normal.y, normal.z ])

            return normalsHash[ hash ]

        def getColorIndex( color ):
            hash = color.r.toString() + color.g.toString() + color.b.toString()

            if colorsHash[ hash ] != None:
                return colorsHash[ hash ]

            colorsHash[ hash ] = len(colors)
            colors.append( color.getHex() )

            return colorsHash[ hash ]

        def getUvIndex( uv ):
            hash = uv.x.toString() + uv.y.toString()

            if uvsHash[ hash ] != None:
                return uvsHash[ hash ]

            uvsHash[ hash ] = len(uvs) / 2
            uvs.extend([ uv.x, uv.y ])

            return uvsHash[ hash ]


        # // standard Geometry serialization

        data.uuid = self.uuid
        data.type = self.type
        if self.name != '':
            data.name = self.name

        if self.parameters != None:
            parameters = self.parameters

            for key in parameters:
                if parameters[ key ] != None:
                    data[ key ] = parameters[ key ]

            return data

        vertices = []

        for i in range(len(self.vertices)):
            vertex = self.vertices[ i ]
            vertices.extend([ vertex.x, vertex.y, vertex.z ])

        faces = []
        normals = []
        normalsHash = {}
        colors = []
        colorsHash = {}
        uvs = []
        uvsHash = {}

        for i in range(len(self.faces)):
            face = self.faces[ i ]

            hasMaterial = True
            hasFaceUv = False     # // deprecated
            hasFaceVertexUv = self.faceVertexUvs[ 0 ][ i ] != None
            hasFaceNormal = face.normal.length() > 0
            hasFaceVertexNormal = len(face.vertexNormals) > 0
            hasFaceColor = face.color.r != 1 or face.color.g != 1 or face.color.b != 1
            hasFaceVertexColor = face.vertexColors.length > 0

            faceType = 0

            faceType = setBit( faceType, 0, 0 )     # // isQuad
            faceType = setBit( faceType, 1, hasMaterial )
            faceType = setBit( faceType, 2, hasFaceUv )
            faceType = setBit( faceType, 3, hasFaceVertexUv )
            faceType = setBit( faceType, 4, hasFaceNormal )
            faceType = setBit( faceType, 5, hasFaceVertexNormal )
            faceType = setBit( faceType, 6, hasFaceColor )
            faceType = setBit( faceType, 7, hasFaceVertexColor )

            faces.append( faceType )
            faces.extend([ face.a, face.b, face.c ])
            faces.append( face.materialIndex )

            if hasFaceVertexUv:
                faceVertexUvs = self.faceVertexUvs[ 0 ][ i ]

                faces.extend([
                    getUvIndex( faceVertexUvs[ 0 ] ),
                    getUvIndex( faceVertexUvs[ 1 ] ),
                    getUvIndex( faceVertexUvs[ 2 ] )
                    ])

            if hasFaceNormal:
                faces.append( getNormalIndex( face.normal ) )

            if hasFaceVertexNormal:
                vertexNormals = face.vertexNormals

                faces.extend([
                    getNormalIndex( vertexNormals[ 0 ] ),
                    getNormalIndex( vertexNormals[ 1 ] ),
                    getNormalIndex( vertexNormals[ 2 ] )
                    ])

            if hasFaceColor:
                faces.append( getColorIndex( face.color ) )

            if hasFaceVertexColor:
                vertexColors = face.vertexColors

                faces.extend([
                    getColorIndex( vertexColors[ 0 ] ),
                    getColorIndex( vertexColors[ 1 ] ),
                    getColorIndex( vertexColors[ 2 ] )
                    ])

        data.data = {}

        data.data.vertices = vertices
        data.data.normals = normals
        if len(colors) > 0:
            data.data.colors = colors
        if len(uvs) > 0:
            data.data.uvs = [ uvs ]     # // temporal backward compatibility
        data.data.faces = faces

        return data

    def clone(self):
        return Geometry().copy( self )

    def copy(self, source ):
        # // reset

        self.vertices = []
        self.colors = []
        self.faces = []
        self.faceVertexUvs = [[]]
        self.morphTargets = []
        self.morphNormals = []
        self.skinWeights = []
        self.skinIndices = []
        self.lineDistances = []
        self.boundingBox = None
        self.boundingSphere = None

        # // name

        self.name = source.name

        # // vertices

        vertices = source.vertices

        for i in range(len(vertices)):
            self.vertices.append( vertices[ i ].clone() )

        # // colors

        colors = source.colors

        for i in range(len(colors)):
            self.colors.append( colors[ i ].clone() )

        # // faces

        faces = source.faces

        for i in range(len(faces)):
            self.faces.append( faces[ i ].clone() )

        # // face vertex uvs

        for i in range(len(source.faceVertexUvs)):
            faceVertexUvs = source.faceVertexUvs[ i ]

            if self.faceVertexUvs[ i ] == None:
                self.faceVertexUvs[ i ] = []

            for j in range(len(faceVertexUvs)):
                uvs = faceVertexUvs[ j ], uvsCopy = []

                for k in range(len(uvs)):
                    uv = uvs[ k ]

                    uvsCopy.append( uv.clone() )

                self.faceVertexUvs[ i ].append( uvsCopy )

        # // morph targets

        morphTargets = source.morphTargets

        for i in range(len(morphTargets)):
            morphTarget = {}
            morphTarget.name = morphTargets[ i ].name

            # // vertices

            if morphTargets[ i ].vertices != None:
                morphTarget.vertices = []

                for j in range(len(morphTargets[ i ].vertices)):
                    morphTarget.vertices.extend([ morphTargets[ i ].vertices[ j ].clone() ])

            # // normals

            if morphTargets[ i ].normals != None:
                morphTarget.normals = []

                for j in range(len(morphTargets[ i ].normals)):
                    morphTarget.normals.extend([ morphTargets[ i ].normals[ j ].clone() ])

            self.morphTargets.append( morphTarget )

        # // morph normals

        morphNormals = source.morphNormals

        for i in range(len(morphNormals)):
            morphNormal = {}

            # // vertex normals

            if morphNormals[ i ].vertexNormals != None:
                morphNormal.vertexNormals = []

                for j in range(len(morphNormals[ i ].vertexNormals)):
                    srcVertexNormal = morphNormals[ i ].vertexNormals[ j ]
                    destVertexNormal = {}

                    destVertexNormal.a = srcVertexNormal.a.clone()
                    destVertexNormal.b = srcVertexNormal.b.clone()
                    destVertexNormal.c = srcVertexNormal.c.clone()

                    morphNormal.vertexNormals.append( destVertexNormal )

            # // face normals

            if morphNormals[ i ].faceNormals != None:
                morphNormal.faceNormals = []

                for j in range(len(morphNormals[ i ].faceNormals)):
                    morphNormal.faceNormals.append( morphNormals[ i ].faceNormals[ j ].clone() )

            self.morphNormals.append( morphNormal )

        # // skin weights

        skinWeights = source.skinWeights

        for i in range(len(skinWeights)):
            self.skinWeights.append( skinWeights[ i ].clone() )

        # // skin indices

        skinIndices = source.skinIndices

        for i in range(len(skinIndices)):
            self.skinIndices.append( skinIndices[ i ].clone() )

        # // line distances

        lineDistances = source.lineDistances

        for i in range(len(lineDistances)):
            self.lineDistances.append( lineDistances[ i ] )

        # // bounding box

        boundingBox = source.boundingBox

        if boundingBox != None:
            self.boundingBox = boundingBox.clone()

        # // bounding sphere

        boundingSphere = source.boundingSphere

        if boundingSphere != None:
            self.boundingSphere = boundingSphere.clone()

        # // update flags

        self.elementsNeedUpdate = source.elementsNeedUpdate
        self.verticesNeedUpdate = source.verticesNeedUpdate
        self.uvsNeedUpdate = source.uvsNeedUpdate
        self.normalsNeedUpdate = source.normalsNeedUpdate
        self.colorsNeedUpdate = source.colorsNeedUpdate
        self.lineDistancesNeedUpdate = source.lineDistancesNeedUpdate
        self.groupsNeedUpdate = source.groupsNeedUpdate

        return self

    def onDispose(self, callback):
        self.callback = callback

    def dispose(self):
        if self.callback:
            return self.callback(self)

