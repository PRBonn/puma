import open3d as o3d

from .method_selector import get_te_method


def run_icp(src, tgt, trans_init, config):
    te = get_te_method(config.method)
    if config.method == "gicp":
        return o3d.pipelines.registration.registration_generalized_icp(
            src, tgt, config.threshold, trans_init, te
        ).transformation

    return o3d.pipelines.registration.registration_icp(
        src, tgt, config.threshold, trans_init, te
    ).transformation
