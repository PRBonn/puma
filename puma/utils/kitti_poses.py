import numpy as np


def save_poses(filename, poses):
    rows = []
    for pose in poses:
        rows.append(np.concatenate((pose[0], pose[1], pose[2])))

    np.savetxt(filename, np.array(rows))


def load_poses(pose_file):
    """Load ground truth poses (T_w_cam0) from file."""

    # Read and parse the poses
    poses = []
    try:
        with open(pose_file, "r") as f:
            for line in f.readlines():
                T_w_cam0 = np.fromstring(line, dtype=float, sep=" ")
                T_w_cam0 = T_w_cam0.reshape(3, 4)
                T_w_cam0 = np.vstack((T_w_cam0, [0, 0, 0, 1]))
                poses.append(T_w_cam0)

    except FileNotFoundError:
        print("GT Poses file not found: " + pose_file)

    return poses
