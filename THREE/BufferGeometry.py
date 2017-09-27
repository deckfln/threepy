"""
	/**
	 * @author mrdoob / http://mrdoob.com/
	 */
"""

import math
import numpy as np

import THREE._Math as _Math
from THREE.Matrix3 import *
from THREE.Matrix4 import *
from THREE.arrayMax import *
from THREE.Box3 import *
from THREE.Sphere import *
from THREE.Object3D import *
from THREE.BufferAttribute import *
from THREE.DirectGeometry import *


_gIdcount = 0


def GeometryIdCount():
    global _gIdcount
    _gIdcount += 1
    return _gIdcount

    
class _attributesList(object):
    def __init__(self):
        super().__setattr__('_attr', {})

    def __getitem__(self, item):
        if isinstance(item, bytes):
            item = item.decode("utf-8")
        return self._attr[item]

    def __setitem__(self, item, value):
        self._attr[item] = value

    def __getattr__(self, k):
        if isinstance(k, bytes):
            k = k.decode("utf-8")

        try:
            return self._attr[k]
        except KeyError:
            raise AttributeError("Missing attribute %s" % k)
            
    def __setattr__(self, key, value):
        self._attr[key] = value

    def __delattr__(self, key):
        del self._attr[key]

    def __iter__(self):
        return iter(self._attr)


class _drawRange:
    def __init__(self, start, count):
        self.start = start
        self.count = count


class _groups:
    def __init__(self, start, count, mi):
        self.start = start
        self.count = count
        self.materialIndex = mi


class BufferGeometry(pyOpenGLObject):
    MaxIndex = 65535
    count = 0
    isBufferGeometry = True

    def __init__(self):
        self.id = GeometryIdCount()

        self.uuid = _Math.generateUUID()
        self.name = ''
        self.type = 'BufferGeometry'
        self.index = None
        self.attributes = _attributesList()
        self.morphAttributes = {}
        self.groups = []
        self.boundingBox = None    
        self.boundingSphere = None
        self.drawRange = _drawRange(0, float('+inf'))
        self.callback = None

    def getIndex(self):
        return self.index
        
    def setIndex(self, index ):
        if isinstance(index, list):
            if arrayMax(index) > 65535:
                self.index = Uint32BufferAttribute( index, 1 )
            else:
                self.index = Uint16BufferAttribute(index, 1)
        else:
            self.index = index

    def addAttribute(self, name, attribute):
        if not ( attribute and attribute.isBufferAttribute ) and not ( attribute and attribute.isInterleavedBufferAttribute):
            print( 'THREE.BufferGeometry: .addAttribute() now expects ( name, attribute ).' )
            self.addAttribute( name, BufferAttribute( arguments[ 1 ], arguments[ 2 ] ) )
            return

        if name == 'index':
            print( 'THREE.BufferGeometry.addAttribute: Use .setIndex() for index attribute.' )                
            self.setIndex( attribute )
            return

        self.attributes[name] = attribute
        return self
        
    def getAttribute(self, name ):
        return self.attributes[name]

    def removeAttribute(self, name ):
        del self.attributes[name]
        return self
        
    def addGroup(self, start, count, materialIndex=0 ):
        self.groups.append( _groups(start, count, materialIndex))

    def clearGroups(self):
        self.groups = []
        
    def setDrawRange(self, start, count ):
        self.drawRange.start = start
        self.drawRange.count = count
        
    def applyMatrix(self, matrix ):
        position = self.attributes.position
        if position is not None:
            matrix.applyToBufferAttribute( position )
            position.needsUpdate = True

        normal = self.attributes.normal
        if normal is not None:
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
        self.computeBoundingBox()
        offset = self.boundingBox.getCenter().negate()
        self.translate( offset.x, offset.y, offset.z )
        return offset
        
    def setFromObject(self, object ):
        # // console.log( 'THREE.BufferGeometry.setFromObject(). Converting', object, self )
        geometry = object.geometry
        if object.isPoints or object.isLine:
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
        elif object.isMesh:
            if geometry and geometry.isGeometry:
                self.fromGeometry( geometry )

        return self
        
    def updateFromObject(self, object ):
        geometry = object.geometry
        if object.isMesh:
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

        if len(geometry.indices) > 0:
            if geometry.indices.count > 65535:
                indices = np.zeros(len(geometry.indices) * 3, "L" )
            else:
                indices = np.zeros(len(geometry.indices) * 3, "S" )
            self.setIndex( BufferAttribute( indices, 1 ).copyIndicesArray( geometry.indices ) )

        # // groups
        self.groups = geometry.groups
        # // morphs
        for name in geometry.morphTargets:
            array = []
            morphTargets = geometry.morphTargets[ name ]
            for i in range(len(morphTargets)):
                morphTarget = morphTargets[ i ]
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
        box = Box3()
        vector = Vector3()
        if self.boundingSphere is None:
            self.boundingSphere = Sphere()

        position = self.attributes.position
        if position:
            center = self.boundingSphere.center
            box.setFromBufferAttribute( position )
            box.getCenter( center )
            # // hoping to find a boundingSphere with a radius smaller than the
            # // boundingSphere of the boundingBox: sqrt(3) smaller in the best case

            maxRadiusSq = 0
            for i in range(int(position.count)):
                vector.x = position.getX( i )
                vector.y = position.getY( i )
                vector.z = position.getZ( i )
                maxRadiusSq = max( maxRadiusSq, center.distanceToSquared( vector ) )

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
            if 'normal' not in attributes:
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
                    start = group.start
                    count = group.count
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
        if not ( geometry and geometry.isBufferGeometry ):
            print( 'THREE.BufferGeometry.merge(): geometry not an instance of THREE.BufferGeometry.', geometry )
            return

        attributes = self.attributes
        for key in attributes:
            if geometry.attributes[ key ] is None:
                continue
            attribute1 = attributes[ key ]
            attributeArray1 = attribute1.array
            attribute2 = geometry.attributes[ key ]
            attributeArray2 = attribute2.array
            attributeSize = attribute2.itemSize
            j = j = attributeSize * offset
            for i in range (len(attributeArray2)):
                attributeArray1[ j ] = attributeArray2[ i ]
                j += 1

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

        return geometry2
        
    def toJSON(self):
        data = {
            'metadata': {
                'version': '4.5',
                'type': 'BufferGeometry',
                'generator': 'BufferGeometry.toJSON'
            }
        }
        # // standard BufferGeometry serialization
        data.uuid = self.uuid
        data.type = self.type
        if self.name != '':
            data.name = self.name
        if self.parameters is not None:
            parameters = self.parameters
            for key in parameters:
                if parameters[ key ] is not None:
                    data[ key ] = parameters[ key ]

            return data

        data.data = { 'attributes': {} }
        index = self.index
        if index != None:
            array = Array.prototype.slice.call( index.array )
            data.data.index = {
                'type': index.array.constructor.name,
                'array': array
            }

        attributes = self.attributes
        for key in attributes:
            attribute = attributes[ key ]
            array = Array.prototype.slice.call( attribute.array )
            data.data.attributes[ key ] = {
                'itemSize': attribute.itemSize,
                'type': attribute.array.constructor.name,
                'array': array,
                'normalized': attribute.normalized
            }

        groups = self.groups
        if len(groups) > 0:
            data.data.groups = JSON.parse( JSON.stringify( groups ) )

        boundingSphere = self.boundingSphere
        if boundingSphere is not None:
            data.data.boundingSphere = {
                'center': boundingSphere.center.toArray(),
                'radius': boundingSphere.radius
            }

        return data
        
    def clone(self):
        return type(self)().copy( self )
        
    def copy(self, source ):
        # // reset
        self.index = None
        self.attributes = {}
        self.morphAttributes = {}
        self.groups = []
        self.boundingBox = None
        self.boundingSphere = None

        # // name
        self.name = source.name

        # // index
        index = source.index
        if index is not None:
            self.setIndex( index.clone() )

        # // attributes
        attributes = source.attributes
        for name in attributes:
            attribute = attributes[ name ]
            self.addAttribute( name, attribute.clone() )

        # // morph attributes
        morphAttributes = source.morphAttributes
        for name in morphAttributes:
            array = []
            morphAttribute = morphAttributes[ name ]; # // morphAttribute: array of Float32BufferAttributes

            for i in range(len(morphAttribute)):
                array.append( morphAttribute[ i ].clone() )

            self.morphAttributes[ name ] = array

        # // groups
        groups = source.groups
        for i in range(len(groups)):
            group = groups[ i ]
            self.addGroup( group.start, group.count, group.materialIndex )

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

        return self

    def onDispose(self, callback):
        self.callback = callback

    def dispose(self):
        if self.callback:
            return self.callback(self)
