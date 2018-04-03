"""
"""
import re
from THREE.pyOpenGLObject import *


class PropertyBinding:
    BindingType = {
        'Direct': 0,
        'EntireArray': 1,
        'ArrayElement': 2,
        'HasFromToArray': 3
    }

    Versioning = {
        'None': 0,
        'NeedsUpdate': 1,
        'MatrixWorldNeedsUpdate': 2
    }

    def __init__(self, rootNode, path, parsedPath ):
        self.path = path
        self.parsedPath = parsedPath or PropertyBinding.parseTrackName( path )

        self.node = PropertyBinding.findNode( rootNode, self.parsedPath['nodeName'] ) or rootNode

        self.rootNode = rootNode

    def create(root, path, parsedPath ):
        if not ( root and hasattr(root, 'isAnimationObjectGroup')):
            return PropertyBinding( root, path, parsedPath )
        else:
            return PropertyBinding.Composite( root, path, parsedPath )

    def sanitizeNodeName( name ):
        """
         * Replaces spaces with underscores and removes unsupported characters from
         * node names, to ensure compatibility with parseTrackName().
         *
         * @param  {string} name Node name to be sanitized.
         * @return {string}
        """
        r = re.sub("\s", '_', name )
        return re.sub("[^\w-]", '', r )

    def parseTrackName(trackName):
        # Parent directories, delimited by '/' or ':'. Currently unused, but must
        # be matched to parse the rest of the track name.
        directoryRe = '((?:[\w-]+[\/:])*)'

        # Target node. May contain word characters (a-zA-Z0-9_) and '.' or '-'.
        nodeRe = '([\w\-\.]+)?'

        # Object on target node, and accessor. Name may contain only word
        # characters. Accessor may contain any character except closing bracket.
        objectRe = '(?:\.([\w-]+)(?:\[(.+)\])?)?'

        # Property and accessor. May contain only word characters. Accessor may
        # contain any non-bracket characters.
        propertyRe = '\.([\w-]+)(?:\[(.+)\])?'

        trackRe = '^' + directoryRe + nodeRe + objectRe + propertyRe + '$'

        supportedObjectNames = [ 'material', 'materials', 'bones' ]

        matches = re.search(trackRe, trackName )

        if not matches:
            raise RuntimeError( 'PropertyBinding: Cannot parse trackName: ' + trackName )

        results = {
            # directoryName: matches[ 1 ], # (tschw) currently unused
            'nodeName': matches.group(2),
            'objectName': matches.group(3),
            'objectIndex': matches.group(4),
            'propertyName': matches.group(5),     # required
            'propertyIndex': matches.group(6)
        }

        lastDot = results['nodeName'] and results['nodeName'].rfind( '.' )

        if lastDot is not None and lastDot != -1:
            objectName = results['nodeName'][lastDot + 1:]

            # Object names must be checked against a whitelist. Otherwise, there
            # is no way to parse 'foo.bar.baz': 'baz' must be a property, but
            # 'bar' could be the objectName, or part of a nodeName (which can
            # include '.' characters).
            if supportedObjectNames.index( objectName ) != -1:
                results['nodeName'] = results['nodeName'][0:lastDot]
                results['objectName'] = objectName

        if results['propertyName'] is None or len(results['propertyName']) == 0:
            raise RuntimeError( 'PropertyBinding: can not parse propertyName from trackName: ' + trackName )

        return results

    def findNode( root, nodeName ):
        if not nodeName or nodeName == "" or nodeName == "root" or nodeName == "." or nodeName == - 1 or nodeName == root.name or nodeName == root.uuid:
            return root

        # search into skeleton bones.
        if root.skeleton:
            def searchSkeleton( skeleton ):
                for bone in skeleton.bones:
                    if bone.name == nodeName:
                        return bone

                return None

            bone = searchSkeleton( root.skeleton )

            if bone:
                return bone

        # search into node subtree.
        if root.children:
            def searchNodeSubtree( children ):
                for childNode in children:
                    if childNode.name == nodeName or childNode.uuid == nodeName:
                        return childNode

                    result = searchNodeSubtree( childNode.children )

                    if result:
                        return result

                return None

            subTreeNode = searchNodeSubtree( root.children )

            if subTreeNode:
                return subTreeNode

        return None


    # these are used to "bind" a nonexistent property
    def _getValue_unavailable(self):
        return

    def _setValue_unavailable(self):
        return

    def getValue(self, targetArray, offset ):
        # TODO FDE  wtf
        # getValue: function getValue_unbound(targetArray, offset):

        self.bind()
        self.getValue( targetArray, offset )

        # Note: This class uses a State pattern on a per-method basis:
        # 'bind' sets 'self.getValue' / 'setValue' and shadows the
        # prototype version of these methods with one that represents
        # the bound state. When the property is not found, the methods
        # become no-ops.

    def setValue(self, sourceArray, offset ):
        # TODO FDE  wtf
        # setValue: function getValue_unbound( sourceArray, offset ):

        self.bind()
        self.setValue( sourceArray, offset )

    # create getter / setter pair for a property in the scene graph
    def bind(self):
        targetObject = self.node
        parsedPath = self.parsedPath

        objectName = parsedPath['objectName']
        propertyName = parsedPath['propertyName']
        propertyIndex = parsedPath['propertyIndex']

        if not targetObject:
            targetObject = PropertyBinding.findNode(
                    self.rootNode, parsedPath['nodeName'] ) or self.rootNode

            self.node = targetObject

        # set fail state so we can just 'return' on error
        self.getValue = self._getValue_unavailable
        self.setValue = self._setValue_unavailable

        # ensure there is a value node
        if not targetObject:
            raise RuntimeError( 'THREE.PropertyBinding: Trying to update node for track: ' + self.path + ' but it wasn\'t found.' )

        if objectName:
            objectIndex = parsedPath['objectIndex']

            # special cases were we need to reach deeper into the hierarchy to get the face materials....
            if objectName == 'materials':
                if not targetObject.material:
                    raise RuntimeError( 'THREE.PropertyBinding: Can not bind to material as node does not have a material.', self )

                if not targetObject.material.materials:
                    raise RuntimeError( 'THREE.PropertyBinding: Can not bind to material.materials as node.material does not have a materials array.', self )

                targetObject = targetObject.material.materials

            elif objectName == 'bones':
                if not targetObject.skeleton:
                    raise RuntimeError( 'THREE.PropertyBinding: Can not bind to bones as node does not have a skeleton.', self )

                # potential future optimization: skip self if propertyIndex is already an integer
                # and convert the integer string to a true integer.

                targetObject = targetObject.skeleton.bones

                # support resolving morphTarget names into indices.
                for i in range(len(targetObject)):
                    if targetObject[ i ].name == objectIndex:
                        objectIndex = i
                        break

            else:
                if targetObject[ objectName ] is None:
                    raise RuntimeError( 'THREE.PropertyBinding: Can not bind to objectName of node undefined.', self )

                targetObject = targetObject[ objectName ]

            if objectIndex is not None:
                if targetObject[ objectIndex ] is None:
                    raise RuntimeError( 'THREE.PropertyBinding: Trying to bind to objectIndex of objectName, but is undefined.', self, targetObject )

                targetObject = targetObject[ objectIndex ]

        # resolve property
        if propertyName == "quaternion":
            propertyName = "_quaternion"

        if propertyName not in targetObject:
            nodeName = parsedPath['nodeName']
            raise RuntimeError( 'THREE.PropertyBinding: Trying to update property for track: %s.%s but it wasn\'t found' % (nodeName,propertyName))

        nodeProperty = targetObject[ propertyName ]

        # determine versioning scheme
        versioning = self.Versioning['None']

        if hasattr(targetObject, 'needsUpdate'):     # material
            versioning = self.Versioning['NeedsUpdate']
            self.targetObject = targetObject

        elif targetObject.matrixWorldNeedsUpdate is not None:  # node transform
            versioning = self.Versioning['MatrixWorldNeedsUpdate']
            self.targetObject = targetObject

        # determine how the property gets bound
        bindingType = self.BindingType['Direct']

        if propertyIndex is not None:
            # access a sub element of the property array (only primitives are supported right now)

            if propertyName == "morphTargetInfluences":
                # potential optimization, skip self if propertyIndex is already an integer, and convert the integer string to a true integer.

                # support resolving morphTarget names into indices.
                if not targetObject.geometry:
                    raise RuntimeError( 'THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.', self )

                if targetObject.geometry.my_class(isBufferGeometry):
                    if not targetObject.geometry.morphAttributes:
                        raise RuntimeError( 'THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.morphAttributes.', self )

                    for i in range(len(self.node.geometry.morphAttributes.position)):
                        if targetObject.geometry.morphAttributes.position[ i ].name == propertyIndex:
                            propertyIndex = i

                else:
                    if not targetObject.geometry.morphTargets:
                        raise RuntimeError( 'THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.morphTargets.', self )

                    for i in range(len(self.node.geometry.morphTargets)):
                        if targetObject.geometry.morphTargets[ i ].name == propertyIndex:
                            propertyIndex = i

            bindingType = self.BindingType['ArrayElement']

            self.resolvedProperty = nodeProperty
            self.propertyIndex = propertyIndex

        elif nodeProperty.fromArray is not None and nodeProperty.toArray is not None:
            # must use copy for Object3D.Euler/Quaternion

            bindingType = self.BindingType['HasFromToArray']

            self.resolvedProperty = nodeProperty

        elif isinstance(nodeProperty, list):
            bindingType = self.BindingType['EntireArray']

            self.resolvedProperty = nodeProperty

        else:
            self.propertyName = propertyName

        # select getter / setter
        getterByBindingType = [
            self.getValue_direct,
            self.getValue_array,
            self.getValue_arrayElement,
            self.getValue_toArray
        ]

        setterByBindingTypeAndVersioning = [
            [
                # Direct
                self.setValue_direct,
                self.setValue_direct_setNeedsUpdate,
                self.setValue_direct_setMatrixWorldNeedsUpdate
            ],
            [
                # EntireArray
                self.setValue_array,
                self.setValue_array_setNeedsUpdate,
                self.setValue_array_setMatrixWorldNeedsUpdate
            ],
            [
                # ArrayElement
                self.setValue_arrayElement,
                self.setValue_arrayElement_setNeedsUpdate,
                self.setValue_arrayElement_setMatrixWorldNeedsUpdate
            ],
            [
                # HasToFromArray
                self.setValue_fromArray,
                self.setValue_fromArray_setNeedsUpdate,
                self.setValue_fromArray_setMatrixWorldNeedsUpdate
            ]
        ]

        self.getValue = getterByBindingType[ bindingType ]
        self.setValue = setterByBindingTypeAndVersioning[ bindingType ][ versioning ]

    def unbind(self):
        self.node = None

        # back to the prototype version of getValue / setValue
        # note: avoiding to mutate the shape of 'self' via 'delete'
        self.getValue = self._getValue_unbound
        self.setValue = self._setValue_unbound

    def getValue_direct(self, buffer, offset):
        buffer[offset] = self.node[self.propertyName],

    def getValue_array(self, buffer, offset):
        source = self.resolvedProperty

        for s in source:
            buffer[offset] = s
            offset += 1

    def getValue_arrayElement(self, buffer, offset):
        buffer[offset] = self.resolvedProperty[self.propertyIndex]

    def getValue_toArray(self, buffer, offset):
        self.resolvedProperty.toArray(buffer, offset)  # Direct

    def setValue_direct(self, buffer, offset):
        self.node[self.propertyName] = buffer[offset]

    def setValue_direct_setNeedsUpdate(self, buffer, offset):
        self.node[self.propertyName] = buffer[offset]
        self.targetObject.needsUpdate = True

    def setValue_direct_setMatrixWorldNeedsUpdate(self, buffer, offset):
        self.node[self.propertyName] = buffer[offset]
        self.targetObject.matrixWorldNeedsUpdate = True  # EntireArray

    def setValue_array(self, buffer, offset):
        dest = self.resolvedProperty

        for i in range(len(dest)):
            dest[i] = buffer[offset]
            offset += 1

    def setValue_array_setNeedsUpdate(self, buffer, offset):
        dest = self.resolvedProperty

        for i in range(len(dest)):
            dest[i] = buffer[offset]
            offset += 1

        self.targetObject.needsUpdate = True

    def setValue_array_setMatrixWorldNeedsUpdate(self, buffer, offset):
        dest = self.resolvedProperty

        for i in range(len(dest)):
            dest[i] = buffer[offset]
            offset += 1

        self.targetObject.matrixWorldNeedsUpdate = True

    # ArrayElement

    def setValue_arrayElement(self, buffer, offset ):
        self.resolvedProperty[ self.propertyIndex ] = buffer[ offset ]

    def setValue_arrayElement_setNeedsUpdate(self, buffer, offset ):
        self.resolvedProperty[ self.propertyIndex ] = buffer[ offset ]
        self.targetObject.needsUpdate = True

    def setValue_arrayElement_setMatrixWorldNeedsUpdate(self, buffer, offset ):
        self.resolvedProperty[ self.propertyIndex ] = buffer[ offset ]
        self.targetObject.matrixWorldNeedsUpdate = True

    # HasToFromArray

    def setValue_fromArray(self, buffer, offset ):
        self.resolvedProperty.fromArray( buffer, offset )

    def setValue_fromArray_setNeedsUpdate(self, buffer, offset ):
        self.resolvedProperty.fromArray( buffer, offset )
        self.targetObject.needsUpdate = True

    def setValue_fromArray_setMatrixWorldNeedsUpdate(self, buffer, offset ):
        self.resolvedProperty.fromArray( buffer, offset )
        self.targetObject.matrixWorldNeedsUpdate = True


# TODO FDE wtf
"""
#!\ DECLARE ALIAS AFTER assign prototype !
Object.assign( PropertyBinding.prototype, {

    # initial state of these methods that calls 'bind'
    _getValue_unbound: PropertyBinding.prototype.getValue,
    _setValue_unbound: PropertyBinding.prototype.setValue,

} )
"""