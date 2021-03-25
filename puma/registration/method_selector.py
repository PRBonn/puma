import open3d as o3d

from .o3d_aliases import GICP, PointToPlane, PointToPoint


def get_te_method(str_method):
    if str_method == "gicp":
        return GICP()
    if str_method == "p2p":
        return PointToPoint()
    if str_method == "p2l":
        loss = o3d.pipelines.registration.HuberLoss(0.5)
        return PointToPlane(loss)
    return None
