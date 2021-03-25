#!/usr/bin/env python3

import os
from pathlib import Path

import click
import numpy as np
import pykitti
import rosbag
import rospy
import sensor_msgs.point_cloud2 as pcl2
import tf
from geometry_msgs.msg import Transform, TransformStamped
from sensor_msgs.msg import PointField
from std_msgs.msg import Header
from tf2_msgs.msg import TFMessage
from tqdm import tqdm


def write_gt_pose_to_bag(bag, gt_pose, timestamp):
    tf_msg = TFMessage()
    tf_stamped = TransformStamped()
    tf_stamped.header.stamp = rospy.Time.from_sec(timestamp)
    tf_stamped.header.frame_id = "world"
    tf_stamped.child_frame_id = "velodyne"

    t = gt_pose[0:3, 3]
    q = tf.transformations.quaternion_from_matrix(gt_pose)
    transform = Transform()

    transform.translation.x = t[0]
    transform.translation.y = t[1]
    transform.translation.z = t[2]

    transform.rotation.x = q[0]
    transform.rotation.y = q[1]
    transform.rotation.z = q[2]
    transform.rotation.w = q[3]

    tf_stamped.transform = transform
    tf_msg.transforms.append(tf_stamped)

    bag.write("/tf", tf_msg, tf_msg.transforms[0].header.stamp)


def write_scan_to_bag(bag, scan, timestamp):
    # create header
    header = Header()
    header.frame_id = "velodyne"
    header.stamp = rospy.Time.from_sec(timestamp)

    # fill pcl msg
    fields = [
        PointField("x", 0, PointField.FLOAT32, 1),
        PointField("y", 4, PointField.FLOAT32, 1),
        PointField("z", 8, PointField.FLOAT32, 1),
        PointField("intensity", 12, PointField.FLOAT32, 1),
    ]
    pcl_msg = pcl2.create_cloud(header, fields, scan)

    bag.write("/velodyne_points", pcl_msg, t=pcl_msg.header.stamp)


def get_kitti_odometry(dataset, sequence):
    data = pykitti.odometry(dataset, sequence)
    n_scans = len(data)
    T_cam_velo = data.calib.T_cam0_velo
    T_velo_cam = np.linalg.inv(T_cam_velo)

    gt_poses = T_velo_cam @ data.poses @ T_cam_velo
    timestamps = [dt.total_seconds() for dt in data.timestamps]
    # Hack: Add 1 nano sec in the first timestamp, ros python has bug in the
    # implementation, this doesn't happen in the C++ one
    timestamps[0] += 1e-9

    return n_scans, gt_poses, timestamps, data.velo


@click.command()
@click.option(
    "--dataset",
    "-d",
    type=click.Path(exists=True),
    help="Location of the KITTI-like dataset",
)
@click.option(
    "--out_dir",
    "-o",
    default="./results/",
    type=click.Path(exists=True),
    help="name of the rosbag file",
)
@click.option(
    "--sequence", "-s", type=str, default="00", help="Sequence number"
)
def main(dataset, out_dir, sequence):
    filename = Path(dataset).parent.name + "_seq_" + sequence + ".bag"
    rosbag_filename = os.path.join(out_dir, filename)

    n_scans, gt_poses, timestamps, scans = get_kitti_odometry(dataset, sequence)

    bag = rosbag.Bag(rosbag_filename, "w")
    try:

        iterable_data = tqdm(zip(timestamps, scans, gt_poses), total=n_scans)
        for dt, scan, gt_pose in iterable_data:
            write_scan_to_bag(bag, scan, dt)
            write_gt_pose_to_bag(bag, gt_pose, dt)

    finally:
        print(bag)
        bag.close()


if __name__ == "__main__":
    main()
