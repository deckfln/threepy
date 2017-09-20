"""
	/**
	 * @author mrdoob / http://mrdoob.com/
	 * @author Mugen87 / https://github.com/Mugen87
	 */
"""
import math
from THREE.Vector3 import *
from THREE.BufferGeometry import *

        
class BoxBufferGeometry(BufferGeometry):
    def __init__(self, width, height, depth, widthSegments, heightSegments, depthSegments ):
        super().__init__()

        self.type = 'BoxBufferGeometry'

        self.parameters = {
            'width': width,
            'height': height,
            'depth': depth,
            'widthSegments': widthSegments,
            'heightSegments': heightSegments,
            'depthSegments': depthSegments
        }

        # // segments
        widthSegments = math.floor( widthSegments ) or 1
        heightSegments = math.floor( heightSegments ) or 1
        depthSegments = math.floor( depthSegments ) or 1

        # // buffers
        self.indices = []
        self.vertices = []
        self.normals = []
        self.uvs = []

        # // helper variables
        self.numberOfVertices = 0
        self.groupStart = 0

        # // build each side of the box geometry
        self.buildPlane( 'z', 'y', 'x', - 1, - 1, depth, height,   width,  depthSegments, heightSegments, 0 ); # // px
        self.buildPlane( 'z', 'y', 'x',   1, - 1, depth, height, - width,  depthSegments, heightSegments, 1 ); # // nx
        self.buildPlane( 'x', 'z', 'y',   1,   1, width, depth,    height, widthSegments, depthSegments,  2 ); # // py
        self.buildPlane( 'x', 'z', 'y',   1, - 1, width, depth,  - height, widthSegments, depthSegments,  3 ); # // ny
        self.buildPlane( 'x', 'y', 'z',   1, - 1, width, height,   depth,  widthSegments, heightSegments, 4 ); # // pz
        self.buildPlane( 'x', 'y', 'z', - 1, - 1, width, height, - depth,  widthSegments, heightSegments, 5 ); # // nz

        # // build geometry
        self.setIndex( self.indices )
        self.addAttribute( 'position', Float32BufferAttribute( self.vertices, 3 ) )
        self.addAttribute( 'normal', Float32BufferAttribute( self.normals, 3 ) )
        self.addAttribute( 'uv', Float32BufferAttribute( self.uvs, 2 ) )

        # // free memory
        self.indices = self.vertices = self.normals = self.uvs = None

    def buildPlane(self, u, v, w, udir, vdir, width, height, depth, gridX, gridY, materialIndex ):
        segmentWidth = width / gridX
        segmentHeight = height / gridY

        widthHalf = width / 2
        heightHalf = height / 2
        depthHalf = depth / 2

        gridX1 = gridX + 1
        gridY1 = gridY + 1

        vertexCounter = 0
        groupCount = 0

        vector = Vector3()

        # // generate vertices, normals and uvs
        for iy in range(gridY1):
            y = iy * segmentHeight - heightHalf
            for ix in range(gridX1):
                x = ix * segmentWidth - widthHalf

                # // set values to correct vector component
                vector.setComponent(u, x * udir)
                vector.setComponent(v, y * vdir)
                vector.setComponent(w, depthHalf)

                # // now apply vector to vertex buffer
                self.vertices.extend([ vector.x, vector.y, vector.z ])

                # // set values to correct vector component
                vector.setComponent(u, 0)
                vector.setComponent(v, 0)
                vector.setComponent(w, -1)
                if depth > 0:
                    vector.setComponent(w, 1)

                # // now apply vector to normal buffer
                self.normals.extend( [vector.x, vector.y, vector.z] )

                # // uvs
                self.uvs.append( ix / gridX )
                self.uvs.append( 1 - ( iy / gridY ) )

                # // counters
                vertexCounter += 1

        # // indices

        # // 1. you need three indices to draw a single face
        # // 2. a single segment consists of two faces
        # // 3. so we need to generate six (2*3) indices per segment

        for iy in range(gridY):
            for ix in range(gridX):
                a = self.numberOfVertices + ix + gridX1 * iy
                b = self.numberOfVertices + ix + gridX1 * ( iy + 1 )
                c = self.numberOfVertices + ( ix + 1 ) + gridX1 * ( iy + 1 )
                d = self.numberOfVertices + ( ix + 1 ) + gridX1 * iy

                # // faces
                self.indices.extend([ a, b, d ])
                self.indices.extend([ b, c, d ])

                # // increase counter
                groupCount += 6

        # // add a group to the geometry. self will ensure multi material support
        self.addGroup( self.groupStart, groupCount, materialIndex )

        # // calculate start value for groups
        self.groupStart += groupCount

        # // update total number of vertices
        self.numberOfVertices += vertexCounter
