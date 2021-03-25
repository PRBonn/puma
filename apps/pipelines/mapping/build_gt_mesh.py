#!/usr/bin/env python3

import glob
import os
from pathlib import Path

import click
import numpy as np
import open3d as o3d
import pykitti
from tqdm import tqdm

from puma.mesh import run_poisson
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
    "--depth",
    type=int,
    default=10,
    help="Depth of the tree that will be used for reconstruction",
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
    default="range_image",
    help="Which normal computation to use",
)
@click.option(
    "--min_density",
    "-md",
    type=float,
    default=0.1,
    help="The minimun vertex density of the final mesh",
)
def main(
    dataset,
    out_dir,
    sequence,
    n_scans,
    start,
    depth,
    visualize,
    normals,
    min_density,
):
    """This script can be used to create GT mesh-model maps using GT poses. It
    assumes you have the data in the kitti-like format and all the scans where
    already pre-converted to '.ply', for example:

    \b
    kitti/ply
    ├── poses
    │   └── 00.txt
    └── sequences
        └── 00
            ├── calib.txt
            ├── poses.txt
            ├── times.txt
            └── velodyne
                ├── 000000.ply
                ├── 000001.ply
                └── ...

    You would also need the .txt files calib.txt and times.txt, altough not
    really used in this script, for convince, we reuse pykitti functionality
    that requires these files to be created.

    How to run it and check a quick example:

    \b
    $ ./build_gt_mesh.py -d $DATASETS/kitti/ply/ -s 00 -n 200 --depth 10
    """
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
    print("Processing " + str(n_scans) + " scans in " + scans)
    cloud_map = o3d.geometry.PointCloud()
    for idx in tqdm(range(start, start + n_scans)):
        source = preprocess_cloud(
            o3d.io.read_point_cloud(scan_names[idx]),
            normals=normals,
        )
        source.transform(gt_poses[idx])
        cloud_map += source

    print("Running Poisson Surface Reconstruction, go grab a coffee")
    o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Debug)

    mesh, _ = run_poisson(cloud_map, depth, -1, min_density)
    map_name = (
        "gt_"
        + dataset_name
        + "_seq_"
        + sequence
        + "_scans_"
        + str(n_scans)
        + "_depth_"
        + str(depth)
        + "_"
        + normals
    )
    mesh_file = os.path.join(out_dir, map_name + "_mesh.ply")
    print("Saving mesh to " + mesh_file)
    o3d.io.write_triangle_mesh(mesh_file, mesh)
    if visualize:
        o3d.visualization.draw_geometries([mesh])


if __name__ == "__main__":
    o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Info)

main()
