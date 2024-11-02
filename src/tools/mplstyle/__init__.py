"""Matplotlib Style Sheets

This subpackage contains style sheets for matplotlib. When loading the
style, it is advisable to combine it with "default" library to reset
any changes that might have occurred before. It is not necessary to
import the tools package in order to use the command

> plt.style.use(["default","tools.mplstyle.<style-name>"])

The following styles are available

* clean : a minimalistic design.
* LaTeX : used in academic papers.

Additional style sheets for the color are

* dark 
* forest 

This is based on the official documentation
https://matplotlib.org/stable/users/explain/customizing.html#distributing-styles
"""