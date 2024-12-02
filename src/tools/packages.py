"""Regularly used packages

This module contains packages that I use in many projects. When starting
something new, I usually spend a few minutes importing all the necessary
packages, only to realize later that something is still missing. This is
especially annoying when using Python to quickly handle something. While
certainly not recommendable for larger projects, with this module, I can
just import everything needed and have everything ready. This does not
include "specialized" modules that are only used in one area.

Missing topics: 
* Astronomy : packages like astropy or photutils
* Geography : geopandas, rasterio, shapely etc.
* APIs      : for online databases like TMDb
"""

# basic packages
import calendar
import datetime
import time
import hashlib
import json
import yaml
import re
from pathlib import Path 
from tqdm import tqdm

# we are not necessarily inclined to use german
#from icalendar import Calendar, Event
#import locale
#locale.setlocale(locale.LC_TIME, 'de_DE')

# packages to handle data
import numpy as np
import pandas as pd
#import scipy 

# plot the result
import matplotlib.pyplot as plt
import matplotlib as mpl

# packages to handle shapes and perform geo transformations
#import shapely

# packages to handle images
#from PIL import Image

# package to handle graphs for navigation
#import networkx as nx

# access web data
from requests import get
from bs4 import BeautifulSoup 
#from io import BytesIO
