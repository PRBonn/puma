# Installation <!-- omit in toc -->

- [Local Installation](#local-installation)
  - [Hard dependencies](#hard-dependencies)
  - [Open3D](#open3d)
  - [Embree](#embree)
  - [puma](#puma)
- [Testing Installation](#testing-installation)

## Local Installation

If your some reason you plan to develop on top of this code, then the best
idea is to build the dependencies from source and work "locally". All the
commands from the example are still valid, the only difference is that you
don't need to use any `docker-compose` command at all. Just run the plain
python scripts.

### Hard dependencies

- Open3D, our fork with [Generalized ICP support][gicp]
- [Intel Embree][embree] >= v2.17.7 # but not 3.x
- [`pyembree`][pyembree] library
- `pybind11` python API

The rest dependencies should be solved by the build system.

### Open3D

For the moment you will need to manually install our own [fork of Open3D][gicp]

```sh
bash 3rdparty/Open3D.sh
```

That should give you the power of `Open3D` with the Generalized ICP algorithm
implementation. If you can't install `Open3D` please refer to the [original
documentation](http://www.open3d.org/docs/release/compilation.html)

### Embree

Just run the installation script provided by the author of `trimesh`:

```sh
bash 3rdparty/embree.sh
```

That should give you the pyembree library

### puma

There are different ways of installing this package, probably the easiest is to
clone this source and just run

```shell
pip install pybind11
pip install --user .
```

## Testing Installation

Just `cd` out of the source dir and run an interactive python shell:

```python
import puma
```

If that doesn't fail then you can assume you've installed puma successfully.

<!-- References -->

[pyembree]: https://github.com/scopatz/pyembree
[embree]: https://www.embree.org/
[gicp]: https://github.com/nachovizzo/Open3D/tree/nacho/generalized_icp
