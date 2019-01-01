"""
        <title>three.js webgl - materials - cube reflection / refraction [Walt]</title>
        <p>Walt Disney head by <a href="http:# //davidoreilly.com/post/18087489343/disneyhead" target="_blank" rel="noopener">David OReilly</a>
        <p>Texture by <a href="http:# //www.humus.name/index.php?page=Textures" target="_blank" rel="noopener">Humus</a>
"""
import sys, os.path
mango_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) )
sys.path.append(mango_dir)

from datetime import datetime

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.loaders.BinaryLoader import *
from THREE.controls.OrbitControls import *
from THREE.loaders.OBJLoader import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.container = None
        self.mesh = None
        self.geometry = None
        self.pointLight = None
        self.controls = none


def init(p):
    # /// Global : renderer
    p.container = pyOpenGL(p)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})

    p.windowHalfX = window.innerWidth / 2
    p.windowHalfY = window.innerHeight / 2

    p.camera = THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 1, 5000)
    p.camera.position.z = 2000

    # controls var
    p.controls = OrbitControls(p.camera, p.container)
    p.controls.enableZoom = False
    p.controls.enablePan = False
    p.controls.minPolarAngle = math.pi / 4
    p.controls.maxPolarAngle = math.pi / 1.5

    # cubemap

    cwd = os.path.dirname(os.path.abspath(__file__))
    path = cwd+"/textures/cube/SwedishRoyalCastle/"
    format = '.jpg'
    urls = [
            path + 'px' + format, path + 'nx' + format,
            path + 'py' + format, path + 'ny' + format,
            path + 'pz' + format, path + 'nz' + format
        ]

    reflectionCube = THREE.CubeTextureLoader().load(urls)
    reflectionCube.format = THREE.RGBFormat

    refractionCube = CubeTextureLoader().load( urls )
    refractionCube.mapping = THREE.CubeRefractionMapping
    refractionCube.format = THREE.RGBFormat

    p.scene = THREE.Scene()
    p.scene.background = reflectionCube

    # // LIGHTS
    ambient = THREE.AmbientLight(0xffffff)
    p.scene.add(ambient)

    p.pointLight = THREE.PointLight(0xffffff, 2)
    p.scene.add(p.pointLight)

    # materials
    cubeMaterial3 = THREE.MeshLambertMaterial({'color': 0xff6600, 'envMap': reflectionCube, 'combine': THREE.MixOperation, 'reflectivity': 0.3})
    cubeMaterial2 = THREE.MeshLambertMaterial({'color': 0xffee00, 'envMap': refractionCube, 'refractionRatio': 0.95})
    cubeMaterial1 = THREE.MeshLambertMaterial({'color': 0xffffff, 'envMap': reflectionCube})

    # models
    objLoader = OBJLoader()

    objLoader.setPath( cwd+'/models/obj/walt' )
    obj = objLoader.load( 'WaltHead.obj')

    head = obj.children[0]

    head.scale.multiplyScalar( 15 )
    head.position.y = -500
    head.material = cubeMaterial1

    head2 = head.clone()
    head2.position.x = - 900
    head2.material = cubeMaterial2

    head3 = head.clone()
    head3.position.x = 900
    head3.material = cubeMaterial3

    p.scene.add([head, head2, head3])

    p.container.addEventListener('resize', onWindowResize, False)

    
def onWindowResize(event, p):
    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()

    p.renderer.setSize(window.innerWidth, window.innerHeight)

    
# # //


def animate(p):
    render(p)


def render(p):
    p.renderer.render(p.scene, p.camera)


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
