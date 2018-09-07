"""
webgl_buffergeometry
"""
from datetime import datetime

from THREE import *
from THREE.pyOpenGL.pyOpenGL import *


class Params:
    def __init__(self):
        self.camera = None
        self.scene = None
        self.renderer = None
        self.container = None
        self.mesh = None


def init(p):
    p.container = pyOpenGL(p)

    p.camera = THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 1, 3500)
    p.camera.position.z = 1750

    p.scene = THREE.Scene()
    p.scene.background = THREE.Color( 0x050505 )
    p.scene.fog = THREE.Fog( 0x050505, 2000, 3500 )

    #

    p.scene.add( THREE.AmbientLight( 0x444444 ) )

    light1 = THREE.DirectionalLight( 0xffffff, 0.5 )
    light1.position.set( 1, 1, 1 )
    p.scene.add( light1 )

    light2 = THREE.DirectionalLight( 0xffffff, 1.5 )
    light2.position.set( 0, -1, 0 )
    p.scene.add( light2 )

    #

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

    p.mesh = THREE.Mesh( geometry, material )
    p.scene.add( p.mesh )

    #

    p.renderer = THREE.pyOpenGLRenderer({'antialias': True})
    p.renderer.setSize( window.innerWidth, window.innerHeight )

    #

    p.container.addEventListener( 'resize', onWindowResize, False )


def onWindowResize(event, params):
    params.camera.aspect = window.innerWidth / window.innerHeight
    params.camera.updateProjectionMatrix()

    params.renderer.setSize( window.innerWidth, window.innerHeight )


def animate(p):
    render(p)


def render(p):
    time = datetime.now().timestamp() * 1

    p.mesh.rotation.x = time * 0.25
    p.mesh.rotation.y = time * 0.5

    p.renderer.render( p.scene, p.camera )


def main(argv=None):
    params = Params()

    init(params)
    params.container.addEventListener( 'animationRequest', animate)
    return params.container.loop()


if __name__ == "__main__":
    sys.exit(main())
