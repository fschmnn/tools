""" 
This module contains functions and classes to handle colors.

When working with colors and looking for a method to describe them, 
color theory offers a multitude of formats, that are often suited for a 
specific topic (https://en.wikipedia.org/wiki/Color_theory). Many Python
packages like `colorsys` or `matplotlib` already provide collections of
useful functions. However, none of them contains all aspects that are 
relevant to me. Furthermore, there are small differences in how the 
different formats are processed. For example some store RGB in three 
channels with 8 bits [0,255] while others use floats in the range [0,1] 
and the same is true for other formats like HSV or HSL. 

This package combines a collection of existing functions with useful 
additions for me and makes sure they all use the same format.
"""

import colorsys
import re
from typing import Union

#__all__ = ['CNAMES','to_rgb','Color','ColorPalette']


# the following dictionary is based on mpl.colors.BASE_COLORS | mpl.colors.TABLEAU_COLORS | mpl.colors.CSS4_COLORS
# the 166 entries contain only 152 as some keys like `fuchsia` or `magenta` 
# refer to the same color.
BASE_COLORS = {'b': '#0000ff', 'g': '#008000', 'r': '#ff0000', 'c': '#00bfbf', 'm': '#bf00bf', 'y': '#bfbf00', 'k': '#000000', 'w': '#ffffff'} 
CSS4_COLORS = {'aliceblue': '#f0f8ff', 'antiquewhite': '#faebd7', 'aqua': '#00ffff', 'aquamarine': '#7fffd4', 'azure': '#f0ffff', 'beige': '#f5f5dc', 'bisque': '#ffe4c4', 'black': '#000000', 'blanchedalmond': '#ffebcd', 'blue': '#0000ff', 'blueviolet': '#8a2be2', 'brown': '#a52a2a', 'burlywood': '#deb887', 'cadetblue': '#5f9ea0', 'chartreuse': '#7fff00', 'chocolate': '#d2691e', 'coral': '#ff7f50', 'cornflowerblue': '#6495ed', 'cornsilk': '#fff8dc', 'crimson': '#dc143c', 'cyan': '#00ffff', 'darkblue': '#00008b', 'darkcyan': '#008b8b', 'darkgoldenrod': '#b8860b', 'darkgray': '#a9a9a9', 'darkgreen': '#006400', 'darkgrey': '#a9a9a9', 'darkkhaki': '#bdb76b', 'darkmagenta': '#8b008b', 'darkolivegreen': '#556b2f', 'darkorange': '#ff8c00', 'darkorchid': '#9932cc', 'darkred': '#8b0000', 'darksalmon': '#e9967a', 'darkseagreen': '#8fbc8f', 'darkslateblue': '#483d8b', 'darkslategray': '#2f4f4f', 'darkslategrey': '#2f4f4f', 'darkturquoise': '#00ced1', 'darkviolet': '#9400d3', 'deeppink': '#ff1493', 'deepskyblue': '#00bfff', 'dimgray': '#696969', 'dimgrey': '#696969', 'dodgerblue': '#1e90ff', 'firebrick': '#b22222', 'floralwhite': '#fffaf0', 'forestgreen': '#228b22', 'fuchsia': '#ff00ff', 'gainsboro': '#dcdcdc', 'ghostwhite': '#f8f8ff', 'gold': '#ffd700', 'goldenrod': '#daa520', 'gray': '#808080', 'green': '#008000', 'greenyellow': '#adff2f', 'grey': '#808080', 'honeydew': '#f0fff0', 'hotpink': '#ff69b4', 'indianred': '#cd5c5c', 'indigo': '#4b0082', 'ivory': '#fffff0', 'khaki': '#f0e68c', 'lavender': '#e6e6fa', 'lavenderblush': '#fff0f5', 'lawngreen': '#7cfc00', 'lemonchiffon': '#fffacd', 'lightblue': '#add8e6', 'lightcoral': '#f08080', 'lightcyan': '#e0ffff', 'lightgoldenrodyellow': '#fafad2', 'lightgray': '#d3d3d3', 'lightgreen': '#90ee90', 'lightgrey': '#d3d3d3', 'lightpink': '#ffb6c1', 'lightsalmon': '#ffa07a', 'lightseagreen': '#20b2aa', 'lightskyblue': '#87cefa', 'lightslategray': '#778899', 'lightslategrey': '#778899', 'lightsteelblue': '#b0c4de', 'lightyellow': '#ffffe0', 'lime': '#00ff00', 'limegreen': '#32cd32', 'linen': '#faf0e6', 'magenta': '#ff00ff', 'maroon': '#800000', 'mediumaquamarine': '#66cdaa', 'mediumblue': '#0000cd', 'mediumorchid': '#ba55d3', 'mediumpurple': '#9370db', 'mediumseagreen': '#3cb371', 'mediumslateblue': '#7b68ee', 'mediumspringgreen': '#00fa9a', 'mediumturquoise': '#48d1cc', 'mediumvioletred': '#c71585', 'midnightblue': '#191970', 'mintcream': '#f5fffa', 'mistyrose': '#ffe4e1', 'moccasin': '#ffe4b5', 'navajowhite': '#ffdead', 'navy': '#000080', 'oldlace': '#fdf5e6', 'olive': '#808000', 'olivedrab': '#6b8e23', 'orange': '#ffa500', 'orangered': '#ff4500', 'orchid': '#da70d6', 'palegoldenrod': '#eee8aa', 'palegreen': '#98fb98', 'paleturquoise': '#afeeee', 'palevioletred': '#db7093', 'papayawhip': '#ffefd5', 'peachpuff': '#ffdab9', 'peru': '#cd853f', 'pink': '#ffc0cb', 'plum': '#dda0dd', 'powderblue': '#b0e0e6', 'purple': '#800080', 'rebeccapurple': '#663399', 'red': '#ff0000', 'rosybrown': '#bc8f8f', 'royalblue': '#4169e1', 'saddlebrown': '#8b4513', 'salmon': '#fa8072', 'sandybrown': '#f4a460', 'seagreen': '#2e8b57', 'seashell': '#fff5ee', 'sienna': '#a0522d', 'silver': '#c0c0c0', 'skyblue': '#87ceeb', 'slateblue': '#6a5acd', 'slategray': '#708090', 'slategrey': '#708090', 'snow': '#fffafa', 'springgreen': '#00ff7f', 'steelblue': '#4682b4', 'tan': '#d2b48c', 'teal': '#008080', 'thistle': '#d8bfd8', 'tomato': '#ff6347', 'turquoise': '#40e0d0', 'violet': '#ee82ee', 'wheat': '#f5deb3', 'white': '#ffffff', 'whitesmoke': '#f5f5f5', 'yellow': '#ffff00', 'yellowgreen': '#9acd32'}
TABLEAU_COLORS = {'tab:blue': '#1f77b4', 'tab:orange': '#ff7f0e', 'tab:green': '#2ca02c', 'tab:red': '#d62728', 'tab:purple': '#9467bd', 'tab:brown': '#8c564b', 'tab:pink': '#e377c2', 'tab:gray': '#7f7f7f', 'tab:olive': '#bcbd22', 'tab:cyan': '#17becf'}
CNAMES = CSS4_COLORS | TABLEAU_COLORS | BASE_COLORS


def is_hex(string: str) -> bool:
    """check if string is a valid hex triplet (#000000 or 000000)"""
    return bool(re.match(r'^#?([0-9a-fA-F]{6}|[0-9a-fA-F]{8})$',string))

# when converting from [0,1] to [0,255] or [0,360] we round the result
ROUNDING_PRECISION = 2

def rgb_to_RGB(rgb):
    """change the range of the values from [0.0 to 1.0] to [0 to 255]"""
    return tuple(round(255*c) for c in rgb)

def RGB_to_rgb(RGB):
    """change the range of the values from [0 to 255] to [0.0 to 1.0]"""
    return tuple(c/255 for c in RGB)

def rgb_to_hex(rgb):
    """rgb in range [0.0 to 1.0] to hex color #xxxxxx"""
    return '#'+''.join(f'{round(255*i):02x}' for i in rgb)

def hex_to_rgb(hex):
    """hex color #xxxxxx for rgb in range [0.0 to 1.0]"""
    return tuple(int(hex.lstrip('#')[i:i+2],16)/255 for i in [0,2,4])

def rgb_to_cmyk(rgb):
    """rgb in range [0.0 to 1.0] to cmyk in percent [0 to 100]"""
    cmy = tuple(1-i for i in rgb)
    k = min(cmy)
    return tuple(round(100*(i-k)/(1-k),ROUNDING_PRECISION) for i in cmy) + (round(100*k,ROUNDING_PRECISION),)

def cmyk_to_rgb(cmyk):
    """cmyk in percent [0 to 100] to rgb in range [0.0 to 1.0]"""
    return tuple((1-i/100)*(1-cmyk[-1]) for i in cmyk[:-1]) 
    
def rgb_to_hsv(rgb):
    """rgb in range [0.0 to 1.0] to hsv in range [0 to 360,0 to 100,0 to 100]
    
    This function is based on colorsys.rgb_to_hsv but converts the 
    range for hsv from [0.0 to 1.0] to [0 to 360,0 to 100,0 to 100].
    """
    h, s, v = colorsys.rgb_to_hsv(*rgb) 
    return (round(360*h,ROUNDING_PRECISION),
            round(100*s,ROUNDING_PRECISION),
            round(100*v,ROUNDING_PRECISION))

def hsv_to_rgb(hsv):
    """hsv in range [0 to 360,0 to 100,0 to 100] to rgb in range [0.0 to 1.0]
    
    This function is based on colorsys.hsv_to_rgb but converts the 
    range for hsv from [0.0 to 1.0] to [0 to 360,0 to 100,0 to 100]
    """
    return colorsys.hsv_to_rgb(hsv[0]/360,hsv[1]/100,hsv[2]/100)

def rgb_to_hsl(rgb):
    """rgb in range [0.0 to 1.0] to hsl in range [0 to 360,0 to 100,0 to 100]
    
    This function is based on colorsys.rgb_to_hls but converts the 
    range for hsv from [0.0 to 1.0] to [0 to 360,0 to 100,0 to 100]. 
    Also the order of s and l are switched.
    """
    h, l, s = colorsys.rgb_to_hls(*rgb) 
    return (round(360*h,ROUNDING_PRECISION),
            round(100*s,ROUNDING_PRECISION),
            round(100*l,ROUNDING_PRECISION))

def hsl_to_rgb(hsl):
    """ hsl in range [0 to 360,0 to 100,0 to 100] to rgb in range [0.0 to 1.0]
    
    This function is based on colorsys.hls_to_rgb but converts the 
    range for hsv from [0.0 to 1.0] to [0 to 360,0 to 100,0 to 100]. 
    Also the order of s and l are switched.
    """
    return colorsys.hls_to_rgb(hsl[0]/360,hsl[2]/100,hsl[1]/100)
      
      
def to_rgb(*args,**kwargs):
    """Identify format of the input and convert it to rgb.
    
    Parameters
    ----------
    *args 
        The name (e.g. `red`), hex or rgb as tuple or three integers.
    **kwargs 
        The name of the format (rgb, hsv, hsl or cmyk) with value.
        
    Returns 
    -------
    rgb : tuple
        rgb values in range [0.0 to 1.0]
    """
    
    # 1st step: determine format 
    
    # if specified in kwargs, the first one is used
    for k,v in kwargs.items():
        if k.lower() in ['rgb','rgba','hex','hsv','hsb','hls','hsl','cmyk']:
            format, value = k.lower(), v
            break
    else:
        # maybe multiple kwargs are used for r, g and b
        if all(c in kwargs for c in ['r','g','b']):
            format, value = 'rgb', (kwargs['r'],kwargs['g'],kwargs['b'])
        # if we find no match, we continue our search in args
        else:
            # if three args are passed we assume they are (r,g,b)
            if len(args)==3:
                format, value = 'rgb', 
            # otherwise we only check the first arg
            elif len(args)==1:
                arg = args[0]
                # there are strings with len 3 so we also need to check the instance
                if isinstance(arg,(tuple,list)) and (len(arg) == 3):
                    format, value = 'rgb', arg
                elif isinstance(arg,str):
                    # if it is contained in CNAMES, we assign the corresponding color
                    if arg.lower() in CNAMES:
                        format, value = 'name', arg.lower()
                    # optional start with # followed by 6 characters
                    elif is_hex(arg):
                        format, value = 'hex', arg.lower()
    if 'format' not in locals():
        raise ValueError(f'unknown format: args={args}, kwargs={kwargs}')
    
    # 2nd step: convert to rgb
    if format == 'rgb':
        if all([c<=1. for c in value]):
            rgb = value 
        else:
            rgb = tuple(c/255 for c in value)
    elif format == 'rgba':
        if all([c<=1. for c in value[:3]]):
            rgb = value[:3]
        else:
            rgb = tuple(c/255 for c in value[:3])
    elif format == 'name':
        rgb = hex_to_rgb(CNAMES[value])
    elif format == 'hex':
        rgb = hex_to_rgb(value)
    elif format == 'cmyk':
        rgb = cmyk_to_rgb(value)
    elif (format == 'hsv') or (format == 'hsb'):
        rgb = hsv_to_rgb(value)
    elif (format == 'hsl'):
        rgb = hsl_to_rgb(value)  
    elif (format == 'hls'):
        rgb = hsl_to_rgb((value[0],value[2],value[1])) 
    else:
        raise ValueError(f'unexpected error for {format}: {value}')
        
    return rgb 


class Color:
    """
    
    
    Operators
    ---------
    __add__, __sub__, __mul__, __truediv__, __eq__, __str__, _repr_html_
    """
    
    def __init__(self,*args,**kwargs):
        # store the input (mostly for debugging)
        self.args = args
        self.kwargs = kwargs
       
        # if a Color object is passed we skip the to_rgb() 
        if args and isinstance(args[0],Color):
            self._rgb = args[0]._rgb
        else:
            self._rgb = to_rgb(*args,**kwargs)

    @property
    def name(self):
        """Assign a name based on the nearest colors in CNAMES"""
        # create a dictionary with the distance to each named color
        distances = {name: 
            (int(hex[1:3],16)-int(self.hex[1:3],16))**2 +
            (int(hex[3:5],16)-int(self.hex[3:5],16))**2 +
            (int(hex[5:7],16)-int(self.hex[5:7],16))**2
            for name,hex in CNAMES.items()}
        return min(distances,key=distances.get)
    @property
    def cmyk(self):
        return rgb_to_cmyk(self._rgb)
    @property
    def grey(self):
        return 0.2989*self._rgb[0] + 0.5870*self._rgb[1] + 0.1140*self._rgb[2]
    @property
    def hex(self):
        return rgb_to_hex(self._rgb)
    @property
    def hsl(self):
        return rgb_to_hsl(self._rgb)
    @property
    def hsv(self):
        return rgb_to_hsv(self._rgb)
    @property
    def rgb(self):
        return rgb_to_RGB(self._rgb)

    def update(self):
        """Normalize the RGB value to the range [0 to 1]
        The arithmetic operations can return values outside the allowed 
        range of [0 to 1]. This function clips all those values.
        """
        self._rgb = tuple([max(min(c,1.),0.) for c in self._rgb])
        return self

    def __add__(self,summand):
        """Add RGB values of two Color objects""" 
        r1,g1,b1 = self._rgb
        r2,g2,b2 = summand._rgb 
        sum = Color(self)
        sum._rgb = (r1+r2,g1+g2,b1+b2)
        return sum
    
    def __sub__(self,subtrahend):
        """Subtract RGB values of two Color objects""" 
        r1,g1,b1 = self._rgb
        r2,g2,b2 = subtrahend._rgb 
        difference = Color(self)
        difference._rgb = (r1-r2,g1-g2,b1-b2)
        return difference
    
    def __mul__(self,multiplicand):
        """Multiply each RGB values with multiplicand (int or float)"""
        r1,g1,b1 = self._rgb
        product = Color(self)
        product._rgb = (r1*multiplicand,g1*multiplicand,b1*multiplicand)
        return product 
    
    def __truediv__(self,divisor):
        """Divide each RGB values with divisor (int or float)"""
        r1,g1,b1 = self._rgb
        quotient = Color(self)
        quotient._rgb = (r1/divisor,g1/divisor,b1/divisor)
        return quotient 
    
    def __eq__(self,other):
        if isinstance(other,Color):
            return self.hex == other.hex
        else:
            return False
    
    def __str__(self):
        return self.hex

    def _repr_html_(self):
        # this is more a _repr_svg_ but it html it looks nicer
        if self.grey<0.2:
            font_color = 'white'
        else: 
            font_color = 'black'
        
        return (
            '<svg width="128" height="128" xmlns="http://www.w3.org/2000/svg">' 
            # the rectangle with the color
            '<rect width="128" height="128" x="0" y="0" rx="16" ry="16"'
            f'fill="{self.hex}"/>'
            # the text with the hex
            f'<text x="50%" y="50%" text-anchor="middle"' 
            f'fill="{font_color}" font-size="20">{self.hex}</text>'
            '</svg>' 
        )   

# ----------------------------------------------------------------------
# ColorPalette
# ----------------------------------------------------------------------

def complementary(color):
    r,g,b = color.rgb
    return Color((255-r,255-g,255-b))

def analogous(color):
    h,s,v = color.hsv
    # this should be updated to ColorPalette
    return [Color(hsv=(hue,s,v)) for hue in [(h-30)%360,h,(h+30)%360]]

def triadic(color):
    h,s,v = color.hsv
    # this should be updated to ColorPalette
    return [Color(hsv=(hue,s,v)) for hue in [h,(h+120)%360,(h+240)%360]]

def tetradic(color):
    pass 

def square(color):
    h,s,v = color.hsv
    # this should be updated to ColorPalette
    return [Color(hsv=(hue,s,v)) for hue in [h,(h+90)%360,(h+180)%360,(h+270)%360]]


class ColorPalette(list):
    """A subclass of list to store and visualize a collection of colors.
    
    Constructors
    ------------
    __init__()
    complementary()
    analogous() 
    triadic()
    square()
    
    Methods
    -------
    to_hex()
    shift()
    
    Operators
    ---------
    __add__, __iadd__, __radd__, __getitem__, _repr_html_
    """
    
    # Constructors
    @staticmethod
    def complementary(color):
        return ColorPalette([Color(color),complementary(Color(color))])
    
    @staticmethod     
    def analogous(color):
        return ColorPalette(analogous(color))

    @staticmethod     
    def triadic(color):
        return ColorPalette(triadic(color))
    
    @staticmethod     
    def square(color):
        return ColorPalette(square(color))
    
    # Methods
    def to_hex(self,inplace=False):
        """Convert all entries to hex"""
        if inplace:
            for i, color in enumerate(self):
                self[i] = Color(color).hex
        else:
            return ColorPalette([Color(color).hex for color in self])
    
    def shift(self,shift):
        """Shift entries"""
        return ColorPalette(self[shift%len(self):]+self[:shift%len(self)])
    
    # Operators
    def __add__(self, other):
        return ColorPalette(list.__add__(self,other))

    def __iadd__(self, other):
        super().__iadd__(other)
        return self
    
    def __radd__(self,other):
        return ColorPalette(other)+self

    def __getitem__(self, index):
        result = super().__getitem__(index)
        if isinstance(result,list):
            return ColorPalette(result)
        else:
            # a single element should be returned as a color in order to use it
            return result 
        
    def _repr_html_(self):
        if len(self)<=10:
            padding = min([5,50/len(self)])
        else:
            padding = 0
        figsize = (min([80*len(self),800]),80)
        width, height = figsize[0]/len(self)-padding, 80-padding
        svg  = f'<svg width="{figsize[0]}" height="{figsize[1]}" xmlns="http://www.w3.org/2000/svg">'
        for i in range(len(self)):
            x, y = i*(width+padding)+padding, padding/2
            svg += f'<rect width="{width}" height="{height}" x="{x}" y="{y}" fill="{self[i]}"/>'
        svg += '</svg>'
        
        return svg 

        
if __name__=='__main__':
    for kwargs in ({'hsl':(50.59,100,50)},
               {'hsv':(50.59,100,100)},
               {'cmyk':(0,16,100,0)},
               {'r':255,'g':215,'b':0}):
        format, value = to_rgb(**kwargs)
        print(format,value)
    for args in [(255,215,0)]:
        format, value = to_rgb(*args)
        print(format,value)
    for arg in ('#ffd700','gold',(255,215,0)):
        format, value = to_rgb(arg)
        print(format,value)