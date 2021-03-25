#!/usr/bin/env python3
import click
import open3d as o3d

from ..cpp.normal_map import gen_normal_map
from ..projections.range_image import project_to_range_image


def compute_normals(cloud, w, h):
    range_image, vertex_map = project_to_range_image(cloud, w, h)
    normal_map = gen_normal_map(range_image, vertex_map, w, h)
    cloud.points = o3d.utility.Vector3dVector(vertex_map.reshape(h * w, 3))
    cloud.normals = o3d.utility.Vector3dVector(normal_map.reshape(h * w, 3))
    cloud.remove_non_finite_points()
    return cloud


@click.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("-w", default=1024, type=int)
@click.option("-h", default=64, type=int)
def main(file, w, h):
    cloud = compute_normals(o3d.io.read_point_cloud(file), w, h)
    o3d.visualization.draw_geometries([cloud])


if __name__ == "__main__":
    main()
