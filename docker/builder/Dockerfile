# ==== Builder ================================================================#
FROM ubuntu:20.04 AS builder
LABEL maintainer="Ignacio Vizzo <ivizzo@uni-bonn.de>"

# setup environment
ENV TERM xterm
ENV DEBIAN_FRONTEND=noninteractive

# install essentials
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    git \
    python3 \
    python3-dev \
    python3-pip \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Add python3 and pip aliases
RUN update-alternatives \
    --install /usr/bin/python python $(which python3) 20 \
    --slave /usr/bin/pip pip $(which pip3)

# Install 3rdparty dependencies, split dependencies for separate docker overlays
COPY 3rdparty/embree.sh 3rdparty/
RUN bash 3rdparty/embree.sh

# Open3D needs cmake >= 3.18
COPY 3rdparty/cmake.sh 3rdparty/
RUN bash 3rdparty/cmake.sh

# Install generalized_icp branch of Open3D until reaches the main branch
COPY 3rdparty/Open3D.sh 3rdparty/
RUN bash 3rdparty/Open3D.sh

# Install Python dependencies
RUN pip install --upgrade \
    black \
    pybind11 \
    setuptools

# Install puma
COPY . /puma
RUN cd /puma && pip install --upgrade . && rm -rf /puma

# Patch pykitti to avoid pulling opencv-python dependency
COPY 3rdparty/patch_pykitti.sh 3rdparty/
RUN bash 3rdparty/patch_pykitti.sh

# Cleanup
RUN rm -rf 3rdparty
