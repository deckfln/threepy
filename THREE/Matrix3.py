"""
    /**
     * @author alteredq / http://alteredqualia.com/
     * @author WestLangley / http://github.com/WestLangley
     * @author bhouston / http://clara.io
     * @author tschw
     */
"""

import math
from THREE.Vector3 import *
from THREE.pyOpenGLObject import *


class Matrix3(pyOpenGLObject):
    isMatrix3 = True

    def __init__(self):
        self.elements = [
            1, 0, 0,
            0, 1, 0,
            0, 0, 1
        ]

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
        te = self.elements
        me = m.elements

        te[ 0 ] = me[ 0 ]; te[ 1 ] = me[ 1 ]; te[ 2 ] = me[ 2 ]
        te[ 3 ] = me[ 3 ]; te[ 4 ] = me[ 4 ]; te[ 5 ] = me[ 5 ]
        te[ 6 ] = me[ 6 ]; te[ 7 ] = me[ 7 ]; te[ 8 ] = me[ 8 ]

        return self

    def setFromMatrix4(self, m ):
        me = m.elements
        self.set(
            me[ 0 ], me[ 4 ], me[  8 ],
            me[ 1 ], me[ 5 ], me[  9 ],
            me[ 2 ], me[ 6 ], me[ 10 ]
        )
        return self

    def applyToBufferAttribute(self, attribute):
        v1 = Vector3()
        for i in range(int(attribute.count)):
            v1.x = attribute.getX( i )
            v1.y = attribute.getY( i )
            v1.z = attribute.getZ( i )

            v1.applyMatrix3( self )

            attribute.setXYZ( i, v1.x, v1.y, v1.z )

        return attribute

    def multiply(self, m ):
        return self.multiplyMatrices( self, m )

    def  premultiply(self, m ):
        return self.multiplyMatrices( m, self )

    def multiplyMatrices(self, a, b ):
        ae = a.elements
        be = b.elements
        te = self.elements

        a11 = ae[ 0 ]; a12 = ae[ 3 ]; a13 = ae[ 6 ]
        a21 = ae[ 1 ]; a22 = ae[ 4 ]; a23 = ae[ 7 ]
        a31 = ae[ 2 ]; a32 = ae[ 5 ]; a33 = ae[ 8 ]

        b11 = be[ 0 ]; b12 = be[ 3 ]; b13 = be[ 6 ]
        b21 = be[ 1 ]; b22 = be[ 4 ]; b23 = be[ 7 ]
        b31 = be[ 2 ]; b32 = be[ 5 ]; b33 = be[ 8 ]

        te[ 0 ] = a11 * b11 + a12 * b21 + a13 * b31
        te[ 3 ] = a11 * b12 + a12 * b22 + a13 * b32
        te[ 6 ] = a11 * b13 + a12 * b23 + a13 * b33

        te[ 1 ] = a21 * b11 + a22 * b21 + a23 * b31
        te[ 4 ] = a21 * b12 + a22 * b22 + a23 * b32
        te[ 7 ] = a21 * b13 + a22 * b23 + a23 * b33

        te[ 2 ] = a31 * b11 + a32 * b21 + a33 * b31
        te[ 5 ] = a31 * b12 + a32 * b22 + a33 * b32
        te[ 8 ] = a31 * b13 + a32 * b23 + a33 * b33

        return self

    def multiplyScalar(self, s ):
        te = self.elements

        te[ 0 ] *= s; te[ 3 ] *= s; te[ 6 ] *= s
        te[ 1 ] *= s; te[ 4 ] *= s; te[ 7 ] *= s
        te[ 2 ] *= s; te[ 5 ] *= s; te[ 8 ] *= s

        return self

    def determinant(self):
        te = self.elements

        a = te[ 0 ]; b = te[ 1 ]; c = te[ 2 ]
        d = te[ 3 ]; e = te[ 4 ]; f = te[ 5 ]
        g = te[ 6 ]; h = te[ 7 ]; i = te[ 8 ]

        return a * e * i - a * f * h - b * d * i + b * f * g + c * d * h - c * e * g

    def  getInverse(self, matrix, throwOnDegenerate=None ):
        if matrix and matrix.isMatrix4:
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

        detInv = 1 / det

        te[ 0 ] = t11 * detInv
        te[ 1 ] = ( n31 * n23 - n33 * n21 ) * detInv
        te[ 2 ] = ( n32 * n21 - n31 * n22 ) * detInv

        te[ 3 ] = t12 * detInv
        te[ 4 ] = ( n33 * n11 - n31 * n13 ) * detInv
        te[ 5 ] = ( n31 * n12 - n32 * n11 ) * detInv

        te[ 6 ] = t13 * detInv
        te[ 7 ] = ( n21 * n13 - n23 * n11 ) * detInv
        te[ 8 ] = ( n22 * n11 - n21 * n12 ) * detInv

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

    def equals(self, matrix ):
        te = self.elements
        me = matrix.elements

        for i in range(9):
            if te[ i ] != me[ i ]:
                return False

        return True

    def fromArray(self, array, offset=0 ):
        for i in range(9):
            self.elements[ i ] = array[ i + offset ]

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