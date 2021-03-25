#!/bin/bash
# Install Open3D with GeneralizedICP support
# Based on Open3D/util/ci_utils.sh

set -ex

NPROC=${NPROC:-$(getconf _NPROCESSORS_ONLN)} # POSIX: MacOS + Linux

# Patch for PSR
patch_psr() {
    git apply --ignore-whitespace <<EOF
diff --git a/Src/FEMTree.Initialize.inl b/Src/FEMTree.Initialize.inl
index df0e156..cb6ca50 100644
--- a/Src/FEMTree.Initialize.inl
+++ b/Src/FEMTree.Initialize.inl
@@ -190,7 +190,7 @@ size_t FEMTreeInitializer< Dim , Real >::Initialize( FEMTreeNode& root , InputPo
        pointStream.reset();
    }
    if( outOfBoundPoints  ) WARN( "Found out-of-bound points: " , outOfBoundPoints );
-	if( badData           ) WARN( "Found bad data: " , badData );
+	/* if( badData           ) WARN( "Found bad data: " , badData ); */
    if( std::is_same< Real , float >::value )
    {
        std::vector< size_t > badNodeCounts( ThreadPool::NumThreads() , 0 );
diff --git a/Src/FEMTree.IsoSurface.specialized.inl b/Src/FEMTree.IsoSurface.specialized.inl
index 28b5ef0..88710e4 100644
--- a/Src/FEMTree.IsoSurface.specialized.inl
+++ b/Src/FEMTree.IsoSurface.specialized.inl
@@ -1855,7 +1855,7 @@ public:
        FEMTree< Dim , Real >::MemoryUsage();
        if( pointEvaluator ) delete pointEvaluator;
        size_t badRootCount = _BadRootCount;
-		if( badRootCount!=0 ) WARN( "bad average roots: " , badRootCount );
+		/* if( badRootCount!=0 ) WARN( "bad average roots: " , badRootCount ); */
        return isoStats;
    }
 };
EOF
}

build_all() {

    echo "Using cmake: $(which cmake)"
    cmake --version

    mkdir -p build
    cd build

    cmakeOptions=(
        -DCMAKE_BUILD_TYPE=Release
        -DPYTHON_EXECUTABLE="$(which python)"
        -DBUILD_LIBREALSENSE=OFF
        -DBUILD_UNIT_TESTS=OFF
        -DBUILD_BENCHMARKS=OFF
        -DBUILD_EXAMPLES=OFF
        -DENABLE_HEADLESS_RENDERING=ON
        -DBUILD_GUI=OFF
        -DUSE_SYSTEM_GLEW=OFF
        -DUSE_SYSTEM_GLFW=OFF
    )

    echo Running cmake "${cmakeOptions[@]}" ..
    cmake "${cmakeOptions[@]}" ..
    echo "Build & install Open3D..."
    make VERBOSE=1 -j"$NPROC"
    make install -j"$NPROC"
    make VERBOSE=1 install-pip-package -j"$NPROC"
}

# install open3d with python bindings
git clone --depth 1 --recurse-submodules \
    https://github.com/nachovizzo/Open3D.git /tmp/Open3D -b nacho/generalized_icp &&
    cd /tmp/Open3D/

# Patch Poisson Surface Reconstruction so it doesn't fill up the console.
cd 3rdparty/PoissonRecon/PoissonRecon/ && patch_psr && cd -

# Was impossible to pass the SUDO env variable to the script, so remove it :)
sed -i 's/sudo//' util/install_deps_ubuntu.sh

# install Open3D dependencies
bash util/install_deps_ubuntu.sh assume-yes

# Build and cleanup to save space
build_all
rm -rf /tmp/Open3D && rm -rf /var/lib/apt/lists/*
