import open3d as o3d

PointToPoint = o3d.pipelines.registration.TransformationEstimationPointToPoint
PointToPlane = o3d.pipelines.registration.TransformationEstimationPointToPlane
try:
    GICP = o3d.pipelines.registration.TransformationEstimationForGeneralizedICP
except AttributeError as error:
    raise SystemExit(
        "Open3D with GeneralizedICP support not installed, check INSTALL.md"
    )
