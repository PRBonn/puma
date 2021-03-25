#!/usr/bin/env python3

import glob
import os
from pathlib import Path

import click
import numpy as np
import open3d as o3d
from tqdm import trange

from puma.preprocessing import preprocess
from puma.registration import run_icp
from puma.utils import (
    load_config_from_yaml,
    save_config_yaml,
    save_poses,
    vel2cam,
)


def get_scan_names(dataset):
    dataset = os.path.join(dataset, "")
    scan_names = sorted(glob.glob(dataset + "*.ply"))
    return scan_names


@click.command()
@click.option("--config", "-c", default="config/p2p_icp.yml")
@click.option(
    "--dataset",
    "-d",
    type=click.Path(exists=True),
    help="Dataset location, format:ply",
)
@click.option(
    "--n_scans", "-n", type=int, default=-1, help="Number of scans to integrate"
)
@click.option(
    "--start_scan", "-st", type=int, default=0, help="Start from scan"
)
@click.option("--sequence", "-s", type=str, help="Sequence number")
def main(config, dataset, n_scans, start_scan, sequence):
    config = load_config_from_yaml(config)
    if config.debug:
        o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Debug)
    dname = Path(dataset).parent.name
    approach = Path(dataset).name
    dataset = os.path.join(dataset, "sequences", sequence, "velodyne", "")
    map_name = dname + "_" + sequence + "_"
    map_name += config.method + "_frame2frame_icp"

    # Save config
    config_file = map_name + ".yml"
    config_file = os.path.join(config.out_dir, config_file)
    save_config_yaml(config_file, dict(config))

    if not config.out_dir:
        config.out_dir = os.path.join("results", approach)
        os.makedirs(config.out_dir, exist_ok=True)

    poses_file = map_name + ".txt"
    poses_file = os.path.join(config.out_dir, poses_file)
    print("Results will be saved to", poses_file)

    poses = [np.eye(4, 4, dtype=np.float64)]
    deltas = [np.eye(4, 4, dtype=np.float64)]

    # Get dataset
    scan_names = get_scan_names(dataset)

    # Use the whole sequence if -1 is specified
    if n_scans == -1:
        n_scans = len(scan_names)

    print("Processing " + str(n_scans) + " in " + dataset)
    target = preprocess(o3d.io.read_point_cloud(scan_names[0]), config)
    for idx in trange(start_scan + 1, start_scan + n_scans):
        source = preprocess(o3d.io.read_point_cloud(scan_names[idx]), config)

        # Run ICP
        initial_guess = deltas[-1] if config.warm_start else np.eye(4)
        pose = run_icp(source, target, initial_guess, config)
        deltas.append(pose)
        poses.append(poses[-1] @ pose)

        # This scan will be the target in the next iteration
        target = source

    # Save results to txt file
    print("Saving estimated poses [camera frame] to " + poses_file)
    save_poses(poses_file, vel2cam(poses))


if __name__ == "__main__":
    main()
