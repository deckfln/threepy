"""
    <title>three.js webgl - OBJLoader + MTLLoader</title>
"""
from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.LoadingManager import *
from THREE.loaders.OBJLoader import *
from THREE.loaders.MTLLoader import *
from THREE.loaders.DDSLoader import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.container = None
        self.mesh = None
        self.pointLight = None
        self.mouseX = 0
        self.mouseY = 0
        self.windowHalfX = window.innerWidth / 2
        self.windowHalfY = window.innerHeight / 2


def init(p):
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.container.addEventListener( 'mousemove', onDocumentMouseMove, False )
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})

    p.camera = THREE.PerspectiveCamera( 45, window.innerWidth / window.innerHeight, 1, 2000 )
    p.camera.position.z = 250

    # scene

    p.scene = THREE.Scene()

    ambient = THREE.AmbientLight( 0x444444 )
    p.scene.add( ambient )

    directionalLight = THREE.DirectionalLight( 0xffeedd )
    directionalLight.position.set( 0, 0, 1 ).normalize()
    p.scene.add( directionalLight )

    # model

    def onProgress( xhr ):
        if xhr.lengthComputable:
            percentComplete = xhr.loaded / xhr.total * 100
            print( round(percentComplete, 2) + '% downloaded' )

    def onError ( xhr ):
        return

    Loader.Handlers.add( "\.dds$", DDSLoader() )

    mtlLoader = MTLLoader()
    mtlLoader.setPath( 'obj/male02/' )

    def add_object(object):
        object.position.y = - 95
        p.scene.add(object)

    def _onload(materials):
        materials.preload()

        objLoader = OBJLoader()
        objLoader.setMaterials( materials )
        objLoader.setPath( 'obj/male02/' )

        objLoader.load( 'male02.obj', add_object)
    
    mtlLoader.load( 'male02_dds.mtl', _onload, onProgress, onError )


def onWindowResize(event, p):
    p.windowHalfX = window.innerWidth / 2
    p.windowHalfY = window.innerHeight / 2

    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()

    p.renderer.setSize( window.innerWidth, window.innerHeight )

    
def onDocumentMouseMove( event, p ):
    p.mouseX = ( event.clientX - p.windowHalfX ) / 2
    p.mouseY = ( event.clientY - p.windowHalfY ) / 2


def animate(p):
    render(p)


def render(p):
    p.camera.position.x += ( p.mouseX - p.camera.position.x ) * .05
    p.camera.position.y += ( - p.mouseY - p.camera.position.y ) * .05

    p.camera.lookAt( p.scene.position )

    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
