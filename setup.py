from glob import glob

from pybind11.setup_helpers import Pybind11Extension
from setuptools import setup

ext_modules = [
    Pybind11Extension(
        "puma.cpp.normal_map",
        sorted(glob("puma/cpp/*.cpp")),
        extra_compile_args=["-fopenmp"],
        extra_link_args=["-fopenmp"],
    ),
]


setup(
    ext_modules=ext_modules,
)
