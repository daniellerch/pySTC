import os
import ctypes
import glob

module_dir = os.path.dirname(__file__)

shared_libs = glob.glob(os.path.join(module_dir, "stc_extension.*.so"))  # Linux/macOS
if not shared_libs and os.name == "nt":
    shared_libs = glob.glob(os.path.join(module_dir, "stc_extension.*.pyd"))  # Windows

if not shared_libs:
    raise ImportError("Extension not found `stc_extension` in `pystc`.")

stc = ctypes.CDLL(shared_libs[0])

from .pystc import hide, unhide

