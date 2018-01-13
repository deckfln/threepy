"""
        <title>three.js webgl - cameras</title>
"""
import math
from datetime import datetime

from THREE import *
import THREE._Math as _Math
from THREE.pyOpenGL.pyOpenGL import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.mesh = None
        self.cameraRig = None
        self.activeCamera = None
        self.activeHelper = None
        self.cameraPerspective = None
        self.cameraOrtho = None
        self.cameraPerspectiveHelper = None
        self.cameraOrthoHelper = None
        self.frustumSize = 600


def init(p):
    p.container = pyOpenGL(p)

    p.scene = THREE.Scene()

    # //

    aspect = window.innerWidth / window.innerHeight
    p.camera = THREE.PerspectiveCamera(50, 0.5 * aspect, 1, 10000)
    p.camera.position.z = 2500

    p.cameraPerspective = THREE.PerspectiveCamera( 50, 0.5 * aspect, 150, 1000 )

    p.cameraPerspectiveHelper = THREE.CameraHelper( p.cameraPerspective )
    p.scene.add( p.cameraPerspectiveHelper )

    # //
    p.cameraOrtho = THREE.OrthographicCamera( 0.5 * p.frustumSize * aspect / - 2, 0.5 * p.frustumSize * aspect / 2, p.frustumSize / 2, p.frustumSize / - 2, 150, 1000 )

    p.cameraOrthoHelper = THREE.CameraHelper( p.cameraOrtho )
    p.scene.add( p.cameraOrthoHelper )

    # //

    p.activeCamera = p.cameraPerspective
    p.activeHelper = p.cameraPerspectiveHelper


    # // counteract different front orientation of cameras vs rig

    p.cameraOrtho.rotation.y = math.pi
    p.cameraPerspective.rotation.y = math.pi

    p.cameraRig = THREE.Group()

    p.cameraRig.add( p.cameraPerspective )
    p.cameraRig.add( p.cameraOrtho )

    p.scene.add( p.cameraRig )

    # //

    p.mesh = THREE.Mesh(
        THREE.SphereBufferGeometry( 100, 16, 8 ),
        THREE.MeshBasicMaterial( { 'color': 0xffffff, 'wireframe': True } )
    )
    p.scene.add( p.mesh )

    mesh2 = THREE.Mesh(
        THREE.SphereBufferGeometry( 50, 16, 8 ),
        THREE.MeshBasicMaterial( { 'color': 0x00ff00, 'wireframe': True } )
    )
    mesh2.position.y = 150
    p.mesh.add( mesh2 )

    mesh3 = THREE.Mesh(
        THREE.SphereBufferGeometry( 5, 16, 8 ),
        THREE.MeshBasicMaterial( { 'color': 0x0000ff, 'wireframe': True } )
    )
    mesh3.position.z = 150
    p.cameraRig.add( mesh3 )

    # //

    geometry = THREE.Geometry()

    for i in range(10000):
        vertex = THREE.Vector3()
        vertex.x = _Math.randFloatSpread( 2000 )
        vertex.y = _Math.randFloatSpread( 2000 )
        vertex.z = _Math.randFloatSpread( 2000 )

        geometry.vertices.append( vertex )

    particles = THREE.Points( geometry, THREE.PointsMaterial( { 'color': 0x888888 } ) )
    p.scene.add( particles )

    # //

    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize( window.innerWidth, window.innerHeight )
    p.container.addEventListener( 'resize', onWindowResize, False )


def onWindowResize(event, p):
    aspect = window.innerWidth / window.innerHeight

    p.renderer.setSize( window.innerWidth, window.innerHeight )

    p.camera.aspect = 0.5 * aspect
    p.camera.updateProjectionMatrix()

    p.cameraPerspective.aspect = 0.5 * aspect
    p.cameraPerspective.updateProjectionMatrix()

    p.cameraOrtho.left = - 0.5 * p.frustumSize * aspect / 2
    p.cameraOrtho.right = 0.5 * p.frustumSize * aspect / 2
    p.cameraOrtho.top = p.frustumSize / 2
    p.cameraOrtho.bottom = - p.frustumSize / 2
    p.cameraOrtho.updateProjectionMatrix()


def animate(p):
    render(p)


def render(p):
    r = datetime.now().timestamp() * 1

    p.mesh.position.x = 700 * math.cos( r )
    p.mesh.position.z = 700 * math.sin( r )
    p.mesh.position.y = 700 * math.sin( r )

    p.mesh.children[ 0 ].position.x = 70 * math.cos( 2 * r )
    p.mesh.children[ 0 ].position.z = 70 * math.sin( r )

    if p.activeCamera == p.cameraPerspective:
        p.cameraPerspective.fov = 35 + 30 * math.sin( 0.5 * r )
        p.cameraPerspective.far = p.mesh.position.length()
        p.cameraPerspective.updateProjectionMatrix()

        p.cameraPerspectiveHelper.update()
        p.cameraPerspectiveHelper.visible = True

        p.cameraOrthoHelper.visible = False
    else:
        p.cameraOrtho.far = p.mesh.position.length()
        p.cameraOrtho.updateProjectionMatrix()

        p.cameraOrthoHelper.update()
        p.cameraOrthoHelper.visible = True

        p.cameraPerspectiveHelper.visible = False

    p.cameraRig.lookAt( p.mesh.position )

    p.renderer.clear()

    p.activeHelper.visible = False

    p.renderer.setViewport( 0, 0, window.innerWidth/2, window.innerHeight )
    p.renderer.render( p.scene, p.activeCamera )

    p.activeHelper.visible = True

    p.renderer.setViewport( window.innerWidth/2, 0,  window.innerWidth/2, window.innerHeight )
    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
