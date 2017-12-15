"""
        <title>three.js webgl - collada - skinning</title>
        <div id="info">
            <a href="https://threejs.org" target="_blank" rel="noopener">three.js</a> collada loader - skinning
            | Dancing Stormtrooper <a href="https://sketchfab.com/strykerdoesgames" target="_blank" rel="noopener">StrykerDoesAnimation</a> is licensed under <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC Attribution</a>
        </div>
"""

from datetime import datetime

from THREE import *
import THREE._Math as _Math
from THREE.pyOpenGL.pyOpenGL import *
from THREE.controls.OrbitControls import *
from THREE.loaders.ColladaLoader2 import *
import libs.tween as TWEEN


class Params:
    def __init__(self):
        self.container = None
        self.stats = None
        self.camera = None
        self.scene = None
        self.renderer = None
        self.clock = None
        self.controls = None
        self.mixer = None


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    p.camera = THREE.PerspectiveCamera( 25, window.innerWidth / window.innerHeight, 1, 10000 )
    p.camera.position.set( 15, 10, - 15 )

    p.scene = THREE.Scene()

    p.clock = THREE.Clock()

    # collada

    loader = ColladaLoader()
    # loader.options.convertUpAxis = True
    
    def _onload(collada):
        animations = collada.animations
        avatar = collada.scene

        p.mixer = THREE.AnimationMixer( avatar )
        action = p.mixer.clipAction( animations[ 0 ] ).play()

        p.scene.add( avatar )

    loader.load( './models/collada/stormtrooper/stormtrooper.dae', _onload )

    #

    gridHelper = THREE.GridHelper( 10, 20 )
    p.scene.add( gridHelper )

    #

    ambientLight = THREE.AmbientLight( 0xffffff, 0.2 )
    p.scene.add( ambientLight )

    directionalLight = THREE.DirectionalLight( 0xffffff, 0.8 )
    directionalLight.position.set( 1, 1, - 1 )
    p.scene.add( directionalLight )

    #

    p.controls = OrbitControls( p.camera, p.container)
    p.controls.target.set( 0, 2, 0 )
    p.controls.update()

    #

    
def animate(p):
    render(p)

    
def render(p):
    delta = p.clock.getDelta()

    if p.mixer is not None:
        p.mixer.update( delta )

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
