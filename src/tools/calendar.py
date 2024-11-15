""" 
A collection of functions and classes that make it easy to display a
calendar in matplotlib.
"""

import datetime
import locale
locale.setlocale(locale.LC_TIME, 'de_DE')
import warnings

import numpy as np 
import matplotlib as mpl 
import matplotlib.pyplot as plt 

__all__ = ["to_date","Date","range_of_dates",
           "DayCalendar","MonthCalendar","YearCalendar","WeekCalendar"]

# 0 = Monday , 6 = Sunday
FIRST_WEEKDAY = 0
MONTH_SHORT   = {month:datetime.date(2024,month,1).strftime('%b') for month in range(1,13)}
MONTH_LONG    = {month:datetime.date(2024,month,1).strftime('%B') for month in range(1,13)}

# we use January 1, 1900 as a reference. It was a Monday.
WEEKDAY_SHORT = np.array([datetime.date(1900,1,day+FIRST_WEEKDAY).strftime('%a') for day in range(1,8)])
WEEKDAY_LONG  = np.array([datetime.date(1900,1,day+FIRST_WEEKDAY).strftime('%A') for day in range(1,8)])


def to_date(*date,format=r'%Y-%m-%d'):
    """ 
    Convert a number of formats to datetime.date
    """
    
    if len(date)==3:
        return datetime.date(*date)
    else: 
        # the * in the arguments turns arg into (arg,)
        date = date[0]
        
    if isinstance(date,datetime.date):
        return date
    elif isinstance(date,datetime.datetime):
        return date.date()
    elif isinstance(date,(list,tuple)):
        return datetime.date(*date)
    elif isinstance(date,str):
        return datetime.datetime.strptime(date,format).date()
    else:
        raise ValueError(f'unkown dtype/format for {date}')


class Date(datetime.date):
    """
    Class to store dates in the form (year,month,day)
    
    Notes 
    -----
    This class is a child of the  immutable object datetime.date
    https://stackoverflow.com/questions/399022/why-cant-i-subclass-datetime-date
 
    The operators for add and subtract were modified to also accept
    other types (see computations at line 1200)    
    https://github.com/python/cpython/blob/main/Lib/_pydatetime.py
    """
    
    def __new__(self,*args):
        date = to_date(*args)
        return super().__new__(self,date.year,date.month,date.day)

    def __add__(self,other):
        """add timedelta or days"""
        if isinstance(other,datetime.timedelta):
            return super().__add__(other)
        elif isinstance(other,int):
            return super().__add__(datetime.timedelta(other))
        return NotImplemented
    
    __radd__ = __add__
    
    def __sub__(self,other):
        """subtract timedelta, date or days"""
        if isinstance(other,(datetime.timedelta,datetime.date)):
            return super().__sub__(other)
        elif isinstance(other,int):
            return super().__sub__(datetime.timedelta(other))
        return NotImplemented


def range_of_dates(start_date=None,
               end_date=None,
               ndays=None,
               format=r'%Y-%m-%d',
               return_string=False):
    """Create a list of dates
    
    Parameters
    ----------
    start_date : datetime.date or str in format
        The first day in the list. If `None`, the day is calculated based
        on ndays or as the beginning of the current month.
    end_date : datetime.date or str in format
        The last day in the list. If `None`, the day is calculated based
        on ndays or as the ending of the current month.
    ndays : int
        The number of days in the returned list. Only used if start_date
        or end_date are missing.
    format : str (default "%Y-%m-%d")
        Used when start_date or end_date are in string format.
    return_string : bool
        Apply strftime(format) to the returned values.
    """
    
    # incase the dates are provided as str we convert them to datetime.date
    if isinstance(start_date,str):
        start_date = datetime.datetime.strptime(start_date,format).date()
    if isinstance(end_date,str):
        end_date = datetime.datetime.strptime(end_date,format).date()

    if start_date:
        if end_date:
            # we need to add the end day for the loop
            ndays = (end_date - start_date).days + 1
        elif ndays:
            # we go forward ndays
            pass
        else: 
            # with neither end_date and ndays we use the last day of the month as end_date
            end_date = (start_date.replace(day=1) + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
            ndays = (end_date - start_date).days + 1
            
    elif end_date:
        if ndays:
            # we go backwards ndays
            start_date = end_date - datetime.timedelta(days=ndays-1)
        else:
            # we download the month up to this date
            start_date = end_date.replace(day=1)
            ndays = (end_date - start_date).days + 1
            
    else:
        raise ValueError('either start_date or end_date required')

    dates = [start_date+datetime.timedelta(days=n) for n in range(ndays)]   
    
    if return_string:
        return [date.strftime(format) for date in dates]
    else:
        return dates
  

def find_boundaries(grid):
    """
    Search for the boundaries between months

      4_____5
    2_|     |
    |  3  7_|
    |_____|  6
    1     8
    
    Parameters
    ----------
    grid : 2d array
        must be of shape (7,n)
    """

    boundaries = []
    
    # boundaries in x direction
    for i, column in enumerate(grid.T):
        for j, (lower,upper) in enumerate(zip(column,column[1:])):
            if lower!=upper:
                boundaries.append(((i-0.5,i+0.5),(j+0.5,j+0.5)))
    
    # boundaries in y direction
    for i, row in enumerate(grid):
        for j, (left,right) in enumerate(zip(row,row[1:])):
            if left!=right:
                boundaries.append(((j+0.5,j+0.5),(i-0.5,i+0.5)))

    # next the boundaries around the whole plot 
    # try this: mask = first_week[:-1] != first_week[1:]
    for row_in_first_column in range(6,-1,-1):    
        if grid[row_in_first_column,0] != grid[row_in_first_column-1,0]:
            break

    # it seems like the loop does not reach the bottom???
    for row_in_last_column in range(6):
        if grid[row_in_last_column,-1] != grid[row_in_last_column+1,-1]:
            break
    else:
        row_in_last_column += 1

    # row_in_last_column is at the bottom and hence we need to shift it by 1  (6->7)
    x = np.array([0,0,1,1,grid.shape[1],grid.shape[1],grid.shape[1]-1,grid.shape[1]-1,0])-0.5
    y = np.array([7,row_in_first_column,row_in_first_column,0,0,row_in_last_column+1,row_in_last_column+1,7,7])-0.5

    return boundaries + [(x,y)]


def hex2d_to_rgb3d(hex2d):
    """ 
    convert an 2d array that is filled with hex colors to a 3d array 
    with the corresponding rgb values.
    """
    
    rgb3d = np.full(hex2d.shape+(3,),np.nan)
    for hex_string in np.unique(hex2d):
        if hex_string.startswith('#'):
            rgb3d[hex2d==hex_string] = tuple(int(hex_string[i+1:i+3],16)/255  for i in (0, 2, 4)) 
    
    return rgb3d  

  
class DayCalendar:
    
    def __init__(self,start_date,end_date,firstweekday=0):
        """ 
        This is a minimalistic example for a date grid.
        
        Parameters
        ----------
        start_date : datetime.date
            The first day in the calendar.
        end_date : datetime.date
            The last day in the calendar.
        firstweekday : int
            From 0 (Monday) to 6 (Sunday).
        """
        
        self.start_date = start_date
        self.end_date = end_date
        self.ndays = (self.end_date-self.start_date).days + 1
        self.firstweekday = firstweekday
        
        # we create a list of all dates and places to store further input
        # we turn it into a 2d array to utilize generate_image().
        self.dates = np.array([start_date+datetime.timedelta(days) for days in range(self.ndays)]).reshape(1,-1)
        self.events = dict()
        self.colors = dict()
        
    def add_event(self,date,event=1,format=r'%Y-%m-%d'):    
        """
        Add value to the events array at the given date.This method 
        overwrites existing values.
        
        Parameters
        ----------
        date : datetime.date | tuple | list
            The tuple/list (year,month,day) is parsed as date(*tuple).
        event : object 
            Can be any object and is stored under self.events[date] = event.
        format : str
            The format of the date if a string is passed.
        """
        
        # convert datetime or str to date
        if isinstance(date,str):
            date = datetime.datetime.strptime(date,format).date()
        elif isinstance(date,(tuple,list)):
            date = datetime.date(*date)
            
        # we only date of type datetime.date to the dictionary
        if isinstance(date,datetime.date):
            if self.start_date<=date<=self.end_date:
                self.events[date] = event
            else:
                warnings.warn(f"{date.strftime(r'%Y-%m-%d')} lies outside.")

    def update_colors(self,color_dict=None,cmap='Wistia'):
        """ 
        Update the colors dictionary based on the events dictionary.
        """
        
        unique_events = set(self.events.values())
        if not color_dict:
            color_dict = {}
            cmap = plt.get_cmap(cmap,len(unique_events))
            # convert rgba to hex
            color_dict = {event:f'#{int(255*cmap(i)[0]):02x}{int(255*cmap(i)[1]):02x}{int(255*cmap(i)[2]):02x}' 
                            for i,event in enumerate(unique_events)}
        for date, event in self.events.items():
            self.colors[date] = color_dict.get(event,'#000000')
            
        
    def generate_image(self):
        """ 
        Turn the colors dictionary into an 3d array that contains two
        spatial dimensions and a third one for the rgb values.
        """
        
        # we start by creating a 2d array with the hex values
        hex2d = np.empty(self.dates.shape,dtype='U7')
        for date, hex in self.colors.items():
            hex2d[self.dates==date] = hex
        
        # then we add a dimension and convert hex to rgb
        rgb3d = np.full(hex2d.shape+(3,),np.nan)
        for hex_string in np.unique(hex2d):
            if hex_string.startswith('#'):
                rgb3d[hex2d==hex_string] = tuple(int(hex_string[i+1:i+3],16)/255  for i in (0, 2, 4)) 

        return rgb3d

    def plot(self,ax=None):
        """
        A simple example how to showcase the result.
        """
        
        if not ax:
            fig,ax=plt.subplots(figsize=(10,10/self.ndays))
        rgb3d = self.generate_image()
        ax.imshow(rgb3d,aspect='auto')
        ax.axis('off')
        
        return ax

    def __repr__(self):
        ax = self.plot()
        plt.show()
        return ''
    
class MonthCalendar(DayCalendar):
    
    def __init__(self,year,month,firstweekday=0):
        """  
        Create a grid with all days of the given month
        
        Parameters
        ----------
        year : int
            The year of the month.
        month : int
            The number of the month.
        firstweekday : int
            From 0 (Monday) to 6 (Sunday).
        """
        
        self.year = year
        self.month = month
        self.firstweekday = firstweekday
        
        # from those values we compute the standard values
        self.start_date  = datetime.date(year,month,1)
        self.end_date = (self.start_date + datetime.timedelta(days=31)).replace(day=1) - datetime.timedelta(days=1)
        self.ndays = (self.end_date-self.start_date).days + 1

        # the dates array is more complex due to offsets at the start end end
        offset  = (self.start_date.weekday()-firstweekday)%7
        dates = [self.start_date+datetime.timedelta(days)  for days in range(self.ndays)] 
        self.dates = np.array((offset*[np.nan]+dates+(42-offset-len(dates))*[np.nan])).reshape(6,7)

        self.events = dict()
        self.colors = dict()
        
    def add_event(self,date,event=0,format=r'%Y-%m-%d'): 
        # since we know the year and month we can also accept the day as date   
        if isinstance(date,int):
            super().add_event(datetime.date(self.year,self.month,date),event)
        else:
            super().add_event(date,event,format)
    
    def plot(self,ax=None):
        """ 
        Plot the calendar. In order to show the added events, one has to
        run self.update_colors() beforehand.
        """
        
        fontdict_month = {'fontsize':10,'color':'black','weight':'bold','va':'center','ha':'center'}
        fontdict_weekday = {'fontsize':8,'color':'black','weight':'bold','va':'center','ha':'center'}
        fontdict_day = {'fontsize':8,'color':'black','va':'center','ha':'center'}
        
        if not ax:
            fig,ax=plt.subplots(figsize=(4,4))
        
        # write day in calendar
        for date in self.dates.flat:
            if isinstance(date,datetime.date):
                col = (date.weekday()-self.firstweekday)%7
                row = (date.day + (self.start_date.weekday()-self.firstweekday)%7 -1)//7
                ax.text(col,row,f'{date.day:2d}',zorder=5,**fontdict_day)
        
        # we use January 1, 1900 as a reference. It was a Monday.
        weekdays = np.roll([datetime.date(1900,1,day).strftime('%a') for day in range(1,8)],7-self.firstweekday)
        # caption for the weekdays
        for i, weekday in enumerate(weekdays):
            ax.text(i,-1,weekday,zorder=5,**fontdict_weekday)
        # caption for the Month
        ax.text(3.,-2.25,f"{self.start_date.strftime('%B')} {self.year}",zorder=5,**fontdict_month)

        # color the dates form self.events
        rgb3d = self.generate_image()
        ax.imshow(rgb3d)

        ax.set(xlim=[-0.5,6.5],ylim=[5.5,-3])
        ax.axis('off')
    	
        return ax 
    

class YearCalendar:
    """Combine all 12 MonthGrids for one year in a nice figure"""
    
    def __init__(self,year,firstweekday=0,ncols=4):
        """     
        Parameters
        ----------
        year : int 
            The year that is used
        firstweekday : int
            From 0 (Monday) to 6 (Sunday).
        ncols : int
            Number of columns (can be 1,2,3,4,6 or 12).
        """
        
        self.year = year 
        self.firstweekday = firstweekday
        self.ncols = ncols
        self.nrows = int(12/ncols)
        
        # a dict with MonthGrid objects for each month
        self.months = {month:MonthCalendar(year,month,firstweekday) for month in range(1,13)}

    def add_event(self,date,event=1,format=r'%Y-%m-%d'):    
        """
        Pass the date and value to the correct month
        
        Add value to the events array at the given date.This method 
        overwrites existing values.
        
        Parameters
        ----------
        date : datetime.date | tuple | list
            The tuple/list (month,day) is passed to date(*tuple).
        event : object 
            Stored in self.events.
        format : str
            The format if the date is passed as a string.
        """
        
        # convert datetime or str to date
        if isinstance(date,str):
            date = datetime.datetime.strptime(date,format).date()
        # the case of a tuple/list we add the year and pass to datetime.date
        elif isinstance(date,(tuple,list)):
            if len(date)==2:
                date = (self.year,)+tuple(date)
            date = datetime.date(*date)

        # add the event to the corresponding month
        self.months[date.month].add_event(date,event)

    def plot(self,axis_size=2.36):

        fontdict_year = {'weight':'bold','color':'#1e5d3f'}
        fontdict_month = {'fontsize':10,'color':'white','weight':'bold','va':'center','ha':'center'}
        fontdict_weekday = {'fontsize':8,'color':'white','weight':'bold','va':'center','ha':'center'}
        fontdict_day = {'fontsize':8,'color':'black','va':'center','ha':'center'}
            
        # for one month the default is 6cm = 2.36in. Since we are using
        # imshow, we need to already consider the limits here
        width  = axis_size*self.ncols 
        height = axis_size*self.nrows #* 1.214
        
        fig, axes = plt.subplots(figsize=(width,height),
                                 ncols=self.ncols,nrows=self.nrows)
        fig.patch.set_facecolor('#ececec')
        
        for month, grid in self.months.items():
            # select the corresponding axes
            #ax = axes[(month-1)//self.ncols,(month-1)%self.ncols]
            ax = axes.flat[month-1]
            
            # write day in calendar
            for date in grid.dates.flat:
                if isinstance(date,datetime.date):
                    col = (date.weekday()-grid.firstweekday)%7
                    row = (date.day + (grid.start_date.weekday()-grid.firstweekday)%7 -1)//7
                    ax.text(col,row,f'{date.day:2d}',zorder=5,**fontdict_day)
            
            # we use January 1, 1900 as a reference. It was a Monday.
            weekdays = np.roll([datetime.date(1900,1,day).strftime('%a') for day in range(1,8)],7-self.firstweekday)
            # caption for the weekdays
            for i, weekday in enumerate(weekdays):
                ax.text(i,-1,weekday,zorder=5,**fontdict_weekday)
            # caption for the Month
            ax.text(3.,-2.25,f"{grid.start_date.strftime('%B')} {self.year}",zorder=5,**fontdict_month)
            
            # color the dates form self.events
            grid.update_colors()
            rgb3d = grid.generate_image()
            ax.imshow(rgb3d,zorder=2,aspect='auto')
            
            # white background for calendar
            ax.add_patch(mpl.patches.Rectangle((-0.5,-0.5),7.5,5,color='white',zorder=1))
            ax.add_patch(mpl.patches.Circle((5.5,4.5),1,edgecolor='none',facecolor='white',zorder=1))
            ax.add_patch(mpl.patches.Rectangle((-0.5,4.5),6,1,edgecolor='none',facecolor='white',zorder=1))
            
            # caption for the Month
            ax.add_patch(mpl.patches.Circle((0.5,-2.),1,edgecolor='none',facecolor='#1e5d3f',zorder=2))
            ax.add_patch(mpl.patches.Rectangle((-0.5,-2),1,0.5,edgecolor='none',facecolor='#1e5d3f',zorder=2))
            ax.add_patch(mpl.patches.Rectangle((0.5,-3),7.5,1.5,edgecolor='none',facecolor='#1e5d3f',zorder=2))

            # caption for the weekdays
            ax.add_patch(mpl.patches.Rectangle((-0.5,-1.5),7.5,1,color='#00a770',zorder=3))
            
            # we draw the grid by hand
            for x in range(6):
                ax.plot([x+0.5,x+0.5],[-0.5,5.5],color='#ececec',zorder=2)
            for y in range(5):
                ax.plot([-0.5,6.5],[y+0.5,y+0.5],color='#ececec',zorder=2)
            
            ax.set(xlim=[-0.5,6.5],ylim=[5.5,-3])
            ax.axis('off')
            
        fig.suptitle(self.year,fontsize=16,y=0.98,**fontdict_year)
        plt.tight_layout()
        
        return fig, axes
    

class WeekCalendar(DayCalendar):
    """ 
    Create a (7xn) grid with all the dates in the given range
    """
    
    def __init__(self,start_date,end_date,firstweekday=0):
        """ 
        Parameters
        ----------
        start : datetime.date
            The first day in the calendar.
        finish : datetime.date
            The last day in the calendar.
        firstweekday : int
            From 0 (Monday) to 6 (Sunday). 
        """
                
        self.start_date = start_date
        self.end_date = end_date
        self.firstweekday = firstweekday

        
        ndays = (end_date-start_date).days + 1

        # offset in the first column 
        # this happens when first_day.weekday() differs from firstweekday
        offset  = (start_date.weekday()-firstweekday)%7
        remnant = (7-(ndays+offset))%7
        
        dates = [start_date+datetime.timedelta(days)  for days in range(ndays)] 
        # a 2d array for the dates within the range
        self.dates = np.array((offset*[np.nan]+dates+remnant*[np.nan])).reshape(7,-1,order='F')
        # a 2d array with the months based on the previous array
        self.months = np.array((offset*[-1]+[date.month for date in dates]+remnant*[-1])).reshape(7,-1,order='F')
        self.events = dict()
        self.colors = dict()

        self.boundaries = find_boundaries(self.months)

    def plot(self,ax=None,weekday_ticks=True,grid=False):
        """ 
        This is just a simple example to showcase the grid
        """
        
        if not ax:
            fig,ax=plt.subplots(figsize=np.array(self.dates.shape)[::-1] * 0.2)
            fig.patch.set_facecolor('#ececec')
            ax.patch.set_facecolor('#ececec')
 
        rgb3d = self.generate_image()
        ax.imshow(rgb3d,zorder=1)

       
        for x,y in self.boundaries:
            ax.plot(x,y,color='gray',linewidth=1,zorder=2,clip_on=False)
        
        # remove xticks and set yticks to weekdays
        ax.set_xticks([])
        if weekday_ticks:
            weekdays = np.roll([datetime.date(1900,1,day).strftime('%a') for day in range(1,8)],7-self.firstweekday)
            ax.set_yticks(np.arange(0,7),weekdays)
        else:
            ax.set_yticks([])
        ax.tick_params(axis='both', which='both', length=0)
        ax.spines[["top","bottom","left","right"]].set_visible(False)
        
        if grid:
            ax.set_xticks(np.arange(self.dates.shape[1])-0.5, minor=True)
            ax.set_yticks(np.arange(7)-0.5, minor=True)
            ax.grid(which='minor', color='#ececec', linestyle='-', linewidth=1)
        
        return fig,ax 
    
    