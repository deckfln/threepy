"""
        <title>three.js webgl - materials - cube reflection / refraction [Walt]</title>
        <p>Walt Disney head by <a href="http:# //davidoreilly.com/post/18087489343/disneyhead" target="_blank" rel="noopener">David OReilly</a>
        <p>Texture by <a href="http:# //www.humus.name/index.php?page=Textures" target="_blank" rel="noopener">Humus</a>
"""
from datetime import datetime

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.loaders.BinaryLoader import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.container = None
        self.mesh = None
        self.geometry = None
        self.loader = None
        self.pointLight = None
        self.mouseX = 0
        self.mouseY = 0
        self.windowHalfX = 0
        self.windowHalfY = 0


def createScene(geometry, m1, m2, m3, scene):
    s = 15

    mesh = THREE.Mesh(geometry, m1)
    mesh.position.z = - 100
    mesh.scale.x = mesh.scale.y = mesh.scale.z = s
    scene.add(mesh)

    mesh = THREE.Mesh(geometry, m2)
    mesh.position.x = - 900
    mesh.position.z = - 100
    mesh.scale.x = mesh.scale.y = mesh.scale.z = s
    scene.add(mesh)

    mesh = THREE.Mesh(geometry, m3)
    mesh.position.x = 900
    mesh.position.z = - 100
    mesh.scale.x = mesh.scale.y = mesh.scale.z = s
    scene.add(mesh)


def init(p):
    # /// Global : renderer
    p.container = pyOpenGL(p)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})

    p.windowHalfX = window.innerWidth / 2
    p.windowHalfY = window.innerHeight / 2

    p.container.addEventListener('mousemove', onDocumentMouseMove, False)

    p.camera = THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 1, 5000)
    p.camera.position.z = 2000

    # //

    path = "textures/cube/SwedishRoyalCastle/"
    format = '.jpg'
    urls = [
            path + 'px' + format, path + 'nx' + format,
            path + 'py' + format, path + 'ny' + format,
            path + 'pz' + format, path + 'nz' + format
        ]

    reflectionCube = THREE.CubeTextureLoader().load(urls)
    reflectionCube.format = THREE.RGBFormat

    p.scene = THREE.Scene()
    p.scene.background = reflectionCube

    # // LIGHTS

    ambient = THREE.AmbientLight(0xffffff)
    p.scene.add(ambient)

    p.pointLight = THREE.PointLight(0xffffff, 2)
    p.scene.add(p.pointLight)

    # // light representation

    sphere = THREE.SphereGeometry(100, 16, 8)

    p.mesh = THREE.Mesh(sphere, THREE.MeshBasicMaterial({'color': 0xffaa00}))
    p.mesh.scale.set(0.05, 0.05, 0.05)
    p.pointLight.add(p.mesh)

    refractionCube = THREE.CubeTextureLoader().load(urls)
    refractionCube.mapping = THREE.CubeRefractionMapping
    refractionCube.format = THREE.RGBFormat

    # //cubeMaterial3 = THREE.MeshPhongMaterial({ color: 0x000000, specular:0xaa0000, envMap: reflectionCube, combine: THREE.MixOperation, reflectivity: 0.25 })
    cubeMaterial3 = THREE.MeshLambertMaterial({'color': 0xff6600, 'envMap': reflectionCube, 'combine': THREE.MixOperation, 'reflectivity': 0.3})
    cubeMaterial2 = THREE.MeshLambertMaterial({'color': 0xffee00, 'envMap': refractionCube, 'refractionRatio': 0.95})
    cubeMaterial1 = THREE.MeshLambertMaterial({'color': 0xffffff, 'envMap': reflectionCube})

    # //
    def _create(geometry, material):
        createScene(geometry, cubeMaterial1, cubeMaterial2, cubeMaterial3, p.scene)

    loader = BinaryLoader()

    loader.load("obj/walt/WaltHead_bin.js", _create)

    # //

    p.container.addEventListener('resize', onWindowResize, False)

    
def onWindowResize(event, p):
    windowHalfX = window.innerWidth / 2
    windowHalfY = window.innerHeight / 2

    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()

    p.renderer.setSize(window.innerWidth, window.innerHeight)

    
def onDocumentMouseMove(event, p):
    p.mouseX = (event.clientX - p.windowHalfX) * 4
    p.mouseY = (event.clientY - p.windowHalfY) * 4


# # //


def animate(p):
    render(p)


def render(p):
    timer = -0.2 * datetime.now().timestamp()

    p.pointLight.position.x = 1500 * math.cos(timer)
    p.pointLight.position.z = 1500 * math.sin(timer)

    p.camera.position.x += (p.mouseX - p.camera.position.x) * .05
    p.camera.position.y += (- p.mouseY - p.camera.position.y) * .05

    p.camera.lookAt(p.scene.position)

    p.renderer.render(p.scene, p.camera)


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
