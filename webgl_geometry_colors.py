"""
        <title>three.js webgl - geometry - vertex colors</title>
"""
from PIL import Image
from THREE import *

import math
from THREE.pyOpenGL.pyOpenGL import *


class Params:
    def __init__(self):
        self.container = None
        self.camera=None
        self.scene=None
        self.renderer=None
        self.mesh=None
        self.group1=None
        self.group2=None
        self.group3=None
        self.light=None
        self.mouseX = 0
        self.mouseY = 0
        self.windowHalfX = 0
        self.windowHalfY = 0


def init(p):
    p.container = pyOpenGL(p)

    p.windowHalfX = window.innerWidth / 2
    p.windowHalfY = window.innerHeight / 2

    p.camera = THREE.PerspectiveCamera( 20, window.innerWidth / window.innerHeight, 1, 10000 )
    p.camera.position.z = 1800

    p.scene = THREE.Scene()
    p.scene.background = THREE.Color( 0xffffff )

    p.light = THREE.DirectionalLight( 0xffffff )
    p.light.position.set( 0, 0, 1 )
    p.scene.add( p.light )

    # // shadow
    #  https: // stackoverflow.com / questions / 30608035 / plot - gradients - using - pil - in -python
    image = Image.new('RGBA', (128, 128))  # Create the image
    innerColor = [210, 210, 210]  # Color at the center
    outerColor = [255, 255, 255]  # Color at the corners

    for y in range(128):
        for x in range(128):
            # Find the distance to the center
            distanceToCenter = math.sqrt((x - 128 / 2) ** 2 + (y - 128 / 2) ** 2)

            # Make it on a scale from 0 to 1
            distanceToCenter = float(distanceToCenter) / (math.sqrt(2) * 128 / 2)

            # Calculate r, g, and b values
            r = outerColor[0] * distanceToCenter + innerColor[0] * (1 - distanceToCenter)
            g = outerColor[1] * distanceToCenter + innerColor[1] * (1 - distanceToCenter)
            b = outerColor[2] * distanceToCenter + innerColor[2] * (1 - distanceToCenter)

            # Place the pixel
            image.putpixel((x, y), (int(r), int(g), int(b)))

    shadowTexture = THREE.Texture( image )
    shadowTexture.needsUpdate = True

    shadowMaterial = THREE.MeshBasicMaterial( { 'map': shadowTexture } )
    shadowGeo = THREE.PlaneBufferGeometry( 300, 300, 1, 1 )

    mesh = THREE.Mesh( shadowGeo, shadowMaterial )
    mesh.position.y = - 250
    mesh.rotation.x = - math.pi / 2
    p.scene.add( mesh )

    mesh = THREE.Mesh( shadowGeo, shadowMaterial )
    mesh.position.y = - 250
    mesh.position.x = - 400
    mesh.rotation.x = - math.pi / 2
    p.scene.add( mesh )

    mesh = THREE.Mesh( shadowGeo, shadowMaterial )
    mesh.position.y = - 250
    mesh.position.x = 400
    mesh.rotation.x = - math.pi / 2
    p.scene.add( mesh )

    faceIndices = [ 'a', 'b', 'c' ]

    radius = 200

    geometry  = THREE.IcosahedronGeometry( radius, 1 )
    geometry2 = THREE.IcosahedronGeometry( radius, 1 )
    geometry3 = THREE.IcosahedronGeometry( radius, 1 )

    for i in range(len(geometry.faces)):
        f  = geometry.faces[ i ]
        f2 = geometry2.faces[ i ]
        f3 = geometry3.faces[ i ]

        for j in range(3):
            vertexIndex = f[ faceIndices[ j ] ]

            v = geometry.vertices[ vertexIndex ]

            color = THREE.Color( 0xffffff )
            color.setHSL( ( v.y / radius + 1 ) / 2, 1.0, 0.5 )

            f.vertexColors.append(color)

            color = THREE.Color( 0xffffff )
            color.setHSL( 0.0, ( v.y / radius + 1 ) / 2, 0.5 )

            f2.vertexColors.append(color)

            color = THREE.Color( 0xffffff )
            color.setHSL( 0.125 * vertexIndex/len(geometry.vertices), 1.0, 0.5 )

            f3.vertexColors.append(color)

    materials = [

        THREE.MeshPhongMaterial( { 'color': 0xffffff, 'flatShading': True, 'vertexColors': THREE.VertexColors, 'shininess': 0 } ),
        THREE.MeshBasicMaterial( { 'color': 0x000000, 'wireframe': True, 'transparent': True } )

    ]

    p.group1 = THREE.SceneUtils.createMultiMaterialObject( geometry, materials )
    p.group1.position.x = -400
    p.group1.rotation.x = -1.87
    p.scene.add( p.group1 )

    p.group2 = THREE.SceneUtils.createMultiMaterialObject( geometry2, materials )
    p.group2.position.x = 400
    p.group2.rotation.x = 0
    p.scene.add( p.group2 )

    p.group3 = THREE.SceneUtils.createMultiMaterialObject( geometry3, materials )
    p.group3.position.x = 0
    p.group3.rotation.x = 0
    p.scene.add( p.group3 )

    p.renderer = THREE.pyOpenGLRenderer( { 'antialias': True } )
    p.renderer.setSize( window.innerWidth, window.innerHeight )

    p.container.addEventListener( 'mousemove', onDocumentMouseMove, False )

    # //

    p.container.addEventListener( 'resize', onWindowResize, False )


def onWindowResize(event, p):
    p.windowHalfX = window.innerWidth / 2
    p.windowHalfY = window.innerHeight / 2

    p.camera.aspect = window.innerWidth / window.innerHeight
    p.camera.updateProjectionMatrix()

    p.renderer.setSize( window.innerWidth, window.innerHeight )

    
def onDocumentMouseMove( event, p ):
    p.mouseX = ( event.clientX - p.windowHalfX )
    p.mouseY = ( event.clientY - p.windowHalfY )


def animate(p):
    render(p)


def render(p):
    p.camera.position.x += ( p.mouseX - p.camera.position.x ) * 0.05
    p.camera.position.y += ( - p.mouseY - p.camera.position.y ) * 0.05

    p.camera.lookAt( p.scene.position )

    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
