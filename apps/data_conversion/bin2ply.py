#!/usr/bin/env python3

import glob
import os

import click
import numpy as np
import open3d as o3d
import pykitti
from tqdm import tqdm


def load_velo_scan(file):
    """Load and parse a velodyne binary file."""
    scan = np.fromfile(file, dtype=np.float32)
    return scan.reshape((-1, 4))


def yield_velo_scans(velo_files):
    """Generator to parse velodyne binary files into arrays."""
    for file in velo_files:
        yield load_velo_scan(file)


def vel2ply(points, use_intensity=False):
    pcd = o3d.geometry.PointCloud()
    points_xyz = points[:, :3]
    points_i = points[:, -1].reshape(-1, 1)
    pcd.points = o3d.utility.Vector3dVector(points_xyz)
    if use_intensity:
        pcd.colors = o3d.utility.Vector3dVector(
            np.full_like(points_xyz, points_i)
        )
    return pcd


@click.command()
@click.option(
    "--dataset",
    "-d",
    type=click.Path(exists=True),
    default=os.environ["DATASETS"] + "/kitti-odometry/dataset/",
    show_default=True,
    help="Location of the KITTI dataset",
)
@click.option(
    "--out_dir",
    "-o",
    type=click.Path(exists=False),
    default="data/kitti-odometry/ply/",
    show_default=True,
    help="Where to store the results",
)
@click.option(
    "--sequence",
    "-s",
    type=str,
    default=None,
    required=False,
    help="Sequence number",
)
@click.option(
    "--use_intensity",
    is_flag=True,
    default=False,
    help="Encode the intensity value in the color channel",
)
def main(dataset, out_dir, sequence, use_intensity):
    """Utility script to convert from the binary form found in the KITTI
    odometry dataset to .ply files. The intensity value for each measurement is
    encoded in the color channel of the output PointCloud.

    If a given sequence it's specified then it assumes you have a clean copy of
    the KITTI odometry benchmark, because it uses pykitti. If you only have a
    folder with just .bin files the script will most likely fail.

    If no sequence is specified then it blindly reads all the *.bin file in the
    specified dataset directory
    """
    print(
        "Converting .bin scans into .ply fromat from:{orig} to:{dest}".format(
            orig=dataset, dest=out_dir
        )
    )

    os.makedirs(out_dir, exist_ok=True)
    if sequence:
        # Means KITTI like format
        base_path = os.path.join(out_dir, "sequences", sequence, "velodyne", "")
        os.makedirs(base_path, exist_ok=True)
        data = pykitti.odometry(dataset, sequence)
        velo_files = data.velo_files
        scans = data.velo
    else:
        # Read all the *.bin scans from the dataset folder
        base_path = os.path.join(out_dir, "")
        os.makedirs(base_path, exist_ok=True)
        velo_files = sorted(glob.glob(os.path.join(dataset, "*.bin")))
        scans = yield_velo_scans(velo_files)

    for points, scan_name in tqdm(
        zip(scans, velo_files), total=len(velo_files)
    ):
        pcd = vel2ply(points, use_intensity)
        stem = os.path.splitext(scan_name.split("/")[-1])[0]
        filename = base_path + stem + ".ply"
        o3d.io.write_point_cloud(filename, pcd)


if __name__ == "__main__":
    main()
