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

# Install Open3D system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    libgl1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade \
    black \
    pybind11 \
    setuptools

# Install modern version of Open3D
RUN pip install --upgrade --pre \
    https://files.pythonhosted.org/packages/10/02/4f777e87131b3e111f91e16c1782da707b8b6a5777dbbe11a19e0dc7d1a3/open3d-0.15.2-cp38-cp38-manylinux_2_27_x86_64.whl

# Install puma
COPY . /puma
RUN cd /puma \
    && pip install --no-cache-dir --requirement requirements.txt \
    && pip install --no-cache-dir --upgrade . \
    && rm -rf /puma

# Install 3rdparty dependencies, split dependencies for separate docker overlays
COPY 3rdparty/embree.sh 3rdparty/
RUN bash 3rdparty/embree.sh

# Patch pykitti to avoid pulling opencv-python dependency
COPY 3rdparty/patch_pykitti.sh 3rdparty/
RUN bash 3rdparty/patch_pykitti.sh

# Cleanup
RUN rm -rf 3rdparty
