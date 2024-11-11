from pathlib import Path 
import numpy as np 
import matplotlib as mpl
import matplotlib.pyplot as plt 
from matplotlib import font_manager
    
# when using xkcd, we need to add some additional fonts
font_path  = Path(__file__).parent/'xkcd-fonts'
for filename in font_path.glob('*'):
    font_manager.fontManager.addfont(filename)
    
class xkcd:
    """Turn on xkcd sketch-style drawing mode
    
    This context manager is based on plt.xkcd() and adds small adjustments.
    https://matplotlib.org/stable/gallery/showcase/xkcd.html#sphx-glr-gallery-showcase-xkcd-py
    The axis are centered around (0,0), there are no outer spines and
    additional arrows are added to the end.
    https://matplotlib.org/stable/gallery/spines/centered_spines_with_arrows.html
    
    
    Parameters
    ----------
    **kwargs
        Parameters when creating the figure with plt.subplots(**kwargs)

    Notes
    -----
    plt.show() must be called outside the context!
   
    Adjustments to the limits or ticks should happen in with xkcd():
   
    If an axis extends below 0, the label for the other one has to be
    moved manually and ylabel looks better with ax.set_ylabel('',rotation=0)
    ax.yaxis.set_label_coords(0,1,transform=ax.get_xaxis_transform())
    
    When using fill_between() together with plot(), the former should
    have a higher zorder or both should have the same and fill_between()
    should be called after plot().
    """
    
    def __init__(self,**kwargs):
        """All parameters are passed to plt.subplots()"""
        self.kwargs = kwargs
    
    def __enter__(self):

        # changes to the rcParams compared to standard xkcd
        rc = {"xtick.direction" : "inout", 
              "ytick.direction" : "inout",
              "xtick.major.size" : 8,
              "xtick.major.width" : 1.5,
              "ytick.major.size" : 8,
              "ytick.major.width" : 1.5,
              "axes.linewidth" : 1.5,
              "axes.autolimit_mode" : "data"
              }

        with plt.style.context('default') and plt.xkcd() and plt.rc_context(rc):

            fig, self.ax = plt.subplots(**self.kwargs) 
                   
            # check if ax is an axes or an array of axes 
            if isinstance(self.ax,mpl.axes._axes.Axes):
                axes = np.array([self.ax])
            else:
                axes = self.ax.ravel()

            for ax in axes:
                # let axes run through the center (0,0)
                # this does not work when called in __exit__
                ax.spines[["left", "bottom"]].set_position(("data", 0))
                ax.spines[["top", "right"]].set_visible(False)
                    
            return self.ax
            
    def __exit__(self,*args):
        
        # check if ax is an axes or an array of axes 
        if isinstance(self.ax,mpl.axes._axes.Axes):
            axes = np.array([self.ax])
        else:
            axes = self.ax.ravel()

        for ax in axes:
            
            # the follwing code might move xlim and ylim. In case they
            # are specified, we save them here to restore them again later
            xlim, ylim = ax.get_xlim(), ax.get_ylim()
            # lower limits >0 does not make sense for this style
            xlim, ylim = [min(xlim[0],0),xlim[1]], [min(ylim[0],0),ylim[1]]
            ax.set(xlim=xlim,ylim=ylim)

            # draw the arrow at the end of the axes
            ax.plot(1, 0, ">k", markersize=10, transform=ax.get_yaxis_transform(), clip_on=False,zorder=5)
            ax.plot(0, 1, "^k", markersize=10, transform=ax.get_xaxis_transform(), clip_on=False,zorder=5)
            
            # remove the last tick (and sometimes 0) from the axis
            xticks, yticks = ax.get_xticks(), ax.get_yticks()
            if ylim[0]<0:
                ax.set_xticks(xticks[xticks!=0][:-1])   
            else: 
                ax.set_xticks(xticks[:-1]) 
            if xlim[0]<0:
                ax.set_yticks(yticks[yticks!=0][:-1])     
            else: 
                ax.set_yticks(yticks[:-1])     

            ax.set(xlim=xlim,ylim=ylim)
            # show axes above the plot
            ax.set_axisbelow(False)
