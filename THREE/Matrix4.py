"""
    /**
     * @author mrdoob / http://mrdoob.com/
     * @author supereggbert / http://www.paulbrunt.co.uk/
     * @author philogb / http://blog.thejit.org/
     * @author jordi_ros / http://plattsoft.com
     * @author D1plo1d / http://github.com/D1plo1d
     * @author alteredq / http://alteredqualia.com/
     * @author mikael emtinger / http://gomo.se/
     * @author timknip / http://www.floorplanner.com/
     * @author bhouston / http://clara.io
     * @author WestLangley / http://github.com/WestLangley
     */
"""
import math
from THREE.Vector3 import *
from THREE.pyOpenGLObject import *
from THREE.cython.cthree import *

_temp = np.array([0, 0, 0, 1.0, 0, 0, 0, 1.0, 0, 0, 0, 1.0, 1.0, 1.0, 1.0, 1.0])


class Matrix4(pyOpenGLObject):
    isMatrix4 = True

    def __init__(self):
        super().__init__()
        self.set_class(isMatrix4)

        self.elements = np.array([
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
            ], dtype=np.float64)
        self.matrix = self.elements.reshape(4, 4)

        self.old = np.zeros(16, dtype=np.float64)
        self.updated = True

    def is_updated(self):
        """
        Check if the matrix got updated and set the flag
        :return:
        """
        if not np.array_equal(self.elements, self.old):
            self.updated = True
            np.copyto(self.old, self.elements)
        else:
            self.updated = False

        return self.updated

    def set(self, n11, n12, n13, n14, n21, n22, n23, n24, n31, n32, n33, n34, n41, n42, n43, n44):
        te = self.elements

        te[0] = n11; te[4] = n12; te[8] = n13; te[12] = n14
        te[1] = n21; te[5] = n22; te[9] = n23; te[13] = n24
        te[2] = n31; te[6] = n32; te[10] = n33; te[14] = n34
        te[3] = n41; te[7] = n42; te[11] = n43; te[15] = n44

        return self

    def get(self):
        return [
            [self.elements[0], self.elements[1], self.elements[2], self.elements[3]],
            [self.elements[4], self.elements[5], self.elements[6], self.elements[7]],
            [self.elements[8], self.elements[9], self.elements[10], self.elements[11]],
            [self.elements[12], self.elements[13], self.elements[14], self.elements[15]]
       ]
    
    def identity(self):
            self.set(
                1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, 0, 0, 1
           )
            return self

    def clone(self):
        return type(self)().fromArray(self.elements)

    def copy(self, m):
        np.copyto(self.elements, m.elements)
        """
        te = self.elements
        me = m.elements
        
        te[0] = me[0]; te[1] = me[1]; te[2] = me[2]; te[3] = me[3]
        te[4] = me[4]; te[5] = me[5]; te[6] = me[6]; te[7] = me[7]
        te[8] = me[8]; te[9] = me[9]; te[10] = me[10]; te[11] = me[11]
        te[12] = me[12]; te[13] = me[13]; te[14] = me[14]; te[15] = me[15]
        """
        return self

    def copyPosition(self, m):
        te = self.elements
        me = m.elements

        te[12] = me[12]
        te[13] = me[13]
        te[14] = me[14]

        return self

    def extractBasis(self, xAxis, yAxis, zAxis):
        xAxis.setFromMatrixColumn(self, 0)
        yAxis.setFromMatrixColumn(self, 1)
        zAxis.setFromMatrixColumn(self, 2)

        return self

    def makeBasis(self, xAxis, yAxis, zAxis):
        self.set(
            xAxis.x, yAxis.x, zAxis.x, 0,
            xAxis.y, yAxis.y, zAxis.y, 0,
            xAxis.z, yAxis.z, zAxis.z, 0,
            0,       0,       0,       1
       )
        return self

    def extractRotation(self, m):
        v1 = Vector3()
        te = self.elements
        me = m.elements

        scaleX = 1 / v1.setFromMatrixColumn(m, 0).length()
        scaleY = 1 / v1.setFromMatrixColumn(m, 1).length()
        scaleZ = 1 / v1.setFromMatrixColumn(m, 2).length()

        te[0] = me[0] * scaleX
        te[1] = me[1] * scaleX
        te[2] = me[2] * scaleX

        te[4] = me[4] * scaleY
        te[5] = me[5] * scaleY
        te[6] = me[6] * scaleY

        te[8] = me[8] * scaleZ
        te[9] = me[9] * scaleZ
        te[10] = me[10] * scaleZ

        return self

    def makeRotationFromEuler(self, euler):
        if not (euler and euler.isEuler):
            print('THREE.Matrix4: .makeRotationFromEuler() now expects a Euler rotation rather than a Vector3 and order.')

        te = self.elements

        x = euler.x; y = euler.y; z = euler.z
        a = math.cos(x)
        b = math.sin(x)
        c = math.cos(y)
        d = math.sin(y)
        e = math.cos(z)
        f = math.sin(z)

        if euler.order == 'XYZ':
            ae = a * e
            af = a * f
            be = b * e
            bf = b * f
            te[0] = c * e
            te[4] = - c * f
            te[8] = d

            te[1] = af + be * d
            te[5] = ae - bf * d
            te[9] = - b * c

            te[2] = bf - ae * d
            te[6] = be + af * d
            te[10] = a * c
        elif euler.order == 'YXZ':
            ce = c * e
            cf = c * f
            de = d * e
            df = d * f

            te[0] = ce + df * b
            te[4] = de * b - cf
            te[8] = a * d

            te[1] = a * f
            te[5] = a * e
            te[9] = - b

            te[2] = cf * b - de
            te[6] = df + ce * b
            te[10] = a * c
        elif euler.order == 'ZXY':
            ce = c * e
            cf = c * f
            de = d * e
            df = d * f

            te[0] = ce - df * b
            te[4] = - a * f
            te[8] = de + cf * b

            te[1] = cf + de * b
            te[5] = a * e
            te[9] = df - ce * b

            te[2] = - a * d
            te[6] = b
            te[10] = a * c
        elif euler.order == 'ZYX':
            ae = a * e
            af = a * f
            be = b * e
            bf = b * f

            te[0] = c * e
            te[4] = be * d - af
            te[8] = ae * d + bf

            te[1] = c * f
            te[5] = bf * d + ae
            te[9] = af * d - be

            te[2] = - d
            te[6] = b * c
            te[10] = a * c
        elif euler.order == 'YZX':
            ac = a * c
            ad = a * d
            bc = b * c
            bd = b * d

            te[0] = c * e
            te[4] = bd - ac * f
            te[8] = bc * f + ad

            te[1] = f
            te[5] = a * e
            te[9] = - b * e

            te[2] = - d * e
            te[6] = ad * f + bc
            te[10] = ac - bd * f
        elif euler.order == 'XZY':
            ac = a * c
            ad = a * d
            bc = b * c
            bd = b * d

            te[0] = c * e
            te[4] = - f
            te[8] = d * e

            te[1] = ac * f + bd
            te[5] = a * e
            te[9] = ad * f - bc

            te[2] = bc * f - ad
            te[6] = b * e
            te[10] = bd * f + ac

        # // last column
        te[3] = 0
        te[7] = 0
        te[11] = 0

        # // bottom row
        te[12] = 0
        te[13] = 0
        te[14] = 0
        te[15] = 1

        return self

    def makeRotationFromQuaternion(self, q):
        te = self.elements
        x = q._x; y = q._y; z = q._z; w = q._w
        c_Matrix4_makeRotationFromQuaternion(te, x, y, z, w)

        return self

    def _makeRotationFromQuaternion(self, q):
        te = self.elements

        x = q._x; y = q._y; z = q._z; w = q._w
        x2 = x + x; y2 = y + y; z2 = z + z
        xx = x * x2; xy = x * y2; xz = x * z2
        yy = y * y2; yz = y * z2; zz = z * z2
        wx = w * x2; wy = w * y2; wz = w * z2

        te[0] = 1 - (yy + zz)
        te[4] = xy - wz
        te[8] = xz + wy

        te[1] = xy + wz
        te[5] = 1 - (xx + zz)
        te[9] = yz - wx

        te[2] = xz - wy
        te[6] = yz + wx
        te[10] = 1 - (xx + yy)

        # // last column
        te[3] = 0
        te[7] = 0
        te[11] = 0

        # // bottom row
        te[12] = 0
        te[13] = 0
        te[14] = 0
        te[15] = 1

        return self

    def lookAt(self, eye, target, up):
        x = THREE.Vector3()
        y = THREE.Vector3()
        z = THREE.Vector3()

        te = self.elements

        z.subVectors(eye, target)

        if z.lengthSq() == 0:
            # // eye and target are in the same position
            z.z = 1

        z.normalize()
        x.crossVectors(up, z)

        if x.lengthSq() == 0:
            # // up and z are parallel
            if abs(up.z) == 1:
                z.x += 0.0001
            else:
                z.z += 0.0001

            z.normalize()
            x.crossVectors(up, z)

        x.normalize()
        y.crossVectors(z, x)

        te[0] = x.np[0]; te[4] = y.np[0]; te[8] = z.np[0]
        te[1] = x.np[1]; te[5] = y.np[1]; te[9] = z.np[1]
        te[2] = x.np[2]; te[6] = y.np[2]; te[10] = z.np[2]

        return self

    def multiply(self, m, n=None):
        if n is not None:
            print('THREE.Matrix4: .multiply() now only accepts one argument. Use .multiplyMatrices(a, b) instead.')
            return self.multiplyMatrices(m, n)

        return self.multiplyMatrices(self, m)

    def premultiply(self, m):
        return self.multiplyMatrices(m, self)

    def multiplyMatrices(self, a, b):
        amatrix = a.elements.reshape(4, 4)
        bmatrix = b.elements.reshape(4, 4)

        t = np.dot(bmatrix, amatrix)
        self.matrix = t
        self.elements = self.matrix.reshape(16)


        """
        ae = a.elements
        be = b.elements
        te = self.elements

        a11 = ae[0]; a12 = ae[4]; a13 = ae[8]; a14 = ae[12]
        a21 = ae[1]; a22 = ae[5]; a23 = ae[9]; a24 = ae[13]
        a31 = ae[2]; a32 = ae[6]; a33 = ae[10]; a34 = ae[14]
        a41 = ae[3]; a42 = ae[7]; a43 = ae[11]; a44 = ae[15]

        b11 = be[0]; b12 = be[4]; b13 = be[8]; b14 = be[12]
        b21 = be[1]; b22 = be[5]; b23 = be[9]; b24 = be[13]
        b31 = be[2]; b32 = be[6]; b33 = be[10]; b34 = be[14]
        b41 = be[3]; b42 = be[7]; b43 = be[11]; b44 = be[15]

        te[0] = a11 * b11 + a12 * b21 + a13 * b31 + a14 * b41
        te[4] = a11 * b12 + a12 * b22 + a13 * b32 + a14 * b42
        te[8] = a11 * b13 + a12 * b23 + a13 * b33 + a14 * b43
        te[12] = a11 * b14 + a12 * b24 + a13 * b34 + a14 * b44

        te[1] = a21 * b11 + a22 * b21 + a23 * b31 + a24 * b41
        te[5] = a21 * b12 + a22 * b22 + a23 * b32 + a24 * b42
        te[9] = a21 * b13 + a22 * b23 + a23 * b33 + a24 * b43
        te[13] = a21 * b14 + a22 * b24 + a23 * b34 + a24 * b44

        te[2] = a31 * b11 + a32 * b21 + a33 * b31 + a34 * b41
        te[6] = a31 * b12 + a32 * b22 + a33 * b32 + a34 * b42
        te[10] = a31 * b13 + a32 * b23 + a33 * b33 + a34 * b43
        te[14] = a31 * b14 + a32 * b24 + a33 * b34 + a34 * b44

        te[3] = a41 * b11 + a42 * b21 + a43 * b31 + a44 * b41
        te[7] = a41 * b12 + a42 * b22 + a43 * b32 + a44 * b42
        te[11] = a41 * b13 + a42 * b23 + a43 * b33 + a44 * b43
        te[15] = a41 * b14 + a42 * b24 + a43 * b34 + a44 * b44

        t1 = t.reshape(16)
        for i in range(16):
            if t1[i] != te[i]:
                print("not the same")
        """

        return self

    def multiplyScalar(self, s):
        self.elements *= s

        """
        te = self.elements
        te[0] *= s
        te[4] *= s
        te[8] *= s
        te[12] *= s
        te[1] *= s
        te[5] *= s
        te[9] *= s
        te[13] *= s
        te[2] *= s
        te[6] *= s
        te[10] *= s
        te[14] *= s
        te[3] *= s
        te[7] *= s
        te[11] *= s
        te[15] *= s
        """
        return self

    def applyToBufferAttribute(self, attribute):
        _v1 = THREE.Vector3(0, 0, 0)
        for i in range(0, len(attribute.array), 3):
            _v1.np[0] = attribute.array[i]
            _v1.np[1] = attribute.array[i + 1]
            _v1.np[2] = attribute.array[i + 2]

            _v1.applyMatrix4(self)

            attribute.array[i] = _v1.np[0]
            attribute.array[i + 1] = _v1.np[1]
            attribute.array[i + 2] = _v1.np[2]

        return attribute

    def determinant(self):
        te = self.elements

        n11 = te[0]; n12 = te[4]; n13 = te[8]; n14 = te[12]
        n21 = te[1]; n22 = te[5]; n23 = te[9]; n24 = te[13]
        n31 = te[2]; n32 = te[6]; n33 = te[10]; n34 = te[14]
        n41 = te[3]; n42 = te[7]; n43 = te[11]; n44 = te[15]

        # //TODO: make self more efficient
        # //(based on http:# //www.euclideanspace.com/maths/algebra/matrix/functions/inverse/fourD/index.htm)

        return (
            n41 * (
                + n14 * n23 * n32
                 - n13 * n24 * n32
                 - n14 * n22 * n33
                 + n12 * n24 * n33
                 + n13 * n22 * n34
                 - n12 * n23 * n34
           ) +
            n42 * (
                + n11 * n23 * n34
                 - n11 * n24 * n33
                 + n14 * n21 * n33
                 - n13 * n21 * n34
                 + n13 * n24 * n31
                 - n14 * n23 * n31
           ) +
            n43 * (
                + n11 * n24 * n32
                 - n11 * n22 * n34
                 - n14 * n21 * n32
                 + n12 * n21 * n34
                 + n14 * n22 * n31
                 - n12 * n24 * n31
           ) +
            n44 * (
                - n13 * n22 * n31
                 - n11 * n23 * n32
                 + n11 * n22 * n33
                 + n13 * n21 * n32
                 - n12 * n21 * n33
                 + n12 * n23 * n31
           )
       )

    def transpose(self):
        te = self.elements

        tmp = te[1]; te[1] = te[4]; te[4] = tmp
        tmp = te[2]; te[2] = te[8]; te[8] = tmp
        tmp = te[6]; te[6] = te[9]; te[9] = tmp

        tmp = te[3]; te[3] = te[12]; te[12] = tmp
        tmp = te[7]; te[7] = te[13]; te[13] = tmp
        tmp = te[11]; te[11] = te[14]; te[14] = tmp

        return self

    def setPosition(self, v):
        te = self.elements

        te[12] = v.np[0]
        te[13] = v.np[1]
        te[14] = v.np[2]

        return self

    def getInverse(self, m, throwOnDegenerate=False):
        # // based on http:# //www.euclideanspace.com/maths/algebra/matrix/functions/inverse/fourD/index.htm
        te = self.elements
        me = m.elements

        n11 = me[0]; n21 = me[1]; n31 = me[2]; n41 = me[3]
        n12 = me[4]; n22 = me[5]; n32 = me[6]; n42 = me[7]
        n13 = me[8]; n23 = me[9]; n33 = me[10]; n43 = me[11]
        n14 = me[12]; n24 = me[13]; n34 = me[14]; n44 = me[15]

        t11 = n23 * n34 * n42 - n24 * n33 * n42 + n24 * n32 * n43 - n22 * n34 * n43 - n23 * n32 * n44 + n22 * n33 * n44
        t12 = n14 * n33 * n42 - n13 * n34 * n42 - n14 * n32 * n43 + n12 * n34 * n43 + n13 * n32 * n44 - n12 * n33 * n44
        t13 = n13 * n24 * n42 - n14 * n23 * n42 + n14 * n22 * n43 - n12 * n24 * n43 - n13 * n22 * n44 + n12 * n23 * n44
        t14 = n14 * n23 * n32 - n13 * n24 * n32 - n14 * n22 * n33 + n12 * n24 * n33 + n13 * n22 * n34 - n12 * n23 * n34

        det = n11 * t11 + n21 * t12 + n31 * t13 + n41 * t14

        if det == 0:
            raise RuntimeWarning("THREE.Matrix4: .getInverse() can't invert matrix, determinant is 0")
            return self.identity()

        detInv = 1 / det

        te[0] = t11
        te[1] = (n24 * n33 * n41 - n23 * n34 * n41 - n24 * n31 * n43 + n21 * n34 * n43 + n23 * n31 * n44 - n21 * n33 * n44)
        te[2] = (n22 * n34 * n41 - n24 * n32 * n41 + n24 * n31 * n42 - n21 * n34 * n42 - n22 * n31 * n44 + n21 * n32 * n44)
        te[3] = (n23 * n32 * n41 - n22 * n33 * n41 - n23 * n31 * n42 + n21 * n33 * n42 + n22 * n31 * n43 - n21 * n32 * n43)

        te[4] = t12
        te[5] = (n13 * n34 * n41 - n14 * n33 * n41 + n14 * n31 * n43 - n11 * n34 * n43 - n13 * n31 * n44 + n11 * n33 * n44)
        te[6] = (n14 * n32 * n41 - n12 * n34 * n41 - n14 * n31 * n42 + n11 * n34 * n42 + n12 * n31 * n44 - n11 * n32 * n44)
        te[7] = (n12 * n33 * n41 - n13 * n32 * n41 + n13 * n31 * n42 - n11 * n33 * n42 - n12 * n31 * n43 + n11 * n32 * n43)

        te[8] = t13
        te[9] = (n14 * n23 * n41 - n13 * n24 * n41 - n14 * n21 * n43 + n11 * n24 * n43 + n13 * n21 * n44 - n11 * n23 * n44)
        te[10] = (n12 * n24 * n41 - n14 * n22 * n41 + n14 * n21 * n42 - n11 * n24 * n42 - n12 * n21 * n44 + n11 * n22 * n44)
        te[11] = (n13 * n22 * n41 - n12 * n23 * n41 - n13 * n21 * n42 + n11 * n23 * n42 + n12 * n21 * n43 - n11 * n22 * n43)

        te[12] = t14
        te[13] = (n13 * n24 * n31 - n14 * n23 * n31 + n14 * n21 * n33 - n11 * n24 * n33 - n13 * n21 * n34 + n11 * n23 * n34)
        te[14] = (n14 * n22 * n31 - n12 * n24 * n31 - n14 * n21 * n32 + n11 * n24 * n32 + n12 * n21 * n34 - n11 * n22 * n34)
        te[15] = (n12 * n23 * n31 - n13 * n22 * n31 + n13 * n21 * n32 - n11 * n23 * n32 - n12 * n21 * n33 + n11 * n22 * n33)

        self.elements /= det
        return self

    def scale(self, v):
        te = self.elements

        _temp[0] = _temp[1] = _temp[2] = v.np[0]
        _temp[4] = _temp[5] = _temp[6] = v.np[1]
        _temp[8] = _temp[9] = _temp[10] = v.np[2]

        te *= _temp
        """
        te[0] *= x
        te[4] *= y 
        te[8] *= z
        te[1] *= x 
        te[5] *= y 
        te[9] *= z
        te[2] *= x 
        te[6] *= y 
        te[10] *= z
        te[3] *= x 
        te[7] *= y 
        te[11] *= z
        """
        return self

    def getMaxScaleOnAxis(self):
        te = self.elements

        scaleXSq = te[0] * te[0] + te[1] * te[1] + te[2] * te[2]
        scaleYSq = te[4] * te[4] + te[5] * te[5] + te[6] * te[6]
        scaleZSq = te[8] * te[8] + te[9] * te[9] + te[10] * te[10]

        return math.sqrt(max(scaleXSq, scaleYSq, scaleZSq))

    def makeTranslation(self, x, y, z):
        self.set(
            1, 0, 0, x,
            0, 1, 0, y,
            0, 0, 1, z,
            0, 0, 0, 1
       )
        return self

    def makeRotationX(self, theta):
        c = math.cos(theta); s = math.sin(theta)

        self.set(
            1, 0,  0, 0,
            0, c, - s, 0,
            0, s,  c, 0,
            0, 0,  0, 1
       )
        return self

    def makeRotationY(self, theta):
        c = math.cos(theta); s = math.sin(theta)

        self.set(
             c, 0, s, 0,
             0, 1, 0, 0,
            - s, 0, c, 0,
             0, 0, 0, 1
       )
        return self

    def makeRotationZ(self, theta):
        c = math.cos(theta); s = math.sin(theta)

        self.set(
            c, - s, 0, 0,
            s,  c, 0, 0,
            0,  0, 1, 0,
            0,  0, 0, 1
       )
        return self

    def makeRotationAxis(self, axis, angle):
        # // Based on http:# //www.gamedev.net/reference/articles/article1199.asp
        c = math.cos(angle)
        s = math.sin(angle)
        t = 1 - c
        x = axis.x; y = axis.y; z = axis.z
        tx = t * x; ty = t * y

        self.set(
            tx * x + c, tx * y - s * z, tx * z + s * y, 0,
            tx * y + s * z, ty * y + c, ty * z - s * x, 0,
            tx * z - s * y, ty * z + s * x, t * z * z + c, 0,
            0, 0, 0, 1
       )
        return self

    def makeScale(self, x, y, z):
        self.set(
            x, 0, 0, 0,
            0, y, 0, 0,
            0, 0, z, 0,
            0, 0, 0, 1
       )
        return self

    def makeShear(self, x, y, z):
        self.set(
            1, y, z, 0,
            x, 1, z, 0,
            x, y, 1, 0,
            0, 0, 0, 1
       )
        return self

    def compose(self, position, quaternion, scale):
        self.makeRotationFromQuaternion(quaternion)
        self.scale(scale)
        self.setPosition(position)

        return self

    def decompose(self, position, quaternion, scale):
        vector = THREE.Vector3()
        matrix = Matrix4()
        te = self.elements

        sx = vector.set(te[0], te[1], te[2]).length()
        sy = vector.set(te[4], te[5], te[6]).length()
        sz = vector.set(te[8], te[9], te[10]).length()

        # // if determine is negative, we need to invert one scale
        det = self.determinant()
        if det < 0:
            sx = - sx

        position.x = te[12]
        position.y = te[13]
        position.z = te[14]

        # // scale the rotation part
        matrix.copy(self)

        invSX = 1 / sx
        invSY = 1 / sy
        invSZ = 1 / sz

        matrix.elements[0] *= invSX
        matrix.elements[1] *= invSX
        matrix.elements[2] *= invSX

        matrix.elements[4] *= invSY
        matrix.elements[5] *= invSY
        matrix.elements[6] *= invSY

        matrix.elements[8] *= invSZ
        matrix.elements[9] *= invSZ
        matrix.elements[10] *= invSZ

        quaternion.setFromRotationMatrix(matrix)

        scale.x = sx
        scale.y = sy
        scale.z = sz

        return self

    def makePerspective(self, left, right, top, bottom, near, far=None):
        if far is None:
            print('THREE.Matrix4: .makePerspective() has been redefined and has a signature. Please check the docs.')

        te = self.elements
        x = 2 * near / (right - left)
        y = 2 * near / (top - bottom)

        a = (right + left) / (right - left)
        b = (top + bottom) / (top - bottom)
        c = - (far + near) / (far - near)
        d = - 2 * far * near / (far - near)

        te[0] = x;    te[4] = 0;    te[8] = a;    te[12] = 0
        te[1] = 0;    te[5] = y;    te[9] = b;    te[13] = 0
        te[2] = 0;    te[6] = 0;    te[10] = c;    te[14] = d
        te[3] = 0;    te[7] = 0;    te[11] = - 1;    te[15] = 0

        return self

    def makeOrthographic(self, left, right, top, bottom, near, far):
        te = self.elements
        w = 1.0 / (right - left)
        h = 1.0 / (top - bottom)
        p = 1.0 / (far - near)

        x = (right + left) * w
        y = (top + bottom) * h
        z = (far + near) * p

        te[0] = 2 * w;    te[4] = 0;    te[8] = 0;    te[12] = - x
        te[1] = 0;    te[5] = 2 * h;    te[9] = 0;    te[13] = - y
        te[2] = 0;    te[6] = 0;    te[10] = - 2 * p;    te[14] = - z
        te[3] = 0;    te[7] = 0;    te[11] = 0;    te[15] = 1

        return self

    def equals(self, matrix):
        te = self.elements
        me = matrix.elements

        for i in range(16):
            if te[i] != me[i]:
                return False

        return True

    def fromArray(self, array, offset=0):
        self.elements[0:16] = array[offset:offset+16]
        return self

    def toArray(self, array=None, offset=0):
        if array is None:
            array = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        array[offset:offset+16] = self.elements[:]
        # te = self.elements

        # array[offset] = float(te[0])
        # array[offset + 1] = float(te[1])
        # array[offset + 2] = float(te[2])
        # array[offset + 3] = float(te[3])

        # array[offset + 4] = float(te[4])
        # array[offset + 5] = float(te[5])
        # array[offset + 6] = float(te[6])
        # array[offset + 7] = float(te[7])

        # array[offset + 8] = float(te[8])
        # array[offset + 9] = float(te[9])
        # array[offset + 10] = float(te[10])
        # array[offset + 11] = float(te[11])

        # array[offset + 12] = float(te[12])
        # array[offset + 13] = float(te[13])
        # array[offset + 14] = float(te[14])
        # array[offset + 15] = float(te[15])

        return array
