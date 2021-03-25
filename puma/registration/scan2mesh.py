import numpy as np
import open3d as o3d

from .run_icp import run_icp
from .scan2mesh_icp import scan2mesh_icp


def lost_track(delta, max_t_err=0.4):
    """Return True if the estimation from the mesh is to big."""
    t_err = np.linalg.norm(delta[:3, 3])
    return t_err > max_t_err


def register_scan_to_mesh(
    source, mesh, initial_guess, deltas, last_scan, config
):
    te = config.method
    th = config.threshold
    if config.strategy == "sample":
        tgt = o3d.geometry.PointCloud()
        tgt.points = o3d.utility.Vector3dVector(mesh.vertices)
        tgt.normals = o3d.utility.Vector3dVector(mesh.vertex_normals)
        pose = run_icp(source, tgt, initial_guess, config)
    else:
        success, pose = scan2mesh_icp(mesh, source, initial_guess, th, te)
        if not success:
            return run_icp(source, last_scan, initial_guess, config)

        if lost_track(np.linalg.inv(deltas[-1]) @ pose):
            pose = run_icp(source, last_scan, initial_guess, config)
    return pose
