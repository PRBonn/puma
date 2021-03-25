import copy

import numpy as np
import open3d as o3d
import trimesh

if not trimesh.ray.has_embree:
    raise "PyEmbree engine not installed, this experiment will never end"


def outlier_rejection(
    source_points, source_normals, target_points, target_normals, max_dist=2.0
):
    # Prune long rays, max_distance threshold
    ray_distances = np.linalg.norm(target_points - source_points, axis=1)

    # Get distance inliers
    source_points = source_points[ray_distances < max_dist]
    target_points = target_points[ray_distances < max_dist]
    source_normals = source_normals[ray_distances < max_dist]
    target_normals = target_normals[ray_distances < max_dist]

    return source_points, source_normals, target_points, target_normals


def project_scan_to_mesh(tmesh, source, max_dist=2.0):
    """Project a PointCloud to the given mesh using ray to triangle
    intersections."""

    # Create the rays we will shoot
    source_points = np.asarray(source.points)
    source_normals = np.asarray(source.normals)
    ray_directions = copy.deepcopy(source_points)
    ray_origins = np.zeros_like(ray_directions)

    # run the mesh- ray query
    target_points, index_ray, index_tri = tmesh.ray.intersects_location(
        ray_origins=ray_origins,
        ray_directions=ray_directions,
        multiple_hits=False,
    )

    # Manually pick all the points and normals that did hit any of the triangles
    source_points = source_points[index_ray]
    source_normals = source_normals[index_ray]
    target_normals = np.asarray(tmesh.face_normals[index_tri])

    (
        source_points,
        source_normals,
        target_points,
        target_normals,
    ) = outlier_rejection(
        source_points, source_normals, target_points, target_normals, max_dist
    )

    # Create the new source and target PointClouds
    source_cloud = o3d.geometry.PointCloud()
    source_points = o3d.utility.Vector3dVector(np.asarray(source_points))
    source_normals = o3d.utility.Vector3dVector(np.asarray(source_normals))
    source_cloud.points = source_points
    source_cloud.normals = source_normals

    target_cloud = o3d.geometry.PointCloud()
    target_points = o3d.utility.Vector3dVector(np.asarray(target_points))
    target_normals = o3d.utility.Vector3dVector(np.asarray(target_normals))
    target_cloud.points = target_points
    target_cloud.normals = target_normals
    return source_cloud, target_cloud
