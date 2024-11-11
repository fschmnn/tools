"""Python tools

This package contains collection of functions and classes, that are used 
in multiple projects, in order to avoid diverging versions.
"""

from .filemanager import File
from .hashfunction import simplehash
from .progressbar import pbar
from .mplstyle.xkcd import xkcd


# add mplstyles to the the matplotlib library. This is copy-paste from: 
# https://github.com/garrettj403/SciencePlots/blob/master/scienceplots/__init__.py

from pathlib import Path
import matplotlib.pyplot as plt

path = Path(__file__).parent / 'mplstyle'
stylesheets = plt.style.core.read_style_directory(path)

plt.style.core.update_nested_dict(plt.style.library, stylesheets)
plt.style.core.available[:] = sorted(plt.style.library.keys())
