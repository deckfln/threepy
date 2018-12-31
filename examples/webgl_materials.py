"""
        <title>three.js webgl - materials</title>
"""
from datetime import datetime
import random

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.container = None
        self.mesh = None
        self.pointLight = None
        self.objects = []
        self.materials = []


def init(p):
    # /// Global : renderer
    p.container = pyOpenGL(p)
    p.container.addEventListener('resize', onWindowResize, False)
    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})

    p.windowHalfX = window.innerWidth / 2
    p.windowHalfY = window.innerHeight / 2

    p.camera = THREE.PerspectiveCamera( 45, window.innerWidth / window.innerHeight, 1, 2000 )
    p.camera.position.set( 0, 200, 800 )

    p.scene = THREE.Scene()

    # Grid

    helper = THREE.GridHelper( 1000, 40, 0x303030, 0x303030 )
    helper.position.y = - 75
    p.scene.add( helper )

    # Materials

    texture = THREE.Texture( generateTexture() )
    texture.needsUpdate = True

    p.materials.append( THREE.MeshLambertMaterial( { 'map': texture, 'transparent': True } ) )
    p.materials.append( THREE.MeshLambertMaterial( { 'color': 0xdddddd } ) )
    p.materials.append( THREE.MeshPhongMaterial( { 'color': 0xdddddd, 'specular': 0x009900, 'shininess': 30, 'flatShading': True } ) )
    p.materials.append( THREE.MeshNormalMaterial() )
    p.materials.append( THREE.MeshBasicMaterial( { 'color': 0xffaa00, 'transparent': True, 'blending': THREE.AdditiveBlending } ) )
    p.materials.append( THREE.MeshBasicMaterial( { 'color': 0xff0000, 'blending': THREE.SubtractiveBlending } ) )

    p.materials.append( THREE.MeshLambertMaterial( { 'color': 0xdddddd } ) )
    p.materials.append( THREE.MeshPhongMaterial( { 'color': 0xdddddd, 'specular': 0x009900, 'shininess': 30, 'map': texture, 'transparent': True } ) )
    p.materials.append(THREE.MeshNormalMaterial({'flatShading': True}) )
    p.materials.append( THREE.MeshBasicMaterial( { 'color': 0xffaa00, 'wireframe': True } ) )
    p.materials.append( THREE.MeshDepthMaterial() )

    p.materials.append( THREE.MeshLambertMaterial( { 'color': 0x666666, 'emissive': 0xff0000 } ) )
    p.materials.append( THREE.MeshPhongMaterial( { 'color': 0x000000, 'specular': 0x666666, 'emissive': 0xff0000, 'shininess': 10, 'opacity': 0.9, 'transparent': True } ) )

    p.materials.append( THREE.MeshBasicMaterial( { 'map': texture, 'transparent': True } ) )

    # Spheres geometry

    geometry = THREE.SphereGeometry( 70, 32, 16 )

    for face in geometry.faces:
        face.materialIndex = int( random.random() * len(p.materials))

    geometry.sortFacesByMaterialIndex()

    for material in p.materials:
        addMesh(p, geometry, material )

    addMesh(p, geometry, p.materials )

    # Lights

    p.scene.add( THREE.AmbientLight( 0x111111 ) )

    directionalLight = THREE.DirectionalLight( 0xffffff, 0.125 )

    directionalLight.position.x = random.random() - 0.5
    directionalLight.position.y = random.random() - 0.5
    directionalLight.position.z = random.random() - 0.5
    directionalLight.position.normalize()

    p.scene.add( directionalLight )

    p.pointLight = THREE.PointLight( 0xffffff, 1 )
    p.scene.add( p.pointLight )

    p.pointLight.add( THREE.Mesh( THREE.SphereBufferGeometry( 4, 8, 8 ), THREE.MeshBasicMaterial( { 'color': 0xffffff } ) ) )


def addMesh(p, geometry, material ):
    mesh = THREE.Mesh( geometry, material )

    mesh.position.x = ( len(p.objects) % 4 ) * 200 - 400
    mesh.position.z = int( len(p.objects) / 4 ) * 200 - 200

    mesh.rotation.x = random.random() * 200 - 100
    mesh.rotation.y = random.random() * 200 - 100
    mesh.rotation.z = random.random() * 200 - 100

    p.objects.append( mesh )

    p.scene.add( mesh )


def onWindowResize(event, p):
    windowHalfX = window.innerWidth / 2
    windowHalfY = window.innerHeight / 2

    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()

    p.renderer.setSize(window.innerWidth, window.innerHeight)


def generateTexture():
    image = Image.new('RGBA', (256, 256))  # Create the image

    for x in range(256):
        for y in range(256):
            image.putpixel((x, y), (255, 255, 255, int(x ^ y)))

    return image


def animate(p):
    render(p)


def render(p):
    timer = -0.1 * datetime.now().timestamp()

    p.camera.position.x = math.cos( timer ) * 1000
    p.camera.position.z = math.sin( timer ) * 1000

    p.camera.lookAt( p.scene.position )

    for object in p.objects:
        object.rotation.x += 0.01
        object.rotation.y += 0.005

    p.materials[ len(p.materials) - 2 ].emissive.setHSL( 0.54, 1, 0.35 * ( 0.5 + 0.5 * math.sin( 35 * timer ) ) )
    p.materials[ len(p.materials) - 3 ].emissive.setHSL( 0.04, 1, 0.35 * ( 0.5 + 0.5 * math.cos( 35 * timer ) ) )

    p.pointLight.position.x = math.sin( timer * 7 ) * 300
    p.pointLight.position.y = math.cos( timer * 5 ) * 400
    p.pointLight.position.z = math.cos( timer * 3 ) * 300

    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener('animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
