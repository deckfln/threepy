"""
        <title>three.js webgl - collada</title>
         Elf Girl by <a href="https:#sketchfab.com/yellow09" target="_blank" rel="noopener">halloween</a> is licensed under <a href="https:#creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC Attribution</a>
"""


from datetime import datetime

from THREE import *
import THREE._Math as _Math
from THREE.pyOpenGL.pyOpenGL import *
from THREE.controls.TrackballControls import *
from THREE.loaders.ColladaLoader2 import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.elf = None
        self.clock = None


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize(window.innerWidth, window.innerHeight)

    p.camera = THREE.PerspectiveCamera( 45, window.innerWidth / window.innerHeight, 0.1, 2000 )
    p.camera.position.set( 8, 10, 8 )
    p.camera.lookAt( THREE.Vector3( 0, 3, 0 ) )

    p.scene = THREE.Scene()

    p.clock = THREE.Clock()

    # loading manager
    def _loading():
        p.scene.add( p.elf )
    
    loadingManager = THREE.LoadingManager( _loading )

    # collada
    def _loader( collada ):
        p.elf = collada.scene
        p.scene.add(p.elf)
        
    loader = ColladaLoader( loadingManager)
    # loader.options.convertUpAxis = True
    loader.load( './models/collada/elf/elf.dae',  _loader)

    #
    ambientLight = THREE.AmbientLight( 0xcccccc, 0.4 )
    p.scene.add( ambientLight )

    directionalLight = THREE.DirectionalLight( 0xffffff, 0.8 )
    directionalLight.position.set( 1, 1, 0 ).normalize()
    p.scene.add( directionalLight )


def onWindowResize(event, p):
    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()

    p.renderer.setSize( window.innerWidth, window.innerHeight )


def animate(p):
    render(p)


def render(p):
    delta = p.clock.getDelta()

    if p.elf is not None:
        p.elf.rotation.z += delta * 0.5

    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
