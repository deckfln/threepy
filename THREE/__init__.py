from THREE.RootObject import *
from THREE.Constants import *
from THREE.Vector2 import *
from THREE.Vector3 import *
from THREE.Vector4 import *
from THREE.Quaternion import *
from THREE.Matrix4 import *
from THREE.Matrix3 import *
from THREE.Euler import *
from THREE.Layers import *
from THREE.BufferGeometry import *
from THREE.Box3 import *
from THREE.Sphere import *
from THREE.BoxBufferGeometry import *
from THREE.BufferAttribute import *
from THREE.Color import *
from THREE.Object3D import *
from THREE.Camera import *
from THREE.ShaderChunk import *
from THREE.Material import *
from THREE.ShaderMaterial import *
from THREE.pyOpenGLState import *
from THREE.Uniforms import *
from THREE.pyOpenGL import *
from THREE.pyOpenGLProgram import *
from THREE.pyOpenGLPrograms import *


"""
    /**
     * @author mrdoob / http://mrdoob.com/
     */
"""
def arrayMax( array ):
    if len(array) == 0:
        return float('-inf')

    max = array[ 0 ]

    for i in range(len(array)):
        if array[ i ] > max:
            max = array[ i ]

    return max
