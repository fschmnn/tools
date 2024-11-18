"""
Useful functions when dealing with multidimensional arrays. Superior and
more versatile versions might be available in packages like `scipy` or 
`skimage`, but the ones here were more suitable for my projects.
"""

import numpy as np

def find_segments(array,nan=-1):
    """Divide array into continuous segments with identical values.
    
    This functions uses `scipy.ndimage.label` to generate a separate map
    for each unique value from the input. The result is merged and 
    returned as a single array.
    
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.label.html

    Parameters
    ----------
    array : ndarray
        Array which is to be divided into individual segments.
    
    Returns
    -------
    segments : ndarray
        Array in which each segment is assigned a label, starting with 1.
    labels : list
        List with values of the segments.
    """
    
    try: 
        import scipy.ndimage as ndimage 
    except:
        raise ImportError('this function needs `scipy`')
        
    segments = []
    # we do this for every unique value that is not nan
    for value in np.unique(array[~np.isnan(array)]):
        segment, labels = ndimage.label(array==value)
        # zero is returned as background
        for label in range(1,labels+1):
            segments.append(segment==label)
    
    # we add up all layers and assign nan to the missing values
    segments = np.sum([segment*i for i,segment in enumerate(segments,1)],axis=0,dtype=float)
    segments[segments==0] = np.nan
    labels = np.unique(segments[~np.isnan(segments)])
        
    return segments, labels


def find_contours(segments,labels=None):
    """Find list of coordinates (x,y) for contours around labels.
    
    Parameters
    ----------
    segments : ndarray
        2D array where each segment is marked by a label.
    labels : list, optional
        List of labels around which a border is drawn. If not specified,
        all unique values in segments (except nan) are used as labels.  
        
    Returns
    -------
    contours : list of tuples
        Each element is represented by a tuple ((x1,x2),(y1,y2)).
        
    Notes
    -----
    This function just returns a list of lines between differing cells.
    They are not ordered and hence a bit tricky to convert to a polygon.
    To achieve that, the first step is to convert the two tuples that 
    represent x and y to two points    
        ((x1,x2),(y1,y2)) -> ((x1,y1),(x2,y2))
    We can then utilize `linemerge` from `shapely` to convert them into
    a sorted LineString. Finally we can create a polygon.

    > import shapely
    > points = [((c[0][0],c[1][0]),(c[0][1],c[1][1])) for c in contours]
    > line = shapely.ops.linemerge(points)
    > polygon = shapely.Polygon([point for point in line.coords])
    """
    
    if labels is None:
        labels=np.unique(segments[~np.isnan(segments)])
    indices = np.transpose(np.indices(segments.shape),axes=(1,2,0))

    contours = []
    for label in labels:
        points = indices[segments==label].tolist()
        for point in points:
            # right
            if [point[0],point[1]+1] not in points:
                contours.append(((point[1]+0.5,point[1]+0.5),(point[0]-0.5,point[0]+0.5)))
            # left
            if [point[0],point[1]-1] not in points:
                contours.append(((point[1]-0.5,point[1]-0.5),(point[0]-0.5,point[0]+0.5)))
            # top
            if [point[0]+1,point[1]] not in points:
                contours.append(((point[1]-0.5,point[1]+0.5),(point[0]+0.5,point[0]+0.5)))
            # bottom
            if [point[0]-1,point[1]] not in points:
                contours.append(((point[1]-0.5,point[1]+0.5),(point[0]-0.5,point[0]-0.5)))
    
    return contours 


def hex2d_to_rgb3d(hex2d):
    """ 
    Convert a 2D array that is filled with hex colors to a 3D array 
    with the corresponding rgb values.
    
    Parameters
    ----------
    hex2d : ndarray
        2D array containing 
        
    Returns
    -------
    rgb2d : ndarray
        3D array
    """
    
    rgb3d = np.full(hex2d.shape+(3,),np.nan)
    for hex_string in np.unique(hex2d):
        if hex_string.startswith('#'):
            rgb3d[hex2d==hex_string] = tuple(int(hex_string[i+1:i+3],16)/255  for i in (0, 2, 4)) 
    
    return rgb3d  