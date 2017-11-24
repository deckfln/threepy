"""
        <title>three.js webgl - collada - kinematics</title>
        <div id="info">
            <a href="http:#threejs.org" target="_blank" rel="noopener">three.js</a> collada loader - kinematics
             | robot from <a href="https:#github.com/rdiankov/collada_robots" target="_blank" rel="noopener">collada robots</a>
        </div>
"""

from datetime import datetime

from THREE import *
import THREE._Math as _Math
from THREE.pyOpenGL.pyOpenGL import *
from THREE.controls.TrackballControls import *
from THREE.loaders.ColladaLoader2 import *
import libs.tween as TWEEN


class Params:
    def __init__(self):
        self.container = None
        self.stats = None
        self.camera = None
        self.scene = None
        self.renderer = None
        self.objects = None
        self.particleLight = None
        self.kinematics = None
        self.kinematicsTween = None
        self.tweenParameters = {}
        self.Tween = None


def setupTween(p):
    duration = _Math.randInt( 1000, 5000 )
    target = {}

    for i in range(len(p.kinematics.joints)):
        joint = p.kinematics.joints[ i ]

        if i in p.tweenParameters:
            position = p.tweenParameters[ i ]
        else:
            position = joint.zeroPosition

        p.tweenParameters[ i ] = position

        target[ i ] = _Math.randInt( joint.limits.min, joint.limits.max )

    p.kinematicsTween = TWEEN.Tween( p.tweenParameters ).to( target, duration ).easing( TWEEN.Easing_Quadratic_Out )

    def _onUpdate(obj, value):
        for i in range(len(p.kinematics.joints)):
            p.kinematics.setJointValue( i, obj[ i ] )

    p.kinematicsTween.onUpdate(  _onUpdate )

    p.kinematicsTween.start()


def init(p):
    loader = ColladaLoader()
    # loader.options.convertUpAxis = True

    dae = None
    kinematics = None

    def _onLoad(collada):
        nonlocal dae
        nonlocal kinematics

        dae = collada.scene

        def _traverse(child, scope):
            if isinstance(child, THREE.Mesh):
                # model does not have normals
                child.material.flatShading = True

        dae.traverse(_traverse)

        dae.scale.x = dae.scale.y = dae.scale.z = 10.0
        dae.updateMatrix()

        kinematics = collada.kinematics

    loader.load('./models/collada/kawada-hironx.dae', _onLoad)
    p.kinematics = kinematics

    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    p.camera = THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 1, 2000)
    p.camera.position.set(2, 2, 3)

    p.scene = THREE.Scene()

    # Grid

    grid = THREE.GridHelper(20, 20)
    p.scene.add(grid)

    # Add the COLLADA
    p.scene.add(dae)

    p.particleLight = THREE.Mesh(THREE.SphereGeometry(4, 8, 8), THREE.MeshBasicMaterial({'color': 0xffffff}))
    p.scene.add(p.particleLight)

    # Lights
    light = THREE.HemisphereLight(0xffeeee, 0x111122)
    p.scene.add(light)

    pointLight = THREE.PointLight(0xffffff, 0.3)
    p.particleLight.add(pointLight)

    setupTween(p)


def onWindowResize(event, p):
    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()

    p.renderer.setSize( window.innerWidth, window.innerHeight )


def animate(p):
    render(p)
    TWEEN.Tweens.update()

    if not p.kinematicsTween._isPlaying:
        setupTween(p)

def render(p):
    timer = datetime.now().timestamp() * 0.1

    # setupTween(p)

    p.camera.position.x = math.cos( timer ) * 17
    p.camera.position.y = 10
    p.camera.position.z = math.sin( timer ) * 17

    p.camera.lookAt( p.scene.position )

    p.particleLight.position.x = math.sin( timer * 4 ) * 3009
    p.particleLight.position.y = math.cos( timer * 5 ) * 4000
    p.particleLight.position.z = math.cos( timer * 4 ) * 3009

    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
