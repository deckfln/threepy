"""
    /**
     * @author alteredq / http://alteredqualia.com/
     */
"""
from THREE.objects.Group import *
from THREE.objects.Mesh import *
from THREE.math.Matrix4 import *


def createMultiMaterialObject( geometry, materials ):
    group = Group()

    for i in range(len(materials)):
        group.add( Mesh( geometry, materials[ i ] ) )

    return group


def detach( child, parent, scene ):
    child.applyMatrix( parent.matrixWorld )
    parent.remove( child )
    scene.add( child )

def attach( child, scene, parent ):
    child.applyMatrix( Matrix4().getInverse( parent.matrixWorld ) )

    scene.remove( child )
    parent.add( child )