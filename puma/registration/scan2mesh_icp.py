import copy

import numpy as np
import open3d as o3d
import trimesh

from ..projections import project_scan_to_mesh
from .method_selector import get_te_method


def align_clouds(source, target, method):
    """Align 2 PointCloud objects assuming 1-1 correspondences."""
    assert len(source.points) == len(target.points), "N of points must match!"
    corr = np.zeros((len(source.points), 2))
    corr[:, 0] = np.arange(len(source.points))
    corr[:, 1] = np.arange(len(target.points))
    te = get_te_method(method)
    return te.compute_transformation(
        source, target, o3d.utility.Vector2iVector(corr)
    )


def scan2mesh_icp(
    mesh,
    pcd,
    trans_init=np.eye(4, 4),
    max_dist=0.1,
    method="gicp",
    max_iterations=30,
    tolerance=0.00001,
    debug=False,
):
    source = copy.deepcopy(pcd)
    prev_error = 0
    distances = 0
    transformation = trans_init
    source.transform(trans_init)

    # Convert from Open3D mesh object to a trimesh one
    tmesh = trimesh.Trimesh(
        vertices=np.asarray(mesh.vertices), faces=np.asarray(mesh.triangles)
    )
    for i in range(max_iterations):
        # Project the input cloud to the mesh and obtain the projected cloud
        source, target = project_scan_to_mesh(tmesh, source, max_dist)
        if (
            not target.has_points()
            or not target.has_normals()
            or len(target.points) < 1000
        ):
            return False, None

        # compute the transformation between clouds
        T = align_clouds(source, target, method)

        # update the current source
        source.transform(T)
        transformation = T @ transformation

        # check error
        distances = source.compute_point_cloud_distance(target)
        mean_error = np.mean(distances)
        if np.abs(prev_error - mean_error) < tolerance:
            break

        if debug:
            print("Iteration {} completed".format(i))
            print("Number of inliers :", len(source.points))
            print(
                "mean_error = {err}, prev_error = {prev}".format(
                    err=mean_error, prev=prev_error
                )
            )
        prev_error = mean_error

    return True, transformation
