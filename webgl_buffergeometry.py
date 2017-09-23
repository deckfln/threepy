"""
webgl_buffergeometry
"""
from datetime import datetime

from THREE import *

camera = None
scene=None
renderer=None
mesh = None


def init():
    global camera, renderer, mesh, scene
    # //
    renderer = pyOpenGLRenderer(None, reshape, render, keyboard, mouse, motion, animate)
    width, height = renderer.screen_size()

    renderer.setPixelRatio( 1 )
    renderer.setSize( width, height )

    renderer.gammaInput = True
    renderer.gammaOutput = True

    camera = THREE.PerspectiveCamera( 27, width / height, 1, 3500 )
    camera.position.z = 2750

    scene = THREE.Scene()
    scene.background = THREE.Color( 0x050505 )
    scene.fog = THREE.Fog( 0x050505, 2000, 3500 )

    # //

    scene.add( THREE.AmbientLight( 0x444444 ) )

    light1 = THREE.DirectionalLight( 0xffffff, 0.5 )
    light1.position.set( 1, 1, 1 )
    scene.add( light1 )

    light2 = THREE.DirectionalLight( 0xffffff, 1.5 )
    light2.position.set( 0, -1, 0 )
    scene.add( light2 )

    # //

    triangles = 160000

    geometry = THREE.BufferGeometry()

    positions = Float32Array( triangles * 3 * 3 )
    normals = Float32Array( triangles * 3 * 3 )
    colors = Float32Array( triangles * 3 * 3 )

    color = THREE.Color()

    n = 800
    n2 = n/2    #    // triangles spread in the cube
    d = 12
    d2 = d/2    #    // individual triangle size

    pA = THREE.Vector3()
    pB = THREE.Vector3()
    pC = THREE.Vector3()

    cb = THREE.Vector3()
    ab = THREE.Vector3()

    for i in range(0, len(positions), 9 ):

        # // positions

        x = random.random() * n - n2
        y = random.random() * n - n2
        z = random.random() * n - n2

        ax = x + random.random() * d - d2
        ay = y + random.random() * d - d2
        az = z + random.random() * d - d2

        bx = x + random.random() * d - d2
        by = y + random.random() * d - d2
        bz = z + random.random() * d - d2

        cx = x + random.random() * d - d2
        cy = y + random.random() * d - d2
        cz = z + random.random() * d - d2

        positions[ i ]     = ax
        positions[ i + 1 ] = ay
        positions[ i + 2 ] = az

        positions[ i + 3 ] = bx
        positions[ i + 4 ] = by
        positions[ i + 5 ] = bz

        positions[ i + 6 ] = cx
        positions[ i + 7 ] = cy
        positions[ i + 8 ] = cz

        # // flat face normals

        pA.set( ax, ay, az )
        pB.set( bx, by, bz )
        pC.set( cx, cy, cz )

        cb.subVectors( pC, pB )
        ab.subVectors( pA, pB )
        cb.cross( ab )

        cb.normalize()

        nx = cb.x
        ny = cb.y
        nz = cb.z

        normals[ i ]     = nx
        normals[ i + 1 ] = ny
        normals[ i + 2 ] = nz

        normals[ i + 3 ] = nx
        normals[ i + 4 ] = ny
        normals[ i + 5 ] = nz

        normals[ i + 6 ] = nx
        normals[ i + 7 ] = ny
        normals[ i + 8 ] = nz

        # // colors

        vx = ( x / n ) + 0.5
        vy = ( y / n ) + 0.5
        vz = ( z / n ) + 0.5

        color.setRGB( vx, vy, vz )

        colors[ i ]     = color.r
        colors[ i + 1 ] = color.g
        colors[ i + 2 ] = color.b

        colors[ i + 3 ] = color.r
        colors[ i + 4 ] = color.g
        colors[ i + 5 ] = color.b

        colors[ i + 6 ] = color.r
        colors[ i + 7 ] = color.g
        colors[ i + 8 ] = color.b

    geometry.addAttribute( 'position', THREE.BufferAttribute( positions, 3 ) )
    geometry.addAttribute( 'normal', THREE.BufferAttribute( normals, 3 ) )
    geometry.addAttribute( 'color', THREE.BufferAttribute( colors, 3 ) )

    geometry.computeBoundingSphere()

    material = THREE.MeshPhongMaterial( {
        'color': 0xaaaaaa,
        'specular': 0xffffff,
        'shininess': 250,
        'side': THREE.DoubleSide,
        'vertexColors': THREE.VertexColors
    } )

    mesh = THREE.Mesh( geometry, material )
    scene.add( mesh )

    # //

    return renderer

def reshape(width, height):
    """window reshape callback."""
    global camera, renderer

    camera.aspect = width / height
    camera.updateProjectionMatrix()

    renderer.setSize(width, height)

    glViewport(0, 0, width, height)


def animate():
    render()


def render():
    global camera, mesh, renderer
    
    time = datetime.now().timestamp() * 0.01

    mesh.rotation.x = time * 0.25
    mesh.rotation.y = time * 0.5

    renderer.render( scene, camera )


def mouse(button, state, x, y):
    if button == GLUT_LEFT_BUTTON:
        rotating = (state == GLUT_DOWN)
    elif button == GLUT_RIGHT_BUTTON:
        scaling = (state == GLUT_DOWN)


def motion(x1, y1):
    glutPostRedisplay()


def keyboard(c, x=0, y=0):
    """keyboard callback."""

    if c == b'q':
        sys.exit(0)

    glutPostRedisplay()


"""
"""
def main(argv=None):
    global renderer, camera, scene

    renderer = init()
    return renderer.loop()


if __name__ == "__main__":
    sys.exit(main())
