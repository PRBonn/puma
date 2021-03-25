#!/usr/bin/env python3
import glob
import os
from pathlib import Path

import click
import numpy as np
import open3d as o3d
import pykitti
from tqdm import tqdm

from puma.preprocessing import preprocess_cloud


@click.command()
@click.option(
    "--dataset",
    "-d",
    type=click.Path(exists=True),
    default=os.environ["HOME"] + "/data/kitti-odometry/ply/",
    help="Location of the KITTI-like dataset",
)
@click.option(
    "--out_dir",
    type=click.Path(exists=True),
    default="./results/",
    help="Location of the output directory",
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
@click.option(
    "--visualize",
    is_flag=True,
    default=False,
    help="Visualize all the preprocess pipeline",
)
@click.option(
    "--normals",
    type=click.Choice(["range_image", "kdtree"], case_sensitive=False),
    default=None,
    help="Which normal computation to use",
)
def main(dataset, out_dir, sequence, n_scans, start, visualize, normals):
    """From a set of input PointClouds create one unique aggreated map cloud."""
    o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Info)
    dataset = os.path.join(dataset, "")

    dataset_name = Path(dataset).parent.name

    data = pykitti.odometry(dataset, sequence)
    T_cam_velo = data.calib.T_cam0_velo
    T_velo_cam = np.linalg.inv(T_cam_velo)

    gt_poses = T_velo_cam @ data.poses @ T_cam_velo

    scans = os.path.join(dataset, "sequences", sequence, "velodyne", "")
    scan_names = sorted(glob.glob(scans + "*.ply"))

    # Use the whole sequence if -1 is specified
    n_scans = len(scan_names) if n_scans == -1 else n_scans
    print("Processing " + str(n_scans) + " in " + scans)
    cloud_map = o3d.geometry.PointCloud()
    for idx in tqdm(range(start, start + n_scans)):
        source = preprocess_cloud(
            o3d.io.read_point_cloud(scan_names[idx]),
            normals=normals,
        )

        source.transform(gt_poses[idx])
        cloud_map += source

    map_name = (
        "gt_"
        + str(n_scans)
        + "_scans_"
        + sequence
        + "_"
        + dataset_name
        + ".ply"
    )
    out_file = os.path.join(out_dir, map_name)
    print("saving map to " + out_file)
    o3d.io.write_point_cloud(out_file, cloud_map)

    if visualize:
        o3d.visualization.draw_geometries([cloud_map])


if __name__ == "__main__":
    main()
