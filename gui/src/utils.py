"""Some important variables. Mostly here to prevent circular imports"""

import os
import sys

src_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
root_dir = os.path.normpath(os.path.join(src_dir, ".."))
config_dir = os.path.join(root_dir, "config")
