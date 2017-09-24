"""
/**
 * @author alteredq / http:# //alteredqualia.com/
 * @author Mugen87 / https:# //github.com/Mugen87
 *
 *    - shows frustum, line of sight and up of the camera
 *    - suitable for fast updates
 *     - based on frustum visualization in lightgl.js shadowmap example
 *        http:# //evanw.github.com/lightgl.js/tests/shadowmap.html
 */
"""
from THREE.LineSegments import *
from THREE.Vector3 import *
from THREE.Camera import *


class CameraHelper(LineSegments):
    def __init__(self, camera ):
        geometry = BufferGeometry()
        material = LineBasicMaterial( { 'color': 0xffffff, 'vertexColors': FaceColors } )

        vertices = []
        colors = []

        pointMap = {}

        # // colors

        colorFrustum = Color( 0xffaa00 )
        colorCone = Color( 0xff0000 )
        colorUp = Color( 0x00aaff )
        colorTarget = Color( 0xffffff )
        colorCross = Color( 0x333333 )

        def addPoint( id, color ):
            nonlocal vertices, colors, pointMap
            
            vertices.extend([ 0, 0, 0 ])
            colors.extend([ color.r, color.g, color.b ])

            if id not in pointMap:
                pointMap[ id ] = []

            pointMap[ id ].append( ( len(vertices) / 3 ) - 1 )

        def addLine( a, b, color ):
            addPoint( a, color )
            addPoint( b, color )
        
        # // near

        addLine( "n1", "n2", colorFrustum )
        addLine( "n2", "n4", colorFrustum )
        addLine( "n4", "n3", colorFrustum )
        addLine( "n3", "n1", colorFrustum )

        # // far

        addLine( "f1", "f2", colorFrustum )
        addLine( "f2", "f4", colorFrustum )
        addLine( "f4", "f3", colorFrustum )
        addLine( "f3", "f1", colorFrustum )

        # // sides

        addLine( "n1", "f1", colorFrustum )
        addLine( "n2", "f2", colorFrustum )
        addLine( "n3", "f3", colorFrustum )
        addLine( "n4", "f4", colorFrustum )

        # // cone

        addLine( "p", "n1", colorCone )
        addLine( "p", "n2", colorCone )
        addLine( "p", "n3", colorCone )
        addLine( "p", "n4", colorCone )

        # // up

        addLine( "u1", "u2", colorUp )
        addLine( "u2", "u3", colorUp )
        addLine( "u3", "u1", colorUp )

        # // target

        addLine( "c", "t", colorTarget )
        addLine( "p", "c", colorCross )

        # // cross

        addLine( "cn1", "cn2", colorCross )
        addLine( "cn3", "cn4", colorCross )

        addLine( "cf1", "cf2", colorCross )
        addLine( "cf3", "cf4", colorCross )


        geometry.addAttribute( 'position', Float32BufferAttribute( vertices, 3 ) )
        geometry.addAttribute( 'color', Float32BufferAttribute( colors, 3 ) )

        super().__init__( geometry, material )

        self.camera = camera
        if self.camera.updateProjectionMatrix:
            self.camera.updateProjectionMatrix()

        self.matrix = camera.matrixWorld
        self.matrixAutoUpdate = False

        self.pointMap = pointMap

        self.update()

    def update(self):
        vector = Vector3()
        camera = Camera()
        geometry = self.geometry
        pointMap = self.pointMap

        w = 1
        h = 1

        # // we need just camera projection matrix
        # // world matrix must be identity

        camera.projectionMatrix.copy( self.camera.projectionMatrix )

        def setPoint( point, x, y, z ):
            vector.set( x, y, z ).unproject( camera )

            points = pointMap[ point ]

            if points is not None:
                position = geometry.getAttribute( 'position' )

                for i in range(len(points)):
                    position.setXYZ( int(points[ i ]), vector.x, vector.y, vector.z )
        
        # // center / target

        setPoint( "c", 0, 0, - 1 )
        setPoint( "t", 0, 0,  1 )

        # // near

        setPoint( "n1", - w, - h, - 1 )
        setPoint( "n2",   w, - h, - 1 )
        setPoint( "n3", - w,   h, - 1 )
        setPoint( "n4",   w,   h, - 1 )

        # // far

        setPoint( "f1", - w, - h, 1 )
        setPoint( "f2",   w, - h, 1 )
        setPoint( "f3", - w,   h, 1 )
        setPoint( "f4",   w,   h, 1 )

        # // up

        setPoint( "u1",   w * 0.7, h * 1.1, - 1 )
        setPoint( "u2", - w * 0.7, h * 1.1, - 1 )
        setPoint( "u3",         0, h * 2,   - 1 )

        # // cross

        setPoint( "cf1", - w,   0, 1 )
        setPoint( "cf2",   w,   0, 1 )
        setPoint( "cf3",   0, - h, 1 )
        setPoint( "cf4",   0,   h, 1 )

        setPoint( "cn1", - w,   0, - 1 )
        setPoint( "cn2",   w,   0, - 1 )
        setPoint( "cn3",   0, - h, - 1 )
        setPoint( "cn4",   0,   h, - 1 )

        geometry.getAttribute( 'position' ).needsUpdate = True
