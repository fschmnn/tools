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

__all__ = ['CNAMES','nameColor','hexColor','hsvColor','hslColor',
           'cmykColor','rgbColor','to_color','ColorPalette',
           'complementary','analogous','triadic','tetradic','square',
           'hsv_gradient','rgb_gradient']

# the following dictionary is based on mpl.colors.BASE_COLORS | mpl.colors.TABLEAU_COLORS | mpl.colors.CSS4_COLORS
# the 166 entries contain only 152 as some keys like `fuchsia` or `magenta` 
# refer to the same color.
BASE_COLORS = {'b': '#0000ff', 'g': '#008000', 'r': '#ff0000', 'c': '#00bfbf', 'm': '#bf00bf', 'y': '#bfbf00', 'k': '#000000', 'w': '#ffffff'} 
CSS4_COLORS = {'aliceblue': '#f0f8ff', 'antiquewhite': '#faebd7', 'aqua': '#00ffff', 'aquamarine': '#7fffd4', 'azure': '#f0ffff', 'beige': '#f5f5dc', 'bisque': '#ffe4c4', 'black': '#000000', 'blanchedalmond': '#ffebcd', 'blue': '#0000ff', 'blueviolet': '#8a2be2', 'brown': '#a52a2a', 'burlywood': '#deb887', 'cadetblue': '#5f9ea0', 'chartreuse': '#7fff00', 'chocolate': '#d2691e', 'coral': '#ff7f50', 'cornflowerblue': '#6495ed', 'cornsilk': '#fff8dc', 'crimson': '#dc143c', 'cyan': '#00ffff', 'darkblue': '#00008b', 'darkcyan': '#008b8b', 'darkgoldenrod': '#b8860b', 'darkgray': '#a9a9a9', 'darkgreen': '#006400', 'darkgrey': '#a9a9a9', 'darkkhaki': '#bdb76b', 'darkmagenta': '#8b008b', 'darkolivegreen': '#556b2f', 'darkorange': '#ff8c00', 'darkorchid': '#9932cc', 'darkred': '#8b0000', 'darksalmon': '#e9967a', 'darkseagreen': '#8fbc8f', 'darkslateblue': '#483d8b', 'darkslategray': '#2f4f4f', 'darkslategrey': '#2f4f4f', 'darkturquoise': '#00ced1', 'darkviolet': '#9400d3', 'deeppink': '#ff1493', 'deepskyblue': '#00bfff', 'dimgray': '#696969', 'dimgrey': '#696969', 'dodgerblue': '#1e90ff', 'firebrick': '#b22222', 'floralwhite': '#fffaf0', 'forestgreen': '#228b22', 'fuchsia': '#ff00ff', 'gainsboro': '#dcdcdc', 'ghostwhite': '#f8f8ff', 'gold': '#ffd700', 'goldenrod': '#daa520', 'gray': '#808080', 'green': '#008000', 'greenyellow': '#adff2f', 'grey': '#808080', 'honeydew': '#f0fff0', 'hotpink': '#ff69b4', 'indianred': '#cd5c5c', 'indigo': '#4b0082', 'ivory': '#fffff0', 'khaki': '#f0e68c', 'lavender': '#e6e6fa', 'lavenderblush': '#fff0f5', 'lawngreen': '#7cfc00', 'lemonchiffon': '#fffacd', 'lightblue': '#add8e6', 'lightcoral': '#f08080', 'lightcyan': '#e0ffff', 'lightgoldenrodyellow': '#fafad2', 'lightgray': '#d3d3d3', 'lightgreen': '#90ee90', 'lightgrey': '#d3d3d3', 'lightpink': '#ffb6c1', 'lightsalmon': '#ffa07a', 'lightseagreen': '#20b2aa', 'lightskyblue': '#87cefa', 'lightslategray': '#778899', 'lightslategrey': '#778899', 'lightsteelblue': '#b0c4de', 'lightyellow': '#ffffe0', 'lime': '#00ff00', 'limegreen': '#32cd32', 'linen': '#faf0e6', 'magenta': '#ff00ff', 'maroon': '#800000', 'mediumaquamarine': '#66cdaa', 'mediumblue': '#0000cd', 'mediumorchid': '#ba55d3', 'mediumpurple': '#9370db', 'mediumseagreen': '#3cb371', 'mediumslateblue': '#7b68ee', 'mediumspringgreen': '#00fa9a', 'mediumturquoise': '#48d1cc', 'mediumvioletred': '#c71585', 'midnightblue': '#191970', 'mintcream': '#f5fffa', 'mistyrose': '#ffe4e1', 'moccasin': '#ffe4b5', 'navajowhite': '#ffdead', 'navy': '#000080', 'oldlace': '#fdf5e6', 'olive': '#808000', 'olivedrab': '#6b8e23', 'orange': '#ffa500', 'orangered': '#ff4500', 'orchid': '#da70d6', 'palegoldenrod': '#eee8aa', 'palegreen': '#98fb98', 'paleturquoise': '#afeeee', 'palevioletred': '#db7093', 'papayawhip': '#ffefd5', 'peachpuff': '#ffdab9', 'peru': '#cd853f', 'pink': '#ffc0cb', 'plum': '#dda0dd', 'powderblue': '#b0e0e6', 'purple': '#800080', 'rebeccapurple': '#663399', 'red': '#ff0000', 'rosybrown': '#bc8f8f', 'royalblue': '#4169e1', 'saddlebrown': '#8b4513', 'salmon': '#fa8072', 'sandybrown': '#f4a460', 'seagreen': '#2e8b57', 'seashell': '#fff5ee', 'sienna': '#a0522d', 'silver': '#c0c0c0', 'skyblue': '#87ceeb', 'slateblue': '#6a5acd', 'slategray': '#708090', 'slategrey': '#708090', 'snow': '#fffafa', 'springgreen': '#00ff7f', 'steelblue': '#4682b4', 'tan': '#d2b48c', 'teal': '#008080', 'thistle': '#d8bfd8', 'tomato': '#ff6347', 'turquoise': '#40e0d0', 'violet': '#ee82ee', 'wheat': '#f5deb3', 'white': '#ffffff', 'whitesmoke': '#f5f5f5', 'yellow': '#ffff00', 'yellowgreen': '#9acd32'}
TABLEAU_COLORS = {'tab:blue': '#1f77b4', 'tab:orange': '#ff7f0e', 'tab:green': '#2ca02c', 'tab:red': '#d62728', 'tab:purple': '#9467bd', 'tab:brown': '#8c564b', 'tab:pink': '#e377c2', 'tab:gray': '#7f7f7f', 'tab:olive': '#bcbd22', 'tab:cyan': '#17becf'}
CNAMES = CSS4_COLORS | TABLEAU_COLORS | BASE_COLORS


class templateColor:
    """Class template for all color formats.
        
    How to describe a color varies widely across the different color 
    models. The underlying data type can differ (e.g. str or tuple) and
    it is therefor pointless to include it in this general template.
    Instead this class is kept minimalistic and only contains some 
    shared functionally.
    
    The first two methods are placeholders that are needed in 
    `_repr_html_` and should be updated in the subclass.
    """
    format = 'not specified'
    @property
    def rgb(self):
        return (255,255,255)
    
    def __repr__(self):
        return 'please update `__repr__`'
    
    def __eq__(self,other):
        """Compare the RGB value of two colors"""
        if not isinstance(other,templateColor):
            return False
        else:
            return self.rgb[:] == other.rgb[:]

    def _repr_html_(self):
        r,g,b = self.rgb
        if 0.2989*r + 0.5870*g + 0.1140*b > 128:
            font_color = 'black'
        else:
            font_color = 'white'
        
        return (
            '<svg width="162" height="100" xmlns="http://www.w3.org/2000/svg">' 
            '<rect width="162" height="100" x="0" y="0" rx="16" ry="16"'
            f'fill="rgb({r},{g},{b})"/>'
            f'<text x="50%" y="50%" text-anchor="middle"' 
            f'fill="{font_color}" font-size="12">{self}</text>'
            '</svg>' 
        )   
        

class nameColor(templateColor,str):
    format = 'name'
    def __new__(cls,name):
        """
        Parameters
        ----------
        name : str
            Name of the color (based on 166 entries from Matplotlib).
        """
        if name.lower() in CNAMES:
            return super().__new__(cls,name.lower())
        else:
            raise ValueError(f'unknown color name `{name}`')
    @property
    def rgb(self):
        """Get an object with the corresponding RGB values."""
        # the list of colors contains hex values
        hex = CNAMES[self.lower()]
        return rgbColor(int(hex.lstrip('#')[i:i+2],16) for i in [0,2,4])
    
    
class hexColor(templateColor,str):
    format = 'hex'
    def __new__(cls,hex):
        """
        Parameters
        ----------
        hex : str
            A hexadecimal number like #000000 that is 6 (or 8) digits in
            length and optionally starts with `#`.
        """
        if re.match(r'^#?([0-9a-fA-F]{6}|[0-9a-fA-F]{8})$',hex):
            if not hex.startswith('#'):
                hex = '#' + hex
            return super().__new__(cls,hex)
        else:
            raise ValueError(f'`{hex}` is no valid hex color')
    @property
    def rgb(self):
        """Get an object with the corresponding RGB values."""
        return rgbColor(int(self.lstrip('#')[i:i+2],16) for i in [0,2,4])
   
   
class cmykColor(templateColor,tuple):
    format = 'cmyk'
    def __new__(cls,cmyk):
        """ 
        Parameters
        ----------
        cmyk : tuple
            A tuple (cyan, magenta, yellow, key) in percent.
        """
        return super().__new__(cls,cmyk)
    @property
    def rgb(self):
        """Get an object with the corresponding RGB values."""
        return rgbColor((255*(1-i/100)*(1-self[-1]/100) for i in self[:-1]))
    def __repr__(self):
        c,m,y,k = self
        return f'cmyk({c:.1f}%, {m:.1f}%, {y:.1f}%, {k:.1f}%)' 
    
    
class hslColor(templateColor,tuple):
    format = 'hsl'
    def __new__(cls,hsl):
        """ 
        Parameters
        ----------
        hsl : tuple
            A tuple (hue, saturation, lightness) in degree and percent.
        """
        return super().__new__(cls,hsl)
    @property
    def rgb(self):
        """Get an object with the corresponding RGB values."""
        rgb = colorsys.hls_to_rgb(self[0]/360,self[2]/100,self[1]/100)   
        return rgbColor(255*c for c in rgb)
    def __repr__(self):
        h,s,l = self
        return f'hsl({h:.0f}°, {s:.0f}%, {l:.0f}%)'
    
    
class hsvColor(templateColor,tuple):
    format = 'hsv'
    def __new__(cls,hsv):
        """ 
        Parameters
        ----------
        hsv : tuple
            A tuple (hue, saturation, value) in degree and percent. 
            Sometimes also called hsb with b for brightness.
        """
        return super().__new__(cls,hsv)
    @property
    def rgb(self):
        """Get an object with the corresponding rgb values."""
        rgb = colorsys.hsv_to_rgb(self[0]/360,self[1]/100,self[2]/100)   
        return rgbColor(255*c for c in rgb)
    def __repr__(self):
        h,s,v = self
        return f'hsv({h:.0f}°, {s:.0f}%, {v:.0f}%)'


class rgbColor(templateColor,tuple):
    """Color class for RGB.
    
    This class serves as a intersection for all other formats. Therefore
    all other color classes should contain a method to convert to RGB,
    while this class contains a reverse function to get back. It is also
    the only one that provides a collection of arithmetic operations.
    """
    format = 'rgb'
    def __new__(cls,rgb):
        """ 
        Parameters
        ----------
        rgb : tuple
            A tuple (red, green, blue) in percent. 
        """
        return super().__new__(cls,rgb)
        
    # Properties
    @property
    def rgb(self):
        return self
    @property
    def grey(self):
        """Grayscale weighed average Y = 0.2989*r + 0.5870*g + 0.1140*b"""
        return 0.2989*self[0] + 0.5870*self[1] + 0.1140*self[2]
    @property
    def name(self):
        """Assign a name based on the nearest colors in CNAMES"""
        # create a dictionary with the distance to each named color
        distances = {name: 
            (int(hex[1:3],16)-int(self.hex[1:3],16))**2 +
            (int(hex[3:5],16)-int(self.hex[3:5],16))**2 +
            (int(hex[5:7],16)-int(self.hex[5:7],16))**2
            for name,hex in CNAMES.items()}
        return nameColor(min(distances,key=distances.get))
    @property
    def hex(self):
        """Return 6 digit hexadecimal representation."""
        string = '#'+''.join(f'{round(i):02x}' for i in self)
        return hexColor(string)
    @property
    def cmyk(self):
        """Return cyan, magenta, yellow and key representation."""
        cmy = tuple(1-i/255 for i in self)
        k = min(cmy)
        return cmykColor(tuple(100*(i-k)/(1-k) for i in cmy) + (100*k,))
    @property
    def hsl(self):
        """Return hue, saturation, lightness representation"""
        h, l, s = colorsys.rgb_to_hls(*(c/255 for c in self))
        return hslColor((360*h,100*s,100*l))
    @property
    def hsv(self):
        """Return hue, saturation, value representation"""
        h, s, v = colorsys.rgb_to_hsv(*(c/255 for c in self)) 
        return hsvColor((360*h,100*s,100*v))

    
    def normalize(self):
        """Normalize the RGB value to the range [0 to 255]
        The arithmetic operations can return values outside the allowed 
        range of [0 to 255]. This function scales them back down based
        on the largest one.
        
        The values could also be clipped with
        [max(min(c,255),0) for c in self]
        """
        if max(self)>255:
            return rgbColor([c*255/max(self) for c in self])
        else:
            return self
    
    def __add__(self,summand):
        """Add RGB values of two rgbColor objects""" 
        r1,g1,b1 = self
        r2,g2,b2 = summand 
        # based on human vision, some suggest adding in squares
        #sum = rgbColor((c1**2+c2**2)**(1/2) for c1,c2 in zip(self,summand))
        sum = rgbColor((r1+r2,g1+g2,b1+b2))
        return sum
    
    def __sub__(self,subtrahend):
        """Subtract RGB values of two Color objects""" 
        r1,g1,b1 = self
        r2,g2,b2 = subtrahend 
        difference = rgbColor((r1-r2,g1-g2,b1-b2))
        return difference
    
    def __mul__(self,multiplicand):
        """Multiply each RGB values with multiplicand (int or float)"""
        r1,g1,b1 = self
        product = rgbColor((r1*multiplicand,g1*multiplicand,b1*multiplicand))
        return product 
    
    def __rmul__(self,multiplicand):
        return self.__mul__(multiplicand)
    
    def __truediv__(self,divisor):
        """Divide each RGB values with divisor (int or float)"""
        r1,g1,b1 = self
        quotient = rgbColor((r1/divisor,g1/divisor,b1/divisor))
        return quotient 
    
    def __pow__(self,exponent):
        """Exponentiation each RGB values with exponent (int or float)"""
        r1,g1,b1 = self
        product = rgbColor((r1**exponent,g1**exponent,b1**exponent))
        return product 
    
    def __repr__(self):
        r,g,b = self
        return f'rgb({r:.0f}, {g:.0f}, {b:.0f})'
    
    

def to_color(*args,**kwargs):
    """Identify the format of the input and convert it to RGB.
    
    Parameters
    ----------
    *args 
        The name (e.g. `red`), hex or rgb as tuple or three integers.
    **kwargs 
        The name of the format (rgb, hsv, hsl or cmyk) with value.
        
    Returns 
    -------
    rgbColor
    """
    
    if args and isinstance(args[0],templateColor):
        return args[0]
    else:
        # if specified in kwargs, the first one is used
        for k,v in kwargs.items():
            if k.lower() in ['rgb','rgba','hex','hsv','hsb','hls','hsl','cmyk','cmyb']:
                format, value = k.lower(), v
                break
        else:
            # maybe multiple kwargs are used for r, g and b etc.
            if all(c in kwargs for c in ['r','g','b']):
                format, value = 'rgb', (kwargs['r'],kwargs['g'],kwargs['b'])
            elif all(c in kwargs for c in ['c','m','y','k']):
                format, value = 'cmyk', (kwargs['c'],kwargs['m'],kwargs['y'],kwargs['k'])
            elif all(c in kwargs for c in ['h','s','l']):
                format, value = 'hsl', (kwargs['h'],kwargs['s'],kwargs['l'])
            elif all(c in kwargs for c in ['h','s','v']):
                format, value = 'hsv', (kwargs['h'],kwargs['s'],kwargs['v'])             
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
                        elif re.match(r'^#?([0-9a-fA-F]{6}|[0-9a-fA-F]{8})$',arg):
                            format, value = 'hex', arg.lower()
        if 'format' not in locals():
            raise ValueError(f'unknown format: args={args}, kwargs={kwargs}')
        
        # 2nd step: create appropriate class and convert to rgb
        if (format=='rgb') or (format=='rgba'):
            return rgbColor(value[:3]).rgb
        elif format == 'name':
            return nameColor(value).rgb
        elif format == 'hex':
            return hexColor(value).rgb
        elif (format == 'cmyk') or (format == 'cmyb'):
            return cmykColor(value).rgb
        elif (format == 'hsv') or (format == 'hsb'):
            return hsvColor(value).rgb
        elif (format == 'hsl'):
            return hslColor(value).rgb
        elif (format == 'hls'):
            return hslColor((value[0],value[2],value[1])).rgb
        else:
            raise ValueError(f'unexpected error for {format}: {value}')
            
# ---------------------------------------------------------------------
# Palette of colors and colormaps
# ---------------------------------------------------------------------
    
# https://www.colorsexplained.com/color-theory/

def complementary(color):
    r,g,b = color.rgb
    return to_color((255-r,255-g,255-b))

def analogous(color):
    h,s,v = color.hsv
    # this should be updated to ColorPalette
    return [to_color(hsv=(hue,s,v)) for hue in [(h-30)%360,h,(h+30)%360]]

def triadic(color):
    h,s,v = color.hsv
    # this should be updated to ColorPalette
    return [to_color(hsv=(hue,s,v)) for hue in [h,(h+120)%360,(h+240)%360]]

def tetradic(color):
    pass 

def square(color):
    h,s,v = color.hsv
    # this should be updated to ColorPalette
    return [to_color(hsv=(hue,s,v)) for hue in [h,(h+90)%360,(h+180)%360,(h+270)%360]]


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
        return ColorPalette([to_color(color),complementary(to_color(color))])
    
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
                self[i] = to_color(color).rgb.hex
        else:
            return ColorPalette([to_color(color).rgb.hex for color in self])
    
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
    
    
def rgb_gradient(color1,color2,N=16):
    """Compute a list of colors between color1 and color2 in RGB space.
    
    Parameters
    ----------
    color1 and color2 : 
        A valid input to `Color`.
    N : int
        Number of colors in the output.
        
    Returns 
    -------
    ColorPalette
    """
    
    r1,g1,b1 = to_color(color1).rgb
    r2,g2,b2 = to_color(color2).rgb
    dr,dg,db = (r2-r1)/(N-1),  (g2-g1)/(N-1),  (b2-b1)/(N-1)
    return ColorPalette([to_color((r1+i*dr,g1+i*dg,b1+i*db)) for i in range(N)])


def hsv_gradient(color1,color2,N=16,direction='shortest'):
    """Compute a list of colors between color1 and color2 in HSV space.
    
    Parameters
    ----------
    color1 and color2 : 
        A valid input to `Color`.
    N : int
        Number of colors in the output.
        
    Returns 
    -------
    ColorPalette
    """
    
    h1,s1,v1 = to_color(color1).rgb.hsv
    h2,s2,v2 = to_color(color2).rgb.hsv
    if direction=='shortest':
        dh = ((h2-h1-180)%360-180)/(N-1)
    else:
        dh = (h2-h1)/(N-1)
    ds,dv =  (s2-s1)/(N-1),  (v2-v1)/(N-1)
    return ColorPalette([to_color(hsv=((h1+i*dh)%360,s1+i*ds,v1+i*dv)).rgb for i in range(N)])

