""" 
Very basic functions
"""

__all__ = ["pbar","shift"]

import tqdm

# Adjust the bar_format for the tqdm progress bar
def pbar(iterable,
         bar_format='{desc} {percentage:3.0f}%|{bar:32}| {n_fmt}/{total_fmt} ({elapsed})',
         color='blue',
         **kwargs):
    return tqdm.tqdm(iterable,bar_format=bar_format,colour=color,**kwargs)
pbar.__doc__ = tqdm.tqdm.__doc__


def shift(list,shift):
    """Shift a list or tuple
    
    This function moves the elements of a list or tuple similar to 
    `numpy.roll`. However the direction is reversed, with a positive 
    shift moving elements to the left and negative shift to the right. 
    
    Parameters
    ----------
    list : list or tuple
    shift : int 
    """
    
    return list[shift%len(list):]+list[:shift%len(list)]