"""
        <title>three.js webgl - io blender - vertex colors</title>
"""
from THREE import *
from THREE.pyOpenGL.pyOpenGL import *
from THREE.Javascript import *


params = javascriptObject({})


def init(param):
    container = pyOpenGL(params)

    camera = THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 1, 10000)
    camera.position.z = 1800

    params.scene = scene = THREE.Scene()

    light = THREE.DirectionalLight(0xffffff)
    light.position.set(0, 0, 1).normalize()
    scene.add(light)

    loader = THREE.JSONLoader()

    loader.load("obj/cubecolors/cubecolors.js", createScene1)
    loader.load("obj/cubecolors/cube_fvc.js", createScene2)

    renderer = THREE.pyOpenGLRenderer({'antialias': True})
    renderer.setSize(window.innerWidth, window.innerHeight)

    container.addEventListener('mousemove', onDocumentMouseMove, False)

    container.addEventListener('resize', onWindowResize, False)

    param.container  = container
    param.camera = camera
    param.scene = scene
    param.renderer = renderer

    param.light = light

    param.mouseX = 0
    param.mouseY = 0

    param.windowHalfX = window.innerWidth / 2
    param.windowHalfY = window.innerHeight / 2


def onWindowResize(event, param):
    param.windowHalfX = window.innerWidth / 2
    param.windowHalfY = window.innerHeight / 2

    param.camera.aspect = window.innerWidth / window.innerHeight
    param.camera.updateProjectionMatrix()

    param.renderer.setSize(window.innerWidth, window.innerHeight)

    
def createScene1(geometry, materials):
    global params

    params.mesh = THREE.Mesh(geometry, materials)
    params.mesh.position.x = 400
    params.mesh.scale.x = params.mesh.scale.y = params.mesh.scale.z = 250
    params.scene.add(params.mesh)


def createScene2(geometry, materials):
    global params

    params.mesh2 = THREE.Mesh(geometry, materials)
    params.mesh2.position.x = - 400
    params.mesh2.scale.x = params.mesh2.scale.y = params.mesh2.scale.z = 250
    params.scene.add(params.mesh2)


def onDocumentMouseMove(event, param):
    param.mouseX = (event.clientX - param.windowHalfX)
    param.mouseY = (event.clientY - param.windowHalfY)


def animate(param):
    render(param)

    
def render(param):
    param.camera.position.x += (param.mouseX - param.camera.position.x) * 0.05
    param.camera.position.y += (- param.mouseY - param.camera.position.y) * 0.05

    param.camera.lookAt(param.scene.position)

    if param.mesh:
        param.mesh.rotation.x += 0.01
        param.mesh.rotation.y += 0.01

    if param.mesh2:
        param.mesh2.rotation.x += 0.01
        param.mesh2.rotation.y += 0.01

    param.renderer.render(param.scene, param.camera)


def main(argv=None):
    global container

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
