"""
/**
 * @author mrdoob / http://mrdoob.com/
 */
"""

from THREE.core.BufferGeometry import *
from THREE.javascriparray import *
from THREE.loaders.FileLoader import *


TYPED_ARRAYS = {
    'Int8Array': Int8Array,
    'Uint8Array': Uint8Array,
    'Uint8ClampedArray''': Uint8ClampedArray,
    'Int16Array': Int16Array,
    'Uint16Array': Uint16Array,
    'Int32Array': Int32Array,
    'Uint32Array': Uint32Array,
    'Float32Array': Float32Array,
    'Float64Array': Float64Array
}


class BufferGeometryLoader:
    def __init__(self, manager=None ):
        self.manager = manager if ( manager ) else DefaultLoadingManager

    def load(self, url, onLoad, onProgress=None, onError=None ):
        loader = FileLoader( self.manager )
        
        def _load(text):
            onLoad( self.parse( json.loads( text ) ))
        
        loader.load( url, _load, onProgress, onError )

    def parse(self, json ):
        geometry = BufferGeometry()

        if 'index' in json['data']:
            index = json['data']['index']

            typedArray = TYPED_ARRAYS[ index.type ]( index['array'] )
            geometry.setIndex( BufferAttribute( typedArray, 1 ) )

        attributes = json['data']['attributes']

        for key in attributes:
            attribute = attributes[ key ]
            typedArray = TYPED_ARRAYS[ attribute['type'] ]( attribute['array'] )

            normalized = attribute['normalized'] if 'normalized' in attribute else False
            geometry.addAttribute( key, BufferAttribute( typedArray, attribute['itemSize'], normalized ) )

        groups = None
        if 'groups' in json['data']:
            groups = json['data']['groups']
        elif 'drawcalls' in json['data']:
            groups = json['data']['drawcalls']
        elif 'offsets' in json['data']:
            groups = json['data']['offsets']
        
        if groups:
            for group in groups:
                geometry.addGroup( group['start'], group['count'], group['materialIndex'] )

        if 'boundingSphere' in json['data']:
            boundingSphere = json['data']['boundingSphere']

            center = Vector3()

            if 'center' in boundingSphere:
                center.fromArray( boundingSphere['center'] )

            geometry.boundingSphere = Sphere( center, boundingSphere['radius'] )

        return geometry
