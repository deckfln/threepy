"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""

import THREE._Math as _Math
from THREE.arrayMax import *
from THREE.math.Box3 import *
from THREE.BoundingSphere import *
from THREE.core.Object3D import *
from THREE.core.BufferAttribute import *
from THREE.core.DirectGeometry import *

_gIdcount = 0
_box = Box3()
_vector = Vector3()


class _attributesList:
    def __init__(self):
        self.position = None
        self.normal = None
        self.uv = None
        self.uv2 = None
        self.colors = None
        self.skinIndex = None


class _drawRange:
    def __init__(self, start, count):
        self.start = start
        self.count = count


class _groups:
    def __init__(self, start, count, mi):
        self.start = start
        self.count = count
        self.materialIndex = mi


_bufferGeometryId = 1   # BufferGeometry uses odd numbers as Id
_v3 = Vector3()


class BufferGeometry(pyOpenGLObject):
    count = 0
    isBufferGeometry = True

    def __init__(self):
        global _bufferGeometryId

        self.id = _bufferGeometryId
        _bufferGeometryId += 2

        super().__init__()
        self.set_class(isBufferGeometry)

        self.uuid = _Math.generateUUID()
        self.name = ''
        self.type = 'BufferGeometry'
        self.index = None
        self.attributes = _attributesList()
        self.morphAttributes = morphTargets()
        self.groups = []
        self.boundingBox = None    
        self.boundingSphere = None
        self.matrixWorldBoundingSphere = None           # cached bounding sphere with matrix world updated
        self.drawRange = _drawRange(0, float('+inf'))
        self.callback = None
        self.bones = None
        self.userData = {}

    def dispose(self):
        return

    def getIndex(self):
        return self.index
        
    def setIndex(self, index):
        if isinstance(index, list):
            if arrayMax(index) > 65535:
                self.index = Uint32BufferAttribute( index, 1 )
            else:
                self.index = Uint16BufferAttribute(index, 1)
        else:
            self.index = index

    def addAttribute(self, name, attribute):
        if not ( attribute and attribute.my_class(isBufferAttribute) ) and not ( attribute and attribute.my_class(isInterleavedBufferAttribute)):
            print( 'THREE.BufferGeometry: .addAttribute() now expects ( name, attribute ).' )
            return self.addAttribute( name, BufferAttribute( arguments[ 1 ], arguments[ 2 ] ) )

        if name == 'index':
            print( 'THREE.BufferGeometry.addAttribute: Use .setIndex() for index attribute.' )                
            self.setIndex( attribute )
            return self

        self.attributes.__dict__[name] = attribute
        return self

    def getAttribute(self, name ):
        return self.attributes.__dict__[name]

    def removeAttribute(self, name ):
        if hasattr(self.attributes, name):
            del self.attributes.__dict__[name]
        return self
        
    def addGroup(self, start, count, materialIndex=0 ):
        self.groups.append( _groups(start, count, materialIndex))

    def clearGroups(self):
        self.groups = []
        
    def setDrawRange(self, start, count ):
        self.drawRange.start = start
        self.drawRange.count = count
        
    def applyMatrix(self, matrix ):
        if self.attributes.position is not None:
            position = self.attributes.position
            matrix.applyToBufferAttribute( position )
            position.needsUpdate = True

        if self.attributes.normal is not None:
            normal = self.attributes.normal
            normalMatrix = Matrix3().getNormalMatrix( matrix )
            normalMatrix.applyToBufferAttribute( normal )
            normal.needsUpdate = True

        if self.boundingBox is not None:
            self.computeBoundingBox()

        if self.boundingSphere is not None:
            self.computeBoundingSphere()

        return self
        
    def rotateX(self, angle):
        # // rotate geometry around world x-axis
        m1 = Matrix4()
        m1.makeRotationX( angle )
        self.applyMatrix( m1 )
        return self

    def rotateY(self, angle):
        # // rotate geometry around world y-axis
        m1 = Matrix4()
        m1.makeRotationY( angle )
        self.applyMatrix( m1 )
        return self

    def rotateZ(self, angle):
        # // rotate geometry around world z-axis
        m1 = Matrix4()
        m1.makeRotationZ( angle )
        self.applyMatrix( m1 )
        return self

    def translate(self, x, y, z):
        # // translate geometry
        m1 = Matrix4()
        m1.makeTranslation( x, y, z )
        self.applyMatrix( m1 )
        return self

    def scale(self, x, y, z):
        # // scale geometry
        m1 = Matrix4()
        m1.makeScale( x, y, z )
        self.applyMatrix( m1 )
        return self

    def lookAt(self, vector):
        obj = Object3D()
        obj.lookAt( vector )
        obj.updateMatrix()
        self.applyMatrix( obj.matrix )

    def center(self):
        global _v3
        offset = _v3
        self.computeBoundingBox()
        self.boundingBox.getCenter(offset).negate()
        self.translate( offset.x, offset.y, offset.z )
        return self
        
    def setFromObject(self, object ):
        # // console.log( 'THREE.BufferGeometry.setFromObject(). Converting', object, self )
        geometry = object.geometry
        if object.my_class(isPoints) or object.my_class(isLine):
            positions = Float32BufferAttribute( len(geometry.vertices) * 3, 3 )
            colors = Float32BufferAttribute( len(geometry.colors) * 3, 3 )
            self.addAttribute( 'position', positions.copyVector3sArray( geometry.vertices ) )
            self.addAttribute( 'color', colors.copyColorsArray( geometry.colors ) )
            if geometry.lineDistances and len(geometry.lineDistances) == len(geometry.vertices):
                lineDistances = Float32BufferAttribute( len(geometry.lineDistances), 1 )
                self.addAttribute( 'lineDistance', lineDistances.copyArray( geometry.lineDistances ) )

            if geometry.boundingSphere is not None:
                self.boundingSphere = geometry.boundingSphere.clone()

            if geometry.boundingBox is not None:
                self.boundingBox = geometry.boundingBox.clone()
        elif object.my_class(isMesh):
            if geometry and geometry.my_class(isGeometry):
                self.fromGeometry( geometry )

        return self

    def setFromPoints(self, points):
        position = []

        for point in points:
            position.append( point.x, point.y, point.z or 0 )

        self.addAttribute( 'position', Float32BufferAttribute( position, 3 ) )

        return self

    def updateFromObject(self, object ):
        geometry = object.geometry
        if object.my_class(isMesh):
            direct = geometry._directGeometry
            if geometry.elementsNeedUpdate:
                direct = None
                geometry.elementsNeedUpdate = False

            if direct is None:
                return self.fromGeometry( geometry )

            direct.verticesNeedUpdate = geometry.verticesNeedUpdate
            direct.normalsNeedUpdate = geometry.normalsNeedUpdate            
            direct.colorsNeedUpdate = geometry.colorsNeedUpdate            
            direct.uvsNeedUpdate = geometry.uvsNeedUpdate
            direct.groupsNeedUpdate = geometry.groupsNeedUpdate
            geometry.verticesNeedUpdate = False
            geometry.normalsNeedUpdate = False
            geometry.colorsNeedUpdate = False
            geometry.uvsNeedUpdate = False
            geometry.groupsNeedUpdate = False
            geometry = direct

        if geometry.verticesNeedUpdate:
            attribute = self.attributes.position
            if attribute is not None:
                attribute.copyVector3sArray( geometry.vertices )
                attribute.needsUpdate = True

            geometry.verticesNeedUpdate = False

        if geometry.normalsNeedUpdate:
            attribute = self.attributes.normal
            if attribute is not None:
                attribute.copyVector3sArray( geometry.normals )
                attribute.needsUpdate = True

            geometry.normalsNeedUpdate = False

        if geometry.colorsNeedUpdate:
            attribute = self.attributes.color
            if attribute is not None:
                attribute.copyColorsArray( geometry.colors )
                attribute.needsUpdate = True

            geometry.colorsNeedUpdate = False

        if geometry.uvsNeedUpdate:
            attribute = self.attributes.uv
            if attribute is not None:
                attribute.copyVector2sArray( geometry.uvs )
                attribute.needsUpdate = True

            geometry.uvsNeedUpdate = False

        if geometry.lineDistancesNeedUpdate:
            attribute = self.attributes.lineDistance
            if attribute is not None:
                attribute.copyArray( geometry.lineDistances )
                attribute.needsUpdate = True

            geometry.lineDistancesNeedUpdate = False

        if geometry.groupsNeedUpdate:
            geometry.computeGroups( object.geometry )
            self.groups = geometry.groups
            geometry.groupsNeedUpdate = False

        return self
        
    def fromGeometry(self, geometry ):
        geometry._directGeometry = DirectGeometry().fromGeometry( geometry )
        return self.fromDirectGeometry( geometry._directGeometry )
        
    def fromDirectGeometry(self, geometry ):
        positions = np.zeros( len(geometry.vertices) * 3, 'f' )
        self.addAttribute( 'position', BufferAttribute( positions, 3 ).copyVector3sArray( geometry.vertices ) )
        if len(geometry.normals)> 0:
            normals = np.zeros( len(geometry.normals) * 3, 'f' )
            self.addAttribute( 'normal', BufferAttribute( normals, 3 ).copyVector3sArray( geometry.normals ) )

        if len(geometry.colors) > 0:
            colors = np.zeros( len(geometry.colors) * 3, 'f' )
            self.addAttribute( 'color', BufferAttribute( colors, 3 ).copyColorsArray( geometry.colors ) )

        if len(geometry.uvs)> 0:
            uvs = np.zeros( len(geometry.uvs) * 2, 'f' )
            self.addAttribute( 'uv', BufferAttribute( uvs, 2 ).copyVector2sArray( geometry.uvs ) )

        if len(geometry.uvs2) > 0:
            uvs2 = np.zeros( len(geometry.uvs2) * 2, 'f' )
            self.addAttribute( 'uv2', BufferAttribute( uvs2, 2 ).copyVector2sArray( geometry.uvs2 ) )

        # // groups
        self.groups = geometry.groups
        # // morphs
        for name in geometry.morphTargets:
            array = []
            morphTargets = geometry.morphTargets[ name ]
            for morphTarget in morphTargets:
                attribute = Float32BufferAttribute( len(morphTarget) * 3, 3 )
                array.append( attribute.copyVector3sArray( morphTarget ) )

            self.morphAttributes[ name ] = array

        # // skinning
        if len(geometry.skinIndices)> 0:
            skinIndices = Float32BufferAttribute( len(geometry.skinIndices) * 4, 4 )
            self.addAttribute( 'skinIndex', skinIndices.copyVector4sArray( geometry.skinIndices ) )

        if len(geometry.skinWeights)> 0:
            skinWeights = Float32BufferAttribute( len(geometry.skinWeights) * 4, 4 )
            self.addAttribute( 'skinWeight', skinWeights.copyVector4sArray( geometry.skinWeights ) )

        # //
        if geometry.boundingSphere is not None:
            self.boundingSphere = geometry.boundingSphere.clone()

        if geometry.boundingBox is not None:
            self.boundingBox = geometry.boundingBox.clone()

        return self
        
    def computeBoundingBox(self):
        if self.boundingBox is None:
            self.boundingBox = Box3()

        position = self.attributes.position
        if position is not None:
            self.boundingBox.setFromBufferAttribute( position )
        else:
            self.boundingBox.makeEmpty()

        if math.isnan( self.boundingBox.min.x ) or math.isnan( self.boundingBox.min.y ) or math.isnan( self.boundingBox.min.z ):
            print( 'THREE.BufferGeometry.computeBoundingBox: Computed min/max have NaN values. The "position" attribute is likely to have NaN values.', self )

    def computeBoundingSphere(self):
        if self.boundingSphere is None:
            self.boundingSphere = BoundingSphere()

        position = self.attributes.position
        if position:
            center = self.boundingSphere.center
            _box.setFromBufferAttribute( position )
            _box.getCenter( center )
            # // hoping to find a boundingSphere with a radius smaller than the
            # // boundingSphere of the boundingBox: sqrt(3) smaller in the best case

            maxRadiusSq = 0
            for i in range(0, len(position.array) - 2, position.itemSize):
                _vector.np[0] = position.array[ i ]
                _vector.np[1] = position.array[ i + 1 ]
                _vector.np[2] = position.array[ i + 2 ]
                maxRadiusSq = max( maxRadiusSq, center.distanceToSquared( _vector ) )

            self.boundingSphere.radius = math.sqrt( maxRadiusSq )
            if math.isnan( self.boundingSphere.radius ):
                print( 'THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.', self )

    def computeFaceNormals(self):
        # // backwards compatibility
        return None

    def computeVertexNormals(self):
        index = self.index
        attributes = self.attributes
        groups = self.groups
        if attributes.position:
            positions = attributes.position.array
            if attributes.normal is None:
                self.addAttribute( 'normal', BufferAttribute( np.zeros( len(positions), 'f' ), 3 ) )
            else:
                # // reset existing normals to zero
                array = attributes.normal.array
                for i in range(len(array)):
                    array[ i ] = 0

            normals = attributes.normal.array
            
            pA = Vector3()
            pB = Vector3()
            pC = Vector3()
            cb = Vector3()
            ab = Vector3()
            # // indexed elements
            if index:
                indices = index.array
                if len(groups) == 0:
                    self.addGroup( 0, len(indices) )

                for j in range(len(groups)):
                    group = groups[ j ]
                    start = int(group.start)
                    count = int(group.count)
                    for i in range(start, start + count, 3 ):
                        vA = indices[ i + 0 ] * 3
                        vB = indices[ i + 1 ] * 3
                        vC = indices[ i + 2 ] * 3
                        pA.fromArray( positions, vA )
                        pB.fromArray( positions, vB )
                        pC.fromArray( positions, vC )
                        cb.subVectors( pC, pB )
                        ab.subVectors( pA, pB )
                        cb.cross( ab )
                        normals[ vA ] += cb.x
                        normals[ vA + 1 ] += cb.y
                        normals[ vA + 2 ] += cb.z
                        normals[ vB ] += cb.x
                        normals[ vB + 1 ] += cb.y
                        normals[ vB + 2 ] += cb.z
                        normals[ vC ] += cb.x
                        normals[ vC + 1 ] += cb.y
                        normals[ vC + 2 ] += cb.z
            else:
                # // non-indexed elements (unconnected triangle soup)
                for i in range(0, len(positions), 9):
                    pA.fromArray( positions, i )
                    pB.fromArray( positions, i + 3 )
                    pC.fromArray( positions, i + 6 )
                    cb.subVectors( pC, pB )
                    ab.subVectors( pA, pB )
                    cb.cross( ab )
                    normals[ i ] = cb.x
                    normals[ i + 1 ] = cb.y
                    normals[ i + 2 ] = cb.z
                    normals[ i + 3 ] = cb.x
                    normals[ i + 4 ] = cb.y
                    normals[ i + 5 ] = cb.z
                    normals[ i + 6 ] = cb.x
                    normals[ i + 7 ] = cb.y
                    normals[ i + 8 ] = cb.z

            self.normalizeNormals()
            attributes.normal.needsUpdate = True

    def merge(self, geometry, offset=0 ):
        if not ( geometry and geometry.my_class(isBufferGeometry) ):
            print( 'THREE.BufferGeometry.merge(): geometry not an instance of THREE.BufferGeometry.', geometry )
            return

        attributes = self.attributes
        for key in attributes.__dict__:
            if geometry.attributes.__dict__[ key ] is None:
                continue

            attribute2 = geometry.attributes.__dict__[ key ]
            attribute1 = attributes.__dict__[ key ]

            if attribute1 is None:
                attributes.__dict__[key] = attribute2.clone()
            else:
                xv = np.concatenate([attribute1.array, attribute2.array])
                attribute1.array = xv

        return self
        
    def normalizeNormals(self):
        vector = Vector3()
        normals = self.attributes.normal
        for i in range(int(normals.count)):
            vector.x = normals.getX( i )
            vector.y = normals.getY( i )
            vector.z = normals.getZ( i )
            vector.normalize()
            normals.setXYZ( i, vector.x, vector.y, vector.z )

    def toNonIndexed(self):
        if self.index == None:
            print( 'THREE.BufferGeometry.toNonIndexed(): Geometry is already non-indexed.' )
            return self

        geometry2 = BufferGeometry()
        indices = self.index.array
        attributes = self.attributes
        for name in attributes:
            attribute = attributes[ name ]
            array = attribute.array
            itemSize = attribute.itemSize
            array2 = array.constructor( len(indices) * itemSize )
            index = 0
            index2 = 0
            for i in range(len(indices)):
                index = indices[ i ] * itemSize
                for j in range(itemSize):
                    array2[ index2 ] = array[ index ]
                    index2 += 1
                    index += 1

            geometry2.addAttribute( name, BufferAttribute( array2, itemSize ) )

        groups = self.groups

        for group in groups:
            geometry2.addGroup( group.start, group.count, group.materialIndex )

        return geometry2
        
    def toJSON(self, meta=None):
        data = {
            'metadata': {
                'version': '4.5',
                'type': 'BufferGeometry',
                'generator': 'BufferGeometry.toJSON'
            }
        }
        # // standard BufferGeometry serialization
        data['uuid'] = self.uuid
        data['type'] = self.type
        if self.name != '':
            data['name'] = self.name
        if len(self.userData) > 0:
            data['userData'] = self.userData

        if self.parameters is not None:
            parameters = self.parameters
            for key in parameters:
                if parameters[ key ] is not None:
                    data[ key ] = parameters[ key ]

            return data

        data['data'] = { 'attributes': {} }
        index = self.index
        if index is not None:
            array = index.array.tolist()
            type = index.__class__.__name__.replace("BufferAttribute", "Array")
            data['data']['index'] = {
                'type': type,
                'array': array
            }

        attributes = self.attributes
        for key in attributes:
            attribute = attributes[ key ]
            array = attribute.array.tolist()
            type = attribute.__class__.__name__.replace("BufferAttribute", "Array")
            data['data']['attributes'][ key ] = {
                'itemSize': attribute.itemSize,
                'type': type,
                'array': array,
                'normalized': attribute.normalized
            }

        groups = self.groups
        if len(groups) > 0:
            data['data']['groups'] = json.loads( json.dumps( groups ) )

        boundingSphere = self.boundingSphere
        if boundingSphere is not None:
            data['data']['boundingSphere'] = {
                'center': boundingSphere.center.toArray(),
                'radius': boundingSphere.radius
            }

        return data
        
    def clone(self):
        return type(self)().copy(self)
        
    def copy(self, source):
        # // reset
        self.index = None
        self.attributes = _attributesList()
        self.morphAttributes = _attributesList()
        self.groups = []
        self.boundingBox = None
        self.boundingSphere = None

        # // name
        self.name = source.name

        # // index
        index = source.index
        if index is not None:
            self.setIndex(index.clone())

        # // attributes
        attributes = source.attributes
        for name in attributes.__dict__:
            attribute = attributes.__dict__[name]
            if attribute is not None:
                self.addAttribute(name, attribute.clone())

        # // morph attributes
        morphAttributes = source.morphAttributes
        for name in morphAttributes.__dict__:
            array = []
            morphAttribute = morphAttributes.__dict__[name]     # // morphAttribute: array of Float32BufferAttributes

            if morphAttribute is not None:
                for morphAttribut in morphAttribute:
                    array.append(morphAttribut.clone())

                self.morphAttributes.__dict__[name] = array

        # // groups
        groups = source.groups
        for group in groups:
            self.addGroup(group.start, group.count, group.materialIndex)

        # // bounding box
        boundingBox = source.boundingBox
        if boundingBox is not None:
            self.boundingBox = boundingBox.clone()

        # // bounding sphere
        boundingSphere = source.boundingSphere
        if boundingSphere is not None:
            self.boundingSphere = boundingSphere.clone()

        # // draw range
        self.drawRange.start = source.drawRange.start
        self.drawRange.count = source.drawRange.count

        # user data
        self.userData = self.userData

        return self

    def onDispose(self, callback):
        self.callback = callback

    def dispose(self):
        if self.callback:
            return self.callback(self)

    def rebuild_id(self):
        global _bufferGeometryId

        self.id = _bufferGeometryId
        _bufferGeometryId += 2
