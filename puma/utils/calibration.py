import numpy as np
import pykitti


T_cam_velo = np.array(
    [
        [4.27680239e-04, -9.99967248e-01, -8.08449168e-03, -1.19845993e-02],
        [-7.21062651e-03, 8.08119847e-03, -9.99941316e-01, -5.40398473e-02],
        [9.99973865e-01, 4.85948581e-04, -7.20693369e-03, -2.92196865e-01],
        [0.00000000e00, 0.00000000e00, 0.00000000e00, 1.00000000e00],
    ]
)

T_velo_cam = np.array(
    [
        [4.27679428e-04, -7.21062673e-03, 9.99973959e-01, 2.91804720e-01],
        [-9.99967209e-01, 8.08119861e-03, 4.85949420e-04, -1.14055066e-02],
        [-8.08449174e-03, -9.99941381e-01, -7.20693461e-03, -5.6239412e-02],
        [0.00000000e00, 0.00000000e00, 0.00000000e00, 1.00000000e00],
    ]
)


def cam2vel(poses):
    return T_velo_cam @ poses @ T_cam_velo


def vel2cam(poses):
    return T_cam_velo @ poses @ T_velo_cam


def load_kitti_gt_poses(dataset, sequence):
    data = pykitti.odometry(dataset, sequence)
    return T_velo_cam @ data.poses @ T_cam_velo
