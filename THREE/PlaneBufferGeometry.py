"""
    /**
     * @author mrdoob / http://mrdoob.com/
     * @author Mugen87 / https://github.com/Mugen87
     */
"""
from THREE.Geometry import *
from THREE.BufferGeometry import *


# // PlaneGeometry

class PlaneGeometry(Geometry):
    def __init__(self, width, height, widthSegments, heightSegments ):
        super().__init__()
        self.type = 'PlaneGeometry'

        self.parameters = {
            'width': width,
            'height': height,
            'widthSegments': widthSegments,
            'heightSegments': heightSegments
        };

        self.fromBufferGeometry( PlaneBufferGeometry( width, height, widthSegments, heightSegments ) )
        self.mergeVertices()

# // PlaneBufferGeometry


class PlaneBufferGeometry(BufferGeometry):
    def __init__(self, width, height, widthSegments=1, heightSegments=1 ):
        """

        :param width:
        :param height:
        :param widthSegments:
        :param heightSegments:
        """
        super().__init__()
        self.parameters = {"width": width, "height": height, "widthSegments": widthSegments, "heightSegments": heightSegments}
        self.type = "PlaneBufferGeometry"

        width_half = width / 2
        height_half = height / 2
        gridX = int(widthSegments)
        gridY = int(heightSegments)
        gridX1 = gridX + 1
        gridY1 = gridY + 1
        segment_width = width / gridX
        segment_height = height / gridY
        indices = []
        vertices = []
        normals = []
        uvs = []
        # // generate vertices, normals and uvs
        for iy in range(gridY1):
            y = iy * segment_height - height_half
            for ix in range(gridX1):
                x = ix * segment_width - width_half
                vertices.extend([x, - y, 0])
                normals.extend([0, 0, 1])
                uvs.append(ix / gridX)
                uvs.append(1 - ( iy / gridY ))
        # // indices
        for iy in range(gridY):
            for ix in range(gridX):
                a = ix + gridX1 * iy
                b = ix + gridX1 * ( iy + 1 )
                c = ( ix + 1 ) + gridX1 * ( iy + 1 )
                d = ( ix + 1 ) + gridX1 * iy

                # // faces

                indices.extend([a, b, d])
                indices.extend([b, c, d])
        # // build geometry
        self.setIndex( indices )
        self.addAttribute( 'position', Float32BufferAttribute(vertices, 3))
        self.addAttribute( 'normal', Float32BufferAttribute(normals, 3))
        self.addAttribute( 'uv', Float32BufferAttribute(uvs, 2))
