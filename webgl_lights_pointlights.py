"""
        <title>three.js webgl - lights - point lights</title>
"""        

from datetime import datetime

from THREE import *
import THREE._Math as _Math
from THREE.pyOpenGL.pyOpenGL import *
from THREE.loaders.BinaryLoader import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.particle1 = None
        self.particle2 = None
        self.container = None
        self.clock = None
        self.light1 = None
        self.light2 = None
        self.light3 = None
        self.light4 = None
        self.obj = None


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    p.camera = THREE.PerspectiveCamera( 50, window.innerWidth / window.innerHeight, 1, 1000 )
    p.camera.position.z = 100

    p.clock = THREE.Clock()

    p.scene = THREE.Scene()

    loader = BinaryLoader()

    def callback( geometry, material=None ):
        p.obj = THREE.Mesh( geometry, THREE.MeshPhongMaterial( { 'color': 0x555555, 'specular': 0x111111, 'shininess': 50 }  )  )
        p.obj.scale.x = p.obj.scale.y = p.obj.scale.z = 0.80
        p.scene.add( p.obj )

    loader.load( "obj/walt/WaltHead_bin.js", callback )

    sphere = THREE.SphereGeometry( 0.5, 16, 8 )

    p.light1 = THREE.PointLight( 0xff0040, 2, 50 )
    p.light1.add( THREE.Mesh( sphere, THREE.MeshBasicMaterial( { 'color': 0xff0040 } ) ) )
    p.scene.add( p.light1 )

    p.light2 = THREE.PointLight( 0x0040ff, 2, 50 )
    p.light2.add( THREE.Mesh( sphere, THREE.MeshBasicMaterial( { 'color': 0x0040ff } ) ) )
    p.scene.add( p.light2 )

    p.light3 = THREE.PointLight( 0x80ff80, 2, 50 )
    p.light3.add( THREE.Mesh( sphere, THREE.MeshBasicMaterial( { 'color': 0x80ff80 } ) ) )
    p.scene.add( p.light3 )

    p.light4 = THREE.PointLight( 0xffaa00, 2, 50 )
    p.light4.add( THREE.Mesh( sphere, THREE.MeshBasicMaterial( { 'color': 0xffaa00 } ) ) )
    p.scene.add( p.light4 )


def onWindowResize(event, p):
    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()

    p.renderer.setSize( window.innerWidth, window.innerHeight )


def animate(p):
    render(p)


def render(p):
    timer = datetime.now().timestamp() * 0.5
    delta = p.clock.getDelta()

    if p.obj:
        p.obj.rotation.y -= 0.5 * delta

    p.light1.position.x = math.sin( timer * 0.7 ) * 30
    p.light1.position.y = math.cos( timer * 0.5 ) * 40
    p.light1.position.z = math.cos( timer * 0.3 ) * 30

    p.light2.position.x = math.cos( timer * 0.3 ) * 30
    p.light2.position.y = math.sin( timer * 0.5 ) * 40
    p.light2.position.z = math.sin( timer * 0.7 ) * 30

    p.light3.position.x = math.sin( timer * 0.7 ) * 30
    p.light3.position.y = math.cos( timer * 0.3 ) * 40
    p.light3.position.z = math.sin( timer * 0.5 ) * 30

    p.light4.position.x = math.sin( timer * 0.3 ) * 30
    p.light4.position.y = math.cos( timer * 0.7 ) * 40
    p.light4.position.z = math.sin( timer * 0.5 ) * 30

    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
