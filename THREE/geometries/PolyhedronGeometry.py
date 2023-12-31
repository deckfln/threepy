"""
/**
 * @author clockworkgeek / https:# //github.com/clockworkgeek
 * @author timothypratley / https:# //github.com/timothypratley
 * @author WestLangley / http:# //github.com/WestLangley
 * @author Mugen87 / https:# //github.com/Mugen87
 */
"""
from THREE.core.Geometry import *
from THREE.core.BufferGeometry import *


# // PolyhedronGeometry

class PolyhedronGeometry(Geometry):
    def __init__(self, vertices, indices, radius, detail ):
        super().__init__()

        self.type = 'PolyhedronGeometry'

        self.parameters = {
            'vertices': vertices,
            'indices': indices,
            'radius': radius,
            'detail': detail
        }

        self.fromBufferGeometry( PolyhedronBufferGeometry( vertices, indices, radius, detail ) )
        self.mergeVertices()


# // PolyhedronBufferGeometry

class PolyhedronBufferGeometry(BufferGeometry):
    def __init__(self, vertices, indices, radius=1, detail=0 ):
        super().__init__( )

        self.type = 'PolyhedronBufferGeometry'

        self.parameters = {
            'vertices': vertices,
            'indices': indices,
            'radius': radius,
            'detail': detail
        }

        # // default buffer data

        vertexBuffer = []
        uvBuffer = []

        # // helper defs

        def subdivide( detail ):
            a = Vector3()
            b = Vector3()
            c = Vector3()

            # // iterate over all faces and apply a subdivison with the given detail value

            for i in range(0, len(indices), 3):
                # // get the vertices of the face

                getVertexByIndex( indices[ i + 0 ], a )
                getVertexByIndex( indices[ i + 1 ], b )
                getVertexByIndex( indices[ i + 2 ], c )

                # // perform subdivision

                subdivideFace( a, b, c, detail )

        def subdivideFace( a, b, c, detail ):
            cols = int(math.pow( 2, detail ))

            # // we use self multidimensional array as a data structure for creating the subdivision

            v = [[] for i in range(cols+1)]

            # // construct all of the vertices for self subdivision

            for i in range(cols+1):
                aj = a.clone().lerp( c, i / cols )
                bj = b.clone().lerp( c, i / cols )

                rows = cols - i

                v[i] = [ None for j in range(rows + 1) ]

                for j in range(rows+1):
                    if j == 0 and i == cols:
                        v[ i ][ j ] = aj
                    else:
                        v[ i ][ j ] = aj.clone().lerp( bj, j / rows )

            # // construct all of the faces

            for i in range(cols):
                for j in range(2 * ( cols - i ) - 1):
                    k = math.floor( j / 2 )

                    if j % 2 == 0:
                        pushVertex( v[ i ][ k + 1 ] )
                        pushVertex( v[ i + 1 ][ k ] )
                        pushVertex( v[ i ][ k ] )

                    else:
                        pushVertex( v[ i ][ k + 1 ] )
                        pushVertex( v[ i + 1 ][ k + 1 ] )
                        pushVertex( v[ i + 1 ][ k ] )

        def appplyRadius( radius ):
            vertex = Vector3()

            # // iterate over the entire buffer and apply the radius to each vertex

            for i in range(0, len(vertexBuffer), 3 ):
                vertex.x = vertexBuffer[ i + 0 ]
                vertex.y = vertexBuffer[ i + 1 ]
                vertex.z = vertexBuffer[ i + 2 ]

                vertex.normalize().multiplyScalar( radius )

                vertexBuffer[ i + 0 ] = vertex.x
                vertexBuffer[ i + 1 ] = vertex.y
                vertexBuffer[ i + 2 ] = vertex.z

        def generateUVs():
            vertex = Vector3()

            for i in range(0, len(vertexBuffer), 3 ):
                vertex.x = vertexBuffer[ i + 0 ]
                vertex.y = vertexBuffer[ i + 1 ]
                vertex.z = vertexBuffer[ i + 2 ]

                u = azimuth( vertex ) / 2 / math.pi + 0.5
                v = inclination( vertex ) / math.pi + 0.5
                uvBuffer.extend([ u, 1 - v ])

            correctUVs()

            correctSeam()

        def correctSeam():
            # // handle case when face straddles the seam, see #3269

            for i in range(0, len(uvBuffer), 6 ):
                # // uv data of a single face

                x0 = uvBuffer[ i + 0 ]
                x1 = uvBuffer[ i + 2 ]
                x2 = uvBuffer[ i + 4 ]

                mx = max( x0, x1, x2 )
                mn = min( x0, x1, x2 )

                # // 0.9 is somewhat arbitrary

                if mx > 0.9 and mn < 0.1:
                    if x0 < 0.2:
                        uvBuffer[ i + 0 ] += 1
                    if x1 < 0.2:
                        uvBuffer[ i + 2 ] += 1
                    if x2 < 0.2:
                        uvBuffer[ i + 4 ] += 1


        def pushVertex( vertex ):
            vertexBuffer.extend([ vertex.x, vertex.y, vertex.z ])

        def getVertexByIndex( index, vertex ):
            stride = index * 3

            vertex.x = vertices[ stride + 0 ]
            vertex.y = vertices[ stride + 1 ]
            vertex.z = vertices[ stride + 2 ]

        def correctUVs():
            a = Vector3()
            b = Vector3()
            c = Vector3()

            centroid = Vector3()

            uvA = Vector2()
            uvB = Vector2()
            uvC = Vector2()

            j = 0
            for i in range(0, len(vertexBuffer), 9):
                a.set( vertexBuffer[ i + 0 ], vertexBuffer[ i + 1 ], vertexBuffer[ i + 2 ] )
                b.set( vertexBuffer[ i + 3 ], vertexBuffer[ i + 4 ], vertexBuffer[ i + 5 ] )
                c.set( vertexBuffer[ i + 6 ], vertexBuffer[ i + 7 ], vertexBuffer[ i + 8 ] )

                uvA.set( uvBuffer[ j + 0 ], uvBuffer[ j + 1 ] )
                uvB.set( uvBuffer[ j + 2 ], uvBuffer[ j + 3 ] )
                uvC.set( uvBuffer[ j + 4 ], uvBuffer[ j + 5 ] )

                centroid.copy( a ).add( b ).add( c ).divideScalar( 3 )

                azi = azimuth( centroid )

                correctUV( uvA, j + 0, a, azi )
                correctUV( uvB, j + 2, b, azi )
                correctUV( uvC, j + 4, c, azi )

                j += 6

        def correctUV( uv, stride, vector, azimuth ):
            if ( azimuth < 0 ) and ( uv.x == 1 ):
                uvBuffer[ stride ] = uv.x - 1

            if ( vector.x == 0 ) and ( vector.z == 0 ):
                uvBuffer[ stride ] = azimuth / 2 / math.pi + 0.5


        # // Angle around the Y axis, counter-clockwise when looking from above.

        def azimuth( vector ):
            return math.atan2( vector.z, - vector.x )

        # // Angle above the XZ plane.

        def inclination( vector ):
            return math.atan2( - vector.y, math.sqrt( ( vector.x * vector.x ) + ( vector.z * vector.z ) ) )

        # // the subdivision creates the vertex buffer data

        subdivide( detail )

        # // all vertices should lie on a conceptual sphere with a given radius

        appplyRadius( radius )

        # // finally, create the uv data

        generateUVs()

        # // build non-indexed geometry

        self.addAttribute( 'position', Float32BufferAttribute( vertexBuffer, 3 ) )
        self.addAttribute( 'normal', Float32BufferAttribute( vertexBuffer, 3 ) )
        self.addAttribute( 'uv', Float32BufferAttribute( uvBuffer, 2 ) )

        if detail == 0:
            self.computeVertexNormals()    # // flat normals
        else:
            self.normalizeNormals()     # // smooth normals
