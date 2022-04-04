#!/bin/bash
set -ex

# Obtain the location of the pykitti package
pykitti_dir=$(
python3 - <<-EOF

import sys
import traceback
import os

try:
    import pykitti
except ModuleNotFoundError as err:
    print(os.path.dirname(traceback.extract_tb(sys.exc_info()[2])[-1].filename))
EOF
)

echo "Patching pykitti in $pykitti_dir"
sed -i '/import cv2/d' "${pykitti_dir}/tracking.py"
