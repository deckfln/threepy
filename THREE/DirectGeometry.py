"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 */
"""
from THREE.Vector2 import *


class _group:
    def __init__(self, start, materialIndex):
        self.start = start
        self.materialIndex = materialIndex


class DirectGeometry:
    def __init__(self):
        self.indices = []
        self.vertices = []
        self.normals = []
        self.colors = []
        self.uvs = []
        self.uvs2 = []

        self.groups = []

        self.morphTargets = {}

        self.skinWeights = []
        self.skinIndices = []

        # // self.lineDistances = []

        self.boundingBox = None
        self.boundingSphere = None

        # // update flags

        self.verticesNeedUpdate = False
        self.normalsNeedUpdate = False
        self.colorsNeedUpdate = False
        self.uvsNeedUpdate = False
        self.groupsNeedUpdate = False
        self.lineDistancesNeedUpdate = False

    def computeGroups(self, geometry ):
        groups = []
        materialIndex = None

        faces = geometry.faces

        group = None

        for i in range(len(faces)):
            face = faces[ i ]

            # // materials

            if face.materialIndex != materialIndex:
                materialIndex = face.materialIndex

                if group is not None:
                    group.count = ( i * 3 ) - group.start
                    groups.append( group )

                group = _group(i * 3, materialIndex)

        if group is not None:
            group.count = ( i * 3 ) - group.start
            groups.append( group )

        self.groups = groups

    def fromGeometry(self, geometry ):
        faces = geometry.faces
        vertices = geometry.vertices
        faceVertexUvs = geometry.faceVertexUvs

        hasFaceVertexUv = faceVertexUvs[ 0 ] and len(faceVertexUvs[ 0 ]) > 0
        hasFaceVertexUv2 = len(faceVertexUvs) > 1 and len(faceVertexUvs[ 1 ]) > 0

        # // morphs

        morphTargets = geometry.morphTargets
        morphTargetsLength =len(morphTargets)

        if morphTargetsLength > 0:
            morphTargetsPosition = []

            for i in range(morphTargetsLength):
                morphTargetsPosition[ i ] = []

            self.morphTargets.position = morphTargetsPosition

        morphNormals = geometry.morphNormals
        morphNormalsLength = len(morphNormals)

        if morphNormalsLength > 0:
            morphTargetsNormal = []

            for i in range(morphNormalsLength):
                morphTargetsNormal[ i ] = []

            self.morphTargets.normal = morphTargetsNormal

        # // skins

        skinIndices = geometry.skinIndices
        skinWeights = geometry.skinWeights

        hasSkinIndices = len(skinIndices) == len(vertices)
        hasSkinWeights = len(skinWeights) == len(vertices)

        # //

        for i in range(len(faces)):
            face = faces[ i ]

            self.vertices.extend([ vertices[ face.a ], vertices[ face.b ], vertices[ face.c ] ])

            vertexNormals = face.vertexNormals

            if len(vertexNormals) == 3:
                self.normals.extend([ vertexNormals[ 0 ], vertexNormals[ 1 ], vertexNormals[ 2 ] ])
            else:
                normal = face.normal

                self.normals.extend([ normal, normal, normal ])

            vertexColors = face.vertexColors

            if len(vertexColors) == 3:
                self.colors.extend([ vertexColors[ 0 ], vertexColors[ 1 ], vertexColors[ 2 ] ])
            else:
                color = face.color

                self.colors.extend([ color, color, color ])

            if hasFaceVertexUv == True:
                vertexUvs = faceVertexUvs[ 0 ][ i ]

                if vertexUvs is not None:
                    self.uvs.extend([ vertexUvs[ 0 ], vertexUvs[ 1 ], vertexUvs[ 2 ] ])
                else:
                    print( 'THREE.DirectGeometry.fromGeometry(): Undefined vertexUv ', i )
                    self.uvs.extend([ Vector2(), Vector2(), Vector2() ])

            if hasFaceVertexUv2 == True:
                vertexUvs = faceVertexUvs[ 1 ][ i ]

                if vertexUvs is not None:
                    self.uvs2.push( vertexUvs[ 0 ], vertexUvs[ 1 ], vertexUvs[ 2 ] )
                else:
                    print( 'THREE.DirectGeometry.fromGeometry(): Undefined vertexUv2 ', i )
                    self.uvs2.extend([ Vector2(), Vector2(), Vector2() ])

            # // morphs

            for j in range(morphTargetsLength):
                morphTarget = morphTargets[ j ].vertices

                morphTargetsPosition[ j ].extend([ morphTarget[ face.a ], morphTarget[ face.b ], morphTarget[ face.c ] ])

            for j in range(morphNormalsLength):
                morphNormal = morphNormals[ j ].vertexNormals[ i ]

                morphTargetsNormal[ j ].extend([ morphNormal.a, morphNormal.b, morphNormal.c ])

            # // skins

            if hasSkinIndices:
                self.skinIndices.extend([ skinIndices[ face.a ], skinIndices[ face.b ], skinIndices[ face.c ] ])

            if hasSkinWeights:
                self.skinWeights.extend([ skinWeights[ face.a ], skinWeights[ face.b ], skinWeights[ face.c ] ])

        self.computeGroups( geometry )

        self.verticesNeedUpdate = geometry.verticesNeedUpdate
        self.normalsNeedUpdate = geometry.normalsNeedUpdate
        self.colorsNeedUpdate = geometry.colorsNeedUpdate
        self.uvsNeedUpdate = geometry.uvsNeedUpdate
        self.groupsNeedUpdate = geometry.groupsNeedUpdate

        return self
