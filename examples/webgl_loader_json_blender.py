"""
        <title>three.js webgl - blender -json</title>
"""
from datetime import datetime

from THREE import *
import THREE._Math as _Math
from THREE.pyOpenGL.pyOpenGL import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.container = None
        self.mesh = None
        self.clock = None
        self.mixer = None
        self.objects = None
        self.clock = 0


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    p.clock = THREE.Clock()

    p.scene = THREE.Scene()
    # p.scene.fog = THREE.FogExp2( 0x000000, 0.035 )

    p.camera = THREE.PerspectiveCamera( 50, window.innerWidth / window.innerHeight, 1, 2000 )
    p.camera.position.set( 2, 4, 5 )
    p.camera.lookAt( p.scene.position )

    p.mixer = THREE.AnimationMixer( p.scene )

    loader = THREE.JSONLoader()

    def _onLoad(geometry, materials):
        # adjust color a bit

        material = materials[0]

        material.morphTargets = True
        material.color.setHex(0xffaaaa)

        for i in range(729):
            p.mesh = mesh = THREE.Mesh(geometry, material)

            # random placement in a grid

            x = ((i % 27) - 13.5) * 2 + _Math.randFloatSpread(1)
            z = (math.floor(i / 27) - 13.5) * 2 + _Math.randFloatSpread(1)

            mesh.position.set(x, 0, z)

            s = _Math.randFloat(0.00075, 0.001)
            s = 0.001
            mesh.scale.set(s, s, s)

            mesh.rotation.y = _Math.randFloat(-0.25, 0.25)

            mesh.matrixAutoUpdate = False
            mesh.updateMatrix()

            p.scene.add(mesh)

            # one second
            # random phase (already running)
            # let's go
            p.mixer.clipAction(geometry.animations[0], mesh).setDuration(1).startAt(- random.random()).play()

    loader.load( './models/animated/monster/monster.js', _onLoad )

    # lights

    ambientLight = THREE.AmbientLight( 0xcccccc )
    p.scene.add( ambientLight )

    pointLight = THREE.PointLight( 0xff4400, 5, 30 )
    pointLight.position.set( 5, 0, 0 )
    p.scene.add( pointLight )


def onWindowResize( event, p ):
    p.renderer.setSize( window.innerWidth, window.innerHeight )

    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()


def animate(p):
    render(p)


def render(p):
    timer = datetime.now().timestamp() * 0.1

    p.camera.position.x = math.cos( timer ) * 5
    p.camera.position.y = 2
    p.camera.position.z = math.sin( timer ) * 5

    c = p.clock.getDelta()
    p.mixer.update(c)
    p.renderer.render(p.scene, p.camera)

    p.camera.lookAt( p.scene.position )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
