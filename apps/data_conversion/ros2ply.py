#!/usr/bin/env python3


import os

import click
import numpy as np
import open3d as o3d
import rosbag
import sensor_msgs.point_cloud2 as pc2
from tqdm import tqdm


def convert_bag_to_ply(bag, topic, out_dir):
    field_names = ["x", "y", "z", "intensity"]
    max_intensity = 1000  # HACK: expose parameter
    bag_msgs = bag.read_messages(topics=[topic])
    msg_count = bag.get_message_count(topic)

    for idx, (_, msg, _) in tqdm(enumerate(bag_msgs), total=msg_count):
        points_xyz = []
        points_i = []
        points = pc2.read_points_list(
            cloud=msg, field_names=field_names, skip_nans=True
        )

        for point_xyzi in points:
            x, y, z, i = point_xyzi
            points_xyz.append([x, y, z])
            points_i.append([i, i, i])

        points_xyz = np.asarray(points_xyz)
        points_i = (np.asarray(points_i) / max_intensity).clip(0.0, 1.0)
        assert points_xyz.shape == points_i.shape, "Dimension Missmatch"

        filename = out_dir + str(idx).zfill(6) + ".ply"
        o3d_cloud = o3d.geometry.PointCloud()
        o3d_cloud.points = o3d.utility.Vector3dVector(points_xyz)
        o3d_cloud.colors = o3d.utility.Vector3dVector(points_i)
        o3d.io.write_point_cloud(filename, o3d_cloud)


@click.command()
@click.argument("bagfile", type=click.Path(exists=True))
@click.option(
    "--topic",
    type=str,
    default="/os1_cloud_node/points",
    help="Name of the topic to subscribe and convert the clouds",
)
@click.option(
    "--out_dir",
    type=click.Path(exists=False),
    default="results/",
    help="Where to store the results",
)
def main(bagfile, topic, out_dir):
    """Convert a .bag file into multiple .ply files, one for each scan,
    including intensity information encoded on the color channel of the
    PointCloud. We use Open3D to convert the data from ROS to
    o3d.geometry.PointCloud.

    To run it, start this script, then launch the rosbag file. Make sure you
    pass the right option to this script to select the point cloud topic.

    \b
    $ ./ros2ply.py --topic /points output.bag
    """
    print("Saving results to", out_dir)
    os.makedirs(out_dir, exist_ok=True)
    bag = rosbag.Bag(bagfile)
    assert topic in bag.get_type_and_topic_info().topics, (
        'topic: "' + topic + '" is not recorded in: ' + bagfile
    )

    convert_bag_to_ply(bag, topic, out_dir)
    bag.close()


if __name__ == "__main__":
    main()
