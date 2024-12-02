"""Python tools

This package contains collection of functions and classes, that are used 
in multiple projects, in order to avoid diverging versions.
"""

from .array import find_contours, find_segments, hex2d_to_rgb3d
from .basics import pbar, shift
from .calendar import *
from .colors import *
from .filemanager import File
from .hashfunction import simplehash
