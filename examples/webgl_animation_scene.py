"""
    <title>three.js webgl - scene animation</title>

    <a href="https://clara.io/view/96106133-2e99-40cf-8abd-64defd153e61">Three Gears Scene</a> courtesy of David Sarno
"""
from datetime import datetime

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.controls.OrbitControls import *
from THREE.loaders.ObjectLoader import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.controls = None
        self.renderer = None
        self.container = None
        self.mixer = None
        self.clock =THREE.Clock()


def init(p: Params):
    p.container = pyOpenGL(p)

    url = 'models/json/scene-animation.json'

    SCREEN_WIDTH = window.innerWidth
    SCREEN_HEIGHT = window.innerHeight

    # Load a scene with objects, lights and camera from a JSON file
    loader = ObjectLoader()
    loader.setPath(os.path.dirname(__file__))
    p.scene = loader.load(url)

    p.scene.background = THREE.Color( 0xffffff )

    # If the loaded file contains a perspective camera, use it with adjusted aspect ratio...

    def _traverse(sceneChild, scope):
        if sceneChild.type == 'PerspectiveCamera':
            p.camera = sceneChild
            p.camera.aspect = SCREEN_WIDTH / SCREEN_HEIGHT
            p.camera.updateProjectionMatrix()

    p.scene.traverse(_traverse)

    # ... else create a new camera and use it in the loaded scene

    if p.camera is None:
        camera = THREE.PerspectiveCamera( 30, SCREEN_WIDTH / SCREEN_HEIGHT, 1, 10000 )
        camera.position.set( - 200, 0, 200 )

    controls = OrbitControls( p.camera, p.container )

    # Ground plane and fog: examples for applying additional children and new property values to the loaded scene

    geometry = THREE.PlaneBufferGeometry( 20000, 20000 )
    material = THREE.MeshPhongMaterial( { 'shininess': 0.1 } )
    ground = THREE.Mesh( geometry, material )

    ground.position.set( 0, - 250, 0 )
    ground.rotation.x = - math.pi / 2

    p.scene.add( ground )

    p.scene.fog = THREE.Fog( 0xffffff, 1000, 10000 )

    # Initialization of the loaded animations

    animationClip = p.scene.animations[ 0 ]
    p.mixer = THREE.AnimationMixer( p.scene )
    p.mixer.clipAction( animationClip ).play()

    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize( window.innerWidth, window.innerHeight )

    #

    p.container.addEventListener( 'resize', onWindowResize, False )


def onWindowResize(event, params):
    params.camera.aspect = window.innerWidth / window.innerHeight
    params.camera.updateProjectionMatrix()

    params.renderer.setSize( window.innerWidth, window.innerHeight )


def animate(p):
    render(p)


def render(p: Params):
    delta = 0.75 * p.clock.getDelta()

    p.mixer.update(delta)

    p.renderer.render(p.scene, p.camera)


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
