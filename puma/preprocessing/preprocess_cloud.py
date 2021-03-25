#!/usr/bin/env python3
from copy import deepcopy

import open3d as o3d

from .range_image_normal import compute_normals as ri_normal


def preprocess_cloud(
    pcd,
    voxel_size=0.25,
    max_nn=20,
    normals=None,
    downsample=False,
    W=1024,
    H=64,
):
    if downsample:
        cloud = pcd.voxel_down_sample(voxel_size)
    else:
        cloud = deepcopy(pcd)

    if normals:
        if normals == "range_image":
            ri_normal(cloud, W, H)
        else:
            params = o3d.geometry.KDTreeSearchParamKNN(max_nn)
            cloud.estimate_normals(params)
            cloud.orient_normals_towards_camera_location()

    return cloud


def preprocess(pcd, config):
    return preprocess_cloud(
        pcd,
        config.voxel_size,
        config.max_nn,
        config.normals,
        config.downsample,
        config.W,
        config.H,
    )
