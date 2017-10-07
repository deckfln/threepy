"""
        <title>three.js webgl - geometry - vertex colors</title>
"""
from PIL import Image
from THREE import *
from THREE.pyOpenGL.pyOpenGL import *

import math

container = None

camera=None
scene=None
renderer=None

mesh=None
group1=None
group2=None
group3=None
light=None

mouseX = 0
mouseY = 0

windowHalfX = 0
windowHalfY = 0


def init():
    global container,camera,scene,renderer,mesh,group1,group2,group3,light,windowHalfX,windowHalfY

    container = pyOpenGL()

    windowHalfX = window.innerWidth / 2
    windowHalfY = window.innerHeight / 2

    camera = THREE.PerspectiveCamera( 20, window.innerWidth / window.innerHeight, 1, 10000 )
    camera.position.z = 1800

    scene = THREE.Scene()
    scene.background = THREE.Color( 0xffffff )

    light = THREE.DirectionalLight( 0xffffff )
    light.position.set( 0, 0, 1 )
    scene.add( light )

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
    scene.add( mesh )

    mesh = THREE.Mesh( shadowGeo, shadowMaterial )
    mesh.position.y = - 250
    mesh.position.x = - 400
    mesh.rotation.x = - math.pi / 2
    scene.add( mesh )

    mesh = THREE.Mesh( shadowGeo, shadowMaterial )
    mesh.position.y = - 250
    mesh.position.x = 400
    mesh.rotation.x = - math.pi / 2
    scene.add( mesh )

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

            p = geometry.vertices[ vertexIndex ]

            color = THREE.Color( 0xffffff )
            color.setHSL( ( p.y / radius + 1 ) / 2, 1.0, 0.5 )

            f.vertexColors.append(color)

            color = THREE.Color( 0xffffff )
            color.setHSL( 0.0, ( p.y / radius + 1 ) / 2, 0.5 )

            f2.vertexColors.append(color)

            color = THREE.Color( 0xffffff )
            color.setHSL( 0.125 * vertexIndex/len(geometry.vertices), 1.0, 0.5 )

            f3.vertexColors.append(color)

    materials = [

        THREE.MeshPhongMaterial( { 'color': 0xffffff, 'flatShading': True, 'vertexColors': THREE.VertexColors, 'shininess': 0 } ),
        THREE.MeshBasicMaterial( { 'color': 0x000000, 'wireframe': True, 'transparent': True } )

    ]

    group1 = THREE.SceneUtils.createMultiMaterialObject( geometry, materials )
    group1.position.x = -400
    group1.rotation.x = -1.87
    scene.add( group1 )

    group2 = THREE.SceneUtils.createMultiMaterialObject( geometry2, materials )
    group2.position.x = 400
    group2.rotation.x = 0
    scene.add( group2 )

    group3 = THREE.SceneUtils.createMultiMaterialObject( geometry3, materials )
    group3.position.x = 0
    group3.rotation.x = 0
    scene.add( group3 )

    renderer = THREE.pyOpenGLRenderer( { 'antialias': True } )
    renderer.setSize( window.innerWidth, window.innerHeight )

    container.addEventListener( 'mousemove', onDocumentMouseMove, False )

    # //

    container.addEventListener( 'resize', onWindowResize, False )


def onWindowResize(event, params):
    global container,camera,scene,renderer,mesh,group1,group2,group3,light,windowHalfX,windowHalfY

    windowHalfX = window.innerWidth / 2
    windowHalfY = window.innerHeight / 2

    camera.aspect = window.innerWidth / window.innerHeight
    camera.updateProjectionMatrix()

    renderer.setSize( window.innerWidth, window.innerHeight )

    
def onDocumentMouseMove( event, params ):
    global container,camera,scene,renderer,mesh,group1,group2,group3,light, mouseX, mouseY

    mouseX = ( event.clientX - windowHalfX )
    mouseY = ( event.clientY - windowHalfY )

# //

def animate(params):
    global container,camera,scene,renderer,mesh,group1,group2,group3,light

    render(params)

def render(params):
    global container,camera,scene,renderer,mesh,group1,group2,group3,light

    camera.position.x += ( mouseX - camera.position.x ) * 0.05
    camera.position.y += ( - mouseY - camera.position.y ) * 0.05

    camera.lookAt( scene.position )

    renderer.render( scene, camera )



def main(argv=None):
    global container
    init()
    container.addEventListener( 'animationRequest', animate)
    return container.loop()


if __name__ == "__main__":
    sys.exit(main())
