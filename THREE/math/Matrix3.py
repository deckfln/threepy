"""
    /**
     * @author alteredq / http://alteredqualia.com/
     * @author WestLangley / http://github.com/WestLangley
     * @author bhouston / http://clara.io
     * @author tschw
     */
"""

from THREE.math.Vector3 import *
from THREE.pyOpenGLObject import *
import numpy as np


class Matrix3(pyOpenGLObject):
    isMatrix3 = True

    def __init__(self):
        self.elements = np.array([
            1, 0, 0,
            0, 1, 0,
            0, 0, 1
        ], dtype=np.float32)

        # self.matrix = self.elements.reshape(3, 3)

        super().__init__()
        self.set_class(isMatrix3)
        self.updated = True

    def set(self, n11, n12, n13, n21, n22, n23, n31, n32, n33):
        te = self.elements

        te[ 0 ] = n11; te[ 1 ] = n21; te[ 2 ] = n31
        te[ 3 ] = n12; te[ 4 ] = n22; te[ 5 ] = n32
        te[ 6 ] = n13; te[ 7 ] = n23; te[ 8 ] = n33

        return self

    def identity(self):
        self.set(
            1, 0, 0,
            0, 1, 0,
            0, 0, 1
        )
        return self

    def clone(self):
        return type(self)().fromArray( self.elements )

    def copy(self, m ):
        np.copyto(self.elements, m.elements)
        """
        te = self.elements
        me = m.elements
        
        te[ 0 ] = me[ 0 ]; te[ 1 ] = me[ 1 ]; te[ 2 ] = me[ 2 ]
        te[ 3 ] = me[ 3 ]; te[ 4 ] = me[ 4 ]; te[ 5 ] = me[ 5 ]
        te[ 6 ] = me[ 6 ]; te[ 7 ] = me[ 7 ]; te[ 8 ] = me[ 8 ]
        """

        return self

    def setFromMatrix4(self, m ):
        me = m.elements
        te = self.elements

        te[ 0 ] = me[0]; te[ 1 ] = me[4]; te[ 2 ] = me[8]
        te[ 3 ] = me[1]; te[ 4 ] = me[5]; te[ 5 ] = me[9]
        te[ 6 ] = me[2]; te[ 7 ] = me[6]; te[ 8 ] = me[10]
        return self

    def applyToBufferAttribute(self, attribute):
        global _v1
        for i in range(0, len(attribute.array), 3):
            _v1.np[0] = attribute.array[i]
            _v1.np[1] = attribute.array[i + 1]
            _v1.np[2] = attribute.array[i + 2]

            _v1.applyMatrix3( self )

            attribute.array[i] = _v1.np[0]
            attribute.array[i + 1] = _v1.np[1]
            attribute.array[i + 2] = _v1.np[2]

        return attribute

    def multiply(self, m ):
        return self.multiplyMatrices( self, m )

    def premultiply(self, m ):
        return self.multiplyMatrices( m, self )

    def multiplyMatrices(self, a, b ):
        amatrix = a.elements.reshape(3, 3)
        bmatrix = b.elements.reshape(3, 3)

        t = np.dot(bmatrix, amatrix)
        self.matrix = t
        self.elements = self.matrix.reshape(9)
        return self

    def multiplyScalar(self, s ):
        self.elements *= s

        """
        te = self.elements
        te[ 0 ] *= s; te[ 3 ] *= s; te[ 6 ] *= s
        te[ 1 ] *= s; te[ 4 ] *= s; te[ 7 ] *= s
        te[ 2 ] *= s; te[ 5 ] *= s; te[ 8 ] *= s
        """

        return self

    def determinant(self):
        te = self.elements

        a = te[ 0 ]; b = te[ 1 ]; c = te[ 2 ]
        d = te[ 3 ]; e = te[ 4 ]; f = te[ 5 ]
        g = te[ 6 ]; h = te[ 7 ]; i = te[ 8 ]

        return a * e * i - a * f * h - b * d * i + b * f * g + c * d * h - c * e * g

    def getInverse(self, matrix, throwOnDegenerate=None ):
        if cython:
            cVector3_getInverse(self.elements, matrix.elements)
        else:
            self._getInverse(matrix)
        return self

    def _getInverse(self, matrix, throwOnDegenerate=None ):
        if matrix and matrix.my_class(isMatrix4):
            print( "THREE.Matrix3: .getInverse() no longer takes a Matrix4 argument." )

        me = matrix.elements
        te = self.elements

        n11 = me[ 0 ]; n21 = me[ 1 ]; n31 = me[ 2 ]
        n12 = me[ 3 ]; n22 = me[ 4 ]; n32 = me[ 5 ]
        n13 = me[ 6 ]; n23 = me[ 7 ]; n33 = me[ 8 ]

        t11 = n33 * n22 - n32 * n23
        t12 = n32 * n13 - n33 * n12
        t13 = n23 * n12 - n22 * n13

        det = n11 * t11 + n21 * t12 + n31 * t13

        if det == 0:
            raise RuntimeWarning("THREE.Matrix3: .getInverse() can't invert matrix, determinant is 0")
            return self.identity()

        te[ 0 ] = t11
        te[ 1 ] = ( n31 * n23 - n33 * n21 )
        te[ 2 ] = ( n32 * n21 - n31 * n22 )

        te[ 3 ] = t12
        te[ 4 ] = ( n33 * n11 - n31 * n13 )
        te[ 5 ] = ( n31 * n12 - n32 * n11 )

        te[ 6 ] = t13
        te[ 7 ] = ( n21 * n13 - n23 * n11 )
        te[ 8 ] = ( n22 * n11 - n21 * n12 )

        if det != 1.0:
            self.elements /= det

        # a = inv(matrix.matrix).reshape(9)
        return self

    def transpose(self):
        m = self.elements

        tmp = m[ 1 ]; m[ 1 ] = m[ 3 ]; m[ 3 ] = tmp
        tmp = m[ 2 ]; m[ 2 ] = m[ 6 ]; m[ 6 ] = tmp
        tmp = m[ 5 ]; m[ 5 ] = m[ 7 ]; m[ 7 ] = tmp

        return self

    def getNormalMatrix(self, matrix4 ):
        return self.setFromMatrix4( matrix4 ).getInverse( self ).transpose()

    def transposeIntoArray(self, r ):
        m = self.elements

        r[ 0 ] = m[ 0 ]
        r[ 1 ] = m[ 3 ]
        r[ 2 ] = m[ 6 ]
        r[ 3 ] = m[ 1 ]
        r[ 4 ] = m[ 4 ]
        r[ 5 ] = m[ 7 ]
        r[ 6 ] = m[ 2 ]
        r[ 7 ] = m[ 5 ]
        r[ 8 ] = m[ 8 ]

        return self

    def setUvTransform(self, tx, ty, sx, sy, rotation, cx, cy ):
        c = math.cos( rotation )
        s = math.sin( rotation )

        self.set(
            sx * c, sx * s, - sx * ( c * cx + s * cy ) + cx + tx,
            - sy * s, sy * c, - sy * ( - s * cx + c * cy ) + cy + ty,
            0, 0, 1
        )

    def scale(self, sx, sy):
        te = self.elements

        te[ 0 ] *= sx
        te[ 3 ] *= sx
        te[ 6 ] *= sx
        te[ 1 ] *= sy
        te[ 4 ] *= sy
        te[ 7 ] *= sy

        return self

    def rotate(self, theta ):
        c = math.cos( theta )
        s = math.sin( theta )

        te = self.elements

        a11 = te[ 0 ]
        a12 = te[ 3 ]
        a13 = te[ 6 ]
        a21 = te[ 1 ]
        a22 = te[ 4 ]
        a23 = te[ 7 ]

        te[ 0 ] = c * a11 + s * a21
        te[ 3 ] = c * a12 + s * a22
        te[ 6 ] = c * a13 + s * a23

        te[ 1 ] = - s * a11 + c * a21
        te[ 4 ] = - s * a12 + c * a22
        te[ 7 ] = - s * a13 + c * a23

        return self

    def translate(self, tx, ty ):
        te = self.elements

        te[ 0 ] += tx * te[ 2 ]
        te[ 3 ] += tx * te[ 5 ]
        te[ 6 ] += tx * te[ 8 ]
        te[ 1 ] += ty * te[ 2 ]
        te[ 4 ] += ty * te[ 5 ]
        te[ 7 ] += ty * te[ 8 ]

        return self

    def equals(self, matrix ):
        te = self.elements
        me = matrix.elements

        """
        for i in range(9):
            if te[ i ] != me[ i ]:
                return False

        return True
        """

        return np.array_equal(te, me)

    def fromArray(self, array, offset=0 ):
        self.elements[0:9] = array[offset:offset + 9]
        """
        for i in range(9):
            self.elements[ i ] = array[ i + offset ]
        """
        return self

    def toArray(self, array=None, offset=0):
        if array is None:
            array = []

        te = self.elements

        array[ offset ] = te[ 0 ]
        array[ offset + 1 ] = te[ 1 ]
        array[ offset + 2 ] = te[ 2 ]

        array[ offset + 3 ] = te[ 3 ]
        array[ offset + 4 ] = te[ 4 ]
        array[ offset + 5 ] = te[ 5 ]

        array[ offset + 6 ] = te[ 6 ]
        array[ offset + 7 ] = te[ 7 ]
        array[ offset + 8 ] = te[ 8 ]

        return array


_v1 = Vector3()
