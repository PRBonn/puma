import matplotlib.pyplot as plt
import numpy as np
import open3d as o3d

from ..utils import buffer_to_pointcloud


def plot_density_mesh(mesh, densities, min_density):
    """Inspired in the original open3d implementation."""
    densities = np.asarray(densities)
    density_colors = plt.get_cmap("jet")(
        (densities - densities.min()) / (densities.max() - densities.min())
    )
    density_colors = density_colors[:, :3]
    density_mesh = o3d.geometry.TriangleMesh()
    density_mesh.vertices = mesh.vertices
    density_mesh.triangles = mesh.triangles
    density_mesh.triangle_normals = mesh.triangle_normals
    density_mesh.vertex_colors = o3d.utility.Vector3dVector(density_colors)

    print("Visualize densities")
    o3d.visualization.draw_geometries([density_mesh])

    print("Remove low density vertices")
    vertices_to_remove = densities < np.quantile(densities, min_density)
    density_mesh.remove_vertices_by_mask(vertices_to_remove)
    o3d.visualization.draw_geometries([density_mesh])


def run_poisson(pcd, depth, n_threads, min_density=None):
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        pcd, depth=depth, n_threads=n_threads
    )

    # Post-process the mesh
    if min_density:
        vertices_to_remove = densities < np.quantile(densities, min_density)
        mesh.remove_vertices_by_mask(vertices_to_remove)
    mesh.compute_vertex_normals()

    return mesh, densities


def create_mesh_from_map(buffer, depth, n_threads, min_density=None):
    pcd = buffer_to_pointcloud(buffer)
    return run_poisson(pcd, depth, n_threads, min_density)
