# Python Tools

This package contains a collection of functions and classes that I use in multiple projects. There are a number of lines of code that appear time and time again. Thus far I always had to search for them and simply copied them into the new project, resulting in many, sometimes diverging versions. To avoid this, I started collecting them in this package so I can quickly import them.


**Table of Contents**
1. [basics](#tools.basics)
2. [calendar](#calendar)
3. [colors](#colors)
4. [filemanager](#filemanager)
5. [matplotlib](#mplstyle)



## basics

The package `tqdm` provides a nice progress bar, but I prefer a more minimalistic version.

```python
from tools import pbar
import time 

for i in pbar(range(100)):
    time.sleep(0.24)
    if i==50:
        break
```


  50%|████████████████                | 50/100 (00:12)


​    

Shifting the order of a list is simple but can get annoying to always type out. Therefore it is packed in the following function.


```python
from tools import shift 

lst = [1,2,3,4,5]

print('shift= 1:',shift(lst,1))
print('shift=-1:',shift(lst,-1))
```

    shift= 1: [2, 3, 4, 5, 1]
    shift=-1: [5, 1, 2, 3, 4]



## calendar

The `datetime` package already contains most of the functionality of the `Date` class. But always writing out `datetime.date` or `datetime.timedelta` and passing the date in the correct format can be annoying. This package also simplifies some interactions (`int` is assumed to be a `timedelta` in units of days when adding or subtracting it with `Date`).


```python
from tools.calendar import Date

start_date = Date('2024-11-01')
end_date   = Date(2024,11,27)

print(f'{start_date} and {end_date} lie {(end_date-start_date).days} day apart.')
```

    2024-11-01 and 2024-11-27 lie 26 day apart.


The main functionality of this subpackage is to visualize events in a calendar using `matplotlib`. There are a number of templates, depending on the desired range.

We start by creating a calendar for a the specified range. Then we can add events and assign each event a color.


```python
from tools.calendar import MonthCalendar

calendar = MonthCalendar(2023,8)
calendar.add_event('2023-08-10','event1')
for day in range(19,23):
    calendar.add_event(Date(2023,8,day),'event2')
calendar.update_colors({'event1':'#6a8934','event2':'#f69615'})

calendar
```

![png](reports/MonthCalendar.png)
​    

If the events cover multiple months, the following format might be more useful.


```python
from tools.calendar import WeekCalendar, last_day_of_month

calendar = WeekCalendar(Date('2024-7-01'),Date('2024-12-31'))
for month in range(7,13):
    last_day = last_day_of_month(Date(2024,month,1))
    calendar.add_event(last_day,'last')
calendar.update_colors()
calendar
```

![png](reports/WeekCalendar.png)
​    

And finally a yearly calendar


```python
from tools.calendar import YearCalendar

calendar = YearCalendar(2024)
for date in ((1,1),(1,6),(3,29),(4,1),(5,1),(5,9),(5,20),(5,30),(10,3),(11,1),(12,25),(12,26)):
    calendar.add_event(Date(2024,date[0],date[1]),'holiday')
calendar.update_colors({'holiday':'#e4b391'})
fig,ax=calendar.plot()
```

![png](reports/YearCalendar.png)
​    


The style of the plots (maybe with the exception of the `YearCalendar`) are kept rather simple. Since this part differs from project to project anyways, the implementation is more intended as a template that can be copied and then adapted accordingly.



## colors

To define a color in a specific format, we must pass the values to the corresponding class.


```python
from tools.colors import (nameColor, hexColor, rgbColor,
                          cmykColor, hslColor, hsvColor)

rgb = rgbColor((255,215,0))
rgb
```


<div><span title="gold
#ffd700
rgb(255, 215, 0)
hsv(51°, 100%, 100%)
cmyk(0.0%, 15.7%, 100.0%, 0.0%)"><svg width="162" height="100" xmlns="http://www.w3.org/2000/svg"><rect width="162" height="100" x="0" y="0" rx="16" ry="16"fill="rgb(255,215,0)"/><text x="50%" y="50%" text-anchor="middle"fill="black" font-size="12">rgb(255, 215, 0)</text></svg></span></div>



There are a number of classes available and we can create the same color in different formats and the comparison between them returns `True` (For this comparison, each color is converted to RGB and the values are rounded to `int`. Therefore, slightly differing colors might still appear as equal).


```python
name = nameColor('gold')
hexadecimal = hexColor('#ffd700')
rgb = rgbColor((255, 215, 0))
cmyk = cmykColor((0.0, 15.686, 100.0, 0.0))
hsl = hslColor((50.588, 100, 50))
hsv = hsvColor((50.588, 100, 100))

# when compared, the rgb value is used
name==hexadecimal==rgb==cmyk==hsl==hsv
```


    True



It quickly becomes annoying to always remember to pass the different formats to the appropriate class. `to_color()` provides a factory function that takes care of this and tries to identify the correct format. If a suitable format is found, the input is passed on and an instance of the corresponding class is returned. Below are a few examples with valid inputs.


```python
from tools.colors import to_color

color1 = to_color('gold')
color2 = to_color('#ffd700')
color3 = to_color(hex='#ffd700')
color4 = to_color((255, 215, 0))
color5 = to_color(rgb=(255, 215, 0))
color6 = to_color(r=255,g=215,b=0)
color7 = to_color(h=51,s=100,v=100)
color8 = to_color('hsv(50°, 100%, 100%)')
color9 = to_color(hsl=(50.59,100,50))

# it can even guess strings 
to_color('hsl(50.59°, 100%, 50%)')
```


<div><span title="gold
#ffd700
rgb(255, 215, 0)
hsv(51°, 100%, 100%)
cmyk(0.0%, 15.7%, 100.0%, 0.0%)"><svg width="162" height="100" xmlns="http://www.w3.org/2000/svg"><rect width="162" height="100" x="0" y="0" rx="16" ry="16"fill="rgb(255.0,215.0075,0.0)"/><text x="50%" y="50%" text-anchor="middle"fill="black" font-size="12">hsl(51°, 100%, 50%)</text></svg></span></div>



The main purpose of the package is to compare colors side by side and to find well-matching collections. `ColorPalette` is a `list` subclass that makes it easy to collect colors and visualize them side by side.


```python
from tools.colors import ColorPalette

ColorPalette(['#80957f','#76616e','#a76277','#d07d7e','#e4b391'])
```


<svg width="400" height="80" xmlns="http://www.w3.org/2000/svg"><rect width="75.0" height="75" x="5.0" y="2.5" fill="#80957f"/><rect width="75.0" height="75" x="85.0" y="2.5" fill="#76616e"/><rect width="75.0" height="75" x="165.0" y="2.5" fill="#a76277"/><rect width="75.0" height="75" x="245.0" y="2.5" fill="#d07d7e"/><rect width="75.0" height="75" x="325.0" y="2.5" fill="#e4b391"/></svg>



In addition, this class offers some useful methods that facilitate the creation of beautiful palettes. Instead of defining all colors by hand, we can also pass two colors and calculate a gradient in the RGB or HSV color space. For the latter, we can chose whether to take the short or the long route around the color wheel (for the hue value).


```python
color1 = to_color('#de5437')
color2 = to_color('#00aced')
ColorPalette.rgb_gradient(color1,color2,steps=10)
```


<svg width="800" height="80" xmlns="http://www.w3.org/2000/svg"><rect width="75.0" height="75" x="5.0" y="2.5" fill="rgb(222, 84, 55)"/><rect width="75.0" height="75" x="85.0" y="2.5" fill="rgb(197, 94, 75)"/><rect width="75.0" height="75" x="165.0" y="2.5" fill="rgb(173, 104, 95)"/><rect width="75.0" height="75" x="245.0" y="2.5" fill="rgb(148, 113, 116)"/><rect width="75.0" height="75" x="325.0" y="2.5" fill="rgb(123, 123, 136)"/><rect width="75.0" height="75" x="405.0" y="2.5" fill="rgb(99, 133, 156)"/><rect width="75.0" height="75" x="485.0" y="2.5" fill="rgb(74, 143, 176)"/><rect width="75.0" height="75" x="565.0" y="2.5" fill="rgb(49, 152, 197)"/><rect width="75.0" height="75" x="645.0" y="2.5" fill="rgb(25, 162, 217)"/><rect width="75.0" height="75" x="725.0" y="2.5" fill="rgb(0, 172, 237)"/></svg>


```python
ColorPalette.hsv_gradient(color1,color2,steps=10,direction='short')
```


<svg width="800" height="80" xmlns="http://www.w3.org/2000/svg"><rect width="75.0" height="75" x="5.0" y="2.5" fill="rgb(222, 84, 55)"/><rect width="75.0" height="75" x="85.0" y="2.5" fill="rgb(224, 49, 75)"/><rect width="75.0" height="75" x="165.0" y="2.5" fill="rgb(225, 43, 129)"/><rect width="75.0" height="75" x="245.0" y="2.5" fill="rgb(227, 37, 188)"/><rect width="75.0" height="75" x="325.0" y="2.5" fill="rgb(206, 31, 229)"/><rect width="75.0" height="75" x="405.0" y="2.5" fill="rgb(141, 25, 230)"/><rect width="75.0" height="75" x="485.0" y="2.5" fill="rgb(70, 19, 232)"/><rect width="75.0" height="75" x="565.0" y="2.5" fill="rgb(13, 31, 234)"/><rect width="75.0" height="75" x="645.0" y="2.5" fill="rgb(6, 99, 235)"/><rect width="75.0" height="75" x="725.0" y="2.5" fill="rgb(0, 172, 237)"/></svg>


```python
ColorPalette.hsv_gradient(color1,color2,steps=10,direction='long')
```


<svg width="800" height="80" xmlns="http://www.w3.org/2000/svg"><rect width="75.0" height="75" x="5.0" y="2.5" fill="rgb(222, 84, 55)"/><rect width="75.0" height="75" x="85.0" y="2.5" fill="rgb(224, 140, 49)"/><rect width="75.0" height="75" x="165.0" y="2.5" fill="rgb(225, 200, 43)"/><rect width="75.0" height="75" x="245.0" y="2.5" fill="rgb(188, 227, 37)"/><rect width="75.0" height="75" x="325.0" y="2.5" fill="rgb(120, 229, 31)"/><rect width="75.0" height="75" x="405.0" y="2.5" fill="rgb(47, 230, 25)"/><rect width="75.0" height="75" x="485.0" y="2.5" fill="rgb(19, 232, 70)"/><rect width="75.0" height="75" x="565.0" y="2.5" fill="rgb(13, 234, 142)"/><rect width="75.0" height="75" x="645.0" y="2.5" fill="rgb(6, 235, 219)"/><rect width="75.0" height="75" x="725.0" y="2.5" fill="rgb(0, 172, 237)"/></svg>

We can also extract the colors from the colormaps defined in `matplotlib`.


```python
ColorPalette.from_matplotlib('viridis',N=16)
```


<svg width="800" height="80" xmlns="http://www.w3.org/2000/svg"><rect width="50.0" height="80" x="0.0" y="0.0" fill="rgb(68, 1, 84)"/><rect width="50.0" height="80" x="50.0" y="0.0" fill="rgb(72, 25, 107)"/><rect width="50.0" height="80" x="100.0" y="0.0" fill="rgb(70, 47, 124)"/><rect width="50.0" height="80" x="150.0" y="0.0" fill="rgb(64, 67, 135)"/><rect width="50.0" height="80" x="200.0" y="0.0" fill="rgb(56, 86, 139)"/><rect width="50.0" height="80" x="250.0" y="0.0" fill="rgb(48, 103, 141)"/><rect width="50.0" height="80" x="300.0" y="0.0" fill="rgb(41, 120, 142)"/><rect width="50.0" height="80" x="350.0" y="0.0" fill="rgb(35, 136, 141)"/><rect width="50.0" height="80" x="400.0" y="0.0" fill="rgb(30, 152, 138)"/><rect width="50.0" height="80" x="450.0" y="0.0" fill="rgb(34, 167, 132)"/><rect width="50.0" height="80" x="500.0" y="0.0" fill="rgb(53, 183, 120)"/><rect width="50.0" height="80" x="550.0" y="0.0" fill="rgb(83, 197, 103)"/><rect width="50.0" height="80" x="600.0" y="0.0" fill="rgb(121, 209, 81)"/><rect width="50.0" height="80" x="650.0" y="0.0" fill="rgb(165, 218, 53)"/><rect width="50.0" height="80" x="700.0" y="0.0" fill="rgb(210, 225, 27)"/><rect width="50.0" height="80" x="750.0" y="0.0" fill="rgb(253, 231, 36)"/></svg>



## filemanager

Get properties of a file like size or a unique ID.



## mplstyle

Templates for the style of `matplotlib` plots.

# Installation

This package can be installed in the current environment with

```bash
pip install -e .
```

This ensures that changes to the code make it to the working projects.

Since this project also serves as a kind of notebook, here are some other handy notes. This notebook can be converted to `ReadMe.md` with
```bash
jupyter nbconvert --execute --to markdown ReadMe.ipynb
```

To push this repository from the command line use

```bash
git remote add origin https://github.com/fschmnn/tools.git
git branch -M main
git push -u origin main
```

