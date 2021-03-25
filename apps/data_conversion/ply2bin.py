#!/usr/bin/env python3
import glob
import os
import struct

import click
import numpy as np
import open3d as o3d
from tqdm import tqdm


def save_bin_file(file, points):
    with open(file, "wb") as bin_file:
        for point in points.tolist():
            bin_file.write(struct.pack("f" * len(point), *point))


def get_bin_filaname(dataset_out, scan_name):
    return os.path.join(
        dataset_out, os.path.split(os.path.splitext(scan_name)[0])[1] + ".bin"
    )


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
def main(dataset, out_dir, sequence):
    dataset_in = os.path.join(dataset, "sequences", sequence, "velodyne", "")
    dataset_out = os.path.join(out_dir, "sequences", sequence, "velodyne", "")
    print("Converting ply files from " + dataset_in)

    scan_names = sorted(glob.glob(dataset_in + "*.ply"))
    for scan_name in tqdm(scan_names):
        scan = o3d.io.read_point_cloud(scan_name)
        points = np.asarray(scan.points)
        intensity = np.ones(points.shape[0]) / 2.0
        # convert from (size,) to (size,1)
        intensity = intensity.reshape(-1, 1)
        xyzi_points = np.hstack((points, intensity))
        out_file = get_bin_filaname(dataset_out, scan_name)
        save_bin_file(out_file, xyzi_points)


if __name__ == "__main__":
    main()
