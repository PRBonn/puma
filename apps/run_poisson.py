#!/usr/bin/env python3

import os

import click
import open3d as o3d

from puma.mesh import plot_density_mesh, run_poisson


@click.command()
@click.argument("filename", type=click.Path(exists=True))
@click.option(
    "--depth",
    "-d",
    type=int,
    default=8,
    help="Depth of the tree that will be used for reconstruction",
)
@click.option(
    "--min_density",
    "-md",
    type=float,
    default=0.1,
    help="The minimun vertex density of the final mesh",
)
@click.option(
    "--visualize",
    is_flag=True,
    default=False,
    help="Visualize the reconstructed surface",
)
@click.option(
    "--plot_densities",
    is_flag=True,
    default=False,
    help="Plot the densities of the reconstructed mesh",
)
def main(filename, depth, min_density, visualize, plot_densities):
    """Util script to run the Poisson Surface Reconstruction over a
    determined input PointCloud, usually a pre-build PointCloud map, for
    example like the ones you could build with
    apps/pipelines/mapping/build_gt_cloud.py."""
    print("Reading " + filename + "...")
    pcd = o3d.io.read_point_cloud(filename, print_progress=True)

    print("Running Poisson Surface Reconstruction, go grab a coffe")
    o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Debug)
    mesh, densities = run_poisson(pcd, depth, -1, min_density)

    if plot_densities:
        plot_density_mesh(mesh, densities, min_density)

    print(mesh)
    mesh.compute_vertex_normals()
    mesh_name = os.path.splitext(filename)[0] + "_mesh.ply"
    print("Saving mesh to " + mesh_name)
    o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Error)
    o3d.io.write_triangle_mesh(mesh_name, mesh)
    if visualize:
        o3d.visualization.draw_geometries([mesh])


if __name__ == "__main__":
    main()
