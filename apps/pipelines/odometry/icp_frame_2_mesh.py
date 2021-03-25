#!/usr/bin/env python3

import copy
import glob
import os
from collections import deque
from pathlib import Path

import click
import numpy as np
import open3d as o3d

from puma.mesh import create_mesh_from_map
from puma.preprocessing import preprocess
from puma.registration import register_scan_to_mesh, run_icp
from puma.utils import (
    get_progress_bar,
    load_config_from_yaml,
    print_progress,
    save_config_yaml,
    save_poses,
    vel2cam,
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
    config = load_config_from_yaml(config)
    if config.debug:
        o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Debug)
    dataset = os.path.join(dataset, "")
    os.makedirs(config.out_dir, exist_ok=True)

    map_name = Path(dataset).parent.name
    map_name += "_" + sequence
    map_name += "_depth_" + str(config.depth)
    map_name += "_cropped" if config.min_density else ""
    map_name += "_" + config.method
    map_name += "_" + config.strategy

    # Save config
    config_file = map_name + ".yml"
    config_file = os.path.join(config.out_dir, config_file)
    save_config_yaml(config_file, dict(config))

    poses_file = map_name + ".txt"
    poses_file = os.path.join(config.out_dir, poses_file)
    print("Results will be saved to", poses_file)

    scans = os.path.join(dataset, "sequences", sequence, "velodyne", "")
    scan_names = sorted(glob.glob(scans + "*.ply"))

    # Use the whole sequence if -1 is specified
    n_scans = len(scan_names) if n_scans == -1 else n_scans

    # Create data containers to store the map
    mesh = o3d.geometry.TriangleMesh()

    # Create a circular buffer, the same way we do in the C++ implementation
    local_map = deque(maxlen=config.acc_frame_count)

    poses = [np.eye(4, 4, dtype=np.float64)]
    deltas = [np.eye(4, 4, dtype=np.float64)]
    last_scan = preprocess(o3d.io.read_point_cloud(scan_names[0]), config)

    # Start the Odometry and Mapping pipeline
    scan_count = 0
    pbar = get_progress_bar(1, n_scans)
    for idx in pbar:
        str_size = print_progress(pbar, idx, n_scans)
        scan = preprocess(o3d.io.read_point_cloud(scan_names[idx]), config)
        initial_guess = deltas[-1].copy() if config.warm_start else np.eye(4)
        if mesh.has_vertices():
            msg = "[scan #{}] Registering scan to mesh model".format(idx)
            pbar.set_description(msg.rjust(str_size))
            mesh.transform(np.linalg.inv(poses[-1]))
            pose = register_scan_to_mesh(
                scan, mesh, initial_guess, deltas, last_scan, config
            )
        else:
            pose = run_icp(scan, last_scan, initial_guess, config)
        deltas.append(pose)
        poses.append(poses[-1] @ pose)
        last_scan = copy.deepcopy(scan)
        scan.transform(poses[-1])
        local_map.append(scan)

        scan_count += 1
        if scan_count >= config.acc_frame_count or idx == n_scans - 1:
            save_poses(poses_file, vel2cam(poses))
            msg = "[scan #{}] Running PSR over local_map".format(idx)
            pbar.set_description(msg.rjust(str_size))
            mesh, _ = create_mesh_from_map(
                local_map, config.depth, config.n_threads, config.min_density
            )


if __name__ == "__main__":
    main()
