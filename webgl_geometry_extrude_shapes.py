"""
        <title>three.js webgl - geometry - extrude shapes</title>
"""
import math
import sys
from datetime import datetime
from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.controls.TrackballControls import *
import THREE._Math as _Math


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.container = None
        self.mesh = None
        self.controls = None


def init(p):
    p.container = pyOpenGL(p)

    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize( window.innerWidth, window.innerHeight )

    p.scene = THREE.Scene()
    p.scene.background = THREE.Color( 0x222222 )

    p.camera = THREE.PerspectiveCamera( 45, window.innerWidth / window.innerHeight, 1, 1000 )
    p.camera.position.set( 0, 0, 500 )

    p.controls = TrackballControls( p.camera, p.container)
    p.controls.minDistance = 200
    p.controls.maxDistance = 500

    p.scene.add( THREE.AmbientLight( 0x222222 ) )

    light = THREE.PointLight( 0xffffff )
    light.position.copy( p.camera.position )
    p.scene.add( light )

    # //

    closedSpline = THREE.CatmullRomCurve3( [
        THREE.Vector3( -60, -100,  60 ),
        THREE.Vector3( -60,   20,  60 ),
        THREE.Vector3( -60,  120,  60 ),
        THREE.Vector3(  60,   20, -60 ),
        THREE.Vector3(  60, -100, -60 )
    ] )

    closedSpline.type = 'catmullrom'
    closedSpline.closed = True

    extrudeSettings = {
        'steps'            : 100,
        'bevelEnabled'    : False,
        'extrudePath'        : closedSpline
    }

    pts = []
    count = 3

    for i in range(count):
        l = 20
        a = 2 * i / count * math.pi
        pts.append( THREE.Vector2 ( math.cos( a ) * l, math.sin( a ) * l ) )

    shape = THREE.Shape( pts )
    geometry = THREE.ExtrudeGeometry( shape, extrudeSettings )

    material = THREE.MeshLambertMaterial( { 'color': 0xb00000, 'wireframe': False } )

    mesh = THREE.Mesh( geometry, material )

    p.scene.add( mesh )


    # //


    randomPoints = []

    for i in range(10):
        randomPoints.append( THREE.Vector3( ( i - 4.5 ) * 50, _Math.randFloat( - 50, 50 ), _Math.randFloat( - 50, 50 ) ) )

    randomSpline =  THREE.CatmullRomCurve3( randomPoints )

    # //

    extrudeSettings = {
        'steps'            : 200,
        'bevelEnabled'    : False,
        'extrudePath'        : randomSpline
    }


    pts = []
    numPts = 5

    for i in range(numPts * 2):
        l = 10 if i % 2 == 1 else 20

        a = i / numPts * math.pi

        pts.append( THREE.Vector2 ( math.cos( a ) * l, math.sin( a ) * l ) )

    shape = THREE.Shape( pts )

    geometry = THREE.ExtrudeGeometry( shape, extrudeSettings )

    material2 = THREE.MeshLambertMaterial( { 'color': 0xff8000, 'wireframe': False } )

    mesh = THREE.Mesh( geometry, material2 )

    p.scene.add( mesh )


    # //


    materials = [ material, material2 ]

    extrudeSettings = {
        'amount'            : 20,
        'steps'            : 1,
        'material'        : 1,
        'extrudeMaterial' : 0,
        'bevelEnabled'    : True,
        'bevelThickness'  : 2,
        'bevelSize'       : 4,
        'bevelSegments'   : 1
    }

    geometry = THREE.ExtrudeGeometry( shape, extrudeSettings )

    mesh = THREE.Mesh( geometry, materials )

    mesh.position.set( 50, 100, 50 )

    p.scene.add( mesh )

    p.container.addEventListener( 'resize', onWindowResize, False )


def onWindowResize(event, p):
    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()

    p.renderer.setSize( window.innerWidth, window.innerHeight )

    p.controls.handleResize(window.innerWidth, window.innerHeight)


def animate(p):
    p.controls.update()

    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
