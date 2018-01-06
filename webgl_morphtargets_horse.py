"""
        <title>three.js webgl - morph targets - horse</title>
         webgl - morph targets - horse. model by <a href="http://mirada.com/">mirada</a> from <a href="http://ro.me">rome</a>';
"""

from datetime import datetime

from THREE import *
import THREE._Math as _Math
from THREE.pyOpenGL.pyOpenGL import *


class Params:
    def __init__(self):
        self.container = None
        self.stats = None
        self.camera = None
        self.scene = None
        self.projector = None
        self.renderer = None
        self.mesh = None
        self.mixer = None
        self.radius = 600
        self.theta = 0
        self.prevTime = datetime.now().timestamp()


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    p.camera = THREE.PerspectiveCamera( 50, window.innerWidth / window.innerHeight, 1, 10000 )
    p.camera.position.y = 300
    p.camera.target = THREE.Vector3( 0, 150, 0 )

    p.scene = THREE.Scene()
    p.scene.background = THREE.Color( 0xf0f0f0 )

    #

    light = THREE.DirectionalLight( 0xefefff, 1.5 )
    light.position.set( 1, 1, 1 ).normalize()
    p.scene.add( light )

    light = THREE.DirectionalLight( 0xffefef, 1.5 )
    light.position.set( -1, -1, -1 ).normalize()
    p.scene.add( light )

    loader = THREE.JSONLoader()

    def _load( geometry, material ):
        mesh = THREE.Mesh( geometry, THREE.MeshLambertMaterial( {
            'vertexColors': THREE.FaceColors,
            'morphTargets': True
        } ) )
        mesh.scale.set( 1.5, 1.5, 1.5 )
        p.scene.add( mesh )

        p.mixer = THREE.AnimationMixer( mesh )

        clip = THREE.AnimationClip.CreateFromMorphTargetSequence( 'gallop', geometry.morphTargets, 30 )
        p.mixer.clipAction( clip ).setDuration( 1 ).play()

    loader.load( "models/animated/horse.js", _load);


def animate(p):
    render(p)


def render(p):
    p.theta += 0.1

    p.camera.position.x = p.radius * math.sin( _Math.degToRad( p.theta ) )
    p.camera.position.z = p.radius * math.cos( _Math.degToRad( p.theta ) )

    p.camera.lookAt( p.camera.target )

    if p.mixer:
        time = datetime.now().timestamp()

        p.mixer.update( ( time - p.prevTime ) * 1 )
        p.prevTime = time

    p.renderer.render( p.scene, p.camera )


def onWindowResize(event, p):
    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()

    p.renderer.setSize( window.innerWidth, window.innerHeight )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
