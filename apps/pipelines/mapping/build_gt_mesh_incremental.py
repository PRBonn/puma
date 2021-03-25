#!/usr/bin/env python3

import csv
import glob
import os
from collections import deque
from pathlib import Path

import click
import numpy as np
import open3d as o3d

from puma.mesh import create_mesh_from_map, get_mesh_size_mb
from puma.preprocessing import preprocess
from puma.utils import (
    get_progress_bar,
    load_config_from_yaml,
    load_kitti_gt_poses,
    print_progress,
)


@click.command()
@click.option("--config", "-c", default="config/puma.yml")
@click.option(
    "--dataset",
    "-d",
    type=click.Path(exists=True),
    default=os.environ["HOME"] + "/data/kitti-odometry/ply/",
    help="Location of the KITTI-like dataset",
)
@click.option(
    "--n_scans", "-n", type=int, default=-1, help="Number of scans to integrate"
)
@click.option("--sequence", "-s", type=str, default="00")
def main(config, dataset, n_scans, sequence):
    """Similar to the slam/puma_pipeline.py but uses GT poses intead of
    estimate the ego-motion of the vehivle. Build an incremental map using
    the same technique used in the original puma pipeline."""
    config = load_config_from_yaml(config)
    dataset = os.path.join(dataset, "")
    os.makedirs(config.out_dir, exist_ok=True)

    map_name = Path(dataset).parent.name
    map_name += "_" + sequence
    map_name += "_depth_" + str(config.depth)
    map_name += "_cropped" if config.min_density else ""
    gt_poses = load_kitti_gt_poses(dataset, sequence)
    map_name += "_gt"

    poses_file = map_name + ".txt"
    poses_file = os.path.join(config.out_dir, poses_file)
    print("Results will be saved to", poses_file)

    scans = os.path.join(dataset, "sequences", sequence, "velodyne", "")
    scan_names = sorted(glob.glob(scans + "*.ply"))

    # Create data containers to store the map
    mesh = o3d.geometry.TriangleMesh()

    # Create a circular buffer, the same way we do in the C++ implementation
    local_map = deque(maxlen=config.acc_frame_count)
    global_mesh = o3d.geometry.TriangleMesh()

    poses = [np.eye(4, 4, dtype=np.float64)]

    # Open csv file to output map size
    csv_file = os.path.join(config.out_dir, map_name + ".csv")
    print("Saving Map Size to", csv_file)
    csv_file = open(csv_file, "w")
    csv_writer = csv.writer(csv_file, delimiter=" ", lineterminator="\n")
    csv_writer.writerow(["frames", "vertices", "triangles", "size"])

    # Start the mapping pipeline
    scan_count = 0
    map_count = 0
    pbar = get_progress_bar(1, n_scans)
    for idx in pbar:
        str_size = print_progress(pbar, idx, n_scans)
        scan = preprocess(o3d.io.read_point_cloud(scan_names[idx]), config)
        poses.append(gt_poses[idx])
        scan.transform(poses[-1])
        local_map.append(scan)

        scan_count += 1
        if scan_count >= config.acc_frame_count or idx == n_scans - 1:
            scan_count = 0
            msg = "[scan #{}] Running PSR over local_map".format(idx)
            pbar.set_description(msg.rjust(str_size))
            mesh, _ = create_mesh_from_map(
                local_map, config.depth, config.n_threads, config.min_density
            )

        map_count += 1
        if map_count >= config.acc_map_count or idx == n_scans - 1:
            map_count = 0
            global_mesh += mesh
            global_mesh = global_mesh.remove_duplicated_triangles()
            global_mesh = global_mesh.remove_duplicated_vertices()
            vertices = len(global_mesh.vertices)
            triangles = len(global_mesh.triangles)
            size_mb = get_mesh_size_mb(global_mesh)
            csv_writer.writerow([idx, vertices, triangles, size_mb])

    # Save map to file
    mesh_map_file = os.path.join(config.out_dir, map_name + ".ply")
    print("Saving Map to", mesh_map_file)
    o3d.io.write_triangle_mesh(mesh_map_file, global_mesh)
    csv_file.close()


if __name__ == "__main__":
    main()
