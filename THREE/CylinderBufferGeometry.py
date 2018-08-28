"""
/**
 * @author mrdoob / http:# //mrdoob.com/
 * @author Mugen87 / https:# //github.com/Mugen87
 */
"""

from THREE.Geometry import *
from THREE.BufferGeometry import *


# // CylinderGeometry

class CylinderGeometry(Geometry):
    def __init__(self, radiusTop=50, radiusBottom=20, height=100, radialSegments=8, heightSegments=1, openEnded=False, thetaStart=0, thetaLength=2*math.pi ):
        super().__init__()

        self.type = 'CylinderGeometry'

        self.parameters = {
            'radiusTop': radiusTop,
            'radiusBottom': radiusBottom,
            'height': height,
            'radialSegments': radialSegments,
            'heightSegments': heightSegments,
            'openEnded': openEnded,
            'thetaStart': thetaStart,
            'thetaLength': thetaLength
        }

        self.fromBufferGeometry( CylinderBufferGeometry( radiusTop, radiusBottom, height, radialSegments, heightSegments, openEnded, thetaStart, thetaLength ) )
        self.mergeVertices()

# // CylinderBufferGeometry

class CylinderBufferGeometry(BufferGeometry):
    def __init__(self, radiusTop=50, radiusBottom=20, height=100, radialSegments=8, heightSegments=1, openEnded=False, thetaStart=0, thetaLength=2*math.pi ):
        super().__init__()
        self.type = 'CylinderBufferGeometry'

        self.parameters = {
            'radiusTop': radiusTop,
            'radiusBottom': radiusBottom,
            'height': height,
            'radialSegments': radialSegments,
            'heightSegments': heightSegments,
            'openEnded': openEnded,
            'thetaStart': thetaStart,
            'thetaLength': thetaLength
        }

        self.radiusTop = radiusTop 
        self.radiusBottom = radiusBottom 
        self.height = height 

        self.radialSegments = math.floor( radialSegments )
        self.heightSegments = math.floor( heightSegments ) 

        self.openEnded = openEnded 
        self.thetaStart = thetaStart 
        self.thetaLength = thetaLength 

        # // buffers

        indices = []
        vertices = []
        normals = []
        uvs = []

        # // helper variables

        index = 0
        indexArray = []
        halfHeight = height / 2
        groupStart = 0

        # // generate geometry
        def generateTorso():
            nonlocal radiusTop, radiusBottom, height, radialSegments, heightSegments, openEnded, thetaStart, thetaLength
            nonlocal groupStart, index, halfHeight
            
            normal = Vector3()
            vertex = Vector3()

            groupCount = 0

            # // self will be used to calculate the normal
            slope = ( radiusBottom - radiusTop ) / height

            # // generate vertices, normals and uvs
            for y in range(heightSegments+1):
                indexRow = []

                v = y / heightSegments

                # // calculate the radius of the current row

                radius = v * ( radiusBottom - radiusTop ) + radiusTop

                for x in range(radialSegments+1):
                    u = x / radialSegments

                    theta = u * thetaLength + thetaStart

                    sinTheta = math.sin( theta )
                    cosTheta = math.cos( theta )

                    # // vertex

                    vertex.x = radius * sinTheta
                    vertex.y = - v * height + halfHeight
                    vertex.z = radius * cosTheta
                    vertices.extend([ vertex.x, vertex.y, vertex.z ])

                    # // normal

                    normal.set( sinTheta, slope, cosTheta ).normalize()
                    normals.extend([ normal.x, normal.y, normal.z ])

                    # // uv

                    uvs.extend([ u, 1 - v ])

                    # // save index of vertex in respective row

                    indexRow.append( index )
                    index += 1

                # // now save vertices of the row in our index array

                indexArray.append( indexRow )

            # // generate indices

            for x in range(radialSegments):
                for y in range(heightSegments):
                    # // we use the index array to access the correct indices

                    a = indexArray[ y ][ x ]
                    b = indexArray[ y + 1 ][ x ]
                    c = indexArray[ y + 1 ][ x + 1 ]
                    d = indexArray[ y ][ x + 1 ]

                    # // faces

                    indices.extend([ a, b, d ])
                    indices.extend([ b, c, d ])

                    # // update group counter

                    groupCount += 6

            # // add a group to the geometry. self will ensure multi material support

            self.addGroup( groupStart, groupCount, 0 )

            # // calculate start value for groups

            groupStart += groupCount

        def generateCap( top ):
            nonlocal radiusTop, radiusBottom, height, radialSegments, heightSegments, openEnded, thetaStart, thetaLength
            nonlocal groupStart, index, halfHeight

            uv = Vector2()
            vertex = Vector3()

            groupCount = 0

            radius = radiusTop if ( top ) else radiusBottom
            sign = 1 if ( top ) else - 1

            # // save the index of the first center vertex
            centerIndexStart = index

            # // first we generate the center vertex data of the cap.
            # // because the geometry needs one set of uvs per face,
            # // we must generate a center vertex per face/segment

            for x in range(1, radialSegments+1):
                # // vertex

                vertices.extend([ 0, halfHeight * sign, 0 ])

                # // normal

                normals.extend([ 0, sign, 0 ])

                # // uv

                uvs.extend([ 0.5, 0.5 ])

                # // increase index

                index += 1

            # // save the index of the last center vertex

            centerIndexEnd = index

            # // now we generate the surrounding vertices, normals and uvs

            for x in range(radialSegments+1):
                u = x / radialSegments
                theta = u * thetaLength + thetaStart

                cosTheta = math.cos( theta )
                sinTheta = math.sin( theta )

                # // vertex

                vertex.x = radius * sinTheta
                vertex.y = halfHeight * sign
                vertex.z = radius * cosTheta
                vertices.extend([ vertex.x, vertex.y, vertex.z ])

                # // normal

                normals.extend([ 0, sign, 0 ])

                # // uv

                uv.x = ( cosTheta * 0.5 ) + 0.5
                uv.y = ( sinTheta * 0.5 * sign ) + 0.5
                uvs.extend([ uv.x, uv.y ])

                # // increase index

                index += 1

            # // generate indices

            for x in range(radialSegments):
                c = centerIndexStart + x
                i = centerIndexEnd + x

                if top:
                # // face top
                    indices.extend([i, i + 1, c])
                else:
                    # // face bottom
                    indices.extend([i + 1, i, c])

                groupCount += 3

            # // add a group to the geometry. self will ensure multi material support
            self.addGroup(groupStart, groupCount, 1 if top else 2 )

            # // calculate start value for groups
            groupStart += groupCount

        generateTorso()

        if openEnded == False:
            if radiusTop > 0:
                generateCap( True )
            if radiusBottom > 0:
                generateCap( False )

        # // build geometry

        self.setIndex( indices )
        self.addAttribute( 'position', Float32BufferAttribute( vertices, 3 ) )
        self.addAttribute( 'normal', Float32BufferAttribute( normals, 3 ) )
        self.addAttribute( 'uv', Float32BufferAttribute( uvs, 2 ) )
