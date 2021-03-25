from math import floor

import numpy as np


def get_mesh_size(mesh):
    size = -1
    triangles = np.array(mesh.triangles)
    vertices = np.array(mesh.vertices)
    size += triangles.size * triangles.itemsize
    size += vertices.size * vertices.itemsize
    return size


def get_mesh_size_kb(mesh):
    return floor(get_mesh_size(mesh) / 1024.0)


def get_mesh_size_mb(mesh):
    return floor(get_mesh_size_kb(mesh) / 1024.0)
