"""
    <title>three.js webgl - scene animation</title>

    <a href="https://clara.io/view/96106133-2e99-40cf-8abd-64defd153e61">Three Gears Scene</a> courtesy of David Sarno
"""
from datetime import datetime
import os

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

    p.scene = THREE.Scene()

    grid = THREE.GridHelper(20, 20, 0x888888, 0x888888)
    grid.position.set(0, - 1.1, 0)
    p.scene.add(grid)

    p.camera = THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 1, 100)
    p.camera.position.set(- 5.00, 3.43, 11.31)
    p.camera.lookAt(THREE.Vector3(- 1.22, 2.18, 4.58) )

    p.scene.add(THREE.AmbientLight(0x404040) )

    pointLight = THREE.PointLight(0xffffff, 1)
    pointLight.position.copy(p.camera.position)
    p.scene.add(pointLight)

    loader = ObjectLoader()
    loader.setPath(os.path.dirname(__file__))
    model = loader.load('models/json/pump/pump.json')
    p.scene.add(model)

    p.mixer = THREE.AnimationMixer(model)
    p.mixer.clipAction(model.animations[0]).play()

    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize( window.innerWidth, window.innerHeight )

    #

    p.container.addEventListener( 'resize', onWindowResize, False )


def onWindowResize(event, params):
    params.camera.aspect = window.innerWidth / window.innerHeight
    params.camera.updateProjectionMatrix()

    params.renderer.setSize( window.innerWidth, window.innerHeight )


def animate(p):
    p.mixer.update(p.clock.getDelta())
    render(p)


def render(p: Params):
    p.renderer.render(p.scene, p.camera)


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
