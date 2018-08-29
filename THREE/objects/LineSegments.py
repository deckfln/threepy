"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""
from THREE.objects.Line import *


class LineSegments(Line):
    isLineSegments = True
    
    def __init__(self, geometry=None, material=None ):
        super().__init__( geometry, material )
        self.set_class(isLineSegments)

        self.type = 'LineSegments'

    def computeLineDistances(self):
        start = Vector3()
        end = Vector3()
        geometry = self.geometry

        if geometry.is_class(isBufferGeometry):
            # we assume non-indexed geometry

            if geometry.index is None:
                positionAttribute = geometry.attributes.position
                lineDistances = []

                for i in range(0, positionAttribute.count, 2):
                    start.fromBufferAttribute(positionAttribute, i)
                    end.fromBufferAttribute(positionAttribute, i+1)

                    lineDistances[i] = 0 if i==0 else lineDistances[ i - 1 ]
                    lineDistances[i+1] = lineDistances[i] + start.distanceTo( end )

                geometry.addAttribute( 'lineDistance', Float32BufferAttribute( lineDistances, 1 ) )

            else:
                raise RuntimeWarning('THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.')

        elif geometry.is_class(isGeometry):
            vertices = geometry.vertices
            lineDistances = geometry.lineDistances

            lineDistances[ 0 ] = 0

            for i in range(0, len(vertices), 2):
                start.copy(vertices[i])
                end.copy(vertices[i + 1])

                lineDistances[i] = 0 if i == 0 else lineDistances[i - 1]
                lineDistances[i + 1] = lineDistances[i] + start.distanceTo(end)

        return self

