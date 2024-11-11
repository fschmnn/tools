"""Matplotlib Style Sheets

This subpackage contains style sheets for matplotlib. When loading the
style, it is advisable to combine it with "default" library to reset
any changes that might have occurred before. When the package is loaded,
the matplotlib styles are updated and the desired style can be loaded as

> plt.style.use(["default","<style-name>"])

However it is not necessary to import the tools package 

> plt.style.use(["default","tools.mplstyle.<style-name>"])

The following styles are available

* journal : for use in academic papers.
* TeX : used in my published papers.
* web : a minimalistic design.
* LaTeX-off : turn off usetex (currently not working)
* LaTeX-on : turn on usetex (currently not working)

Additional style sheets for the color are
 
* forest 
* mood
* saturation 

This is based on the official documentation
https://matplotlib.org/stable/users/explain/customizing.html#distributing-styles
"""

from .xkcd import xkcd
