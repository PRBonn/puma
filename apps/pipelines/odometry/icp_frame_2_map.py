#!/usr/bin/env python3

import glob
import os
from collections import deque
from pathlib import Path

import click
import numpy as np
import open3d as o3d

from puma.preprocessing import preprocess
from puma.registration import run_icp
from puma.utils import (
    buffer_to_pointcloud,
    get_progress_bar,
    load_config_from_yaml,
    print_progress,
    save_config_yaml,
    save_poses,
    vel2cam,
)


def get_map_name(config, dataset, sequence):
    dataset_name = Path(dataset).parent.name
    map_name = dataset_name + "_" + sequence + "_frame2map_icp_"
    map_name += config.normals + "_" if config.normals else ""
    map_name += config.method
    return map_name


@click.command()
@click.option("--config", "-c", default="config/p2p_icp.yml")
@click.option(
    "--dataset",
    "-d",
    type=click.Path(exists=True),
    default=os.environ["HOME"] + "/data/kitti-odometry/ply/",
    help="Location of the KITTI-like dataset",
)
@click.option(
    "--sequence", "-s", type=str, default="00", help="Sequence number"
)
@click.option(
    "--n_scans", "-n", type=int, default=-1, help="Number of scans to integrate"
)
@click.option(
    "--start", "-sp", type=int, default=0, help="Start from this scan on"
)
def main(config, dataset, sequence, n_scans, start):
    config = load_config_from_yaml(config)
    if config.debug:
        o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Debug)
    dataset = os.path.join(dataset, "")
    scans = os.path.join(dataset, "sequences", sequence, "velodyne", "")
    scan_names = sorted(glob.glob(scans + "*.ply"))

    os.makedirs(config.out_dir, exist_ok=True)
    map_name = get_map_name(config, dataset, sequence)
    poses_file = map_name + ".txt"
    poses_file = os.path.join(config.out_dir, poses_file)

    # Save config
    config_file = map_name + ".yml"
    config_file = os.path.join(config.out_dir, config_file)
    save_config_yaml(config_file, dict(config))

    # Use the whole sequence if -1 is specified
    if n_scans == -1:
        n_scans = len(scan_names) - start

    first_scan_id = start
    last_scan_id = start + n_scans

    print("Processing " + str(n_scans) + " scans in " + scans)
    poses = [np.eye(4, 4, dtype=np.float64)]
    deltas = [np.eye(4, 4, dtype=np.float64)]

    first_scan = preprocess(o3d.io.read_point_cloud(scan_names[0]), config)
    local_map = deque(maxlen=config.acc_frame_count)
    local_map.append(first_scan)

    # Start the mapping pipeline
    pbar = get_progress_bar(first_scan_id + 1, last_scan_id)
    for idx in pbar:
        print_progress(pbar, idx, n_scans)
        scan = preprocess(o3d.io.read_point_cloud(scan_names[idx]), config)
        # The target model is the local map that is used on the PSR pipeline but
        # running standard ICP.
        target = buffer_to_pointcloud(local_map)
        target.transform(np.linalg.inv(poses[-1]))

        # run frame-to-local-map ICP
        initial_guess = deltas[-1] if config.warm_start else np.eye(4)
        pose = run_icp(scan, target, initial_guess, config)
        deltas.append(pose)
        poses.append(poses[-1] @ pose)

        # This will never exceed config.acc_frame_count scans
        scan.transform(poses[-1])
        local_map.append(scan)

    # Save results to txt file
    print("Saving estimated poses [camera frame] to " + poses_file)
    save_poses(poses_file, vel2cam(poses))


if __name__ == "__main__":
    main()
