#!/bin/bash
# Instructions from https://apt.kitware.com/

set -ex

apt-get update && apt-get install --no-install-recommends -y \
    apt-transport-https \
    ca-certificates \
    gnupg \
    software-properties-common &&
    rm -rf /var/lib/apt/lists/*

wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null |
    gpg --dearmor - |
    tee /etc/apt/trusted.gpg.d/kitware.gpg >/dev/null

apt-add-repository 'deb https://apt.kitware.com/ubuntu/ focal main'
apt-get update && apt-get install --no-install-recommends -y \
    cmake &&
    rm -rf /var/lib/apt/lists/*
