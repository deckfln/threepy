"""
        <title>three.js webgl - convex geometry</title>
"""
import random
import math
import sys
from datetime import datetime
from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.controls.OrbitControls import *
from THREE.geometries.ConvexGeometry import *


import THREE._Math as _Math


class Params:
    def __init__(self):
        self.group = None
        self.camera = None
        self.scene = None
        self.renderer = None
        self.container = None


def init(params):
    container = params.container = pyOpenGL(params)
    scene = params.scene = THREE.Scene()
    renderer = params.renderer = THREE.pyOpenGLRenderer( { 'antialias': True } )
    params.renderer.setSize( window.innerWidth, window.innerHeight )

    # // camera

    camera = params.camera = THREE.PerspectiveCamera( 40, window.innerWidth / window.innerHeight, 1, 1000 )
    camera.position.set( 15, 20, 30 )
    scene.add( camera )

    # // controls

    controls = OrbitControls( camera, container )
    controls.minDistance = 20
    controls.maxDistance = 50
    controls.maxPolarAngle = math.pi / 2

    scene.add( THREE.AmbientLight( 0x222222 ) )

    # // light

    light = THREE.PointLight( 0xffffff, 1 )
    camera.add( light )

    # // helper

    scene.add( THREE.AxisHelper( 20 ) )

    # // textures

    loader = THREE.TextureLoader()
    texture = loader.load( 'textures/sprites/disc.png' )

    group = params.group = THREE.Group()
    scene.add( group )

    # // points

    pointsGeometry = THREE.DodecahedronGeometry( 10 )

    #for i in range(len(pointsGeometry.vertices)):
    #    # //pointsGeometry.vertices[ i ].add( randomPoint().multiplyScalar( 2 ) ); // wiggle the points

    pointsMaterial = THREE.PointsMaterial( {
        'color': 0x0080ff,
        'map': texture,
        'size': 1,
        'alphaTest': 0.5
    } )

    points = THREE.Points( pointsGeometry, pointsMaterial )
    group.add( points )

    # // convex hull

    meshMaterial = THREE.MeshLambertMaterial( {
        'color': 0xffffff,
        'opacity': 0.5,
        'transparent': True
    } )

    meshGeometry = ConvexBufferGeometry( pointsGeometry.vertices )

    mesh = THREE.Mesh( meshGeometry, meshMaterial )
    mesh.material.side = THREE.BackSide    # // back faces
    mesh.renderOrder = 0
    group.add( mesh )

    mesh = THREE.Mesh( meshGeometry, meshMaterial.clone() )
    mesh.material.side = THREE.FrontSide    # // front faces
    mesh.renderOrder = 1
    group.add( mesh )

    #//

    container.addEventListener( 'resize', onWindowResize, False )

    
def randomPoint():
    return THREE.Vector3( _Math.randFloat( - 1, 1 ), _Math.randFloat( - 1, 1 ), _Math.randFloat( - 1, 1 ) )

    
def onWindowResize(event, params):
    params.camera.aspect = window.innerWidth / window.innerHeight
    params.camera.updateProjectionMatrix()

    params.renderer.setSize( window.innerWidth, window.innerHeight )


def animate(params):
    params.group.rotation.y += 0.005

    render(params)


def render(params):
    params.renderer.render( params.scene, params.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
