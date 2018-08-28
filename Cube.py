# -*- coding: utf-8 -*-

"""
Cube model.

Copyright (c) 2010, Renaud Blanch <rndblnch at gmail dot com>
Licence: GPLv3 or higher <http://www.gnu.org/licenses/gpl.html>
"""


# imports ####################################################################

from THREE.math.Triangle import *

# model ######################################################################

bbox = [-1., 1.]
points = [(x, y, z) for x in bbox for y in bbox for z in bbox]

faces  = [
	[0, 1, 2, 3],
	[1, 5, 3, 7],
	[5, 4, 7, 6],
	[4, 0, 6, 2],
	[2, 3, 6, 7],
	[4, 5, 0, 1],
]

def rgb(x, y, z):
	return x/2+.5, y/2+.5, z/2+.5

sizes = []
verticies, normals, colors = [], [], []

for indexes in faces:
	sizes.append(len(indexes))
	p0, p1, p2 = [points[indexes[i]] for i in range(3)]
	
	p0v = Vector3().fromArray(p0)
	p1v = Vector3().fromArray(p1)
	p2v = Vector3().fromArray(p2)
	
	triangle = Triangle(p0v, p1v, p2v)
	normalv = triangle.normal()
	normal = normalv.toArray()
	
	for index in indexes:
		vertex = points[index]
		verticies.append(vertex)
		normals.append(normal)
		colors.append(rgb(*vertex))

tex_coords = verticies
indicies = list(range(sum(sizes)))


__all__ = [
	"sizes",
	"indicies",
	"verticies",
	"tex_coords",
	"normals",
	"colors",
]