"""
        <title>three.js webgl - lights - point lights</title>
"""        

from datetime import datetime
import math

from THREE import *
import THREE._Math as _Math
from THREE.pyOpenGL.pyOpenGL import *
from THREE.controls.TrackballControls import *
from THREE.OcTree import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.container = None
        self.controls = None
        self.clock = None
        self.light1 = None
        self.light2 = None
        self.light3 = None
        self.light4 = None
        self.light5 = None
        self.light6 = None
        self.counter = 0
        self.s = datetime.now().timestamp()
        self.octree = OcTree(THREE.Vector3(0, 0, 0), 256)


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    p.clock = THREE.Clock()

    # CAMERA

    p.camera = THREE.PerspectiveCamera( 50, window.innerWidth / window.innerHeight, 1, 3000 )
    p.camera.position.set( 0, 15, 150 )
    p.camera.lookAt( THREE.Vector3() )

    # SCENE

    p.scene = THREE.Scene()
    p.scene.background = THREE.Color( 0x040306 )
    p.scene.fog = THREE.Fog( 0x040306, 10, 300 )

    # CONTROLS

    p.controls = TrackballControls( p.camera, p.container )

    p.controls.rotateSpeed = 1.0
    p.controls.zoomSpeed = 1.2
    p.controls.panSpeed = 0.8

    p.controls.noZoom = False
    p.controls.noPan = False

    p.controls.staticMoving = False
    p.controls.dynamicDampingFactor = 0.15

    p.controls.keys = [ 65, 83, 68 ]

    # TEXTURES

    textureLoader = THREE.TextureLoader()

    texture = textureLoader.load( "textures/disturb.jpg" )
    texture.repeat.set( 20, 10 )
    texture.wrapS = texture.wrapT = THREE.RepeatWrapping
    texture.format = THREE.RGBFormat

    # MATERIALS

    groundMaterial = THREE.MeshPhongMaterial( { 'color': 0xffffff, 'map': texture } )
    objectMaterial = THREE.MeshStandardMaterial( { 'color': 0xffffff, 'roughness': 0.5, 'metalness': 1.0 } )

    # GROUND

    mesh = THREE.Mesh( THREE.PlaneBufferGeometry( 800, 400, 2, 2 ), groundMaterial )
    mesh.position.y = - 5
    mesh.rotation.x = - math.pi / 2
    p.scene.add( mesh )

    # OBJECTS

    #objectGeometry = THREE.BoxGeometry( 0.5, 1, 1 )
    #objectGeometry = THREE.SphereGeometry( 1.5, 16, 8 )
    objectGeometry = THREE.TorusGeometry( 1.5, 0.4, 8, 16 )

    for i in range(5000):
        mesh = THREE.Mesh( objectGeometry, objectMaterial )

        mesh.position.np[0] = 400 * ( 0.5 - random.random() )
        mesh.position.np[1] = 50 * ( 0.5 - random.random() ) + 25
        mesh.position.np[2] = 200 * ( 0.5 - random.random() )

        mesh.rotation.y = 3.14 * ( 0.5 - random.random() )
        mesh.rotation.x = 3.14 * ( 0.5 - random.random() )

        mesh.matrixAutoUpdate = False
        mesh.updateMatrix()

        p.octree.add(mesh)

    # merge the octrees meshes
    p.octree.merge()
    p.scene.add(p.octree)

    # LIGHTS

    intensity = 2.5
    distance = 100
    decay = 2.0

    c1 = 0xff0040
    c2 = 0x0040ff
    c3 = 0x80ff80
    c4 = 0xffaa00
    c5 = 0x00ffaa
    c6 = 0xff1100

    sphere = THREE.SphereGeometry( 0.25, 16, 8 )

    p.light1 = THREE.PointLight( c1, intensity, distance, decay )
    p.light1.add( THREE.Mesh( sphere, THREE.MeshBasicMaterial( { 'color': c1 } ) ) )
    p.scene.add( p.light1 )

    p.light2 = THREE.PointLight( c2, intensity, distance, decay )
    p.light2.add( THREE.Mesh( sphere, THREE.MeshBasicMaterial( { 'color': c2 } ) ) )
    p.scene.add( p.light2 )

    p.light3 = THREE.PointLight( c3, intensity, distance, decay )
    p.light3.add( THREE.Mesh( sphere, THREE.MeshBasicMaterial( { 'color': c3 } ) ) )
    p.scene.add( p.light3 )

    p.light4 = THREE.PointLight( c4, intensity, distance, decay )
    p.light4.add( THREE.Mesh( sphere, THREE.MeshBasicMaterial( { 'color': c4 } ) ) )
    p.scene.add( p.light4 )

    p.light5 = THREE.PointLight( c5, intensity, distance, decay )
    p.light5.add( THREE.Mesh( sphere, THREE.MeshBasicMaterial( { 'color': c5 } ) ) )
    p.scene.add( p.light5 )

    p.light6 = THREE.PointLight( c6, intensity, distance, decay )
    p.light6.add( THREE.Mesh( sphere, THREE.MeshBasicMaterial( { 'color': c6 } ) ) )
    p.scene.add( p.light6 )

    dlight = THREE.DirectionalLight( 0xffffff, 0.05 )
    dlight.position.set( 0.5, 1, 0 ).normalize()
    p.scene.add( dlight )

    p.renderer.gammaInput = True
    p.renderer.gammaOutput = True


def onWindowResize(event, p):
    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()

    p.renderer.setSize( window.innerWidth, window.innerHeight )

    p.controls.handleResize(window.innerWidth, window.innerHeight)


def animate(p):
    render(p)


def render(p):
    timer = datetime.now().timestamp() * 0.5
    z = 20
    d = 150

    p.light1.position.np[0] = math.sin( timer * 0.7 ) * d
    p.light1.position.np[2] = math.cos( timer * 0.3 ) * d

    p.light2.position.np[0] = math.cos( timer * 0.3 ) * d
    p.light2.position.np[2] = math.sin( timer * 0.7 ) * d

    p.light3.position.np[0] = math.sin( timer * 0.7 ) * d
    p.light3.position.np[2] = math.sin( timer * 0.5 ) * d

    p.light4.position.np[0] = math.sin( timer * 0.3 ) * d
    p.light4.position.np[2] = math.sin( timer * 0.5 ) * d

    p.light5.position.np[0] = math.cos( timer * 0.3 ) * d
    p.light5.position.np[2] = math.sin( timer * 0.5 ) * d

    p.light6.position.np[0] = math.cos( timer * 0.7 ) * d
    p.light6.position.np[2] = math.cos( timer * 0.5 ) * d

    p.controls.update( p.clock.getDelta() )

    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
