"""
 * @author mikael emtinger / http://gomo.se/
 * @author alteredq / http://alteredqualia.com/
 * @author ikerr / http://verold.com
"""

from THREE.Object3D import *


class Bone(Object3D):
	isBone = True
	
	def __init__(self):
		super().__init__( )
		self.type = 'Bone'
