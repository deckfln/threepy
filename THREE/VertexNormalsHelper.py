"""
 @author mrdoob / http://mrdoob.com/
 @author WestLangley / http://github.com/WestLangley
"""
from THREE.objects.LineSegments import *
from THREE.materials.LineBasicMaterial import *


class VertexNormalsHelper(LineSegments):
    def __init__(self, object, size=1, hex=0xff0000, linewidth=1):
        self.object = object

        self.size = size
        color = hex
        width = linewidth

        #

        nNormals = 0
        objGeometry = self.object.geometry

        if objGeometry and objGeometry.my_class(isGeometry):
            nNormals = objGeometry.faces.length * 3
        elif objGeometry and objGeometry.my_class(isBufferGeometry):
            nNormals = objGeometry.attributes.normal.count

        #

        geometry = BufferGeometry()
        positions = Float32BufferAttribute( nNormals * 2 * 3, 3 )
        geometry.addAttribute( 'position', positions )

        super().__init__( geometry, LineBasicMaterial( { 'color': color, 'linewidth': width } ) )

        #

        self.matrixAutoUpdate = False

        self.update()

    def update(self):
        v1 = Vector3()
        v2 = Vector3()
        normalMatrix = Matrix3()

        keys = [ 'a', 'b', 'c' ]

        self.object.updateMatrixWorld( True )

        normalMatrix.getNormalMatrix( self.object.matrixWorld )

        matrixWorld = self.object.matrixWorld

        position = self.geometry.attributes.position

        #

        objGeometry = self.object.geometry

        if objGeometry and objGeometry.my_class(isGeometry ):
            vertices = objGeometry.vertices

            faces = objGeometry.faces

            idx = 0

            for face in faces:
                for j in range(0, len(face.vertexNormals)):
                    vertex = vertices[ face[ keys[ j ] ] ]

                    normal = face.vertexNormals[ j ]

                    v1.copy( vertex ).applyMatrix4( matrixWorld )

                    v2.copy( normal ).applyMatrix3( normalMatrix ).normalize().multiplyScalar( self.size ).add( v1 )

                    position.setXYZ( idx, v1.x, v1.y, v1.z )

                    idx = idx + 1

                    position.setXYZ( idx, v2.x, v2.y, v2.z )

                    idx = idx + 1

        elif objGeometry and objGeometry.my_class(isBufferGeometry ):
            objPos = objGeometry.attributes.position

            objNorm = objGeometry.attributes.normal

            idx = 0

            # for simplicity, ignore index and drawcalls, and render every normal

            for j in range(0, objPos.count):
                v1.set( objPos.getX( j ), objPos.getY( j ), objPos.getZ( j ) ).applyMatrix4( matrixWorld )

                v2.set( objNorm.getX( j ), objNorm.getY( j ), objNorm.getZ( j ) )

                v2.applyMatrix3( normalMatrix ).normalize().multiplyScalar( self.size ).add( v1 )

                position.setXYZ( idx, v1.x, v1.y, v1.z )

                idx = idx + 1

                position.setXYZ( idx, v2.x, v2.y, v2.z )

                idx = idx + 1

        position.needsUpdate = True
