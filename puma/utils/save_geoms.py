import os

import open3d as o3d


def save_cloud(cloud, name, out_dir):
    filename = os.path.join(out_dir, "gt_map_" + name + ".ply")
    print("saving cloud_map to " + filename)
    o3d.io.write_point_cloud(filename, cloud)


def save_mesh(mesh, name, out_dir):
    mesh.compute_vertex_normals()
    mesh.compute_triangle_normals()

    filename = os.path.join(out_dir, name + ".ply")
    print("saving mesh_map to " + filename)
    o3d.io.write_triangle_mesh(filename, mesh, print_progress=True)
